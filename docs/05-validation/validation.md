# Validation Rules

## Two Validation Layers

Validation happens in two distinct layers, each with different failure
behavior — this distinction matters for both API consumers and for
understanding `services/ingestion.py`. See ADR-011 for the architectural
rationale behind keeping these two layers separate instead of building a
centralized validation engine.

### Layer 1 — Field-level (Pydantic, FastAPI-enforced)

Runs automatically when FastAPI parses the request body against the
schema (`HiredEmployeeSchema`, `Departments`, `Jobs`). Checks structural
correctness — anything that can be evaluated from the payload alone,
without querying the database.

**Failure behavior**: the entire request is rejected with `422` before
any record is processed. This is intentional — a malformed request body
(wrong JSON shape, wrong types, invalid values) is a client-side error,
not a data quality issue to log and continue past.

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

---

## Layer 1 — Full Field-Level Rule Set

| Rule | Applies to | Enforced by | Notes |
|---|---|---|---|
| Required fields (not null/missing) | all fields, all schemas | `field_validator(mode="before")` | |
| Non-empty, non-whitespace strings | `name`, `department`, `job` | `field_validator(mode="before")`, `.strip()` check | See Phase 7 gap audit below |
| Positive integer IDs (`> 0`) | `id`, `department_id`, `job_id` | `field_validator` (post-coercion) | See Phase 7 gap audit below |
| ISO 8601 datetime, literal `Z` suffix | `hire_datetime` | regex `ISO_DATETIME_PATTERN` | Offsets like `+00:00` are rejected — see rationale below |
| No unexpected fields | all schemas | `model_config = ConfigDict(extra="forbid")` | See Phase 7 gap audit below |
| Type coercion (e.g. numeric string `"5"` → `int 5`) | `id` fields | Pydantic default behavior | Accepted intentionally — see rationale below |
| Batch size between 1 and 1000 | request body (list length) | router-level check (`HTTPException(422)`) | Enforced before Layer 1/2 processing begins |

### Design rationale for specific rules

**ISO datetime — literal `Z` only, offsets rejected.** `2021-07-27T16:02:08+00:00`
is valid ISO 8601 but is rejected by the current regex. This is a
deliberate scope decision, not an oversight: the challenge's data
dictionary specifies the `Z`-suffixed format explicitly
(`2021-07-27T16:02:08Z`), and the historical CSV source uses this format
exclusively. Accepting additional formats would require normalizing them
before parsing, which is out of scope unless a real client needs it.

**Type coercion — numeric strings accepted for ID fields.** A request
body sending `{"id": "603"}` instead of `{"id": 603}` is accepted;
Pydantic coerces the string to `int` before validation runs. This is
standard, expected behavior for a JSON API (clients in some ecosystems
serialize all values as strings) and was confirmed acceptable during the
Phase 7 gap audit — no change was made.

---

## Phase 7 Gap Audit — Findings and Fixes

Phase 7 ("Validation Engine" in `wbs.md`) was scoped as an audit of the
existing validation coverage rather than new component construction — see
ADR-011. Six original rules were checked against edge cases; four gaps
were found and fixed directly in the Layer 1 schemas.

| # | Edge case | Before | After | Fix |
|---|---|---|---|---|
| 1 | `id <= 0` (negative or zero) | Accepted and inserted | Rejected, `422` | Added `id_must_be_positive` validator (post-coercion) to all three schemas |
| 2 | Whitespace-only string (`"   "`) | Accepted and inserted | Rejected, `422` | Changed required-field check from `value == ""` to `value.strip() == ""` |
| 3 | ISO datetime with `+00:00` offset | Rejected, `422` | No change | Confirmed correct — see rationale above |
| 4 | Unexpected/extra field in request body | Accepted, extra field silently ignored | Rejected, `422` (`extra_forbidden`) | Added `model_config = ConfigDict(extra="forbid")` to all three schemas |
| 5 | `id` sent as numeric string (`"603"`) | Accepted, coerced to int | No change | Confirmed correct — standard Pydantic behavior, acceptable for a public API |
| 6 | Batch size boundaries (0, 1001 rows) | Rejected, `422` | No change | Confirmed already correctly enforced (Phase 6) |

All fixes verified via a manual exploratory probe (`scripts/edge_case_probe.sh`)
against the live API with a real Postgres backend, plus the existing unit
test suite (`tests/test_ingestion_service.py`