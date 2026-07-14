"""
Shared fixtures for Postgres integration tests. Connects to a dedicated
test database (TEST_DB_NAME, default "globant_test") — NOT the
development database used by db/session.py's SessionLocal.
"""

import os
import sys

APP_DIR = os.path.join(os.path.dirname(__file__), "..", "app")
sys.path.insert(0, os.path.abspath(APP_DIR))

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from db.base import Base
from db.config import get_test_database_url
from models import Department, Job, HiredEmployee  # noqa: F401 — registers models
from services.restore import RESTORE_ORDER_PARENT_TO_CHILD


def _ensure_test_database_ready():
    """Creates globant_test if missing, then ensures all tables exist.
    Called explicitly by pg_test_session below — NOT relying on pytest's
    autouse fixture discovery, which does not apply to a plain module
    like this one unless pytest is told to collect fixtures from it."""
    test_url = get_test_database_url()

    if not database_exists(test_url):
        create_database(test_url)

    engine = create_engine(test_url)
    Base.metadata.create_all(engine)
    engine.dispose()


@pytest.fixture()
def pg_test_session():
    test_url = get_test_database_url()

    # Hard safety check: refuse to proceed if this connection isn't
    # unambiguously a test database. This exists because a prior
    # incident (see changelog.md, Phase 9) involved a test fixture
    # connecting to the development database by mistake — this assertion
    # makes that class of bug fail loudly and immediately instead of
    # silently truncating real data.
    db_name = test_url.rsplit("/", 1)[-1]
    assert "test" in db_name.lower(), (
        f"Refusing to run integration tests against database '{db_name}' — "
        f"name does not contain 'test'. This is a safety guardrail against "
        f"accidentally truncating the development database."
    )

    _ensure_test_database_ready()

    engine = create_engine(test_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    all_tables = ", ".join(RESTORE_ORDER_PARENT_TO_CHILD)
    session.execute(text(f"TRUNCATE TABLE {all_tables}"))
    session.commit()

    try:
        yield session
    finally:
        session.execute(text(f"TRUNCATE TABLE {all_tables}"))
        session.commit()
        session.close()
        engine.dispose()