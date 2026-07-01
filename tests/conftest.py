import sqlite3
import uuid

import pytest
from psycopg_pool import ConnectionPool

from flights.config import get_postgres_uri
from flights.infrastructure.repo.sqlite.schema import SCHEMA


@pytest.fixture
def sqlite_session_factory():
    db_uri = f"file:{uuid.uuid4()}?mode=memory&cache=shared"

    main_conn = sqlite3.connect(db_uri, uri=True)
    main_conn.executescript(SCHEMA)

    yield lambda: sqlite3.connect(db_uri, uri=True)

    main_conn.close()


@pytest.fixture(scope="session")
def db_pool():
    db_uri = get_postgres_uri()
    with ConnectionPool(
            conninfo=db_uri,
            min_size=1,
            max_size=4,
    ) as pool:
        yield pool


@pytest.fixture
def db_connection(db_pool):
    with db_pool.connection() as conn:
        yield conn


@pytest.fixture
def clean_db(db_connection):
    with db_connection.cursor() as cur:
        cur.execute("truncate table flights, seats cascade")

    db_connection.commit()

    yield
