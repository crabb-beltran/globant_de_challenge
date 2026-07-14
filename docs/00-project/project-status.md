# Project Status

**Project:** Globant Data Engineering Challenge

**Current Version:** v0.6.0

**Current Branch:** feature/sql-reports

**Last Update:** 2026-07-14

---

# Overall Progress

| Phase | Progress | Branch | Status |
|--------|---------:|-------------------------------|---------|
| Project Setup | 100% | feature/project-setup | ✅ Completed |
| Development Environment | 100% | feature/development-environment | ✅ Completed |
| AWS Infrastructure | 100% | feature/aws-infrastructure | ✅ Completed |
| Database | 100% | feature/database-schema | ✅ Completed |
| Historical Data Migration | 100% | feature/historical-loader | ✅ Completed |
| REST API | 100% | feature/rest-api | ✅ Completed |
| Validation Engine | 100% | feature/validation-engine | ✅ Completed |
| Backup & Restore | 100% | feature/backup-restore | ✅ Completed |
| SQL Reports | 100% | feature/sql-reports | ✅ Completed |
| Testing | 0% | feature/testing | ⏳ Pending |
| CI/CD | 0% | feature/github-actions | ⏳ Pending |
| Deployment | 0% | feature/aws-deployment | ⏳ Pending |
| Project Closure | 0% | feature/final-documentation | ⏳ Pending |
| Release | 0% | release/v1.0 | ⏳ Pending |

---

# Current Sprint

## Active Branch

feature/sql-reports (pending merge to develop)

## Current Goal

- Final review of report endpoints and statistical findings
- Merge into develop
- Open feature/testing — priority: isolate test database from dev
  Postgres (see Lessons Learned, risk of accidental data loss from
  integration test fixtures sharing the dev connection)

## Next Branch

feature/testing

---

# Release Plan

feature/*
│
▼
develop
│
▼
release/v1.0
│
▼
main