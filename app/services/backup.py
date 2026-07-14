"""
AVRO export service — one file per table, written to local filesystem
per ADR-012 (reconciles ADR-006's S3 mention with the challenge's literal
"save it in AVRO format on the filesystem" requirement).
"""

import os
import fastavro
from sqlalchemy.orm import Session

BACKUP_DIR = os.getenv("BACKUP_DIR", "/app/backups")

DEPARTMENT_SCHEMA = {
    "type": "record",
    "name": "Department",
    "namespace": "globant",
    "fields": [{"name": "id", "type": "int"}, {"name": "department", "type": "string"}],
}
JOB_SCHEMA = {
    "type": "record",
    "name": "Job",
    "namespace": "globant",
    "fields": [{"name": "id", "type": "int"}, {"name": "job", "type": "string"}],
}
HIRED_EMPLOYEE_SCHEMA = {
    "type": "record",
    "name": "HiredEmployee",
    "namespace": "globant",
    "fields": [
        {"name": "id", "type": "int"},
        {"name": "name", "type": "string"},
        # Stored as ISO string, not an AVRO logical timestamp type — keeps
        # the schema simple and matches the exact format already used
        # throughout the project (schemas/hired_employee.py regex).
        {"name": "hire_datetime", "type": "string"},
        {"name": "department_id", "type": "int"},
        {"name": "job_id", "type": "int"},
    ],
}


def export_table(
    db: Session, model_cls, schema: dict, table_name: str, record_map
) -> dict:
    """
    record_map: callable(row) -> dict matching `schema`'s fields exactly.
    Writes {table_name}.avro to BACKUP_DIR, overwriting any prior backup
    for that table (a backup is a full-table snapshot, not an append log).
    """
    os.makedirs(BACKUP_DIR, exist_ok=True)
    rows = db.query(model_cls).all()
    records = [record_map(row) for row in rows]

    file_path = os.path.join(BACKUP_DIR, f"{table_name}.avro")
    with open(file_path, "wb") as out:
        fastavro.writer(out, schema, records)

    return {"table": table_name, "file": file_path, "record_count": len(records)}
