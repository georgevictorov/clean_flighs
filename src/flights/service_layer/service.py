from flights.domain import errors, model
from flights.service_layer import commands
from flights.service_layer.uow import AbstractUnitOfWork


class FlightService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def create_flight(self, cmd: commands.CreateFlight):
        with self.uow:
            flight = self.uow.flights.get(cmd.flight_id)

            if flight is not None:
                raise errors.FlightAlreadyExists('flight already exists')

            flight = model.Flight.create_new(cmd.flight_id, cmd.seat_ids)
            self.uow.flights.add(flight)

            self.uow.commit()

    def reserve_seat(self, cmd: commands.ReserveSeat):
        with self.uow:
            flight = self.uow.flights.get(cmd.flight_id)

            if flight is None:
                raise errors.FlightNotFound('flight not found')

            flight.reserve(cmd.passenger_id, cmd.seat_id)

            self.uow.commit()

    def cancel_reservation(self, cmd: commands.CancelReservation):
        with self.uow:
            flight = self.uow.flights.get(cmd.flight_id)

            if flight is None:
                raise errors.FlightNotFound('flight not found')

            flight.cancel(cmd.passenger_id)

            self.uow.commit()
