"""
Generic loader for reference-data tables without foreign keys
(departments, jobs). Idempotent: records whose ID already exists in the
database are skipped, not re-inserted or updated (see ADR-010).
"""

import csv
import sys

from pydantic import ValidationError

from db.session import SessionLocal
from logging_.rejected_records import log_rejected_record


def load_existing_ids(db_session, model_cls) -> set[int]:
    return {row.id for row in db_session.query(model_cls.id).all()}


def load_reference_csv(
    csv_path: str, schema_cls, model_cls, id_field: str, name_field: str
) -> dict:
    """
    schema_cls: Pydantic schema (Departments or Jobs)
    model_cls: SQLAlchemy model (Department or Job)
    id_field / name_field: attribute names, identical on both schema and model
                            (e.g. "id"/"department", or "id"/"job")
    """
    db = SessionLocal()
    inserted_count = 0
    rejected_count = 0
    skipped_count = 0

    try:
        existing_ids = load_existing_ids(db, model_cls)

        with open(csv_path, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    validated = schema_cls(**{id_field: row[0], name_field: row[1]})
                except (ValidationError, ValueError) as e:
                    log_rejected_record(
                        row=row, error=str(e), source="reference_data_loader"
                    )
                    rejected_count += 1
                    continue

                record_id = getattr(validated, id_field)

                if record_id in existing_ids:
                    skipped_count += 1
                    continue

                instance = model_cls(
                    **{
                        id_field: record_id,
                        name_field: getattr(validated, name_field),
                    }
                )
                db.add(instance)
                inserted_count += 1

        db.commit()
        return {
            "inserted": inserted_count,
            "rejected": rejected_count,
            "skipped": skipped_count,
        }

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    from schemas.department import Departments
    from schemas.job import Jobs
    from models import Department, Job

    result_dept = load_reference_csv(
        sys.argv[1], Departments, Department, "id", "department"
    )
    print("Departments:", result_dept)

    result_jobs = load_reference_csv(sys.argv[2], Jobs, Job, "id", "job")
    print("Jobs:", result_jobs)
