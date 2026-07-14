import os
from dotenv import load_dotenv

load_dotenv()


def get_database_url(dbname_override: str | None = None) -> str:
    dbname = dbname_override or os.getenv("DB_NAME")
    return (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{dbname}"
    )


def get_test_database_url() -> str:
    """
    Dedicated test database, same Postgres instance/credentials as
    development but a physically separate database — not a schema
    within the same database. This is a structural safety guarantee:
    even a buggy test fixture (e.g. an unqualified TRUNCATE) cannot
    reach development data, because it's connected to a different
    database entirely, not just a different namespace within the same
    one. See tests/README.md for the incident that motivated this.
    """
    test_dbname = os.getenv("TEST_DB_NAME", "globant_test")
    return get_database_url(dbname_override=test_dbname)