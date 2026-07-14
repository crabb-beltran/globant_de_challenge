# Validation Rules

## Two Validation Layers

Validation happens in two distinct layers, each with different failure
behavior — this distinction matters for both API consumers and for
understanding `services/ingestion.py`.

### Layer 1 — Field-level (Pydantic, FastAPI-enforced)

Runs automatically when FastAPI parses the request body against the
schema (`HiredEmployeeSchema`, `Departments`, `Jobs`). Checks structural
correctness: required fields present, correct types, ISO 8601 datetime
format for `hire_datetime`.

**Failure behavior**: the entire request is rejected with `422` before
any record is processed. This is intentional — a malformed request body
(wrong JSON shape, wrong types) is a client bug, not a data quality issue
to log and continue past.

### Layer 2 — Business rules (`validators/business_rules.py`, DB-state dependent)

Runs inside `services/ingestion.py`, per record, after Layer 1 passes.
Checks conditions that depend on current database state:

| Rule | Function | Applies to | `reason_code` |
|---|---|---|---|
| Department FK exists | `department_exists()` | employees | `FK_VIOLATION` |
| Job FK exists | `job_exists()` | employees | `FK_VIOLATION` |
| ID not already in DB | (inline in `ingest_batch`) | all three | `DUPLICATE_ID` |
| No DB constraint violation | (caught via `IntegrityError`) | all three | `DB_CONSTRAINT_VIOLATION` |

**Failure behavior**: only the offending record is rejected. Isolated
via `db.begin_nested()` (SAVEPOINT), so the rest of the batch commits
normally. This is what makes `207 Multi-Status` possible.

## Structured Rejection Reason Codes

All business-rule rejections raise a typed exception
(`validators/exceptions.py`) carrying a fixed `.code`, rather than being
inferred from free-text error messages. This keeps `reason_code` stable
even if error message wording changes later — important for any client
or dashboard doing programmatic handling (e.g. retry `DUPLICATE_ID`
differently than `FK_VIOLATION`).

| Code | Meaning |
|---|---|
| `FK_VIOLATION` | `department_id` or `job_id` does not exist |
| `DUPLICATE_ID` | `id` already exists in DB or elsewhere in the same batch |
| `DB_CONSTRAINT_VIOLATION` | Database rejected the insert at the constraint level (race condition or unmodeled constraint) |
| `VALIDATION_ERROR` | Fallback — a validator raised a plain `ValueError` instead of a typed subclass (should not normally occur; signals a validator that needs to be updated to use `BusinessRuleViolation`) |

## Relationship to Historical Loader Validation (Fase 5)

The API reuses the exact same `validators/business_rules.py` functions
used by `loaders/historical.py` — no duplicated FK-check logic. The one
behavioral difference: the CSV loader treats duplicate IDs as
**skip** (idempotent re-run, ADR-010), while the API treats duplicate
IDs as **reject** (`DUPLICATE_ID`). This is a deliberate divergence, not
an inconsistency — see `api.md` for the rationale.