from flights.domain.model import Flight
from flights.service_layer.uow import AbstractUnitOfWork
from flights.domain.errors import FlightNotFound


class FlightService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def create_flight(self, flight_id: str, seats: set[str]):
        with self.uow:
            if self.uow.flights.get(flight_id):
                return

            flight = Flight(
                flight_id=flight_id,
                seats=seats,
                reservations={}
            )

            self.uow.flights.add(flight)

            self.uow.commit()

    def reserve_seat(self, flight_id: str, passenger_id: str, seat_id: str):
        with self.uow:
            flight = self._get_flight(flight_id)

            flight.reserve(passenger_id, seat_id)

            self.uow.commit()

    def cancel_reservation(self, flight_id: str, passenger_id: str, seat_id: str):
        with self.uow:
            flight = self._get_flight(flight_id)

            flight.cancel(passenger_id, seat_id)

            self.uow.commit()

    def _get_flight(self, flight_id):
        flight = self.uow.flights.get(flight_id)
        if not flight:
            raise FlightNotFound(f'flight not found, flight_id={flight_id}')
        return flight
