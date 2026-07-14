# Sprint Backlog

**Active Phase:** CI/CD (WBS Phase 11) — CLOSED

**Branch:** feature/github-actions

---

## Goal

Automate quality checks (formatting, linting) and the full two-tier
test suite on every PR and push to `develop`/`main`, plus a Docker
build sanity check — without adding deployment automation yet (Phase 12).

### Implementation Tasks

- [x] Added `.github/workflows/ci.yml` with 3 parallel jobs
- [x] Configured a Postgres service container for Tier 2 integration
      tests in CI, mirroring the local `globant_test` isolation strategy
- [x] Added `.flake8` at repository root

### Quality Debt Cleanup (discovered during this phase)

- [x] Applied Black formatting project-wide (34 files, first
      enforcement since `conventions.md` specified it)
- [x] Removed 3 genuine unused imports found by Flake8
- [x] Fixed 1 over-length line (`main.py`)
- [x] Added `black`, `flake8` to `requirements.txt`

### Incident Resolution

- [x] Diagnosed and fixed `per-file-ignores` pattern matching failure
      (`*/` prefix + relative paths with `..` never matched under
      `fnmatch`) — fixed via base-filename-only patterns
- [x] Verified identical behavior invoking Flake8 from `/app` (local,
      relative paths) and from the repository root (matching CI's
      invocation)

### Documentation Tasks

- [x] Added `docs/11-cicd/cicd.md` — job breakdown and incident writeup

Priority

Medium

Status

✅ Completed — 2026-07-14

---

# Definition of Done (DoD)

A task is considered complete when:

- [x] Code implemented
- [x] Code reviewed
- [x] Tests passed (28 unit / 42 total, confirmed locally under the
      exact commands the workflow runs)
- [x] Documentation updated
- [x] Docker verified (build validation job; full local Compose stack
      unaffected)
- [ ] GitHub pushed
- [ ] Pull Request merged — **first real confirmation that the
      workflow passes on GitHub itself is still pending**, since
      everything above was validated locally by design