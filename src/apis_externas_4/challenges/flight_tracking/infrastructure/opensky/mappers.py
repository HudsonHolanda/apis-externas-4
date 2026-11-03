from __future__ import annotations

from typing import Any

from apis_externas_4.challenges.flight_tracking.domain.models import (
    AircraftPosition,
    AirportFlight,
    FlightTrack,
    FlightWaypoint,
)


def _value(values: list[Any], index: int) -> Any:
    return values[index] if len(values) > index else None


def _float(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int | None:
    try:
        return None if value is None else int(value)
    except (TypeError, ValueError):
        return None


def map_state_vector(values: list[Any]) -> AircraftPosition:
    if len(values) < 17:
        raise ValueError("Vetor de estado OpenSky incompleto: são esperados ao menos 17 campos.")
    return AircraftPosition(
        icao24=str(_value(values, 0) or "").lower(),
        callsign=str(_value(values, 1)).strip() or None if _value(values, 1) else None,
        origin_country=_value(values, 2),
        time_position=_int(_value(values, 3)),
        last_contact=_int(_value(values, 4)),
        longitude=_float(_value(values, 5)),
        latitude=_float(_value(values, 6)),
        baro_altitude_m=_float(_value(values, 7)),
        on_ground=_value(values, 8),
        velocity_m_s=_float(_value(values, 9)),
        true_track_deg=_float(_value(values, 10)),
        vertical_rate_m_s=_float(_value(values, 11)),
        geo_altitude_m=_float(_value(values, 13)),
        squawk=_value(values, 14),
        position_source=_int(_value(values, 16)),
        category=_int(_value(values, 17)),
    )


def map_state_vectors(payload: dict[str, Any]) -> list[AircraftPosition]:
    states = payload.get("states") or []
    if not isinstance(states, list):
        raise ValueError("Campo states da OpenSky deve ser uma lista.")
    aircraft = []
    for state in states:
        if isinstance(state, list):
            try:
                item = map_state_vector(state)
            except ValueError:
                continue
            if item.latitude is not None and item.longitude is not None:
                aircraft.append(item)
    return aircraft


def map_track(payload: dict[str, Any]) -> FlightTrack:
    waypoints = []
    for point in payload.get("path") or []:
        if not isinstance(point, list) or len(point) < 6:
            continue
        waypoint = FlightWaypoint(
            timestamp=int(point[0]),
            latitude=_float(point[1]),
            longitude=_float(point[2]),
            baro_altitude_m=_float(point[3]),
            true_track_deg=_float(point[4]),
            on_ground=point[5],
        )
        if waypoint.latitude is not None and waypoint.longitude is not None:
            waypoints.append(waypoint)
    return FlightTrack(
        icao24=str(payload.get("icao24", "")).lower(),
        start_time=_int(payload.get("startTime")),
        end_time=_int(payload.get("endTime")),
        callsign=payload.get("calllsign") or payload.get("callsign"),
        path=tuple(sorted(waypoints, key=lambda item: item.timestamp)),
    )


def map_airport_flight(payload: dict[str, Any]) -> AirportFlight:
    return AirportFlight(
        icao24=str(payload.get("icao24", "")).lower(),
        first_seen=_int(payload.get("firstSeen")),
        last_seen=_int(payload.get("lastSeen")),
        callsign=payload.get("callsign"),
        est_departure_airport=payload.get("estDepartureAirport"),
        est_arrival_airport=payload.get("estArrivalAirport"),
        departure_airport_candidates=_int(payload.get("departureAirportCandidatesCount")),
        arrival_airport_candidates=_int(payload.get("arrivalAirportCandidatesCount")),
    )
