# Sprint Backlog

**Active Phase:** Backup & Restore (WBS Phase 8) — CLOSED

**Branch:** feature/backup-restore

---

## Goal

Implement AVRO export (`POST /backup`) and restore (`POST /restore`,
`POST /restore/{table_name}`) for `departments`, `jobs`, and
`hired_employees`, following the challenge's literal requirements
(filesystem storage, AVRO format) and reconciling the earlier S3-based
ADR-006 via ADR-012.

### Design Decisions (resolved before implementation)

- [x] Backup trigger: on-demand endpoint, no scheduler (out of scope
      per R-016)
- [x] Backup scope: one AVRO file per table, full-snapshot overwrite
      (no versioning/history in this PoC)
- [x] Storage location: local filesystem (`/app/backups/`), per the
      challenge's literal requirement — ADR-012 reconciles ADR-006
- [x] Restore semantics: TRUNCATE + reload (not skip-if-exists like
      ADR-010's historical loaders) — restoring means returning to a
      known snapshot, not merging with post-backup data
- [x] Restore safety guardrail: explicit `?confirm=true` required,
      given the destructive nature of the operation