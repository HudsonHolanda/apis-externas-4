from apis_externas_4.challenges.flight_tracking.domain.models import (
    AircraftPosition, FlightTrack, FlightWaypoint,
)
from apis_externas_4.challenges.flight_tracking.presentation.maps import (
    create_brazil_aircraft_map, create_track_map,
)


def test_create_aircraft_map_writes_html(tmp_path):
    aircraft = AircraftPosition(
        "abc123", "TEST", "Brazil", 1, 1, -46.6, -23.5, 1000, False,
        200, 90, 0, 1000, None, 0, 8,
    )
    output = create_brazil_aircraft_map([aircraft], tmp_path / "map.html", category="rotorcraft")
    assert output.exists()
    assert "abc123" in output.read_text(encoding="utf-8")


def test_create_track_map_writes_polyline(tmp_path):
    track = FlightTrack(
        "abc123", 1, 2, "TEST",
        (FlightWaypoint(1, -23.0, -46.0, 1000, 90, False),
         FlightWaypoint(2, -22.0, -45.0, 1200, 100, False)),
    )
    output = create_track_map(track, tmp_path / "track.html")
    html = output.read_text(encoding="utf-8")
    assert "Trajetória" in html
    assert "abc123" in html
