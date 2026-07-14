# Backup Strategy

## Storage Location — Filesystem, Not S3

Per the challenge's literal requirement ("save it in AVRO format on the
filesystem") and **ADR-012**, backups are written to local filesystem
(`/app/backups/`), not uploaded to S3. This reconciles an earlier, more
general decision in ADR-006 ("Apache AVRO stored in Amazon S3") with the
graded requirement — see ADR-012 for the full rationale. S3 upload
remains a documented future extension (bucket already provisioned in
Phase 3 infrastructure).

## Trigger — On-Demand, Not Scheduled

`POST /backup` runs synchronously when called. No scheduler (cron,
EventBridge, Airflow) is implemented — the challenge does not require
automation, and adding one would be unjustified scope beyond the PoC's
evaluation criteria (see `risk-register.md` R-016, Overengineering).

**Production note**: a manual, on-demand endpoint is fragile as a real
backup strategy — if nobody calls it, no backup exists. In a production
deployment, this endpoint would be invoked by a scheduled job (e.g. an
EventBridge rule triggering a Lambda) rather than left to manual
operator discipline. Documented here as intent, not implemented, to
keep this phase scoped to what the challenge actually asks for.

## Scope — One File Per Table

Each table (`departments`, `jobs`, `hired_employees`) is exported to its
own AVRO file (`departments.avro`, `jobs.avro`, `hired_employees.avro`),
each with its own AVRO schema matching that table's columns exactly.
This matches the challenge's phrasing ("export **the full content of
each table**") and keeps each file's schema simple and independently
restorable — see `restore.md` for why independent per-table restore is
nonetheless not always safe given FK dependencies.

A backup is a **full-table snapshot**, not an incremental or append-only
log: each call to `POST /backup` overwrites the previous `.avro` file
for that table. There is no backup versioning or history in this PoC —
only "the most recent backup" exists at any time. Extension point:
timestamped filenames (`departments_20260713T120000Z.avro`) would enable
point-in-time restore, out of scope here per the same overengineering
guardrail.

## Endpoint

### `POST /backup`

No request body. Exports all three tables in one call.

**Response**: `200 OK`
```json
{
  "backups": [
    {"table": "departments", "file": "/app/backups/departments.avro", "record_count": 19},
    {"table": "jobs", "file": "/app/backups/jobs.avro", "record_count": 183},
    {"table": "hired_employees", "file": "/app/backups/hired_employees.avro", "record_count": 1930}
  ]
}
```

## AVRO Schemas

Each table's AVRO schema is a flat record type matching its SQLAlchemy
model's columns. `hire_datetime` is stored as a `string` (ISO 8601,
`Z`-suffixed) rather than an AVRO logical timestamp type — this keeps
the schema simple and reuses the exact same format already validated
throughout the project (`schemas/hired_employee.py`), avoiding a second
datetime representation to keep in sync.

## Persistence Note (Local Development)

`/app/backups` is a bind-mounted volume (`./backups:/app/backups` in
`docker-compose.yml`), so backup files persist across container
restarts, same as the Postgres data volume. The mount must be owned by
the container's