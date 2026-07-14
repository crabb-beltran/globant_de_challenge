"""
Integration tests for routers/reports.py's SQL queries — require a real
Postgres connection, NOT the SQLite fixture used by the rest of the unit
suite. SQLite cannot run this module's queries at all: FILTER (WHERE ...),
PERCENTILE_CONT, STDDEV_SAMP, and window functions (OVER()) are Postgres-
specific syntax with no SQLite equivalent — a SQLite-based test would fail
on syntax before testing any actual logic.

Uses a dedicated test database (globant_test), isolated from the
development database used by db/session.py's SessionLocal — see
integration_conftest.py. This isolation exists specifically because an
earlier version of these integration tests connected to the development
database directly and truncated it via cleanup logic, wiping real data
(see docs/00-project/changelog.md, Phase 9 entry).

Seeds a small, hand-verifiable synthetic dataset inside each test rather
than depending on the project's real 1929-row dataset, so assertions
stay exact and independent of whatever real data currently exists.

Run with:
    docker-compose exec api bash
    RUN_INTEGRATION_TESTS=1 python -m pytest /tests/test_reports_integration.py -v
"""

import os
import pytest
from datetime import datetime as dt

from integration_conftest import pg_test_session as pg_session
from models import Department, Job, HiredEmployee
from routers.reports import (
    QUARTERLY_HIRES_SQL, DEPARTMENTS_ABOVE_AVG_SQL, HIRING_DISTRIBUTION_STATS_SQL, Z_SCORE_SQL,
)

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason="requires a live Postgres connection; set RUN_INTEGRATION_TESTS=1 to run",
)


@pytest.fixture()
def seeded_dataset(pg_session):
    """
    Hand-verifiable dataset: 3 departments, 1 job, employees hired in
    2021 (varying quarters) plus one intentionally outside 2021 to
    confirm the year filter works.

    Hiring counts by department (2021 only):
      Engineering (id=1): 3 hires (Q1, Q1, Q3)
      Sales (id=2):       1 hire  (Q2)
      Legal (id=3):       0 hires (LEFT JOIN must still include it)

    Expected: mean = (3+1+0)/3 = 1.333..., only Engineering (3) is
    above that average.
    """
    pg_session.add_all([
        Department(id=1, department="Engineering"),
        Department(id=2, department="Sales"),
        Department(id=3, department="Legal"),
        Job(id=1, job="Analyst"),
    ])
    pg_session.flush()

    pg_session.add_all([
        HiredEmployee(id=1, name="A", hire_datetime=dt(2021, 1, 15), department_id=1, job_id=1),
        HiredEmployee(id=2, name="B", hire_datetime=dt(2021, 2, 10), department_id=1, job_id=1),
        HiredEmployee(id=3, name="C", hire_datetime=dt(2021, 8, 1), department_id=1, job_id=1),
        HiredEmployee(id=4, name="D", hire_datetime=dt(2021, 5, 5), department_id=2, job_id=1),
        # outside 2021 — must be excluded by every report query
        HiredEmployee(id=5, name="E", hire_datetime=dt(2020, 12, 31), department_id=1, job_id=1),
    ])
    pg_session.commit()
    return pg_session


class TestHiringByQuarter:
    def test_counts_match_expected_quarters(self, seeded_dataset):
        rows = seeded_dataset.execute(QUARTERLY_HIRES_SQL).mappings().all()
        by_dept_job = {(r["department"], r["job"]): r for r in rows}

        eng = by_dept_job[("Engineering", "Analyst")]
        assert (eng["q1"], eng["q2"], eng["q3"], eng["q4"]) == (2, 0, 1, 0)

        sales = by_dept_job[("Sales", "Analyst")]
        assert (sales["q1"], sales["q2"], sales["q3"], sales["q4"]) == (0, 1, 0, 0)

    def test_department_with_zero_2021_hires_absent(self, seeded_dataset):
        rows = seeded_dataset.execute(QUARTERLY_HIRES_SQL).mappings().all()
        departments_present = {r["department"] for r in rows}
        assert "Legal" not in departments_present

    def test_pre_2021_hire_excluded(self, seeded_dataset):
        rows = seeded_dataset.execute(QUARTERLY_HIRES_SQL).mappings().all()
        total_hires = sum(r["q1"] + r["q2"] + r["q3"] + r["q4"] for r in rows)
        assert total_hires == 4  # 5 seeded, 1 is from 2020 and must be excluded


class TestDepartmentsAboveAverage:
    def test_only_engineering_above_average(self, seeded_dataset):
        rows = seeded_dataset.execute(DEPARTMENTS_ABOVE_AVG_SQL).mappings().all()
        assert len(rows) == 1
        assert rows[0]["department"] == "Engineering"
        assert rows[0]["hired"] == 3

    def test_zero_hire_department_counted_in_average_via_left_join(self, seeded_dataset):
        rows = seeded_dataset.execute(DEPARTMENTS_ABOVE_AVG_SQL).mappings().all()
        assert len(rows) == 1  # confirms the correct (LEFT JOIN) average was used

    def test_ordered_by_hired_desc(self, seeded_dataset):
        rows = seeded_dataset.execute(DEPARTMENTS_ABOVE_AVG_SQL).mappings().all()
        hired_values = [r["hired"] for r in rows]
        assert hired_values == sorted(hired_values, reverse=True)


class TestHiringDistributionStats:
    def test_summary_stats_computed(self, seeded_dataset):
        result = seeded_dataset.execute(HIRING_DISTRIBUTION_STATS_SQL).mappings().one()
        # Postgres AVG()/PERCENTILE_CONT() on integer columns return
        # NUMERIC, deserialized as Decimal — cast to float before
        # comparing with pytest.approx, which doesn't support
        # float-Decimal subtraction.
        assert float(result["mean_hired"]) == pytest.approx(4 / 3, rel=1e-6)
        assert float(result["median_hired"]) == pytest.approx(1.0)
        assert result["stdev_hired"] is not None

    def test_z_scores_include_zero_hire_department(self, seeded_dataset):
        rows = seeded_dataset.execute(Z_SCORE_SQL).mappings().all()
        departments = {r["department"] for r in rows}
        assert departments == {"Engineering", "Sales", "Legal"}

    def test_highest_hiring_department_has_highest_z_score(self, seeded_dataset):
        rows = seeded_dataset.execute(Z_SCORE_SQL).mappings().all()
        assert rows[0]["department"] == "Engineering"  # ORDER BY z_score DESC