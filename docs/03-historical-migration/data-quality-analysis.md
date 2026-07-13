# Historical Dataset — Data Quality Analysis

**Sources:** `hired_employees.csv` (1999 rows), `departments.csv` (12 rows), `jobs.csv` (183 rows) — none with header row.

## Method

Diagnosed using `awk`/`grep` field-position checks against the data
dictionary (Challenge PDF, Section "Data Model") before designing any
validation schema — verifying actual data shape rather than assuming it.
Findings were cross-validated against the real ingestion pipeline output
(`loaders/historical.py`), which revealed a gap in the initial shell-based
diagnosis (see "Diagnostic Methodology Correction" below).

## File Naming Note

`hired_employees.csv` was received as `hired_employees (1).csv` (space and
parenthetical suffix from the source email attachment). Renamed for
consistency with the data dictionary; no content was modified.

## Row Count Note

`jobs.csv` initially appeared to have 182 rows via `wc -l`. The file's last
line (`183,Administrative Assistant IV`) is not terminated with a trailing
newline, so `wc -l` undercounted by one. Confirmed via `xxd` byte inspection
of the file tail — actual row count is 183, matching the loader's insert
count.

## Diagnostic Commands Used

```bash
# Row counts
wc -l datasets/*.csv

# Structural integrity — expected 5 fields per row
awk -F',' 'NF != 5' datasets/hired_employees.csv | wc -l

# department_id empty
awk -F',' '$4 == ""' datasets/hired_employees.csv | wc -l

# job_id empty (see methodology correction below — this undercounted)
awk -F',' '$5 == ""' datasets/hired_employees.csv | wc -l

# name empty
awk -F',' '$2 == ""' datasets/hired_employees.csv | wc -l

# datetime not matching strict ISO 8601 with UTC 'Z' suffix
awk -F',' '$3 !~ /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$/' datasets/hired_employees.csv | wc -l

# Duplicate id
awk -F',' '{print $1}' datasets/hired_employees.csv | sort | uniq -d

# Records outside year 2021 (informational — not a rejection rule)
awk -F',' '$3 !~ /^2021-/' datasets/hired_employees.csv | wc -l

# department_id referencing a non-existent department
awk -F',' '$4 != "" {print $4}' datasets/hired_employees.csv | sort -un > /tmp/dept_ids_used.txt
awk -F',' '{print $1}' datasets/departments.csv | sort -un > /tmp/dept_ids_valid.txt
comm -23 /tmp/dept_ids_used.txt /tmp/dept_ids_valid.txt
```

## Findings (Corrected)

| Rule | Command | Result |
|---|---|---|
| Structural integrity (5 fields per row) | `awk -F',' 'NF != 5'` | 0 rows |
| `name` empty | `awk -F',' '$2 == ""'` | 19 rows (0.95%) |
| `department_id` empty | `awk -F',' '$4 == ""'` | 21 rows (1.05%) |
| `job_id` empty | production pipeline (`loaders/historical.py`) | **16 rows (0.80%)** — see methodology correction |
| `hire_datetime` not ISO 8601 | `awk` regex match on `$3` | 14 rows (0.70%) |
| Duplicate `id` | `awk -F',' '{print $1}' \| sort \| uniq -d` | 0 |
| `department_id` referencing non-existent department | `comm -23` against `departments.csv` IDs | 0 |
| Records outside year 2021 (informational, not rejected) | `awk -F',' '$3 !~ /^2021-/'` | 314 rows (15.71%) |

## Summary

- Total records: 1999
- Total invalid records: **70 (3.50%)**
- No overlap: each invalid record fails exactly one rule (19 + 21 + 16 + 14 = 70, confirmed against production pipeline output)
- Records outside year 2021 (informational, not rejected): 314 (15.71%)

## Diagnostic Methodology Correction

The initial shell-based check for empty `job_id` (`awk -F',' '$5 == ""'`)
returned **0 rows** — but the production ingestion pipeline
(`loaders/historical.py`, using Python's `csv.reader`) rejected **16 rows**
for exactly this reason.

**Root cause:** the source CSV uses CRLF (`\r\n`) line terminators. `awk`'s
exact string comparison (`$5 == ""`) does not match a field that actually
contains a trailing `\r` character — the field is not empty by strict
string equality, even though it is visually and semantically empty.
Python's `csv.reader`, by contrast, correctly normalizes line terminators
regardless of style, so it evaluates the same field as a true empty string.

Confirmed via:
```bash
file datasets/hired_employees.csv
grep -c $'\r' datasets/hired_employees.csv
```

**Conclusion:** the production validation pipeline is correct; the initial
shell diagnostic undercounted due to a CRLF blind spot in exact string
comparison. This finding is documented as R-024 in `risk-register.md` and
does not indicate any defect in `schemas/hired_employee.py` or
`loaders/historical.py` — both handled the data correctly from the start.