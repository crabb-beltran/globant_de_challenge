# Restore Strategy

## Semantics — Truncate + Reload, Not Skip-If-Exists

Restore returns a table to the exact state captured in its most recent
backup. This is a deliberate divergence from the historical CSV loaders'
idempotency strategy (ADR-010, skip-if-exists): that strategy solves a
different problem — safely re-running a *migration* without losing data
inserted through other channels (e.g. the REST API). Restore solves
"return to a known snapshot," which requires the table's current content
to be fully replaced, not merged with post-backup data. Skip-if-exists
would silently fail to apply this semantic (existing rows would never be
overwritten, and the table would end up in a hybrid state that matches
neither the backup nor the pre-restore state).

**Restore is destructive.** Every restore endpoint requires an explicit
`?confirm=true` query parameter; without it, the request is rejected
with `400` and an explanatory message. This is the PoC's minimal
safety guardrail against an accidental call — not a substitute for
proper access control in a real deployment (see "Future Improvements"
in the main README).

## Two Endpoints, Two Safety Profiles

### `POST /restore` — restore all three tables together (recommended)

Orchestrates `departments`, `jobs`, and `hired_employees` in two phases:

1. **Truncate phase**: a single `TRUNCATE TABLE departments, jobs, hired_employees`
   statement, covering all three tables in one command.
2. **Reload phase**: reload each table from its `.avro` backup file, in
   parent-to-child order (`departments`, `jobs`, then `hired_employees`),
   with an explicit `db.flush()` after each table (see "Incident" below
   for why this is required, not optional).

The entire operation commits atomically at the end — if any phase fails,
nothing is persisted.

### `POST /restore/{table_name}` — restore a single table in isolation

Truncates and reloads only the named table. **Only safe when no other
table has a foreign key constraint referencing this one** — in practice,
this means it's safe for `hired_employees` (nothing references it), but
generally unsafe for `departments` or `jobs` while `hired_employees` has
any rows at all, *regardless of whether those rows would actually
conflict*. If the truncate is rejected, the endpoint returns `409` with
a message pointing to `POST /restore` instead.

Use case for this endpoint: recovering a single reference table when you
already know (or have already cleared) its dependents — e.g. restoring
`hired_employees` alone after a bad API ingestion, without touching
`departments`/`jobs` at all.

## Incident: Why Sequential Per-Table Restore Fails

During implementation, restoring all three tables by calling
`POST /restore/{table_name}` three times in sequence (`hired_employees`,
then `jobs`, then `departments`) was the first design attempted. It
failed, and the failure mode is worth documenting because it corrects
two incorrect assumptions that are easy to make with Postgres `TRUNCATE`
and SQLAlchemy sessions.

### Finding 1 — `TRUNCATE` blocks on FK *existence*, not row count

The initial assumption was: truncate `hired_employees` first (the
child), then `jobs` and `departments` (the parents) would truncate
cleanly since the child table is now empty. This is wrong. Postgres
rejects `TRUNCATE` on a table if **any other table has a FK constraint
referencing it** — irrespective of whether that referencing table
currently holds zero rows or a million. The check is against the
constraint's existence, not the data.

psycopg2.errors.FeatureNotSupported: cannot truncate a table referenced
in a foreign key constraint
DETAIL:  Table "hired_employees" references "departments".
HINT:  Truncate table "hired_employees" at the same time, or use
TRUNCATE ... CASCADE.

Worse: even after `hired_employees` was successfully truncated *and
reloaded* with fresh data (still referencing `jobs`/`departments`),
attempting to then truncate `jobs` failed for the same structural
reason — the constraint still existed, now pointing at freshly-reloaded
rows instead of the original ones.

**Fix**: truncate all FK-related tables in a **single** `TRUNCATE`
statement (`TRUNCATE TABLE departments, jobs, hired_employees`), which
Postgres explicitly supports and is what its own HINT message suggests
(the `CASCADE` alternative was deliberately rejected — see below).

### Finding 2 — `Session.add()` does not guarantee cross-table INSERT order without `flush()`

After fixing the truncate strategy, reload still failed:

psycopg2.errors.ForeignKeyViolation: insert or update on table
"hired_employees" violates foreign key constraint
"hired_employees_job_id_fkey"
DETAIL:  Key (job_id)=(96) is not present in table "jobs".

This looked like a data integrity problem (was `job_id=96` actually
missing from the backup?), but direct inspection of `jobs.avro`
confirmed the backup was complete and correct (183 records, IDs 1–183,
`id=96` present). The real cause: `Session.add()` queues objects for
insertion, but does not insert them immediately. SQLAlchemy 2.0's
bulk-insert optimization (`_exec_insertmany_context`) does not guarantee
that objects are flushed to the database in the order `add()` was
called across different tables within the same unit of work — the
`hired_employees` INSERT could be dispatched before the `jobs` INSERT
it depends on, even though both were already queued in the same
session, because no `flush()` had forced the `jobs` rows to actually
reach Postgres yet.

**Fix**: call `db.flush()` explicitly after loading each table, before
moving to the next. This forces that table's rows to hit the database
immediately, without committing the transaction — the whole restore
still commits atomically at the very end, preserving all-or-nothing
semantics.

### Why not `TRUNCATE ... CASCADE`?

Postgres's own error HINT suggests `CASCADE` as an alternative. It was
deliberately rejected: `CASCADE` truncates *any* table with a FK
pointing at the target, including tables not explicitly part of this
restore's scope — if a future phase adds a new table referencing
`departments`, a `CASCADE` truncate would silently wipe it too, with no
warning. Listing the known, closed set of tables explicitly in one
`TRUNCATE` statement achieves the same result for this project's fixed
schema, without that silent-blast-radius risk.

## Endpoints

### `POST /restore`

Query params: `confirm: bool` (required `true` to proceed).

**Response**: `200 OK`
```json
{
  "restored": [
    {"table": "departments", "restored_count": 19},
    {"table": "jobs", "restored_count": 183},
    {"table": "hired_employees", "restored_count": 1930}
  ]
}
```

| Status | Condition |
|---|---|
| 200 | All three tables restored successfully |
| 400 | Missing `?confirm=true` |
| 404 | One or more `.avro` backup files not found — run `POST /backup` first |

### `POST /restore/{table_name}`

Path param: `table_name` — one of `departments`, `jobs`, `hired_employees`.
Query params: `confirm: bool` (required `true` to proceed).

| Status | Condition |
|---|---|
| 200 | Table restored successfully |
| 400 | Missing `?confirm=true` |
| 404 | Unknown `table_name`, or no backup file found for it |
| 409 | `TRUNCATE` blocked by a FK constraint from another table — use `POST /restore` instead |

## Related Documentation

- `docs/06-backup/backup.md` — backup strategy, AVRO schema design
- ADR-010 — idempotency strategy for historical loaders (contrast with restore's truncate+reload semantics)
- ADR-012 — filesystem-vs-S3 storage reconciliation