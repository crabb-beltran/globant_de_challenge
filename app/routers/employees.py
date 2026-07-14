from datetime import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from models import HiredEmployee
from schemas.hired_employee import HiredEmployeeSchema
from schemas.common import BatchIngestResponse
from validators.business_rules import department_exists, job_exists
from loaders.historical import load_valid_ids, load_existing_employee_ids
from services.ingestion import ingest_batch

router = APIRouter(prefix="/employees", tags=["Employees"])

MAX_BATCH_SIZE = 1000


def _employee_field_map(record: HiredEmployeeSchema) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "hire_datetime": dt.strptime(record.hire_datetime, "%Y-%m-%dT%H:%M:%SZ"),
        "department_id": record.department_id,
        "job_id": record.job_id,
    }


@router.post("", response_model=BatchIngestResponse, status_code=207)
def ingest_employees(payload: list[HiredEmployeeSchema], db: Session = Depends(get_db)):
    if not (1 <= len(payload) <= MAX_BATCH_SIZE):
        raise HTTPException(422, f"batch size must be between 1 and {MAX_BATCH_SIZE} rows")

    valid_department_ids, valid_job_ids = load_valid_ids(db)
    existing_ids = load_existing_employee_ids(db)

    def _validate(record: HiredEmployeeSchema) -> None:
        department_exists(record.department_id, valid_department_ids)
        job_exists(record.job_id, valid_job_ids)

    return ingest_batch(
        db=db,
        records=payload,
        model_cls=HiredEmployee,
        id_field="id",
        field_map=_employee_field_map,
        existing_ids=existing_ids,
        validators=[_validate],
    )