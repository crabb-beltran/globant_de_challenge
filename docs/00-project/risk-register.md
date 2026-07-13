# Risk Register

**Project:** Globant Data Engineering Challenge

**Version:** 1.1

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
| R-001 | Cloud | AWS Free Tier limits exceeded | High | Medium | Zero Spend Budget as detection layer; stop-when-idle discipline for RDS (`rds:StopDBInstance` after each work session); verify billing line items weekly | Stop or delete billable resources immediately; RDS free tier confirmed NOT applicable to this account (older than 12 months) | Project Owner | Monitoring |
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
| R-021 | Infrastructure / IAM | AWS Service-Linked Roles (e.g. `AWSServiceRoleForRDS`) are not auto-created by RDS provisioning calls even when `iam:CreateServiceLinkedRole` is scoped to the service in a custom policy | Medium | Medium | Explicitly create required Service-Linked Roles once, at account level, using an admin-privileged one-time command before running dependent provisioning commands | Grant temporary elevated permissions via a separate admin profile, execute `aws iam create-service-linked-role`, then revoke access immediately | Project Owner | Mitigated |
| R-022 | Infrastructure / IAM | Custom least-privilege IAM policies underestimate required read/describe actions (e.g. `rds:DescribeDBEngineVersions`) not anticipated during initial policy design, discovered only through iterative execution | Medium | Low | Design IAM policies iteratively: attempt the real AWS CLI command first, add missing read-only Describe/List actions as errors surface, rather than guessing the full action set upfront | Add the missing action to the Bootstrap policy, update the document version, wait for propagation, and retry the failing command | Project Owner | Mitigated |
| R-023 | Infrastructure / IAM | Root user access keys required for IAM-on-IAM operations (Service-Linked Role creation, policy detach) because the project operates without a dedicated admin IAM user | Medium | Medium | Generate root access keys only for the specific operation, execute, then deactivate and delete the key immediately; document each occurrence | Create a dedicated admin IAM user with MFA if root operations become recurrent (production-grade approach, out of PoC scope) | Project Owner | Accepted |
| R-024 | Data Quality / Tooling | Shell-based (`awk`) exact-string-equality checks for empty fields (`$N == ""`) silently undercount when the source CSV uses CRLF line terminators — a trailing `\r` makes the last field non-empty by strict comparison even though it is semantically empty | Medium | Low | Cross-validate shell-based data diagnostics against the actual production ingestion pipeline output before finalizing data quality metrics; prefer a language-aware CSV parser (Python `csv.reader`) as the source of truth over raw shell text comparison for anything beyond a quick sanity check | Re-run diagnostics with `file`/`grep -c $'\r'` to confirm CRLF presence; correct the documented findings to match the pipeline's actual behavior | Project Owner | Mitigated |


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

| Date | Lesson | Action Taken |
|------|---------|--------------|
| 2026-07-10 | Custom IAM policies granting `iam:CreateServiceLinkedRole` (even scoped via `iam:AWSServiceName` condition) did not prevent RDS from failing with `InvalidParameterValue: Missing necessary credentials` when `AWSServiceRoleForRDS` did not yet exist at account level. The role required a manual, one-time creation using elevated (admin) credentials, separate from the least-privilege deployer user. | Created `AWSServiceRoleForRDS` manually via `aws iam create-service-linked-role` using a temporary admin CLI profile; profile and its access key were removed immediately after use. Documented as a known first-time-setup step for any AWS account provisioning RDS for the first time. |
| 2026-07-10 | Least-privilege IAM policies designed upfront (Bootstrap) consistently missed narrow read-only Describe/List permissions not obvious until the exact CLI command was attempted (`rds:DescribeDBEngineVersions`, following the earlier `iam:CreateServiceLinkedRole` gap). Both failures were `AccessDenied`/`InvalidParameterValue` errors that only surfaced at execution time, not during policy review. | Adopted an iterative IAM policy design approach: run the intended command against the real AWS API first, treat each `AccessDenied` as a signal to add exactly the missing action (never a broader wildcard) to Bootstrap, then re-verify. Applied this same pattern for `rds:DescribeDBEngineVersions`. |
| 2026-07-11 | RDS free tier (750h/month for 12 months) does not apply to AWS accounts older than 12 months — confirmed via billing line items showing `$0.016 per db.t4g.micro instance hour` charged from hour one. Public IPv4 addresses also bill independently (~$0.005/h) since 2024 and are released while an RDS instance is stopped. The Zero Spend Budget detected the deviation within hours ($0.03), validating the detection-first cost strategy. | Adopted stop-when-idle discipline: `aws rds stop-db-instance` at the end of each work session, `start-db-instance` at the beginning (3-5 min warm-up; instance auto-restarts after 7 days stopped). Added `rds:StopDBInstance`/`rds:StartDBInstance` to the Runtime policy scoped to the instance ARN. Estimated project cost reduced from ~$17.65/month to ~$3-4 total. |
| 2026-07-13 | Initial shell-based data quality diagnosis (`awk -F',' '$5 == ""'`) reported 0 empty `job_id` values, but the production loader rejected 16 records for exactly this reason. Root cause: the source CSV uses CRLF line terminators, and `awk`'s exact string comparison does not match a field containing a trailing `\r`, while Python's `csv.reader` normalizes line terminators correctly. | Confirmed the CRLF hypothesis via `file` and `grep -c $'\r'`. Corrected `data-quality-analysis.md` with the real count (70 invalid records, not 54) and documented the methodology gap. Adopted the practice of cross-validating any shell-based data diagnostic against the real ingestion pipeline's output before treating a metric as final. |

---

# Revision History

| Version | Date | Author | Description |
|----------|------|--------|-------------|
| 1.0 | 2026-07-10 | Cristian Andrés Beltrán | Initial Risk Register |
| 1.1 | 2026-07-10 | Cristian Andrés Beltrán | Added R-021 (IAM Service-Linked Role provisioning gap) and first Lessons Learned entry |
| 1.2 | 2026-07-10 | Cristian Andrés Beltrán | Added R-022 (IAM least-privilege Describe/List permission gap) and corresponding Lessons Learned entry |
| 1.3 | 2026-07-11 | Cristian Andrés Beltrán | R-001 updated to Monitoring (free tier expiry confirmed via billing); added R-023 (root credentials for IAM operations) and cost lesson learned |
| 1.4 | 2026-07-13 | Cristian Andrés Beltrán | Added R-024 (CRLF blind spot in shell-based data diagnostics) and corresponding Lessons Learned entry |