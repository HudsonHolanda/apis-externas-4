from __future__ import annotations

from apis_externas_4.challenges.flight_tracking.domain.models import (
    BRAZIL_BBOX,
    AircraftPosition,
    AirportFlight,
    FlightTrack,
)
from apis_externas_4.challenges.flight_tracking.infrastructure.opensky.client import (
    OpenSkyApiClient,
)
from apis_externas_4.challenges.flight_tracking.infrastructure.opensky.mappers import (
    map_airport_flight,
    map_state_vectors,
    map_track,
)


class OpenSkyRepository:
    def __init__(self, client: OpenSkyApiClient) -> None:
        self.client = client

    def list_aircraft_over_brazil(self) -> list[AircraftPosition]:
        return map_state_vectors(self.client.get_states(BRAZIL_BBOX.to_params(), extended=True))

    def get_track(self, icao24: str, timestamp: int = 0) -> FlightTrack | None:
        payload = self.client.get_track(icao24, timestamp)
        return map_track(payload) if payload else None

    def list_airport_flights(
        self, airport: str, direction: str, begin: int, end: int
    ) -> list[AirportFlight]:
        payload = self.client.get_airport_flights(airport, direction, begin, end)
        return [map_airport_flight(item) for item in payload]
