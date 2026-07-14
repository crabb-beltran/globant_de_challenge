# Sprint Backlog

**Active Phase:** Testing (WBS Phase 10) — CLOSED

**Branch:** feature/testing

---

## Goal

Consolidate the test suite built incrementally across Phases 5-9, and
resolve a structural risk discovered during Phase 9: integration test
fixtures connecting directly to the development database.

### Consolidation Tasks

- [x] Ran full suite without `RUN_INTEGRATION_TESTS` — confirmed 28
      passed, 13 skipped cleanly (Tier 1 default behavior)
- [x] Ran full suite with `RUN_INTEGRATION_TESTS=1` — confirmed 41 passed

### Database Isolation Tasks (priority — see incident)

- [x] Added `db/config.py::get_test_database_url()`
- [x] Built `tests/integration_conftest.py` with an isolated
      `pg_test_session` fixture, auto-creating `globant_test` if missing
- [x] Migrated `test_restore_integration.py` and
      `test_reports_integration.py` off `db.session.SessionLocal`
- [x] Added a structural safety guardrail (`assert "test" in db_name`)
      after the isolation fix was itself bypassed once by a leftover
      local fixture definition
- [x] Added `test_integration_conftest_guardrail.py` — meta-test with
      no live database dependency, proving the guardrail logic itself

### Coverage Gap Closure

- [x] Added `test_db_constraint_violation_integration.py` — closes the
      `DB_CONSTRAINT_VIOLATION` gap deferred since Phase 6

### Documentation Tasks

- [x] Added `docs/09-testing/testing.md` — two-tier strategy, full
      incident writeup

Priority

High — this phase both consolidates existing coverage and resolves a
recurring data-loss risk (two separate incidents during Phase 9).

Status

✅ Completed — 2026-07-14

---

# Definition of Done (DoD)

A task is considered complete when:

- [x] Code implemented
- [x] Code reviewed
- [x] Tests passed (28 unit / 41 total)
- [x] Documentation updated
- [x] Docker verified
- [ ] GitHub pushed
- [ ] Pull Request merged