# Development Conventions

## Git Strategy

Git Flow

main
│
develop
│
feature/*
│
release/*
│
hotfix/*

---

## Commit Convention

Conventional Commits

Examples

feat(api): create employee endpoint
fix(validation): datetime parser
docs(readme): update architecture
refactor(database): improve repository pattern
test(api): add employee tests
chore(docker): update compose
ci(github): add CI workflow

---

## Branch Naming

Pattern: `feature/<wbs-phase-slug>`

Examples used in this project:

feature/project-setup
feature/development-environment
feature/aws-infrastructure
feature/database-schema
feature/historical-loader
feature/rest-api
feature/validation-engine
feature/backup-restore
feature/sql-reports
feature/testing
feature/github-actions
feature/aws-deployment
feature/final-documentation
release/v1.0

Branch names must match exactly the `Branch` column in `project-status.md`.

---

## Pull Request Rules

Every PR must contain

- Description
- Motivation
- Testing
- Checklist

---

## Code Style

**Python**: PEP8, enforced automatically via:

- **Black** — code formatting. Run locally before committing:
```bash
  python -m black app/ tests/
```
- **Flake8** — linting (unused imports, line length, import order). Run locally:
```bash
  python -m flake8 --config=.flake8 app/ tests/
```

Both are enforced as required CI checks (`.github/workflows/ci.yml`,
`quality` job) on every pull request to `develop`/`main` — a PR with
formatting or lint violations will show a failing check and should not
be merged until resolved.

**Configuration**: project-specific Flake8 exceptions live in `.flake8`
(repository root), documented inline for two intentional patterns:
`sys.path` manipulation before imports (test bootstrapping files) and
pytest fixture parameter shadowing (integration test files). See
`docs/11-cicd/cicd.md` for the incident that shaped this configuration
(`per-file-ignores` pattern matching against relative paths).

---

## Testing Conventions

Two-tier test suite — see `docs/09-testing/testing.md` for full detail:

- **Unit tests** (`tests/test_*.py`, no `_integration` suffix): SQLite
  in-memory backend, no external dependencies, run by default.
- **Integration tests** (`tests/test_*_integration.py`): real Postgres,
  isolated `globant_test` database, opt-in via `RUN_INTEGRATION_TESTS=1`.

Naming convention: integration test files are suffixed `_integration.py`
so they're identifiable at a glance and can be targeted individually if
needed (`pytest tests/test_restore_integration.py`).

---

## Documentation

Every feature must update

- README (if needed)
- ADR (if architecture changes)
- Changelog
- Relevant phase documentation under `docs/`

Every completed WBS phase must sync, at minimum:

- `docs/00-project/changelog.md` — what shipped
- `docs/00-project/project-status.md` — phase marked complete, branch updated
- `docs/00-project/backlog.md` — task checklist for the phase, closed
- `README.md` — Project Status table

---

## Docs Folder Numbering

Numbering under `docs/` corresponds 1:1 to WBS phases 4 through 12:

| Folder | WBS Phase |
|---|---|
| `00-project` | Cross-cutting project management docs |
| `01-architecture` | Phase 1 — Project Planning |
| `02-database` | Phase 4 — Database |
| `03-historical-migration` | Phase 5 — Historical Data Migration |
| `04-api` | Phase 6 — REST API |
| `05-validation` | Phase 7 — Validation Engine |
| `06-backup` | Phase 8 — Backup & Restore (backup half) |
| `07-restore` | Phase 8 — Backup & Restore (restore half) |
| `08-reports` | Phase 9 — SQL Reports |
| `09-testing` | Phase 10 — Testing |
| `11-cicd` | Phase 11 — CI/CD |
| `12-deployment` | Phase 12 — Deployment (pending, deferred) |

> Note: `10-deployment` was the originally planned folder name; renamed
> to `12-deployment` mid-project so the numbering stays aligned with the
> actual WBS phase number after Testing (10) and CI/CD (11) were given
> their own dedicated folders. If you find a reference to
> `docs/10-deployment/` anywhere outside this note, it's stale — report
> it.