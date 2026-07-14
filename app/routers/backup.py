from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.session import get_db
from models import Department, Job, HiredEmployee
from services.backup import (
    export_table,
    DEPARTMENT_SCHEMA,
    JOB_SCHEMA,
    HIRED_EMPLOYEE_SCHEMA,
)

router = APIRouter(prefix="/backup", tags=["Backup"])


@router.post("")
def run_backup(db: Session = Depends(get_db)):
    """Exports all three tables to individual AVRO files (filesystem,
    per ADR-012). Triggered on-demand — in production this would be
    invoked by a scheduled job (e.g. EventBridge + Lambda), not a manual
    call; out of scope for this PoC (see risk-register.md R-016)."""

    results = [
        export_table(
            db,
            Department,
            DEPARTMENT_SCHEMA,
            "departments",
            lambda row: {"id": row.id, "department": row.department},
        ),
        export_table(
            db,
            Job,
            JOB_SCHEMA,
            "jobs",
            lambda row: {"id": row.id, "job": row.job},
        ),
        export_table(
            db,
            HiredEmployee,
            HIRED_EMPLOYEE_SCHEMA,
            "hired_employees",
            lambda row: {
                "id": row.id,
                "name": row.name,
                "hire_datetime": row.hire_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "department_id": row.department_id,
                "job_id": row.job_id,
            },
        ),
    ]
    return {"backups": results}
