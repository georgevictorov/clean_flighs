from flights.domain.model import Flight


class InMemoryRepository:
    def __init__(self):
        self.flights: dict[str, Flight] = {}

    def add(self, flight: Flight):
        self.flights[flight.flight_id] = flight

    def get(self, flight_id: str):
        return self.flights.get(flight_id)
