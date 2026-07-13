# Historical Data Migration — Execution Guide

## Prerequisites

- Local Docker stack running (`docker-compose up -d`)
- `datasets/` bind-mounted into the `api` container at `/datasets`
  (added to `docker-compose.yml`: `- ./datasets:/datasets`)
- Database schema migrated (`alembic upgrade head` — see Phase 4)

## Execution Order (mandatory)

Reference data (`departments`, `jobs`) must be loaded before
`hired_employees`, since the latter validates foreign keys against them.

```bash
docker-compose exec api bash
cd /app

# 1. Reference data first
python -m loaders.reference_data /datasets/departments.csv /datasets/jobs.csv

# 2. Historical employee data
python -m loaders.historical /datasets/hired_employees.csv
```

## Verifying Results

```bash
docker-compose exec postgres_rds psql -U globant_de_challenge -d globant_de_challenge -c \
  "SELECT COUNT(*) FROM departments; SELECT COUNT(*) FROM jobs; SELECT COUNT(*) FROM hired_employees;"
```

Expected: 12 departments, 183 jobs, 1929 hired_employees.

## Re-running the Loaders

Both loaders are idempotent (see ADR-010, `decisions.md`) — re-running
against already-loaded data skips existing records rather than failing
or duplicating them. Output includes an explicit `skipped` count.

## Inspecting Rejected Records

Rejected records are logged as structured JSON to stdout:

```bash
docker-compose logs api | grep record_rejected
```

## Known Issues Encountered

| Issue | Root Cause | Resolution | Reference |
|---|---|---|---|
| `datasets/` not accessible inside the `api` container | Directory was not bind-mounted in `docker-compose.yml` | Added `- ./datasets:/datasets` volume to the `api` service | This document |
| Initial `awk`-based data quality check reported 0 empty `job_id` values, but the loader rejected 16 | Source CSV uses CRLF line terminators; `awk` exact-string comparison does not match a field with a trailing `\r` | Cross-validated against Python's `csv.reader` (correct); corrected `data-quality-analysis.md` | `risk-register.md` R-024 |
| `jobs.csv` reported as 182 rows via `wc -l`, but 183 were loaded | Last line has no trailing newline; `wc -l` undercounts in this case | Confirmed via `xxd` byte inspection of file tail | `data-quality-analysis.md` |