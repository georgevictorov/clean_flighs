import pytest
from flights.infrastructure.repo.sqlite.sqlite_repository import SqliteRepository
from flights.domain.errors import InfrastructureError
from flights.domain.model import Flight


def test_get_raises_error_if_conn_closed(sqlite_session_factory):
    conn = sqlite_session_factory()
    repo = SqliteRepository(conn)
    conn.close()
    with pytest.raises(InfrastructureError):
        repo.get("A1")

def test_flush_raises_error_if_conn_closed(sqlite_session_factory):
    flight = Flight.create_new("SU-91", ["A1", "A2", "A3", "A4", "A5", "A6", "A7"])
    conn = sqlite_session_factory()
    repo = SqliteRepository(conn)
    repo.add(flight)
    conn.close()
    with pytest.raises(InfrastructureError):
        repo.flush()