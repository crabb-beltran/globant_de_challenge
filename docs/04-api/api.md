# API Specification

## Design Decisions

**Separate endpoints per table** (not a generic `/ingest/{table}` endpoint).
Rationale: each table has a distinct Pydantic schema and distinct business
rules (only `employees` requires FK existence checks). A generic endpoint
would still need internal dispatch logic without reducing code, while
losing explicit OpenAPI documentation per resource. See `decisions.md`
for the full trade-off if this becomes ADR-worthy.

**Thin router / fat service pattern**: routers (`routers/employees.py`,
`routers/departments.py`, `routers/jobs.py`) only handle HTTP concerns
(status codes, batch size limits). All ingestion logic — validation,
insertion, rejection — lives in `services/ingestion.py`, shared across
all three routers.

**Partial success (HTTP 207)**: a batch of 1-1000 records may contain a
mix of valid and invalid rows. Valid rows are inserted; invalid rows are
rejected and reported individually in the response body. The batch is
never fully rejected due to one bad row (unlike the historical CSV
loader, which is a single all-or-nothing transaction by design — see
Fase 5).

**Duplicate IDs are rejected, not skipped.** Unlike the idempotent
CSV loaders (`loaders/historical.py`, `loaders/reference_data.py`,
ADR-010), which silently skip already-existing IDs during a historical
migration re-run, the REST API treats a duplicate `id` in an ingestion
request as a rejected record with `reason_code: DUPLICATE_ID`. Rationale:
an API client sending a duplicate ID is either a client-side bug or an
unintended retry — both deserve visibility, not silent skipping.

**Per-record isolation via SAVEPOINT** (`db.begin_nested()`): if one
record in a batch violates a database-level constraint not caught by
in-memory validation (e.g. a race condition on a concurrent request),
only that record is rolled back — not the entire batch.

---

## Endpoints

### `POST /employees`

Batch ingestion of hired employees. Body: JSON array, 1-1000 objects.

**Request schema** (`HiredEmployeeSchema`):

| field | type | required | notes |
|---|---|---|---|
| id | int | yes | must not already exist |
| name | string | yes | non-empty |
| hire_datetime | string | yes | ISO 8601 UTC, e.g. `2021-07-27T16:02:08Z` |
| department_id | int | yes | must reference an existing department |
| job_id | int | yes | must reference an existing job |

**Response**: `207 Multi-Status`, body per `BatchIngestResponse` (see
`validation.md` for `reason_code` values).

### `POST /departments`

Batch ingestion of departments. Body: JSON array, 1-1000 objects.

| field | type | required |
|---|---|---|
| id | int | yes |
| department | string | yes |

**Response**: `207 Multi-Status`.

### `POST /jobs`

Batch ingestion of jobs. Body: JSON array, 1-1000 objects.

| field | type | required |
|---|---|---|
| id | int | yes |
| job | string | yes |

**Response**: `207 Multi-Status`.

---

## Response Contract (all three endpoints)

```json
{
  "inserted": 2,
  "rejected": 1,
  "rejected_records": [
    {
      "record": { "id": 5, "name": "...", "department_id": 999, "job_id": 3, "hire_datetime": "..." },
      "reason": "department_id 999 does not reference an existing department",
      "reason_code": "FK_VIOLATION"
    }
  ]
}
```

## Error Handling

| Status | Condition |
|---|---|
| 207 | Batch processed — see `inserted`/`rejected` counts (this is the normal outcome for a partially valid batch) |
| 422 | Batch size outside 1-1000, or a record fails Pydantic field-level validation (malformed JSON structure/types) |
| 500 | Unhandled server error (should not occur under normal operation — indicates a bug) |

Field-level validation errors (missing required field, malformed
`hire_datetime`) are caught by FastAPI/Pydantic **before** reaching
`services/ingestion.py`, and return `422` for the entire request —
this is different from business-rule rejections (FK, duplicate), which
are per-record and return within a `207`. See `validation.md` for the
full distinction.