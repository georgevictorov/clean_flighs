from typing import Protocol
from flights.domain.model import Flight


class AbstractRepository(Protocol):
    def add(self, flight: Flight):
        ...

    def get(self, flight_id: str) -> Flight | None:
        ...
