from apis_externas_4.challenges.flight_tracking.application.track import run_aircraft_track
from apis_externas_4.challenges.flight_tracking.domain.models import FlightTrack, FlightWaypoint


class Repository:
    def __init__(self, track):
        self.track = track
        self.request = None

    def get_track(self, icao24, timestamp):
        self.request = (icao24, timestamp)
        return self.track


def sample_track():
    return FlightTrack(
        icao24="abc123", start_time=100, end_time=300, callsign="TEST",
        path=(
            FlightWaypoint(100, -20, -40, 1000, 90, False),
            FlightWaypoint(200, -21, -41, 1100, 90, False),
            FlightWaypoint(300, -22, -42, 1200, 90, False),
        ),
    )


def test_live_track_keeps_complete_path_when_last_point_is_recent():
    repository = Repository(sample_track())
    result = run_aircraft_track(repository, "ABC123", hours=1, now=3900)
    assert repository.request == ("abc123", 0)
    assert [point.timestamp for point in result.path] == [100, 200, 300]


def test_live_track_rejects_stale_activity():
    repository = Repository(sample_track())
    try:
        run_aircraft_track(repository, "abc123", hours=1, now=4000)
    except ValueError as exc:
        assert "últimas" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_historical_timestamp_is_passed_to_repository():
    repository = Repository(sample_track())
    run_aircraft_track(repository, "abc123", timestamp=250)
    assert repository.request == ("abc123", 250)


def test_invalid_icao24_is_rejected():
    repository = Repository(sample_track())
    try:
        run_aircraft_track(repository, "xyz")
    except ValueError as exc:
        assert "ICAO24" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
