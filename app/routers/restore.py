from datetime import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from db.session import get_db
from models import Department, Job, HiredEmployee
from services.restore import restore_table, restore_all, RestoreOrderError
from services.backup import BACKUP_DIR
import os

router = APIRouter(prefix="/restore", tags=["Restore"])

ROW_MAPS = {
    "departments": lambda r: Department(id=r["id"], department=r["department"]),
    "jobs": lambda r: Job(id=r["id"], job=r["job"]),
    "hired_employees": lambda r: HiredEmployee(
        id=r["id"],
        name=r["name"],
        hire_datetime=dt.strptime(r["hire_datetime"], "%Y-%m-%dT%H:%M:%SZ"),
        department_id=r["department_id"],
        job_id=r["job_id"],
    ),
}


@router.post("")
def run_restore_all(
    confirm: bool = Query(
        False,
        description="Must be true — restores ALL three tables (TRUNCATE + reload each).",
    ),
    db: Session = Depends(get_db),
):
    """
    Restores departments, jobs, and hired_employees together, in the
    only order that is safe given their FK dependencies: TRUNCATE all
    (children first), then reload all (parents first). Use this instead
    of calling POST /restore/{table_name} three times in sequence —
    that sequence fails, see docs/07-restore/restore.md.
    """
    if not confirm:
        raise HTTPException(
            400,
            "restore is destructive: it TRUNCATEs departments, jobs, and "
            "hired_employees before reloading each from backup. Retry "
            "with ?confirm=true to proceed.",
        )

    missing = [
        t for t in ROW_MAPS if not os.path.exists(os.path.join(BACKUP_DIR, f"{t}.avro"))
    ]
    if missing:
        raise HTTPException(
            404, f"missing backup file(s) for: {missing}. Run POST /backup first."
        )

    return restore_all(db, ROW_MAPS, BACKUP_DIR)


@router.post("/{table_name}")
def run_restore_single(
    table_name: str,
    confirm: bool = Query(
        False, description="Must be true — restore is destructive (TRUNCATE + reload)."
    ),
    db: Session = Depends(get_db),
):
    """
    Restores a single table in isolation. Only safe when the target
    table has no active dependent rows (e.g. restoring `departments`
    when `hired_employees` is empty). For restoring multiple related
    tables together, use POST /restore instead.
    """
    if table_name not in ROW_MAPS:
        raise HTTPException(
            404, f"unknown table '{table_name}'. Valid: {list(ROW_MAPS)}"
        )

    if not confirm:
        raise HTTPException(
            400,
            f"restore is destructive: it TRUNCATEs '{table_name}' before reloading from backup. "
            f"Retry with ?confirm=true to proceed.",
        )

    avro_path = os.path.join(BACKUP_DIR, f"{table_name}.avro")
    if not os.path.exists(avro_path):
        raise HTTPException(
            404, f"no backup file found at {avro_path}. Run POST /backup first."
        )

    try:
        return restore_table(db, table_name, avro_path, ROW_MAPS[table_name])
    except RestoreOrderError as e:
        raise HTTPException(409, str(e))
