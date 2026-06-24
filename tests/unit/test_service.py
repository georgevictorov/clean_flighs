import pytest

from flights.infrastructure.uow.memory.memory_uow import InMemoryUnitOfWork
from flights.service_layer.service import FlightService
from flights.domain.errors import FlightNotFound, FlightDeparted, NotReservationOwner
from flights.domain.model import Reservation, FlightStatus


def create_flight_service():
    uow = InMemoryUnitOfWork()
    flight_service = FlightService(uow)
    return flight_service


def test_create_flight():
    service = create_flight_service()

    service.create_flight(
        "A-204",
        {"A1", "A2", "A3", }
    )

    flight = service._get_flight("A-204")

    assert flight.flight_id == "A-204"
    assert flight.seats == {"A1", "A2", "A3"}
    assert flight.reservations == {}


def test_create_flight_should_not_create_duplicate():
    service = create_flight_service()

    service.create_flight("A-204", {"A1", "A2"})
    service.create_flight("A-204", {"B1", "B2"})
    service.create_flight("A-204", {"C1", "C2"})

    flight = service._get_flight("A-204")

    assert flight.seats == {"A1", "A2"}


def test_reserve_seat():
    service = create_flight_service()

    service.create_flight("A-204", {"A1", "A2"})

    service.reserve_seat(
        flight_id="A-204",
        passenger_id="p1",
        seat_id="A1",
    )

    flight = service._get_flight("A-204")

    assert flight.reservations["A1"] == Reservation(
        passenger_id="p1",
        seat_id="A1",
    )


def test_reserve_seat_for_unknown_flight():
    service = create_flight_service()

    with pytest.raises(FlightNotFound):
        service.reserve_seat(
            flight_id="UNKNOWN",
            passenger_id="p1",
            seat_id="A1",
        )


def test_cancel_reservation():
    service = create_flight_service()

    service.create_flight("A-204", {"A1", "A2"})

    service.reserve_seat(
        flight_id="A-204",
        passenger_id="p1",
        seat_id="A1",
    )

    service.cancel_reservation(
        flight_id="A-204",
        passenger_id="p1",
        seat_id="A1",
    )

    flight = service._get_flight("A-204")

    assert "A1" not in flight.reservations


def test_cancel_reservation_for_unknown_flight():
    service = create_flight_service()

    with pytest.raises(FlightNotFound):
        service.cancel_reservation(
            flight_id="UNKNOWN",
            passenger_id="p1",
            seat_id="A1",
        )


def test_cancel_reservation_for_departed_flight():
    service = create_flight_service()

    service.create_flight("A-204", {"A1", "A2"})

    flight = service._get_flight("A-204")
    flight.flight_status = FlightStatus.DEPARTED

    with pytest.raises(FlightDeparted):
        service.cancel_reservation(
            flight_id="A-204",
            passenger_id="p1",
            seat_id="A1",
        )


def test_cancel_nonexistent_reservation_is_noop():
    service = create_flight_service()

    service.create_flight("A-204", {"A1", "A2"})

    service.cancel_reservation(
        flight_id="A-204",
        passenger_id="p1",
        seat_id="A1",
    )

    flight = service._get_flight("A-204")

    assert flight.reservations == {}


def test_cancel_reservation_by_another_passenger():
    service = create_flight_service()

    service.create_flight("A-204", {"A1", "A2"})

    service.reserve_seat(
        flight_id="A-204",
        passenger_id="owner",
        seat_id="A1",
    )

    with pytest.raises(NotReservationOwner):
        service.cancel_reservation(
            flight_id="A-204",
            passenger_id="intruder",
            seat_id="A1",
        )


def test_get_flight():
    service = create_flight_service()

    service.create_flight("A-204", {"A1"})

    flight = service._get_flight("A-204")

    assert flight.flight_id == "A-204"


def test_get_flight_not_found():
    service = create_flight_service()

    with pytest.raises(FlightNotFound):
        service._get_flight("UNKNOWN")
