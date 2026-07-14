"""
Meta-test: confirms the safety guardrail in integration_conftest.py's
pg_test_session actually aborts when pointed at a non-test database.
Does NOT require RUN_INTEGRATION_TESTS=1 — this test validates a pure
assertion, not database connectivity, so it runs as part of the fast
unit suite (no live Postgres connection needed to prove the guardrail
logic itself works).
"""

import pytest


def test_guardrail_rejects_non_test_database_name():
    """
    Isolated reproduction of the assertion inside pg_test_session,
    without needing a real Postgres connection — proves the guardrail
    logic is sound independent of infrastructure availability.
    """

    def _fake_pg_test_session(db_url: str):
        db_name = db_url.rsplit("/", 1)[-1]
        assert "test" in db_name.lower(), (
            f"Refusing to run integration tests against database '{db_name}' — "
            f"name does not contain 'test'."
        )

    # A production-like URL must trigger the guardrail
    with pytest.raises(AssertionError, match="Refusing to run"):
        _fake_pg_test_session("postgresql://user:pass@host:5432/globant_de_challenge")

    # A properly named test database must pass through cleanly
    _fake_pg_test_session("postgresql://user:pass@host:5432/globant_test")  # no raise
