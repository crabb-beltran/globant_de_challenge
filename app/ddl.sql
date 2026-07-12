-- Reference DDL only — NOT executed directly against the database.
-- The authoritative schema source is app/models.py (SQLAlchemy 2.0 models).
-- Schema changes are applied exclusively through Alembic migrations
-- (app/alembic/versions/). This file documents the initial hand-written
-- design that preceded the ORM models, kept for traceability.


CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY NOT NULL,
    job VARCHAR(255)  NOT NULL
);

CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY NOT NULL,
    department VARCHAR(255)  NOT NULL
);

CREATE TABLE IF NOT EXISTS hired_employees (
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR(255)  NOT NULL,
    datetime TIMESTAMPTZ NOT NULL,
	department_id INTEGER NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
	job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS ix_hired_employees_datetime ON hired_employees (datetime);
CREATE INDEX IF NOT EXISTS ix_hired_employees_department_id ON hired_employees (department_id);
CREATE INDEX IF NOT EXISTS ix_hired_employees_job_id ON hired_employees (job_id);