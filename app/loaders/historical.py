import csv
import sys
from datetime import datetime as dt

from pydantic import ValidationError

from db.session import SessionLocal
from models import Department, Job, HiredEmployee
from schemas.hired_employee import HiredEmployeeSchema
from validators.business_rules import department_exists, job_exists
from logging_.rejected_records import log_rejected_record


def load_valid_ids(db_session) -> tuple[set[int], set[int]]:
    department_ids = {row.id for row in db_session.query(Department.id).all()}
    job_ids = {row.id for row in db_session.query(Job.id).all()}
    return department_ids, job_ids


def load_existing_employee_ids(db_session) -> set[int]:
    return {row.id for row in db_session.query(HiredEmployee.id).all()}


def process_row(row: list[str], valid_department_ids: set[int], valid_job_ids: set[int]):
    """
    Validates one CSV row. Returns (validated_record, error) — exactly
    one of the two is always None.
    """
    try:
        validated = HiredEmployeeSchema(
            id=row[0],
            name=row[1],
            hire_datetime=row[2],
            department_id=row[3],
            job_id=row[4],
        )
        department_exists(validated.department_id, valid_department_ids)
        job_exists(validated.job_id, valid_job_ids)
        return validated, None

    except (ValidationError, ValueError) as e:
        return None, str(e)


def run_historical_load(csv_path: str) -> dict:
    db = SessionLocal()
    try:
        valid_department_ids, valid_job_ids = load_valid_ids(db)
        existing_employee_ids = load_existing_employee_ids(db)

        inserted_count = 0
        rejected_count = 0
        skipped_count = 0

        with open(csv_path, newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                record, error = process_row(row, valid_department_ids, valid_job_ids)

                if not record:
                    log_rejected_record(row=row, error=error)
                    rejected_count += 1
                    continue

                if record.id in existing_employee_ids:
                    skipped_count += 1
                    continue

                hire_datetime = dt.strptime(record.hire_datetime, "%Y-%m-%dT%H:%M:%SZ")
                employee = HiredEmployee(
                    id=record.id,
                    name=record.name,
                    hire_datetime=hire_datetime,
                    department_id=record.department_id,
                    job_id=record.job_id,
                )
                db.add(employee)
                inserted_count += 1

        db.commit()
        return {"inserted": inserted_count, "rejected": rejected_count, "skipped": skipped_count}

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    result = run_historical_load(sys.argv[1])
    print(result)