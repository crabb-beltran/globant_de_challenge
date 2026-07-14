"""
Integration tests for services/restore.py — require a real Postgres
connection, NOT the SQLite fixture used by test_ingestion_service.py /
test_schemas.py. SQLite cannot validate this module: it has no TRUNCATE
statement and does not enforce FK constraints by default, so the two
Postgres-specific bugs this phase uncovered (multi-table TRUNCATE
requirement, cross-table INSERT ordering without flush()) would not
reproduce there at all — a SQLite-based test would pass regardless of
whether the fix is present, giving false confidence.

Skipped automatically unless RUN_INTEGRATION_TESTS=1 is set, so the
default `pytest /tests/` run (used in CI / quick local checks) does not
require a live database. Run explicitly with:

    docker-compose exec api bash
    RUN_INTEGRATION_TESTS=1 python -m pytest /tests/test_restore_integration.py -v

Uses the same Postgres instance as local development (db/session.py's
SessionLocal) — NOT an isolated test database. Tests clean up after
themselves via TRUNCATE, but this means it should not be run against a
database whose current state you care about preserving.
"""

import os
import pytest
from datetime import datetime as dt

from db.session import SessionLocal
from models import Department, Job, HiredEmployee
from services.restore import restore_all, restore_table, RestoreOrderError, RESTORE_ORDER_PARENT_TO_CHILD

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="requires a live Postgres connection; set RUN_INTEGRATION_TESTS=1 to run",
)


@pytest.fixture()
def pg_session():
    db = SessionLocal()
    # start from a known-empty state for the three tables under test
    db.execute_text = None  # placeholder to avoid confusion with ORM execute below
    from sqlalchemy import text
    db.execute(text(f"TRUNCATE TABLE {', '.join(RESTORE_ORDER_PARENT_TO_CHILD)}"))
    db.commit()
    try:
        yield db
    finally:
        from sqlalchemy import text
        db.execute(text(f"TRUNCATE TABLE {', '.join(RESTORE_ORDER_PARENT_TO_CHILD)}"))
        db.commit()
        db.close()


@pytest.fixture()
def sample_avro_files(tmp_path):
    """Writes minimal one-row-per-table AVRO backups to a temp dir,
    mirroring services/backup.py's schemas exactly."""
    import fastavro

    dept_schema = {"type": "record", "name": "Department", "fields": [
        {"name": "id", "type": "int"}, {"name": "department", "type": "string"},
    ]}
    job_schema = {"type": "record", "name": "Job", "fields": [
        {"name": "id", "type": "int"}, {"name": "job", "type": "string"},
    ]}
    employee_schema = {"type": "record", "name": "HiredEmployee", "fields": [
        {"name": "id", "type": "int"}, {"name": "name", "type": "string"},
        {"name": "hire_datetime", "type": "string"},
        {"name": "department_id", "type": "int"}, {"name": "job_id", "type": "int"},
    ]}

    with open(tmp_path / "departments.avro", "wb") as f:
        fastavro.writer(f, dept_schema, [{"id": 1, "department": "Engineering"}])
    with open(tmp_path / "jobs.avro", "wb") as f:
        fastavro.writer(f, job_schema, [{"id": 1, "job": "Recruiter"}])
    with open(tmp_path / "hired_employees.avro", "wb") as f:
        fastavro.writer(f, employee_schema, [{
            "id": 1, "name": "Ana Torres", "hire_datetime": "2021-03-15T10:00:00Z",
            "department_id": 1, "job_id": 1,
        }])

    return str(tmp_path)


ROW_MAPS = {
    "departments": lambda r: Department(id=r["id"], department=r["department"]),
    "jobs": lambda r: Job(id=r["id"], job=r["job"]),
    "hired_employees": lambda r: HiredEmployee(
        id=r["id"], name=r["name"],
        hire_datetime=dt.strptime(r["hire_datetime"], "%Y-%m-%dT%H:%M:%SZ"),
        department_id=r["department_id"], job_id=r["job_id"],
    ),
}


class TestRestoreAllAgainstRealPostgres:
    """Regression coverage for the two Phase 8 incident findings —
    see docs/07-restore/restore.md."""

    def test_restore_all_succeeds_with_fk_dependent_data(self, pg_session, sample_avro_files):
        """
        Core regression test: without db.flush() after each table load
        (Finding 2), this raises psycopg2.errors.ForeignKeyViolation on
        the hired_employees insert, because SQLAlchemy does not
        guarantee departments/jobs rows are physically inserted before
        hired_employees rows are added to the same session.
        """
        result = restore_all(pg_session, ROW_MAPS, sample_avro_files)

        assert result["restored"] == [
            {"table": "departments", "restored_count": 1},
            {"table": "jobs", "restored_count": 1},
            {"table": "hired_employees", "restored_count": 1},
        ]
        assert pg_session.query(Department).count() == 1
        assert pg_session.query(Job).count() == 1
        assert pg_session.query(HiredEmployee).count() == 1

    def test_restore_all_truncates_previous_data_before_reload(self, pg_session, sample_avro_files):
        """Confirms restore is a full replace, not a merge — pre-existing
        rows not present in the backup must be gone afterward."""
        pg_session.add(Department(id=999, department="Should Be Wiped"))
        pg_session.commit()

        restore_all(pg_session, ROW_MAPS, sample_avro_files)

        assert pg_session.query(Department).filter_by(id=999).first() is None
        assert pg_session.query(Department).filter_by(id=1).first() is not None

    def test_single_table_restore_of_parent_blocked_by_fk_dependent(self, pg_session, sample_avro_files):
        """
        Regression test for Finding 1: TRUNCATE on 'departments' must
        fail with RestoreOrderError while 'hired_employees' has any FK
        constraint pointing at it — regardless of hired_employees'
        actual row count. First seed hired_employees via restore_all,
        then attempt an isolated single-table restore of departments.
        """
        restore_all(pg_session, ROW_MAPS, sample_avro_files)

        dept_avro = os.path.join(sample_avro_files, "departments.avro")
        with pytest.raises(RestoreOrderError, match="Postgres blocks this regardless"):
            restore_table(pg_session, "departments", dept_avro, ROW_MAPS["departments"])

    def test_single_table_restore_of_leaf_table_succeeds(self, pg_session, sample_avro_files):
        """hired_employees has no dependents, so isolated restore is safe."""
        restore_all(pg_session, ROW_MAPS, sample_avro_files)

        employees_avro = os.path.join(sample_avro_files, "hired_employees.avro")
        result = restore_table(pg_session, "hired_employees", employees_avro, ROW_MAPS["hired_employees"])

        assert result == {"table": "hired_employees", "restored_count": 1}