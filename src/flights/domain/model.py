from dataclasses import dataclass
from enum import Enum

from flights.domain import errors


class FlightStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    DEPARTED = "departed"


@dataclass
class Reservation:
    passenger_id: str
    seat_id: str


class Flight:
    def __init__(
            self,
            flight_id: str,
            seats: set[str],
            reservations: dict[str, Reservation],
            flight_status: FlightStatus = FlightStatus.OPEN,
            version_number: int = 1
    ):
        self.flight_id = flight_id
        self.seats = seats
        self.reservations = reservations
        self.flight_status = flight_status
        self.version_number = version_number

    def reserve(self, passenger_id: str, seat_id: str):
        if self.flight_status != FlightStatus.OPEN:
            raise errors.FlightClosed("flight status must be OPEN")

        reservation = Reservation(passenger_id, seat_id)

        if reservation.seat_id not in self.seats:
            raise errors.SeatDoesNotExist("seat does not exist")
        if reservation.seat_id in self.reservations:
            raise errors.SeatAlreadyReserved("seat already reserved")
        if reservation.passenger_id in {r.passenger_id for r in self.reservations.values()}:
            raise errors.PassengerAlreadyRegistered("passenger already registered")

        self.reservations[reservation.seat_id] = reservation

    def cancel(self, passenger_id: str, seat_id: str):
        if self.flight_status == FlightStatus.DEPARTED:
            raise errors.FlightDeparted("flight already departed")

        reservation = Reservation(passenger_id, seat_id)

        existing = self.reservations.get(reservation.seat_id)

        if not existing:
            return

        if existing.passenger_id != reservation.passenger_id:
            raise errors.NotReservationOwner

        del self.reservations[reservation.seat_id]

    def __eq__(self, other):
        if not isinstance(other, Flight):
            return False
        return self.flight_id == other.flight_id


