import pytest

from apis_externas_4.challenges.flight_tracking.infrastructure.opensky.mappers import (
    map_state_vector,
    map_state_vectors,
    map_track,
)


def test_map_state_vector_with_extended_category():
    item = map_state_vector([
        "abc123", " GLO123 ", "Brazil", 100, 101, -46.6, -23.5, 1200,
        False, 220, 180, 0, None, 1250, "1234", False, 0, 8,
    ])
    assert item.icao24 == "abc123"
    assert item.callsign == "GLO123"
    assert item.category == 8
    assert item.category_name == "Helicóptero"


def test_map_state_vectors_skips_missing_positions_and_short_rows():
    payload = {"states": [["abc", "x", "Brazil"], [
        "abc123", "CALL", "Brazil", 1, 1, -46.0, -23.0, None, False,
        200, 90, 0, None, None, None, False, 0, 4,
    ]]}
    assert len(map_state_vectors(payload)) == 1


def test_map_track_sorts_points_and_skips_missing_coordinates():
    payload = {
        "icao24": "ABC123", "startTime": 100, "endTime": 200, "calllsign": "TEST",
        "path": [[200, -22.0, -44.0, 1000, 180, False], [100, -23.0, -45.0, 900, 170, False], [150, None, None, 800, 160, False]],
    }
    track = map_track(payload)
    assert track.icao24 == "abc123"
    assert [point.timestamp for point in track.path] == [100, 200]


def test_map_state_vector_rejects_incomplete_row():
    with pytest.raises(ValueError):
        map_state_vector(["abc123"])
