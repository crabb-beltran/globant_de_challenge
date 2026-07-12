# Sprint Backlog

**Active Phase:** Historical Data Migration (WBS Phase 5)

**Branch:** feature/historical-loader

---

## Goal

Load the historical CSV datasets (`hired_employees`, `departments`, `jobs`)
into PostgreSQL, enforcing the challenge's validation rules and logging
rejected records.

### Tasks

- [ ] Analyze CSV structure and known data quality issues
- [ ] Design ingestion flow (staging vs direct-validated insert — see
      decisions.md if this becomes a real ADR-worthy choice)
- [ ] Implement CSV reader
- [ ] Implement per-record validation (required fields, FK existence)
- [ ] Implement batch processing
- [ ] Implement rejected-record logging (CloudWatch, per ADR-004)
- [ ] Implement valid-record insertion
- [ ] Verify row counts against source CSVs

Priority

High

Status

Pending

---

# Definition of Done (DoD)

A task is considered complete when:

- [ ] Code implemented
- [ ] Code reviewed
- [ ] Tests passed
- [ ] Documentation updated
- [ ] Docker verified
- [ ] GitHub pushed
- [ ] Pull Request merged