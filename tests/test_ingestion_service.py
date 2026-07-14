"""
Unit tests for services/ingestion.py (Fase 6 - REST API).

Covers the core contract: partial success (207 semantics), structured
reason_code per rejection type, and per-record isolation (one bad row
does not roll back valid rows in the same batch).
"""

from datetime import datetime as dt

from models import Department, Job, HiredEmployee
from schemas.department import Departments
from schemas.job import Jobs
from schemas.hired_employee import HiredEmployeeSchema
from validators.business_rules import department_exists, job_exists
from services.ingestion import ingest_batch


def _employee_field_map(record: HiredEmployeeSchema) -> dict:
    return {
        "id": record.id,
        "name": record.name,
        "hire_datetime": dt.strptime(record.hire_datetime, "%Y-%m-%dT%H:%M:%SZ"),
        "department_id": record.department_id,
        "job_id": record.job_id,
    }


def _department_field_map(record: Departments) -> dict:
    return {"id": record.id, "department": record.department}


class TestDepartmentsIngestion:
    """No FK dependencies — simplest case, validates the base contract."""

    def test_clean_batch_inserts_all(self, db_session):
        records = [Departments(id=1, department="Sales"), Departments(id=2, department="Marketing")]

        result = ingest_batch(
            db=db_session, records=records, model_cls=Department, id_field="id",
            field_map=_department_field_map, existing_ids=set(), validators=None,
        )

        assert result == {"inserted": 2, "rejected": 0, "rejected_records": []}
        assert db_session.query(Department).count() == 2

    def test_duplicate_against_existing_db_row_is_rejected(self, db_session, seed_department):
        records = [Departments(id=1, department="Engineering (dup attempt)")]

        result = ingest_batch(
            db=db_session, records=records, model_cls=Department, id_field="id",
            field_map=_department_field_map, existing_ids={1}, validators=None,
        )

        assert result["inserted"] == 0
        assert result["rejected"] == 1
        assert result["rejected_records"][0]["reason_code"] == "DUPLICATE_ID"
        # original row must remain untouched — no upsert semantics
        assert db_session.query(Department).filter_by(id=1).one().department == "Engineering"

    def test_duplicate_within_same_batch_only_first_inserted(self, db_session):
        records = [Departments(id=5, department="Finance"), Departments(id=5, department="Finance (dup)")]

        result = ingest_batch(
            db=db_session, records=records, model_cls=Department, id_field="id",
            field_map=_department_field_map, existing_ids=set(), validators=None,
        )

        assert result["inserted"] == 1
        assert result["rejected"] == 1
        assert result["rejected_records"][0]["reason_code"] == "DUPLICATE_ID"

    def test_partial_batch_isolates_failure_207_semantics(self, db_session, seed_department):
        """Core contract of Fase 6: one invalid record must not block valid ones."""
        records = [
            Departments(id=1, department="dup, should reject"),  # duplicate vs seed_department
            Departments(id=2, department="Legal"),               # valid
            Departments(id=3, department="IT"),                  # valid
        ]

        result = ingest_batch(
            db=db_session, records=records, model_cls=Department, id_field="id",
            field_map=_department_field_map, existing_ids={1}, validators=None,
        )

        assert result["inserted"] == 2
        assert result["rejected"] == 1
        assert db_session.query(Department).count() == 3  # 1 seeded + 2 new
        assert {r["reason_code"] for r in result["rejected_records"]} == {"DUPLICATE_ID"}


class TestEmployeesIngestion:
    """Exercises FK validation — the only ingestion path with validators."""

    def _validator_pair(self, valid_department_ids, valid_job_ids):
        def _validate(record: HiredEmployeeSchema) -> None:
            department_exists(record.department_id, valid_department_ids)
            job_exists(record.job_id, valid_job_ids)
        return [_validate]

    def test_valid_employee_with_existing_fks_inserts(self, db_session, seed_department, seed_job):
        record = HiredEmployeeSchema(
            id=100, name="Ana Torres", hire_datetime="2021-03-15T10:00:00Z",
            department_id=1, job_id=1,
        )

        result = ingest_batch(
            db=db_session, records=[record], model_cls=HiredEmployee, id_field="id",
            field_map=_employee_field_map, existing_ids=set(),
            validators=self._validator_pair({1}, {1}),
        )

        assert result == {"inserted": 1, "rejected": 0, "rejected_records": []}

    def test_nonexistent_department_fk_rejected_with_correct_code(self, db_session, seed_job):
        record = HiredEmployeeSchema(
            id=101, name="Carlos Ruiz", hire_datetime="2021-03-15T10:00:00Z",
            department_id=999, job_id=1,  # department 999 does not exist
        )

        result = ingest_batch(
            db=db_session, records=[record], model_cls=HiredEmployee, id_field="id",
            field_map=_employee_field_map, existing_ids=set(),
            validators=self._validator_pair(set(), {1}),  # empty valid_department_ids
        )

        assert result["inserted"] == 0
        assert result["rejected"] == 1
        assert result["rejected_records"][0]["reason_code"] == "FK_VIOLATION"
        assert "department_id 999" in result["rejected_records"][0]["reason"]

    def test_nonexistent_job_fk_rejected_with_correct_code(self, db_session, seed_department):
        record = HiredEmployeeSchema(
            id=102, name="Diana Perez", hire_datetime="2021-03-15T10:00:00Z",
            department_id=1, job_id=999,
        )

        result = ingest_batch(
            db=db_session, records=[record], model_cls=HiredEmployee, id_field="id",
            field_map=_employee_field_map, existing_ids=set(),
            validators=self._validator_pair({1}, set()),
        )

        assert result["rejected_records"][0]["reason_code"] == "FK_VIOLATION"
        assert "job_id 999" in result["rejected_records"][0]["reason"]

    def test_mixed_batch_valid_and_fk_violation_isolated(self, db_session, seed_department, seed_job):
        """Two employees in one request: one clean, one with a bad department_id.
        The bad one must not roll back the clean insert (SAVEPOINT isolation)."""
        records = [
            HiredEmployeeSchema(id=200, name="Valid Employee", hire_datetime="2021-01-10T08:00:00Z",
                                 department_id=1, job_id=1),
            HiredEmployeeSchema(id=201, name="Bad FK Employee", hire_datetime="2021-01-11T08:00:00Z",
                                 department_id=999, job_id=1),
        ]

        result = ingest_batch(
            db=db_session, records=records, model_cls=HiredEmployee, id_field="id",
            field_map=_employee_field_map, existing_ids=set(),
            validators=self._validator_pair({1}, {1}),
        )

        assert result["inserted"] == 1
        assert result["rejected"] == 1
        assert db_session.query(HiredEmployee).filter_by(id=200).count() == 1
        assert db_session.query(HiredEmployee).filter_by(id=201).count() == 0