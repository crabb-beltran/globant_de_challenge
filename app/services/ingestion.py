"""
Generic batch ingestion service shared by employees/departments/jobs
routers. Mirrors loaders/historical.py and loaders/reference_data.py —
same validate -> insert -> log-rejection pattern, but the input source
is an HTTP body instead of a CSV row, failures are isolated per-record
(SAVEPOINT), and every rejection carries a structured reason_code
(not just a free-text message) for programmatic handling downstream
(e.g. client retry logic, monitoring dashboards).
"""

from typing import Callable
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logging_.rejected_records import log_rejected_record
from validators.exceptions import BusinessRuleViolation, DuplicateRecordError, ConstraintViolation


def ingest_batch(
    db: Session,
    records: list,
    model_cls,
    id_field: str,
    field_map: Callable,
    existing_ids: set,
    validators: list[Callable] | None = None,
) -> dict:
    inserted = 0
    rejected = 0
    rejected_records = []
    seen_in_batch: set = set()

    for record in records:
        record_id = getattr(record, id_field)
        error_message = None
        error_code = None

        try:
            if validators:
                for validator in validators:
                    validator(record)

            if record_id in existing_ids or record_id in seen_in_batch:
                raise DuplicateRecordError(f"{id_field} {record_id} already exists (duplicate)")

            try:
                with db.begin_nested():  # SAVEPOINT — isolates this record only
                    db.add(model_cls(**field_map(record)))
            except IntegrityError as e:
                raise ConstraintViolation(f"database constraint violation: {e.orig}") from e

            seen_in_batch.add(record_id)
            inserted += 1

        except BusinessRuleViolation as e:
            error_message = str(e)
            error_code = e.code
        except ValueError as e:
            # safety net: any validator that raises plain ValueError
            # instead of a BusinessRuleViolation subclass still gets
            # rejected with a generic code, rather than crashing the batch.
            error_message = str(e)
            error_code = "VALIDATION_ERROR"

        if error_code:
            log_rejected_record(row=record.model_dump(), error=f"[{error_code}] {error_message}", source="rest_api")
            rejected += 1
            rejected_records.append({
                "record": record.model_dump(),
                "reason": error_message,
                "reason_code": error_code,
            })

    db.commit()
    return {"inserted": inserted, "rejected": rejected, "rejected_records": rejected_records}