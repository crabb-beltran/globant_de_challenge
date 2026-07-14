"""
AVRO restore service.

Two restore modes:
  - restore_table(): single-table TRUNCATE+reload. Will ALWAYS fail with
    RestoreOrderError if ANY other table has a FK constraint referencing
    this one — regardless of whether that referencing table currently
    has rows. Postgres blocks TRUNCATE based on the existence of the FK
    constraint, not on current row count (see restore_all for why this
    matters). Safe only for a table with no FK dependents at all.
  - restore_all(): orchestrates all three tables in two phases —
    (1) a SINGLE TRUNCATE statement covering all three tables together
    (required: Postgres refuses to truncate a referenced table unless
    all referencing tables are truncated in the same command), then
    (2) INSERT all tables parent-to-child order, so FK targets exist
    before the rows that reference them. See docs/07-restore/restore.md
    for the full incident writeup — an earlier design attempted
    sequential per-table TRUNCATE (child, then parent) and failed even
    after the child was already empty, which is what revealed this
    Postgres behavior.

CRITICAL: no TRUNCATE ... CASCADE — CASCADE would silently wipe any
future table added to the FK chain that isn't explicitly part of this
restore's scope. Listing tables explicitly in one TRUNCATE is safer and
equally effective for a closed, known set of tables.
"""

import os
import fastavro
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError


class RestoreOrderError(Exception):
    """Raised when TRUNCATE fails because another table's FK constraint
    still references this one. For a single table with any FK
    dependents, use restore_all() instead of restore_table()."""


def _load(db: Session, avro_path: str, row_map) -> int:
    with open(avro_path, "rb") as f:
        records = list(fastavro.reader(f))
    for record in records:
        db.add(row_map(record))
    return len(records)


def restore_table(db: Session, table_name: str, avro_path: str, row_map) -> dict:
    """Single-table TRUNCATE + reload. See module docstring: fails if
    ANY table has a FK constraint referencing table_name, regardless of
    that table's current row count."""
    try:
        db.execute(text(f"TRUNCATE TABLE {table_name}"))
    except DBAPIError as e:
        db.rollback()
        raise RestoreOrderError(
            f"Cannot truncate '{table_name}': another table's foreign key "
            f"constraint references it (Postgres blocks this regardless "
            f"of whether that table currently has rows). Use POST "
            f"/restore (restore_all) to restore related tables together. "
            f"Original error: {e.orig}"
        ) from e

    count = _load(db, avro_path, row_map)
    db.commit()
    return {"table": table_name, "restored_count": count}


# Parent -> child order, used for the reload phase (FK targets must
# exist before rows referencing them are inserted).
RESTORE_ORDER_PARENT_TO_CHILD = ["departments", "jobs", "hired_employees"]


def restore_all(db: Session, table_configs: dict, backup_dir: str) -> dict:
    """
    Phase 1: a single TRUNCATE statement covering all three tables at
    once — required because Postgres refuses to truncate a table
    referenced by another table's FK unless both are truncated together
    in the same command.
    Phase 2: reload all tables, parent to child, with an explicit
    flush() after each table — NOT just db.add() followed by a single
    final commit(). Without the intermediate flush, SQLAlchemy's
    bulk-insert batching (_exec_insertmany_context) does not guarantee
    INSERT execution order matches the order records were added to the
    session, so a hired_employees row can attempt to insert before its
    referenced job/department row has actually been sent to Postgres —
    even though both are already in the Python-side session. flush()
    forces each table's rows to hit the database before the next
    table's rows are added, without committing the transaction (the
    whole restore still commits atomically at the end).
    """
    all_tables = ", ".join(RESTORE_ORDER_PARENT_TO_CHILD)
    db.execute(text(f"TRUNCATE TABLE {all_tables}"))

    results = []
    for table_name in RESTORE_ORDER_PARENT_TO_CHILD:
        row_map = table_configs[table_name]
        avro_path = os.path.join(backup_dir, f"{table_name}.avro")
        count = _load(db, avro_path, row_map)
        db.flush()  # <-- forces this table's INSERTs before the next table's rows are added
        results.append({"table": table_name, "restored_count": count})

    db.commit()
    return {"restored": results}
