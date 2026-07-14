"""
Integration tests for services/restore.py — require a real Postgres
connection, NOT the SQLite fixture used by test_ingestion_service.py /
test_schemas.py. SQLite cannot validate this module: it has no TRUNCATE
statement and does not enforce FK constraints by default, so the two
Postgres-specific bugs this phase uncovered (multi-table TRUNCATE
requirement, cross-table INSERT ordering without flush()) would not
reproduce there at all.

Uses a dedicated test database (globant_test), isolated from the
development database used by db/session.py's SessionLocal — see
integration_conftest.py. This isolation exists specifically because an
earlier version of this file's fixture connected to the development
database directly and truncated it via cleanup logic, wiping real data
(see docs/00-project/changelog.md, Phase 9 entry).

Skipped automatically unless RUN_INTEGRATION_TESTS=1 is set. Run with:

    docker-compose exec api bash
    RUN_INTEGRATION_TESTS=1 python -m pytest /tests/test_restore_integration.py -v
"""

import os
import pytest
from datetime import datetime as dt

from integration_conftest import pg_test_session as pg_session
from models import Department, Job, HiredEmployee
from services.restore import restore_all, restore_table, RestoreOrderError, RESTORE_ORDER_PARENT_TO_CHILD

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="requires a live Postgres connection; set RUN_INTEGRATION_TESTS=1 to run",
)


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
    def test_restore_all_succeeds_with_fk_dependent_data(self, pg_session, sample_avro_files):
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
        pg_session.add(Department(id=999, department="Should Be Wiped"))
        pg_session.commit()

        restore_all(pg_session, ROW_MAPS, sample_avro_files)

        assert pg_session.query(Department).filter_by(id=999).first() is None
        assert pg_session.query(Department).filter_by(id=1).first() is not None

    def test_single_table_restore_of_parent_blocked_by_fk_dependent(self, pg_session, sample_avro_files):
        restore_all(pg_session, ROW_MAPS, sample_avro_files)

        dept_avro = os.path.join(sample_avro_files, "departments.avro")
        with pytest.raises(RestoreOrderError, match="Postgres blocks this regardless"):
            restore_table(pg_session, "departments", dept_avro, ROW_MAPS["departments"])

    def test_single_table_restore_of_leaf_table_succeeds(self, pg_session, sample_avro_files):
        restore_all(pg_session, ROW_MAPS, sample_avro_files)

        employees_avro = os.path.join(sample_avro_files, "hired_employees.avro")
        result = restore_table(pg_session, "hired_employees", employees_avro, ROW_MAPS["hired_employees"])

        assert result == {"table": "hired_employees", "restored_count": 1}