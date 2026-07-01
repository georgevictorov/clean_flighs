import sqlite3

from flights.domain.errors import ConcurrencyError, InfrastructureError
from flights.domain.model import Flight
from flights.infrastructure.repo.mapper import to_domain


class SqliteRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

        # identity map
        self._seen: dict[str, Flight] = {}
        # snapshot
        self._snapshots: dict[str, Flight] = {}

    def get(self, flight_id: str) -> Flight | None:
        if flight_id in self._seen:
            return self._seen[flight_id]

        try:
            flight_row = self._conn.execute(
                """
                select
                    flight_id,
                    status,
                    version
                from flights
                where
                    flight_id = ?
                """,
                (flight_id,),
            ).fetchone()

            if flight_row is None:
                return None

            seat_rows = self._conn.execute(
                """
                select
                    seat_id, 
                    passenger_id
                from seats
                where
                    flight_id = ?
                order by seat_id
                """,
                (flight_id,),
            ).fetchall()

            flight = to_domain(flight_row, seat_rows)

            self._seen[flight_id] = flight
            self._snapshots[flight_id] = flight.persistence_state

            return flight
        except sqlite3.Error as e:
            raise InfrastructureError from e

    def add(self, flight: Flight):
        self._seen[flight.flight_id] = flight

    def flush(self):
        try:
            for flight_id, flight in self._seen.items():

                snapshot = self._snapshots.get(flight_id)

                if snapshot is None:
                    self._insert(flight)
                    self._snapshots[flight_id] = flight.persistence_state
                elif snapshot != flight.persistence_state:
                    self._update(flight)
                    self._snapshots[flight_id] = flight.persistence_state
        except sqlite3.Error as e:
            raise InfrastructureError() from e

    def _insert(self, flight: Flight):

        self._conn.execute(
            """
            insert into flights(
                flight_id,
                status,
                version
            )
            values (?, ?, ?)
            """,
            (
                flight.flight_id,
                flight.flight_status.value,
                flight.version_number,
            ),
        )

        self._conn.executemany(
            """
            insert into seats(
                flight_id,
                seat_id,
                passenger_id
            )
            values (?, ?, ?)
            """,
            [
                (
                    flight.flight_id,
                    seat.seat_id,
                    seat.passenger_id,
                )
                for seat in flight.seats
            ]
        )

    def _update(self, flight: Flight):

        cursor = self._conn.execute(
            """
            update flights
            set
                status = ?,
                version = version + 1
            where 
                flight_id = ? and
                version = ?
            """,
            (
                flight.flight_status.value,
                flight.flight_id,
                flight.version_number,
            ),
        )

        if cursor.rowcount != 1:
            raise ConcurrencyError()

        self._conn.execute(
            """
            delete from seats
            where
                flight_id = ?
            """,
            (flight.flight_id,),
        )

        self._conn.executemany(
            """
            insert into seats(
                flight_id,
                seat_id,
                passenger_id
            )
            values (?, ?, ?)
            """,
            [
                (
                    flight.flight_id,
                    seat.seat_id,
                    seat.passenger_id,
                )
                for seat in flight.seats
            ],
        )

        flight.version_number += 1
