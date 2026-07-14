# Sprint Backlog

**Active Phase:** Validation Engine (WBS Phase 7) — CLOSED

**Branch:** feature/validation-engine

---

## Goal

Audit existing validation coverage (built across Fase 5 and Fase 6) against
the six rules defined in `wbs.md` Phase 7, close any real gaps found, and
document the decision **not** to build a separate centralized validation
engine — consolidating instead the current two-layer model (Pydantic
field-level + business-rule DB-state level, see `docs/05-validation/validation.md`).

This phase was primarily a **gap audit**, not new feature construction —
all six WBS rules already had a working implementation before this phase
opened. Scope creep risk was tracked as R-016 in `risk-register.md`.

### Coverage Audit (confirmed already implemented)

- [x] Required fields — `schemas/*.py`, `field_validator(mode="before")`
- [x] Null validation — same mechanism, rejects `None`/`""`
- [x] ISO Datetime — `schemas/hired_employee.py`, `ISO_DATETIME_PATTERN` regex
- [x] FK validation — `validators/business_rules.py`
- [x] Batch Size (1-1000) — `routers/*.py`
- [x] Duplicate validation — `services/ingestion.py`, `DUPLICATE_ID`

### Gap Analysis Tasks (completed)

- [x] Negative or zero `id` values — confirmed gap; fixed with
      `id_must_be_positive` validator across all three schemas
- [x] Whitespace-only strings (`name="   "`) — confirmed gap; fixed by
      comparing `value.strip() == ""` instead of `value == ""`
- [x] `hire_datetime` with a non-`Z` UTC offset — audited, confirmed
      correct existing behavior (rejected), no change needed
- [x] Extra/unexpected fields in the request body — confirmed gap;
      fixed with `model_config = ConfigDict(extra="forbid")`
- [x] Type coercion edge cases (numeric string `id`) — audited, confirmed
      correct existing behavior (accepted via Pydantic coercion), no
      change needed
- [x] Batch size boundary tests (`len == 0`, `len == 1001`) — audited,
      confirmed already correctly enforced since Fase 6

### Documentation Tasks (completed)

- [x] Added ADR-011: "Validation Engine — Decentralized Model, No Separate
      Component"
- [x] Updated `docs/05-validation/validation.md` with gap-audit findings
      table and rationale for confirmed non-issues
- [x] Added `tests/test_schemas.py`: 19 regression tests for the three
      fixed gaps plus the two confirmed non-issues. Full suite: 27/27
      passing.

Priority

Medium

Status

✅ Completed — 2026-07-13

---

# Definition of Done (DoD)

A task is considered complete when:

- [x] Code implemented
- [x] Code reviewed
- [x] Tests passed
- [x] Documentation updated
- [x] Docker verified
- [ ] GitHub pushed
- [ ] Pull Request merged