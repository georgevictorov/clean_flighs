import pytest

from flights.domain.errors import FlightAlreadyExists, FlightNotFound
from flights.infrastructure.repo.memory.memory_repository import \
    InMemoryRepository
from flights.infrastructure.uow.memory.memory_uow import InMemoryUnitOfWork
from flights.service_layer.commands import (CancelReservation, CreateFlight,
                                            ReserveSeat)
from flights.service_layer.service import FlightService


@pytest.fixture
def uow():
    return InMemoryUnitOfWork(InMemoryRepository())


@pytest.fixture
def service(uow):
    return FlightService(uow)


def create_command_create_flight():
    cmd = CreateFlight(
        flight_id="SU-901",
        seat_ids=["A1", "A2", "A3"],
    )
    return cmd


def create_command_reserve_seat():
    cmd = ReserveSeat(
        flight_id="SU-901",
        passenger_id="p01",
        seat_id="A1"
    )
    return cmd


def create_command_cancel_reservation():
    cmd = CancelReservation(
        flight_id="SU-901",
        passenger_id="p01",
    )

    return cmd


def test_create_flight_success(service, uow):
    cmd = create_command_create_flight()
    service.create_flight(cmd)

    assert uow.flights.get(flight_id="SU-901").flight_id == cmd.flight_id


def test_create_flight_already_exists_failure(service):
    cmd = create_command_create_flight()
    service.create_flight(cmd)

    with pytest.raises(FlightAlreadyExists):
        service.create_flight(cmd)


def test_reserve_seat_success(service, uow):
    cmd = create_command_create_flight()
    service.create_flight(cmd)

    cmd = create_command_reserve_seat()

    service.reserve_seat(cmd)

    flight = uow.flights.get(flight_id="SU-901")
    seat = next(s for s in flight.seats if s.seat_id == cmd.seat_id)

    assert seat.passenger_id == cmd.passenger_id
    assert seat.is_reserved


def test_reserve_seat_flight_not_found_failure(service):
    cmd = create_command_create_flight()
    service.create_flight(cmd)

    with pytest.raises(FlightNotFound):
        service.reserve_seat(ReserveSeat(
            flight_id="SU-902",
            passenger_id="p01",
            seat_id="A1"
        ))


def test_cancel_reservation_success(service, uow):
    cmd = create_command_create_flight()
    service.create_flight(cmd)

    cmd = create_command_reserve_seat()
    service.reserve_seat(cmd)

    cmd = create_command_cancel_reservation()
    service.cancel_reservation(cmd)

    flight = uow.flights.get(flight_id="SU-901")

    seat = next(s for s in flight.seats if s.seat_id == "A1")

    assert seat.passenger_id is None
    assert seat.is_reserved is False


def test_cancel_reservation_flight_not_found_failure(service):
    with pytest.raises(FlightNotFound):
        service.cancel_reservation(CancelReservation(
            flight_id="SU-902",
            passenger_id="p01",
        ))
