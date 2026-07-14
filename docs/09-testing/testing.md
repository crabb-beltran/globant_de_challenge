# Testing Strategy

## Two-Tier Test Suite

This project uses two distinct test tiers, each with a different scope
and a different database backend — the split exists because Postgres-
specific SQL (`TRUNCATE`, `FILTER (WHERE ...)`, window functions,
`STDDEV_SAMP`) has no SQLite equivalent, so a single unified suite
cannot cover both business logic and database-specific behavior.

### Tier 1 — Unit tests (SQLite, in-memory, no external dependencies)

Covers Pydantic schema validation and `services/ingestion.py`'s business
logic (FK checks, duplicate detection, partial-batch isolation) using an
in-memory SQLite database (`tests/conftest.py`, fixture `db_session`).
Runs by default with no setup — no live Postgres connection required.

```bash
docker-compose exec api bash
python -m pytest /tests/ -v
```

**Known limitation**: SQLite requires a documented SAVEPOINT workaround
(`conftest.py`'s `connect`/`begin` event listeners disabling pysqlite's
implicit transaction handling) to make `db.begin_nested()` behave
correctly — without it, `ingest_batch`'s per-record isolation cannot be
tested at all under SQLite.

Files: `test_ingestion_service.py`, `test_schemas.py`,
`test_integration_conftest_guardrail.py` (see "Guardrail" section below
— this one runs in Tier 1 despite living alongside integration tests,
since it validates pure assertion logic with no database connection).

### Tier 2 — Integration tests (real Postgres, dedicated test database)

Covers logic that only manifests against a real Postgres engine:
`TRUNCATE` multi-table semantics, cross-table `flush()` ordering,
analytical SQL (`FILTER`, `PERCENTILE_CONT`, window functions), and
genuine `IntegrityError`/`DBAPIError` behavior that SQLite cannot
reproduce. Skipped by default; opt-in via an environment variable:

```bash
docker-compose exec api bash
RUN_INTEGRATION_TESTS=1 python -m pytest /tests/ -v
```

Files: `test_restore_integration.py`, `test_reports_integration.py`,
`test_db_constraint_violation_integration.py`.

**Current baseline**: 28 passed (Tier 1 only, default run) /
41 passed (both tiers, `RUN_INTEGRATION_TESTS=1`).

## Isolated Test Database

Integration tests connect to a dedicated database, `globant_test` — a
physically separate database on the same Postgres instance, not a
schema within the development database. See `integration_conftest.py`.

### Why a separate database, not a separate schema

A schema-based approach (e.g. `test.departments` alongside
`public.departments`) was considered and rejected. A schema lives inside
the *same* database connection; an unqualified `TRUNCATE` or a
`search_path` misconfiguration could still reach production tables. A
separate database eliminates this failure mode structurally: even a
buggy fixture is connected to a different database entirely and
physically cannot touch development data, regardless of what SQL it
issues.

### Incident: integration tests wiped the development database (twice)

During Phase 9, `tests/test_restore_integration.py`'s original fixture
connected directly to `db.session.SessionLocal` — the same connection
used by the running API in local development — and truncated all three
tables in its setup/teardown logic. Running the integration suite
emptied `departments`, `jobs`, and `hired_employees` in the development
database entirely. Recovery was possible only because a clean AVRO
backup existed from Phase 8 (`POST /restore` restored the pre-incident
state).

The isolated `globant_test` database (this phase's primary deliverable)
was built specifically in response to this incident. It recurred a
second time during the transition, when a leftover local fixture
definition (accidentally duplicating a fixture name already provided by
an import) silently shadowed the new isolated fixture and fell back to
the old direct-connection behavior — reconfirming that **structural**
isolation (a genuinely different database) is necessary; relying on
"the fixture code is written correctly" is not sufficient on its own.

### Guardrail: fail loudly, not silently

`integration_conftest.py`'s `pg_test_session` fixture asserts that the
resolved database name contains the substring `"test"` before
proceeding:

```python
assert "test" in db_name.lower(), (
    f"Refusing to run integration tests against database '{db_name}' — "
    f"name does not contain 'test'."
)
```

This does not prevent every possible misconfiguration, but it converts
the specific failure mode that already occurred twice — a fixture
accidentally resolving to the development database — into an immediate,
loud `AssertionError` instead of a silent `TRUNCATE` of real data.
Covered by `test_integration_conftest_guardrail.py`, which reproduces
the assertion logic directly (no live database needed) so the guardrail
itself has permanent regression coverage independent of infrastructure
availability.

## Cross-Reference: the `flush()` Incident (Phase 8)

A related, distinct Postgres-specific finding — `Session.add()` across
multiple tables does not guarantee cross-table `INSERT` order without an
explicit `db.flush()` — was discovered and fixed during Phase 8's
`restore_all()` implementation, not during this phase. Documented in
full in `docs/07-restore/restore.md`; covered by
`test_restore_integration.py::TestRestoreAllAgainstRealPostgres::test_restore_all_succeeds_with_fk_dependent_data`.
Mentioned here because it's a sibling finding to this phase's database-
isolation incident: both are cases where SQLite-based unit tests would
have passed regardless of whether the underlying bug was fixed, making
Postgres integration testing non-optional for this project's
correctness guarantees — not just a nice-to-have.

## `DB_CONSTRAINT_VIOLATION` Coverage (deferred from Phase 6)

`services/ingestion.py`'s `ConstraintViolation` / `DB_CONSTRAINT_VIOLATION`
reason code was implemented in Phase 6 but never exercised by a real
`IntegrityError` until this phase — SQLite's unit suite cannot trigger
one under the same conditions as Postgres. Covered by
`test_db_constraint_violation_integration.py`, which simulates a race
condition: `existing_ids` is read before a "concurrent" insert lands on
the same `id`, so `ingest_batch`'s in-memory duplicate check passes
(stale read) but the real `INSERT` fails at the database constraint
level — confirming the code path correctly catches and reports this as
`DB_CONSTRAINT_VIOLATION` rather than crashing the batch.

## Running Everything

```bash
# Tier 1 only (fast, default, no Postgres dependency) — 28 passed
docker-compose exec api bash
python -m pytest /tests/ -v

# Both tiers (requires globant_test to exist — auto-created on first run) — 41 passed
RUN_INTEGRATION_TESTS=1 python -m pytest /tests/ -v
```

## Related Documentation

- `docs/06-backup/backup.md`, `docs/07-restore/restore.md` — the
  `flush()` and multi-table `TRUNCATE` incidents (Phase 8)
- `docs/08-reports/reports.md` — analytical SQL query design and its
  own integration test rationale (Phase 9)
- `docs/00-project/risk-register.md` — R-018 (Insufficient test
  coverage), addressed by this phase's consolidation