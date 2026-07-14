# SQL Reports

## Scope

Implements Challenge 2 (Data Analysis) as two required read-only
endpoints, plus one bonus endpoint agreed during Phase 6 design
discussions to surface whether the "above average" threshold is a
reliable signal or distorted by outliers.

All three endpoints reuse the SQL logic originally drafted during Phase
6 exploration and held out of that PR pending a dedicated `feature/sql-reports`
branch, per the WBS scope realignment documented in Phase 6.

## Design Decisions

**Raw SQL via `SQLAlchemy Core` (`text()`), not the ORM query builder.**
The quarterly pivot uses Postgres's `FILTER (WHERE ...)` clause, which
has no clean equivalent in SQLAlchemy's Python expression language
without reconstructing the same logic manually via multiple `CASE WHEN`
expressions. Raw SQL is more readable and directly reviewable as SQL —
relevant given the challenge explicitly evaluates "SQL proficiency
(joins, aggregations, filtering)."

**No materialized views.** The dataset is static post-migration (no
incremental loading in this challenge), so a view would add a schema
object to maintain without solving any real performance problem at this
data volume (~1929 rows). Would be over-engineering per
`risk-register.md` R-016.

**`LEFT JOIN`, not `INNER JOIN`, in `departments-above-average` and
`hiring-distribution-stats`.** A department with zero 2021 hires must
still be included in the average calculation (`hired = 0`), not
silently excluded. Excluding it would inflate the average and change
which departments qualify as "above average" — this is covered by a
dedicated regression test
(`test_zero_hire_department_counted_in_average_via_left_join`).

**Postgres-specific SQL, not dialect-portable.** `FILTER (WHERE ...)`,
`PERCENTILE_CONT`, and window functions with `OVER()` are Postgres
syntax without a direct equivalent in, e.g., MySQL. Accepted trade-off
given ADR-001 already committed to PostgreSQL as the project's database.

## Endpoints

### `GET /reports/hiring-by-quarter`

Required by Challenge 2, Question 1: employees hired per job and
department, aggregated by quarter, for 2021 only, ordered alphabetically
by department then job.

**Response**: `200 OK`, array of:
```json
{"department": "Accounting", "job": "Actuary", "q1": 0, "q2": 1, "q3": 0, "q4": 0}
```

Uses `INNER JOIN` (not `LEFT JOIN`) — a department/job combination with
zero hires in 2021 does not produce a meaningful "quarterly breakdown"
row and is correctly absent from this report (unlike
`departments-above-average`, where zero-hire departments must appear
for the average calculation to be correct — see Design Decisions above).

### `GET /reports/departments-above-average`

Required by Challenge 2, Question 2: departments that hired more
employees than the average across all departments in 2021, ordered by
`hired DESC`.

**Response**: `200 OK`, array of:
```json
{"id": 8, "department": "Support", "hired": 216}
```

### `GET /reports/hiring-distribution-stats` (bonus)

Not required by the challenge. Added per the Phase 6 discussion on
applying statistical fundamentals to infrastructure decisions: the
"average" threshold used by `departments-above-average` is only a
reliable signal if the underlying distribution isn't dominated by one
or two outlier departments. This endpoint surfaces that check without
altering the graded endpoint's contract.

**Response**: `200 OK`
```json
{
  "summary": {
    "mean_hired": 136.92,
    "median_hired": 145.0,
    "stdev_hired": 66.25,
    "coefficient_of_variation": 0.48
  },
  "departments": [
    {"id": 8, "department": "Support", "hired": 216, "z_score": 1.19}
  ]
}
```

- `mean` vs `median`: a large gap signals skew (few departments
  dominating hiring volume).
- `coefficient_of_variation` (`stdev / mean`): normalizes dispersion
  relative to scale; informally, values above ~0.3–0.5 suggest high
  relative variability, though there's no universal threshold.
- `z_score` per department: `|z| > 2` is a common (not rigorous)
  heuristic for flagging an individual outlier. With only 12
  departments, z-scores are noisy — IQR-based outlier detection would
  be more robust to small-sample skew, but was not implemented here to
  avoid adding complexity beyond what the bonus endpoint's purpose
  requires.

**Finding on the actual project dataset** (12 departments, 1929
employees, 2021 only): mean=136.92, median=145.0, CV=0.48. The highest-
hiring department (`Support`, 216 hires) has `z_score ≈ 1.19` — below
the `|z| > 2` heuristic threshold. Conclusion: no single department
dominates the distribution; the "above average" criterion used by
`departments-above-average` is not being distorted by an extreme
outlier in this dataset.

## Testing

Covered by `tests/test_reports_integration.py` (9 tests, integration-only
— see below for why). Uses a small, hand-verified synthetic dataset (3
departments, 1 job, 5 employees with known hire dates) rather than the
project's real data, so expected values are exact and independent of
whatever the current dev database happens to contain.

**Why integration-only, no SQLite unit tests**: `FILTER (WHERE ...)`,
`PERCENTILE_CONT`, `STDDEV_SAMP`, and `OVER()` window functions are
Postgres-specific syntax with no SQLite equivalent — a SQLite-based test
would fail on syntax before validating any actual query logic. Same
convention as `test_restore_integration.py` (Phase 8): skipped by
default, opt-in via `RUN_INTEGRATION_TESTS=1`.

```bash
docker-compose exec api bash
RUN_INTEGRATION_TESTS=1 python -m pytest /tests/test_reports_integration.py -v
```

**Known gotcha, documented for future reference**: Postgres's `AVG()`
and `STDDEV_SAMP()` over `integer`/`bigint` columns return `NUMERIC`,
deserialized by SQLAlchemy as Python `Decimal` — not `float`. This
caused an initial test failure (`TypeError: unsupported operand type(s)
for -: 'float' and 'decimal.Decimal'`) when comparing against
`pytest.approx()`, which doesn't support mixed `float`/`Decimal`
arithmetic. Fixed by casting to `float()` before comparison in the test.
This does **not** affect the actual API response: Pydantic's
`response_model` (`schemas/reports.py`, declaring `mean_hired: float`)
already converts `Decimal → float` automatically during HTTP
serialization — confirmed via the raw JSON values returned in manual
Swagger testing.

## Related Documentation

- `docs/00-project/decisions.md` — ADR-001 (PostgreSQL selection, basis
  for accepting Postgres-specific SQL here)
- `docs/06-backup/backup.md`, `docs/07-restore/restore.md` — the dataset
  these reports query was verified clean (12 departments, 183 jobs, 1929
  hired_employees) after removing test data accumulated during Phases 6–8