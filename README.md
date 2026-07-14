# Globant Data Engineering Challenge

Proof of Concept (PoC) developed for the Globant Data Engineering Challenge.

The project focuses on designing and implementing a cloud-native data ingestion platform using AWS Free Tier services, SQL databases, REST APIs, data validation, backup/restore mechanisms, and analytical SQL queries.

---

# Objectives

- Historical data migration from CSV files
- REST API for batch ingestion
- Data validation
- Logging of invalid records
- AVRO backup and restore
- SQL analytical reports
- Cloud deployment using AWS
- Containerized application
- CI/CD with GitHub Actions

---

# Architecture

The proposed solution follows a serverless-first architecture using AWS managed services.

## Core Stack

| Layer | Technology |
|------------|------------|
| API Framework | FastAPI (ADR-002) |
| API Documentation | Swagger UI / OpenAPI (auto-generated at `/docs`) |
| Data Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.0 |
| Database Migrations | Alembic |
| Database | PostgreSQL (ADR-001) |
| Database Driver | psycopg2 |
| Backup Serialization | fastavro (ADR-008) |
| Compute (planned) | AWS Lambda, Container Image (ADR-003) |
| Lambda Adapter | Mangum |
| Storage | Amazon S3 (provisioned, Phase 3) |
| Logging | CloudWatch Logs (ADR-004) |
| Secrets (planned) | AWS Systems Manager Parameter Store (ADR-005) — currently `.env`, documented deferred work |
| Container | Docker / Docker Compose |
| CI/CD | GitHub Actions (lint, unit + integration tests, Docker build) |

## Testing & Quality Tooling

| Tool | Purpose |
|------|---------|
| pytest | Unit and integration test runner |
| SQLite (in-memory) | Unit test backend — fast, no external dependency |
| sqlalchemy_utils | Isolated test database (`globant_test`) provisioning |
| Black | Code formatting (enforced in CI) |
| Flake8 | Linting (enforced in CI) |

## Local Development

| Component | Technology |
|---|---|
| Local database | PostgreSQL (Docker) |
| AWS service emulation | LocalStack |
| IaC (optional) | Terraform (Future Improvement — not yet implemented) |

---

# Repository Structure

```text
.github/       # GitHub Actions CI workflow
app/           # Application source (FastAPI, SQLAlchemy, Alembic, services)
backups/       # AVRO backup output (gitignored — .gitkeep tracks the folder)
datasets/      # Historical CSV source files (gitignored — .gitkeep tracks the folder)
docs/          # Project management + technical documentation
scripts/       # Utility/diagnostic scripts
tests/         # Unit (SQLite) and integration (Postgres) test suites
```

---

# Getting Started

## Prerequisites

- Docker and Docker Compose
- AWS CLI (configured — required from Phase 3 onward)
- Python 3.12 (optional, only if running scripts outside containers)

## Local Setup

```bash
cp .env.example .env
# fill in all required values — see .env.example for the full list

docker-compose up --build
```

- API: http://localhost:8080
- Interactive docs (Swagger UI): http://localhost:8080/docs
- Health check: http://localhost:8080/health

## Data Setup

The historical CSV files (`hired_employees.csv`, `departments.csv`,
`jobs.csv`) are **not committed to this repository** — `datasets/*.csv` is
gitignored. Place your own copies of the challenge's source files inside
`datasets/` before running the historical loaders; the folder itself is
tracked (via `.gitkeep`) so the expected location is explicit.

## Loading Historical Data

Once the stack is running and the database schema is migrated
(`alembic upgrade head`, run inside the `api` container):

```bash
docker-compose exec api bash
cd /app
python -m loaders.reference_data /datasets/departments.csv /datasets/jobs.csv
python -m loaders.historical /datasets/hired_employees.csv
```

See [docs/03-historical-migration/execution-guide.md](docs/03-historical-migration/execution-guide.md) for full details, including data quality findings and idempotency behavior.

## Running Tests

```bash
docker-compose exec api bash
cd /app

# Tier 1 — unit tests (SQLite, no external dependency), default
python -m pytest ../tests/ -v

# Tier 2 — both tiers, requires a Postgres connection
# (isolated globant_test database, auto-created on first run)
RUN_INTEGRATION_TESTS=1 python -m pytest ../tests/ -v
```

See [docs/09-testing/testing.md](docs/09-testing/testing.md) for the full
two-tier strategy and database isolation rationale.

---

# Documentation

## Project Management

Read in this order:

| Document | Description |
|----------|-------------|
| docs/00-project/project-status.md | Current phase, active branch, submission scope |
| docs/00-project/wbs.md | Work Breakdown Structure |
| docs/00-project/backlog.md | Granular task checklist for the active phase |
| docs/00-project/decisions.md | Architecture Decision Records (ADR-001 through ADR-012) |
| docs/00-project/conventions.md | Coding and tooling conventions |
| docs/00-project/risk-register.md | Identified risks and mitigations |
| docs/00-project/changelog.md | Append-only record of shipped changes |

## Technical Documentation

| Document | Description |
|----------|-------------|
| docs/01-architecture/architecture.md | System Architecture |
| docs/02-database/database.md | Database Design |
| docs/03-historical-migration/data-quality-analysis.md | Historical Dataset Data Quality Findings |
| docs/03-historical-migration/execution-guide.md | Historical Data Migration Execution Guide |
| docs/04-api/api.md | API Specification |
| docs/05-validation/validation.md | Validation Rules |
| docs/06-backup/backup.md | Backup Strategy |
| docs/07-restore/restore.md | Restore Strategy |
| docs/08-reports/reports.md | SQL Reports |
| docs/09-testing/testing.md | Testing Strategy |
| docs/11-cicd/cicd.md | CI/CD Pipeline (GitHub Actions) |
| docs/12-deployment/deployment.md | Deployment Guide — **pending, Phase 12 deferred (see below)** |

---

# Development Workflow

feature/*
↓
develop
↓
release/*
↓
main

---

# Project Status

| Phase | Status |
|--------|--------|
| Project Setup | ✅ |
| Development Environment | ✅ |
| AWS Infrastructure | ✅ |
| Database | ✅ |
| Historical Data Migration | ✅ |
| REST API | ✅ |
| Validation Engine | ✅ |
| Backup & Restore | ✅ |
| SQL Reports | ✅ |
| Testing | ✅ |
| CI/CD | ✅ |
| Deployment | ⏸️ Deferred post-submission |
| Project Closure | ✅ |

**Submission note**: 11 of 13 WBS phases complete. The application runs
fully locally via `docker-compose up --build`, satisfying the
challenge's core Docker requirement. Cloud deployment (AWS Lambda/API
Gateway) is architecturally decided (see ADR-003) but deliberately
deferred rather than rushed under the submission deadline — see
[docs/00-project/project-status.md](docs/00-project/project-status.md)
for the full rationale.

For real-time status, see [docs/00-project/project-status.md](docs/00-project/project-status.md).

---

# Future Improvements

- Infrastructure as Code (Terraform)
- AWS Lambda / API Gateway deployment (Phase 12, deferred)
- Secrets migration to AWS Systems Manager Parameter Store (ADR-005)
- Monitoring Dashboard
- Authentication
- Unit Test Coverage >90%
- Automated deployment pipeline (CD, beyond current CI)

---

# License

MIT
