"""
Regression tests for Layer 1 (Pydantic field-level) validation — Phase 7
gap audit fixes (see docs/05-validation/validation.md, ADR-011).

Covers only what changed in this phase: positive-integer ID enforcement,
whitespace-only string rejection, and extra-field rejection. Does NOT
duplicate Phase 5 tests for required-field/null checks or ISO datetime
format, which were already correct and unchanged.
"""

import pytest
from pydantic import ValidationError

from schemas.department import Departments
from schemas.job import Jobs
from schemas.hired_employee import HiredEmployeeSchema


VALID_EMPLOYEE_KWARGS = dict(
    id=1, name="Ana Torres", hire_datetime="2021-03-15T10:00:00Z",
    department_id=1, job_id=1,
)


class TestPositiveIdEnforcement:
    """Gap #1: id <= 0 was previously accepted and inserted."""

    @pytest.mark.parametrize("bad_id", [-1, 0])
    def test_department_rejects_non_positive_id(self, bad_id):
        with pytest.raises(ValidationError, match="positive integer"):
            Departments(id=bad_id, department="Engineering")

    @pytest.mark.parametrize("bad_id", [-1, 0])
    def test_job_rejects_non_positive_id(self, bad_id):
        with pytest.raises(ValidationError, match="positive integer"):
            Jobs(id=bad_id, job="Recruiter")

    @pytest.mark.parametrize("bad_id", [-1, 0])
    def test_employee_rejects_non_positive_id(self, bad_id):
        kwargs = {**VALID_EMPLOYEE_KWARGS, "id": bad_id}
        with pytest.raises(ValidationError, match="positive integer"):
            HiredEmployeeSchema(**kwargs)

    def test_employee_rejects_non_positive_department_id(self):
        kwargs = {**VALID_EMPLOYEE_KWARGS, "department_id": 0}
        with pytest.raises(ValidationError, match="positive integer"):
            HiredEmployeeSchema(**kwargs)

    def test_employee_rejects_non_positive_job_id(self):
        kwargs = {**VALID_EMPLOYEE_KWARGS, "job_id": -5}
        with pytest.raises(ValidationError, match="positive integer"):
            HiredEmployeeSchema(**kwargs)

    def test_positive_id_still_accepted(self):
        # regression guard: the fix must not reject valid positive IDs
        assert Departments(id=1, department="Engineering").id == 1


class TestWhitespaceOnlyStringRejection:
    """Gap #2: "   " passed the old `value == ""` check."""

    def test_department_rejects_whitespace_only_name(self):
        with pytest.raises(ValidationError, match="whitespace-only"):
            Departments(id=1, department="   ")

    def test_job_rejects_whitespace_only_name(self):
        with pytest.raises(ValidationError, match="whitespace-only"):
            Jobs(id=1, job="\t\t")

    def test_employee_rejects_whitespace_only_name(self):
        kwargs = {**VALID_EMPLOYEE_KWARGS, "name": "   "}
        with pytest.raises(ValidationError, match="whitespace-only"):
            HiredEmployeeSchema(**kwargs)

    def test_non_whitespace_name_still_accepted(self):
        # regression guard: legitimate names with internal spaces must pass
        assert Departments(id=1, department="Human Resources").department == "Human Resources"


class TestExtraFieldRejection:
    """Gap #4: unexpected fields were silently ignored before extra="forbid"."""

    def test_department_rejects_unexpected_field(self):
        with pytest.raises(ValidationError, match="[Ee]xtra"):
            Departments(id=1, department="Sales", unexpected_field="x")

    def test_job_rejects_unexpected_field(self):
        with pytest.raises(ValidationError, match="[Ee]xtra"):
            Jobs(id=1, job="Analyst", unexpected_field="x")

    def test_employee_rejects_unexpected_field(self):
        kwargs = {**VALID_EMPLOYEE_KWARGS, "unexpected_field": "x"}
        with pytest.raises(ValidationError, match="[Ee]xtra"):
            HiredEmployeeSchema(**kwargs)

    def test_exact_expected_fields_still_accepted(self):
        # regression guard: legitimate payloads with only expected fields must pass
        employee = HiredEmployeeSchema(**VALID_EMPLOYEE_KWARGS)
        assert employee.id == 1


class TestConfirmedNonIssues:
    """
    Gaps #3 and #5 were audited and confirmed as correct existing behavior
    (no code change). These tests lock in that behavior so a future change
    doesn't silently alter it without being noticed.
    """

    def test_iso_offset_format_still_rejected(self):
        # confirms Z-only enforcement remains in place
        kwargs = {**VALID_EMPLOYEE_KWARGS, "hire_datetime": "2021-03-15T10:00:00+00:00"}
        with pytest.raises(ValidationError, match="UTC 'Z' suffix"):
            HiredEmployeeSchema(**kwargs)

    def test_numeric_string_id_still_coerced(self):
        # confirms "603" -> 603 coercion remains accepted, per ADR/validation.md
        assert Departments(id="603", department="Finance").id == 603