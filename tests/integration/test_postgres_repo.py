import pytest

from flights.domain.errors import ConcurrencyError, InfrastructureError
from flights.domain.model import Flight
from flights.infrastructure.repo.postgres.postgres_repo import \
    PostgresRepository


def test_get_raises_error_if_conn_closed(db_connection, clean_db):
    repo = PostgresRepository(db_connection)
    db_connection.close()
    with pytest.raises(InfrastructureError):
        repo.get("A1")


def test_flush_raises_error_if_conn_closed(db_connection, clean_db):
    flight = Flight.create_new("SU-91", ["A1", "A2", "A3", "A4", "A5", "A6", "A7"])
    repo = PostgresRepository(db_connection)
    repo.add(flight)
    db_connection.close()
    with pytest.raises(InfrastructureError):
        repo.flush()


def test_flush_raises_concurrency_error_if_version_changed(db_connection, clean_db):
    flight = Flight.create_new(
        "SU-91",
        ["A1", "A2", "A3", "A4", "A5", "A6", "A7"],
    )
    repo = PostgresRepository(db_connection)
    repo.add(flight)
    repo.flush()
    db_connection.commit()

    flight = repo.get("SU-91")
    flight.reserve("P1", "A1")

    # make changes
    with db_connection.cursor() as cur:
        cur.execute(
            """
            UPDATE flights
            SET version = version + 1
            WHERE flight_id = %s
            """,
            ("SU-91",),
        )
    db_connection.commit()

    with pytest.raises(ConcurrencyError):
        repo.flush()
