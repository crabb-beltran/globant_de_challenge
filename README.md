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
docker/
scripts/
.github/
```

---

# Documentation

| Document | Description |
|----------|-------------|
| docs/00-project/wbs.md | Work Breakdown Structure |
| docs/00-project/decisions.md | Architecture Decision Records |
| docs/00-project/backlog.md | Project Backlog |
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

```
feature/*
        ↓

develop
        ↓

release/*
        ↓

main
```

---

# Project Status

| Phase | Status |
|--------|--------|
| Planning | 🟨 |
| Infrastructure | ⬜ |
| Database | ⬜ |
| API | ⬜ |
| Validation | ⬜ |
| Backup | ⬜ |
| Restore | ⬜ |
| Reports | ⬜ |
| Testing | ⬜ |
| Deployment | ⬜ |

---

# Future Improvements

- Infrastructure as Code
- Monitoring Dashboard
- Authentication
- Unit Test Coverage >90%
- Automated Deployment

---

# License

MIT