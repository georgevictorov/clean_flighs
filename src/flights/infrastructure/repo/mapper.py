from flights.domain.model import Flight, FlightStatus, Seat


def to_domain(flight_row, seat_rows):
    return Flight(
        flight_id=flight_row[0],
        flight_status=FlightStatus(flight_row[1]),
        version_number=flight_row[2],
        seats=[
            Seat(
                seat_id=row[0],
                passenger_id=row[1],
            )
            for row in seat_rows
        ],
    )
