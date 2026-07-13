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