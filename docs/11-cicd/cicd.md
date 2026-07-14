# CI/CD Strategy

## Scope

GitHub Actions workflow (`.github/workflows/ci.yml`) running on every
`pull_request` and `push` to `develop`/`main`. Three independent jobs,
run in parallel: linting, test suite (both tiers), and Docker build
validation. No deployment automation in this phase — CD (actual
deployment to AWS) is WBS Phase 12, a separate branch.

## Jobs

### `quality` — Black + Flake8

- `black --check app/ tests/`: fails the job if formatting differs from
  Black's output, without rewriting files — CI reports violations, it
  doesn't silently fix them. Formatting itself is applied locally
  before committing (`black app/ tests/`, no `--check`).
- `flake8 --config=.flake8 app/ tests/`: static analysis for unused
  imports, import ordering, and line length.

### `test` — Two-tier suite, same convention as local development

Runs both tiers using the exact same commands used locally (see
`docs/09-testing/testing.md`), the only difference being a GitHub
Actions **service container** provides Postgres instead of
`docker-compose`'s `postgres_rds` service:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    ports:
      - 5432:5432
```

`DB_HOST=localhost` in CI (not `postgres_rds`) because service
containers are reachable directly on `localhost` from the job's steps —
no Docker network alias needed, unlike the `docker-compose.yml` setup
used for local development.

The isolated `globant_test` database (see `testing.md`) is created
automatically by `tests/integration_conftest.py` on first run, exactly
as it is locally — no special CI-only setup step required.

### `docker-build` — Image build validation only

Confirms the `Dockerfile` still produces a valid image. Does **not**
push to any registry — that belongs to the deployment phase (ECR push,
WBS Phase 12), kept separate per the project's phase-per-branch
discipline.

## Incident: `per-file-ignores` pattern matching failure

While configuring Flake8, `per-file-ignores` patterns prefixed with
`*/` (e.g. `*/conftest.py: E402, F401`) silently failed to match any
file, even though the `.flake8` config file itself was being read
correctly (confirmed via a `max-line-length = 10` sanity check that
did trigger `E501` on every line, ruling out a config-discovery
problem).

**Root cause**: Flake8's `per-file-ignores` matches patterns against
file paths using `fnmatch`. A `*/` prefix expects the wildcard to
absorb exactly one path segment ending in `/`, but when the actual
invoked path contains relative navigation components (`../tests/conftest.py`,
which is how tests were invoked locally from `/app`), `fnmatch` does
not resolve the `..` before attempting the match, so the pattern never
matches.

**Fix**: patterns use only the file's base name (`conftest.py`,
`integration_conftest.py`, `env.py`, etc.), with no path prefix at all.
This avoids depending on the exact path shape entirely, and was
confirmed to behave identically whether invoked from `/app` (with
`../tests/` relative paths) or from the repository root (with
`app/`/`tests/` paths, matching how CI invokes it) — see `.flake8` in
the repository root for the final configuration.

## Related Documentation

- `docs/09-testing/testing.md` — the two-tier test strategy this
  workflow runs
- `docs/00-project/conventions.md` — Black/PEP8 code style, already
  specified but never enforced as an automated gate before this phase