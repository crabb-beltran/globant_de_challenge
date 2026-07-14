from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from models import Department
from schemas.department import Departments
from schemas.common import BatchIngestResponse
from services.ingestion import ingest_batch

router = APIRouter(prefix="/departments", tags=["Departments"])

MAX_BATCH_SIZE = 1000


def _department_field_map(record: Departments) -> dict:
    return {"id": record.id, "department": record.department}


@router.post("", response_model=BatchIngestResponse, status_code=207)
def ingest_departments(payload: list[Departments], db: Session = Depends(get_db)):
    if not (1 <= len(payload) <= MAX_BATCH_SIZE):
        raise HTTPException(
            422, f"batch size must be between 1 and {MAX_BATCH_SIZE} rows"
        )

    existing_ids = {row.id for row in db.query(Department.id).all()}

    return ingest_batch(
        db=db,
        records=payload,
        model_cls=Department,
        id_field="id",
        field_map=_department_field_map,
        existing_ids=existing_ids,
        validators=None,
    )
