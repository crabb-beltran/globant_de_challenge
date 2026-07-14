from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.reports import QuarterlyHiring, DepartmentAboveAverage, HiringDistributionStats

router = APIRouter(prefix="/reports", tags=["Reports"])

# NOTE: column is "datetime" at the DB level (models.py maps the Python
# attribute hire_datetime -> mapped_column("datetime", ...)). Raw SQL
# must reference the real column name.

QUARTERLY_HIRES_SQL = text("""
    SELECT d.department, j.job,
        COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.datetime) = 1) AS q1,
        COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.datetime) = 2) AS q2,
        COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.datetime) = 3) AS q3,
        COUNT(*) FILTER (WHERE EXTRACT(QUARTER FROM e.datetime) = 4) AS q4
    FROM hired_employees e
    JOIN departments d ON d.id = e.department_id
    JOIN jobs j ON j.id = e.job_id
    WHERE EXTRACT(YEAR FROM e.datetime) = 2021
    GROUP BY d.department, j.job
    ORDER BY d.department, j.job
""")

DEPARTMENTS_ABOVE_AVG_SQL = text("""
    WITH hires_per_department AS (
        SELECT d.id, d.department, COUNT(e.id) AS hired
        FROM departments d
        LEFT JOIN hired_employees e
            ON e.department_id = d.id AND EXTRACT(YEAR FROM e.datetime) = 2021
        GROUP BY d.id, d.department
    )
    SELECT id, department, hired
    FROM hires_per_department
    WHERE hired > (SELECT AVG(hired) FROM hires_per_department)
    ORDER BY hired DESC
""")

# Bonus stat endpoint: detects whether "average" is a distorted threshold
# (skew) before departments_above_average is used for business decisions.
HIRING_DISTRIBUTION_STATS_SQL = text("""
    WITH hires_per_department AS (
        SELECT d.id, d.department, COUNT(e.id) AS hired
        FROM departments d
        LEFT JOIN hired_employees e
            ON e.department_id = d.id AND EXTRACT(YEAR FROM e.datetime) = 2021
        GROUP BY d.id, d.department
    )
    SELECT
        AVG(hired) AS mean_hired,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY hired) AS median_hired,
        STDDEV_SAMP(hired) AS stdev_hired,
        CASE WHEN AVG(hired) = 0 THEN NULL
             ELSE STDDEV_SAMP(hired) / AVG(hired) END AS coefficient_of_variation
    FROM hires_per_department
""")

Z_SCORE_SQL = text("""
    WITH hires_per_department AS (
        SELECT d.id, d.department, COUNT(e.id) AS hired
        FROM departments d
        LEFT JOIN hired_employees e
            ON e.department_id = d.id AND EXTRACT(YEAR FROM e.datetime) = 2021
        GROUP BY d.id, d.department
    )
    SELECT id, department, hired,
        CASE WHEN STDDEV_SAMP(hired) OVER () = 0 THEN NULL
             ELSE (hired - AVG(hired) OVER ()) / STDDEV_SAMP(hired) OVER ()
        END AS z_score
    FROM hires_per_department
    ORDER BY z_score DESC NULLS LAST
""")


@router.get("/hiring-by-quarter", response_model=list[QuarterlyHiring])
def hiring_by_quarter(db: Session = Depends(get_db)):
    return [dict(row) for row in db.execute(QUARTERLY_HIRES_SQL).mappings().all()]


@router.get("/departments-above-average", response_model=list[DepartmentAboveAverage])
def departments_above_average(db: Session = Depends(get_db)):
    return [dict(row) for row in db.execute(DEPARTMENTS_ABOVE_AVG_SQL).mappings().all()]


@router.get("/hiring-distribution-stats", response_model=HiringDistributionStats)
def hiring_distribution_stats(db: Session = Depends(get_db)):
    summary = dict(db.execute(HIRING_DISTRIBUTION_STATS_SQL).mappings().one())
    departments = [dict(row) for row in db.execute(Z_SCORE_SQL).mappings().all()]
    return {"summary": summary, "departments": departments}