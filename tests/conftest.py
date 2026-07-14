"""
Shared pytest fixtures for unit tests.

sys.path manipulation is required because the project's modules use
absolute imports assuming WORKDIR /app (e.g. `from db.base import Base`,
not `from app.db.base import Base`) — matching the Docker container's
runtime layout. Tests live outside app/ (sibling directory), so we insert
app/ onto sys.path here rather than changing production import style.
"""

import os
import sys

APP_DIR = os.path.join(os.path.dirname(__file__), "..", "app")
sys.path.insert(0, os.path.abspath(APP_DIR))

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from db.base import Base
from models import (
    Department,
    Job,
    HiredEmployee,
)  # noqa: F401 — registers models on Base.metadata


@pytest.fixture()
def db_session():
    """
    In-memory SQLite session with SAVEPOINT support enabled.

    Known pysqlite quirk: by default, SQLite's DBAPI driver implicitly
    manages transactions in a way that breaks SQLAlchemy's begin_nested()
    (SAVEPOINT). The two event listeners below are SQLAlchemy's documented
    workaround: disable pysqlite's own transaction handling and issue
    BEGIN explicitly, so nested transactions (SAVEPOINTs) behave correctly
    — this is required for ingest_batch's per-record isolation to be
    testable at all under SQLite.
    """
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def _do_connect(dbapi_connection, connection_record):
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def _do_begin(conn):
        conn.exec_driver_sql("BEGIN")

    engine.execute = getattr(
        engine, "execute", None
    )  # no-op, keeps linters quiet on older SQLAlchemy stubs
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def seed_department(db_session):
    dept = Department(id=1, department="Engineering")
    db_session.add(dept)
    db_session.commit()
    return dept


@pytest.fixture()
def seed_job(db_session):
    job = Job(id=1, job="Recruiter")
    db_session.add(job)
    db_session.commit()
    return job
