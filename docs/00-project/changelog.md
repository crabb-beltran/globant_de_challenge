# Changelog

All notable changes to this project will be documented in this file.

The format is based on **Keep a Changelog** and the project follows **Semantic Versioning (SemVer)**.

---

## [Unreleased]

### Added

#### Project Foundation

- Established the initial project structure following Git Flow.
- Added comprehensive project documentation (README, WBS, Backlog, Roadmap, Risk Register, Project Status).
- Added Architecture Decision Records (ADR) to document key architectural decisions.
- Defined project development conventions and commit standards.

#### Repository Governance

- Configured GitHub Rulesets for `main` and `develop` branches, enforcing pull-request-only merges, non-fast-forward pushes, and linear history on `main`.

#### Development Environment

- Added Docker-based local development environment.
- Created `docker-compose.yml` to orchestrate application services.
- Added Dockerfile for containerizing the FastAPI application.
- Configured PostgreSQL container for local database development.
- Configured LocalStack container for AWS service emulation.

#### API

- Initialized the FastAPI application (`app/main.py`).
- Added `/health` endpoint for application health checks.
- Verified successful execution inside Docker Compose.

#### Dependencies

- Added the initial project dependencies in `requirements.txt`.
- Included the required libraries for FastAPI, PostgreSQL connectivity, Docker execution, and AVRO processing.

#### Architecture

- Added **ADR-008** documenting the selection of **fastavro** as the AVRO serialization library.

#### AWS Infrastructure

- Configured a Zero Spend AWS Budget to alert on any spend above $0.01.
- Created IAM user `globant-de-challenge-deployer` for programmatic, CLI-only access (no console login).
- Created and attached two Customer Managed IAM Policies:
  - `globant-de-challenge-bootstrap` — temporary, resource-scoped provisioning permissions (RDS, EC2 networking, S3, CloudWatch Logs, SSM), including `iam:CreateServiceLinkedRole` for RDS.
  - `globant-de-challenge-runtime` — permanent, least-privilege permissions scoped to specific resource ARNs for application runtime use.
- Manually created the `AWSServiceRoleForRDS` Service-Linked Role at account level (required one-time admin-privileged action; documented in `risk-register.md` as R-021).
- Created Security Group `globant-de-challenge-rds-sg` with inbound access on port 5432 restricted to a single `/32` CIDR.
- Created DB Subnet Group `globant-de-challenge-subnet-group` spanning two Availability Zones (`us-east-1d`, `us-east-1f`) within the default VPC.
- Provisioned RDS PostgreSQL 16.9 instance (`globant-de-challenge-db`, db.t4g.micro, Single-AZ, 20GB gp2, publicly accessible with /32-restricted Security Group).
- Verified end-to-end connectivity via psql with TLS 1.3 enforced by default.
- Added `rds:StopDBInstance`/`rds:StartDBInstance` to the Runtime policy and adopted stop-when-idle cost discipline after billing analysis (see risk-register.md R-001, Lessons Learned 2026-07-11).
- Detached the Bootstrap policy from the deployer user post-provisioning — deployer now operates with least-privilege Runtime permissions only.
- Documented the full infrastructure provisioning runbook in `docs/09-deployment/deployment.md`, including IAM policy JSON files with account-id placeholders (`docs/09-deployment/policies/`).

#### Database

- Designed the entity-relationship model for `departments`, `jobs`, and `hired_employees` (1—N relationships), documented in `docs/02-database/database.md`.
- Defined `TIMESTAMPTZ` for `hired_employees.datetime`, `NOT NULL` on all columns, and `ON DELETE RESTRICT` on both foreign keys — all justified against the challenge's validation rules and audit-data semantics.
- Wrote the initial SQL DDL (`app/ddl.sql`) as a manual reference alongside the SQLAlchemy models.
- Implemented SQLAlchemy 2.0 models (`app/models.py`) using `Mapped`/`mapped_column`, with explicit `autoincrement=False` on all primary keys — IDs are sourced from ingested data, not auto-generated (corrected after the first `alembic revision --autogenerate` incorrectly inferred a `SERIAL` sequence).
- Configured Alembic (`alembic init`, `env.py` wired to `Base.metadata` and to `.env`-sourced connection strings).
- Generated and applied the initial migration; verified the materialized schema directly against PostgreSQL (`\d hired_employees`) to confirm indexes, foreign keys, and constraint behavior matched the design.
- Added **ADR-009**, documenting the decision to reject CDC/SCD Type 2 for this project's data model.

#### Historical Data Migration

- Diagnosed source CSVs (`hired_employees.csv`, `departments.csv`, `jobs.csv`) using `awk`/`grep`, documented in `docs/05-historical-migration/data-quality-analysis.md`.
- Implemented `schemas/hired_employee.py`, `schemas/department.py`, `schemas/job.py` (Pydantic) with explicit business-error messages for required-field violations and strict ISO 8601 datetime validation.
- Implemented `validators/business_rules.py` for foreign-key existence checks (`department_id`/`job_id`) against in-memory ID sets, avoiding per-row database queries.
- Implemented `db/config.py` (shared connection string builder, used by both Alembic and the application) and `db/session.py` (SQLAlchemy session factory).
- Implemented `loaders/reference_data.py` (generic loader for `departments`/`jobs`) and `loaders/historical.py` (loader for `hired_employees`, depends on reference data being loaded first).
- Implemented `logging_/rejected_records.py`: structured JSON logging to stdout, forwarded to CloudWatch Logs automatically under the Lambda runtime (ADR-004), parameterized by `source` for future reuse by the REST API (Phase 6).
- Added **ADR-010**: skip-if-exists idempotency strategy for both loaders, chosen over upsert or full-replace.
- Corrected initial data quality diagnosis after discovering a CRLF-related blind spot in shell-based `awk` checks (see `risk-register.md` R-024) — final count: 70 invalid records out of 1999 (3.50%), not the initially reported 54.
- Successfully loaded: 12 departments, 183 jobs, 1929 hired employees (70 rejected, 0 skipped on first run).

#### REST API

- Implemented `services/ingestion.py`: shared batch ingestion service used
  by all three ingestion endpoints (thin router / fat service pattern),
  reusing the FK-existence validators from `validators/business_rules.py`
  (Fase 5) without duplication.
- Implemented `routers/employees.py`, `routers/departments.py`,
  `routers/jobs.py`: `POST` batch endpoints (1-1000 records), returning
  `207 Multi-Status` with per-record partial success — a single invalid
  record no longer blocks the rest of the batch (contrast with the
  all-or-nothing historical CSV loader, Fase 5).
- Implemented per-record transactional isolation via `db.begin_nested()`
  (SAVEPOINT), so a database-level constraint violation on one record
  does not roll back valid records in the same batch.
- Implemented `validators/exceptions.py`: typed exception hierarchy
  (`ForeignKeyViolation`, `DuplicateRecordError`, `ConstraintViolation`)
  carrying a fixed `reason_code`, decoupling structured rejection
  reporting from free-text error messages.
- Decision: duplicate `id` in an API request is **rejected**
  (`DUPLICATE_ID`), diverging from the CSV loaders' skip-if-exists
  idempotency (ADR-010) — documented in `docs/04-api/api.md`.
- Registered all three routers in `app/main.py` (version bumped to
  `0.2.0`). Reports/Backup/Restore endpoints intentionally excluded from
  this phase — see WBS scope realignment below.
- Fixed `logging_/rejected_records.py`: added the missing `source`
  parameter (with a backward-compatible default), preventing a latent
  `TypeError` that `loaders/reference_data.py` was already calling but
  had never triggered in practice.
- Added `docs/04-api/api.md` (endpoint contracts, design rationale) and
  `docs/05-validation/validation.md` (two-layer validation model:
  Pydantic field-level vs business-rule DB-state validation).
- Added `tests/test_ingestion_service.py` and `tests/conftest.py`: unit
  tests covering clean batch insertion, FK violations, duplicate
  detection (both against existing DB rows and within the same batch),
  and partial-batch isolation — using in-memory SQLite with SAVEPOINT
  support enabled via SQLAlchemy event listeners. Integration testing
  against real Postgres (`DB_CONSTRAINT_VIOLATION` path) deferred to
  Fase 10.

#### Project Governance

- Realigned `wbs.md` Fase 6 scope to Employees/Departments/Jobs only,
  matching the branch-per-feature granularity already defined in
  `conventions.md`/`project-status.md` (Reports, Backup, and Restore
  remain their own WBS phases with dedicated branches).

  #### Validation Engine

- Audited existing validation coverage (built across Fase 5 and Fase 6)
  against the six rules originally scoped in `wbs.md` Phase 7. Confirmed
  all six already had a working implementation, distributed across
  Pydantic schemas (structural) and `validators/business_rules.py` /
  `services/ingestion.py` (DB-state) — no centralized validation engine
  was missing.
- Fixed four real gaps found during the audit, all at the Pydantic
  schema level (`schemas/department.py`, `schemas/job.py`,
  `schemas/hired_employee.py`):
  - Negative or zero `id`/`department_id`/`job_id` values were
    previously accepted and inserted; now rejected with `422`.
  - Whitespace-only strings (e.g. `"   "`) passed the previous
    `value == ""` check; now rejected via `.strip()` comparison.
  - Unexpected/extra fields in the request body were silently ignored;
    now rejected with `422` (`extra_forbidden`) via
    `model_config = ConfigDict(extra="forbid")`, per the challenge's
    requirement that non-compliant records must not be inserted.
- Confirmed two audited cases as correct existing behavior, unchanged:
  ISO 8601 datetime with a non-`Z` UTC offset remains rejected (scope
  decision, not a gap); numeric-string IDs (e.g. `"603"`) remain
  accepted via Pydantic's standard type coercion.
- Added **ADR-011**: documented the decision to keep validation as a
  decentralized two-layer model (Pydantic structural validation +
  DB-state business rules) rather than building a separate centralized
  validation engine component — consistent with `risk-register.md`
  R-016 (Overengineering).
- Updated `docs/05-validation/validation.md` with the full Layer 1 rule
  set, the gap audit findings table, and design rationale for the two
  confirmed non-issues.
- Added `tests/test_schemas.py`: 19 regression tests covering the three
  fixed gaps (positive ID enforcement, whitespace rejection, extra
  field rejection) plus the two confirmed non-issues (ISO offset
  rejection, numeric string coercion), locking in current behavior
  against future silent changes. Full suite: 27/27 passing.

  #### Backup & Restore

- Implemented `services/backup.py`: exports `departments`, `jobs`, and
  `hired_employees` to individual AVRO files on the local filesystem
  (`/app/backups/`), one schema per table. Storage location follows the
  challenge's literal requirement over the original ADR-006 (S3) — see
  **ADR-012** for the reconciliation.
- Implemented `routers/backup.py`: `POST /backup`, on-demand, synchronous,
  exports all three tables in one call. No scheduler implemented — out
  of scope per `risk-register.md` R-016; documented as a future
  production extension point instead.
- Implemented `services/restore.py`: two restore modes —
  `restore_all()` (all three tables together, the safe default) and
  `restore_table()` (single-table, only safe for tables with no FK
  dependents).
- Implemented `routers/restore.py`: `POST /restore` and
  `POST /restore/{table_name}`, both requiring an explicit
  `?confirm=true` guardrail given the destructive (TRUNCATE + reload)
  nature of the operation.
- **Incident findings** (full writeup in `docs/07-restore/restore.md`):
  - Postgres `TRUNCATE` rejects a table if *any* other table has a FK
    constraint referencing it, regardless of that table's current row
    count — not just when rows actually conflict. Fixed by truncating
    all three related tables in a single `TRUNCATE` statement instead
    of per-table sequential truncation.
  - `Session.add()` across multiple tables does not guarantee INSERT
    execution order without an explicit `db.flush()` between tables —
    SQLAlchemy 2.0's bulk-insert batching can dispatch a dependent
    table's rows before its FK target's rows are physically inserted,
    even when both were queued in the correct order. Fixed by calling
    `db.flush()` after each table's reload, while still committing the
    whole restore atomically at the end.
  - `TRUNCATE ... CASCADE` was deliberately rejected as a fix, despite
    Postgres suggesting it: `CASCADE` would silently wipe any future
    table referencing the truncated one, outside this restore's known,
    explicit scope.
- Added **ADR-012**: reconciles ADR-006 (S3) with the challenge's literal
  filesystem requirement for backups.
- Added `docs/06-backup/backup.md` and `docs/07-restore/restore.md`,
  including the full incident writeup as living documentation of the
  two Postgres/SQLAlchemy findings above.
- Added `tests/test_restore_integration.py`: 4 integration tests against
  a real Postgres connection (skipped by default; run explicitly with
  `RUN_INTEGRATION_TESTS=1`), covering both incident findings as
  permanent regression coverage — SQLite (used by the rest of the unit
  suite) cannot reproduce either bug, since it lacks `TRUNCATE` and does
  not enforce FK constraints by default.
- Fixed: removed an unused `export_department()` function left over
  from initial `services/backup.py` scaffolding.

#### SQL Reports

- Reactivated `routers/reports.py` (drafted during Phase 6 exploration,
  held out of that PR pending its own branch per WBS scope realignment).
- Implemented `GET /reports/hiring-by-quarter` (Challenge 2, Question 1):
  employees hired per job/department, pivoted by quarter, 2021 only,
  using Postgres `FILTER (WHERE ...)` instead of SQLAlchemy's expression
  language or manual `CASE WHEN` chains.
- Implemented `GET /reports/departments-above-average` (Challenge 2,
  Question 2): departments hiring above the 2021 average, ordered by
  `hired DESC`. Uses `LEFT JOIN` (not `INNER JOIN`) so departments with
  zero 2021 hires are correctly included in the average calculation —
  covered by a dedicated regression test.
- Implemented `GET /reports/hiring-distribution-stats` (bonus, not
  required by the challenge): mean, median, standard deviation,
  coefficient of variation, and per-department z-scores, to verify
  whether the "above average" threshold is distorted by outlier
  departments. Applied to the real project dataset: mean=136.92,
  median=145.0, CV=0.48, highest department z-score≈1.19 (below the
  |z|>2 heuristic) — confirms no single department dominates the
  distribution.
- Added `schemas/reports.py`: typed `response_model` for all three
  endpoints (Swagger previously showed untyped `dict` responses for
  these routes).
- Added `docs/08-reports/reports.md`: design rationale, endpoint
  contracts, and the statistical findings above.
- Added `tests/test_reports_integration.py`: 9 integration tests against
  a real Postgres connection (opt-in via `RUN_INTEGRATION_TESTS=1`),
  using a small hand-verified synthetic dataset rather than the
  project's real data. Covers the LEFT JOIN zero-hire-department
  correctness, the 2021-year filter, and quarter pivot accuracy.
  Documented gotcha: Postgres `NUMERIC` aggregates deserialize as
  `Decimal`, not `float` — requires explicit casting when compared with
  `pytest.approx()` (does not affect the actual API response, which
  Pydantic already converts to `float`).
- **Data hygiene**: identified and removed 7 test `departments`
  (`id`: -1, 0, 501, 502, 601, 602, 603) and 1 test `hired_employees`
  row (`id`: 9002) that had accumulated in the shared development
  Postgres instance from manual Swagger testing across Phases 6–8.
  Confirmed clean state (12 departments, 183 jobs, 1929 hired_employees)
  before validating report output. Regenerated the AVRO backup
  post-cleanup so `POST /restore` no longer reverts to the contaminated
  state.
- **Lesson learned**: `tests/test_restore_integration.py`'s fixture
  operates against the same Postgres instance used for local
  development (not an isolated test database) and truncates all three
  tables before and after each test run. Running it emptied the dev
  database entirely; recovered via the AVRO backup from Phase 8. Noted
  as a risk for `feature/testing` (Phase 10) to address with a properly
  isolated test database.

  
  #### Testing

- Consolidated the full test suite across all prior phases: 28 unit
  tests (Tier 1, SQLite, default run) + 13 integration tests (Tier 2,
  Postgres, opt-in via `RUN_INTEGRATION_TESTS=1`) = 41 total.
- Built a dedicated, isolated test database (`globant_test`) — a
  physically separate database on the same Postgres instance, not a
  schema within the development database. Auto-created on first
  integration test run via `sqlalchemy_utils.create_database`
  (`tests/integration_conftest.py`).
- Added `db/config.py::get_test_database_url()` alongside the existing
  `get_database_url()`, both sharing the same credentials but pointing
  at different database names.
- Migrated `test_restore_integration.py` and `test_reports_integration.py`
  from directly using `db.session.SessionLocal` (development database)
  to the new isolated `pg_test_session` fixture.
- Added a structural safety guardrail in `pg_test_session`: asserts the
  resolved database name contains `"test"` before proceeding, converting
  a misconfigured fixture into an immediate `AssertionError` instead of
  a silent `TRUNCATE` of real data.
- Added `test_integration_conftest_guardrail.py`: meta-test proving the
  guardrail assertion logic itself is sound, independent of live
  database availability (runs as part of the default Tier 1 suite).
- Added `test_db_constraint_violation_integration.py`: closes the
  `DB_CONSTRAINT_VIOLATION` coverage gap deferred since Phase 6, by
  simulating a race condition (stale `existing_ids` read followed by a
  concurrent insert) that SQLite's unit suite cannot reproduce.
- Added `docs/09-testing/testing.md`: two-tier strategy, and full
  incident writeup of the database-isolation failures this phase
  addresses.
- **Incident** (root cause of this phase's priority): an earlier
  integration test fixture connected directly to the development
  Postgres database and truncated all three tables via its
  setup/teardown logic, emptying `departments`/`jobs`/`hired_employees`
  in development on two separate occasions. Both recoveries used the
  AVRO backup from Phase 8 (`POST /restore`). Motivated the database
  isolation and guardrail work in this phase — see `testing.md` for the
  full writeup.