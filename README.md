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

| Component | Technology |
|------------|------------|
| API | FastAPI |
| Compute | AWS Lambda (Container Image) |
| Database | Amazon RDS PostgreSQL |
| Storage | Amazon S3 |
| Logging | CloudWatch Logs |
| Secrets | AWS Systems Manager Parameter Store |
| Container | Docker |
| CI/CD | GitHub Actions |
| IaC (optional) | Terraform (Future Improvement) |

---

# Repository Structure

```text
docs/
app/
tests/
.github/
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

---

# Documentation

## Project Management

Read in this order — see [docs/00-project/README.md](docs/00-project/README.md) for the full index and update workflow.

| Document | Description |
|----------|-------------|
| docs/00-project/project-status.md | Current phase, active branch, next branch |
| docs/00-project/wbs.md | Work Breakdown Structure |
| docs/00-project/backlog.md | Granular task checklist for the active phase |
| docs/00-project/decisions.md | Architecture Decision Records (ADR) |
| docs/00-project/conventions.md | Coding and tooling conventions |
| docs/00-project/risk-register.md | Identified risks and mitigations |
| docs/00-project/changelog.md | Append-only record of shipped changes |

## Technical Documentation

| Document | Description |
|----------|-------------|
| docs/01-architecture/architecture.md | System Architecture |
| docs/02-database/database.md | Database Design |
| docs/03-api/api.md | API Specification |
| docs/04-validation/validation.md | Validation Rules |
| docs/05-backup/backup.md | Backup Strategy |
| docs/06-restore/restore.md | Restore Strategy |
| docs/07-reports/reports.md | SQL Reports |
| docs/08-testing/testing.md | Testing Strategy |
| docs/09-deployment/deployment.md | Deployment Guide |

---

# Development Workflow