# Risk Register

**Project:** Globant Data Engineering Challenge

**Version:** 1.0

**Last Updated:** 2026-07-10

---

# Purpose

This document identifies, evaluates, and tracks the main risks that could affect the successful delivery of the project.

Each risk includes its probability, impact, mitigation strategy, contingency plan, and current status.

---

## Risk Assessment Scale

### Probability

| Level | Description |
|--------|-------------|
| Low | Unlikely to occur |
| Medium | Could occur |
| High | Very likely to occur |

---

### Impact

| Level | Description |
|--------|-------------|
| Low | Minor impact |
| Medium | Moderate impact |
| High | Critical impact |

---

# Risk Register

| ID | Category | Risk | Probability | Impact | Mitigation Strategy | Contingency Plan | Owner | Status |
|----|----------|------|-------------|--------|---------------------|------------------|--------|--------|
| R-001 | Cloud | AWS Free Tier limits exceeded | Low | High | Configure AWS Budgets and monitor usage regularly | Shut down unused resources immediately | Project Owner | Open |
| R-002 | Database | Incorrect relational model design | Medium | High | Design ER diagram before implementation and validate relationships | Refactor schema using Alembic migrations | Project Owner | Open |
| R-003 | Data Quality | Historical CSV contains invalid or inconsistent records | High | High | Implement strict validation rules before inserting data | Log rejected records and continue processing valid data | Project Owner | Open |
| R-004 | API | API accepts invalid payloads | Medium | High | Validate requests using schema validation and business rules | Return descriptive HTTP error responses | Project Owner | Open |
| R-005 | Backup | Backup generation fails | Low | High | Validate generated AVRO files before storing them | Regenerate backup from database | Project Owner | Open |
| R-006 | Restore | Corrupted AVRO backup file | Low | High | Validate file integrity before restore | Restore from previous backup version | Project Owner | Open |
| R-007 | Infrastructure | Incorrect AWS configuration | Medium | Medium | Test each AWS service independently before integration | Recreate infrastructure from documented configuration | Project Owner | Open |
| R-008 | Security | Database credentials exposed | Low | High | Store secrets in AWS Systems Manager Parameter Store | Rotate credentials immediately | Project Owner | Open |
| R-009 | Performance | Batch ingestion becomes inefficient | Medium | Medium | Use batch inserts and optimize database transactions | Reduce batch size temporarily | Project Owner | Open |
| R-010 | Logging | Invalid records are not properly logged | Low | Medium | Centralize logs in CloudWatch with structured JSON | Reprocess rejected batches from source data | Project Owner | Open |
| R-011 | Version Control | Poor Git history due to large commits | Medium | Medium | Use feature branches and small atomic commits | Squash commits before merging if necessary | Project Owner | Open |
| R-012 | Documentation | Documentation becomes outdated | Medium | Medium | Update documentation as part of each completed feature | Perform documentation review before release | Project Owner | Open |
| R-013 | Deployment | Docker image cannot be deployed | Low | High | Validate image locally before publishing | Roll back to previous working image | Project Owner | Open |
| R-014 | CI/CD | GitHub Actions pipeline fails | Medium | Medium | Validate workflow incrementally | Execute deployment manually until fixed | Project Owner | Open |
| R-015 | Schedule | Project takes longer than expected | Medium | High | Follow WBS and prioritize core requirements first | Defer optional improvements | Project Owner | Open |
| R-016 | Scope | Overengineering the solution | High | High | Prioritize challenge requirements over additional features | Remove non-essential components before delivery | Project Owner | Open |
| R-017 | Analytics | SQL queries return incorrect results | Medium | High | Validate results against sample datasets | Review SQL logic and add integration tests | Project Owner | Open |
| R-018 | Testing | Insufficient test coverage | Medium | Medium | Define testing strategy before implementation | Add regression tests before release | Project Owner | Open |
| R-019 | Delivery | Missing required documentation at submission | Low | High | Maintain documentation throughout development | Perform final documentation checklist | Project Owner | Open |
| R-020 | Availability | AWS regional outage or service issue | Low | Medium | Use managed AWS services and monitor service health | Perform local execution using Docker | Project Owner | Open |

---

# Risk Review Schedule

| Frequency | Activity |
|------------|----------|
| Daily | Review newly identified risks during development |
| Weekly | Update probability, impact, and mitigation status |
| Before Release | Perform full risk assessment review |
| Final Delivery | Verify all High Impact risks are mitigated or accepted |

---

# Risk Status Definitions

| Status | Meaning |
|--------|---------|
| Open | Risk identified but not yet mitigated |
| Monitoring | Mitigation in progress |
| Mitigated | Risk reduced to an acceptable level |
| Closed | Risk no longer applies |
| Accepted | Risk acknowledged without further mitigation |

---

# High Priority Risks

The following risks require continuous monitoring:

- R-001 — AWS Free Tier consumption
- R-003 — Invalid historical data
- R-004 — API validation failures
- R-008 — Credential exposure
- R-015 — Schedule delays
- R-016 — Scope creep / Overengineering

---

# Lessons Learned

This section will be completed during project execution.

| Date | Lesson | Action Taken |
|------|---------|--------------|
| YYYY-MM-DD | | |

---

# Revision History

| Version | Date | Author | Description |
|----------|------|--------|-------------|
| 1.0 | 2026-07-10 | Cristian Andrés Beltrán | Initial Risk Register |