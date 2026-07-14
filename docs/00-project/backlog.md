# Sprint Backlog

**Active Phase:** SQL Reports (WBS Phase 9) — CLOSED

**Branch:** feature/sql-reports

---

## Goal

Implement Challenge 2's two required SQL reports (hiring by quarter,
departments above average) plus one bonus statistical endpoint, reusing
the query design drafted during Phase 6 exploration and held out of
that PR.

### Implementation Tasks

- [x] Reactivated `routers/reports.py` from Phase 6 draft
- [x] Added `schemas/reports.py` — typed `response_model` for all
      three endpoints
- [x] Verified `GET /reports/hiring-by-quarter` output against real data
- [x] Verified `GET /reports/departments-above-average` output against
      real data
- [x] Verified `GET /reports/hiring-distribution-stats` (bonus) output
      and interpreted the statistical findings

### Data Hygiene (unplanned, discovered during this phase)

- [x] Diagnosed test-data contamination in `departments` (7 rows) and
      `hired_employees` (1 row) accumulated from manual Swagger testing
      across Phases 6–8
- [x] Removed contaminated rows via targeted `DELETE` by exact ID
      (verified no FK blocking first)
- [x] Regenerated AVRO backup post-cleanup

### Testing Tasks

- [x] Added `tests/test_reports_integration.py` — 9 integration tests
      against real Postgres (opt-in, `RUN_INTEGRATION_TESTS=1`), using a
      small hand-verified synthetic dataset
- [x] Fixed a test bug (not a query bug): `Decimal`/`float` comparison
      in `pytest.approx()` required explicit casting

### Documentation Tasks

- [x] Added `docs/08-reports/reports.md` — design rationale, endpoint
      contracts, statistical findings on the real dataset

Priority

Medium

Status

✅ Completed — 2026-07-14

---

# Definition of Done (DoD)

A task is considered complete when:

- [x] Code implemented
- [x] Code reviewed
- [x] Tests passed (9/9 integration)
- [x] Documentation updated
- [x] Docker verified
- [ ] GitHub pushed
- [ ] Pull Request merged