import pytest

from flights.domain.errors import (FlightDeparted, FlightNotFound,
                                   NotReservationOwner)
from flights.domain.model import FlightStatus
from flights.infrastructure.uow.memory.memory_uow import InMemoryUnitOfWork
from flights.service_layer.service import FlightService


def create_flight_service():
    uow = InMemoryUnitOfWork()
    flight_service = FlightService(uow)
    return flight_service
