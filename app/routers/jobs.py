from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from models import Job
from schemas.job import Jobs
from schemas.common import BatchIngestResponse
from services.ingestion import ingest_batch

router = APIRouter(prefix="/jobs", tags=["Jobs"])

MAX_BATCH_SIZE = 1000


def _job_field_map(record: Jobs) -> dict:
    return {"id": record.id, "job": record.job}


@router.post("", response_model=BatchIngestResponse, status_code=207)
def ingest_jobs(payload: list[Jobs], db: Session = Depends(get_db)):
    if not (1 <= len(payload) <= MAX_BATCH_SIZE):
        raise HTTPException(422, f"batch size must be between 1 and {MAX_BATCH_SIZE} rows")

    existing_ids = {row.id for row in db.query(Job.id).all()}

    return ingest_batch(
        db=db,
        records=payload,
        model_cls=Job,
        id_field="id",
        field_map=_job_field_map,
        existing_ids=existing_ids,
        validators=None,
    )