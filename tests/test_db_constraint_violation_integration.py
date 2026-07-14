"""
Integration test for the DB_CONSTRAINT_VIOLATION path in
services/ingestion.py — deferred since Phase 6 because it requires a
real IntegrityError that neither Pydantic (Layer 1) nor the in-memory
FK/duplicate checks (Layer 2) can catch on their own.

Uses a dedicated test database (globant_test) — see integration_conftest.py.
"""

import os
import pytest

from integration_conftest import pg_test_session as pg_session
from models import Department, Job, HiredEmployee
from schemas.hired_employee import HiredEmployeeSchema
from services.ingestion import ingest_batch
from datetime import datetime as dt

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="requires a live Postgres connection; set RUN_INTEGRATION_TESTS=1 to run",
)


def _employee_field_map(record: HiredEmployeeSchema) -> dict:
    return {
        "id": record.id, "name": record.name,
        "hire_datetime": dt.strptime(record.hire_datetime, "%Y-%m-%dT%H:%M:%SZ"),
        "department_id": record.department_id, "job_id": record.job_id,
    }


class TestDbConstraintViolation:
    def test_race_condition_produces_db_constraint_violation(self, pg_session):
        """
        Simulates a race: existing_ids is computed once, BEFORE a
        concurrent insert lands on the same id. ingest_batch's in-memory
        duplicate check passes (id not in the stale existing_ids set),
        but the real INSERT fails at the database constraint level —
        exactly the scenario DB_CONSTRAINT_VIOLATION exists to catch.
        """
        pg_session.add_all([
            Department(id=1, department="Engineering"),
            Job(id=1, job="Analyst"),
        ])
        pg_session.commit()

        # existing_ids computed BEFORE the "concurrent" insert below —
        # simulates a stale read in a race condition
        existing_ids = {row.id for row in pg_session.query(HiredEmployee.id).all()}
        assert 500 not in existing_ids

        # a "concurrent" process inserts id=500 after the stale read
        pg_session.add(HiredEmployee(
            id=500, name="Concurrent Insert", hire_datetime=dt(2021, 1, 1),
            department_id=1, job_id=1,
        ))
        pg_session.commit()

        record = HiredEmployeeSchema(
            id=500, name="Race Loser", hire_datetime="2021-01-02T00:00:00Z",
            department_id=1, job_id=1,
        )

        result = ingest_batch(
            db=pg_session, records=[record], model_cls=HiredEmployee, id_field="id",
            field_map=_employee_field_map, existing_ids=existing_ids, validators=None,
        )

        assert result["inserted"] == 0
        assert result["rejected"] == 1
        assert result["rejected_records"][0]["reason_code"] == "DB_CONSTRAINT_VIOLATION"

        # confirm the original concurrent row is untouched, no data corruption
        assert pg_session.query(HiredEmployee).filter_by(id=500).one().name == "Concurrent Insert"