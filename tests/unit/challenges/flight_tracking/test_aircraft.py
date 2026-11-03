from apis_externas_4.challenges.flight_tracking.application.aircraft import filter_aircraft
from apis_externas_4.challenges.flight_tracking.domain.models import AircraftPosition


def aircraft(category):
    return AircraftPosition(
        icao24=f"abc{category:03d}", callsign="TEST", origin_country="Brazil",
        time_position=1, last_contact=1, longitude=-46.6, latitude=-23.5,
        baro_altitude_m=1000, on_ground=False, velocity_m_s=200,
        true_track_deg=90, vertical_rate_m_s=0, geo_altitude_m=1000,
        squawk=None, position_source=0, category=category,
    )


def test_filter_rotorcraft_only():
    result = filter_aircraft([aircraft(8), aircraft(4), aircraft(6)], "rotorcraft")
    assert [item.category for item in result] == [8]


def test_commercial_is_large_heavy_category_proxy():
    result = filter_aircraft([aircraft(2), aircraft(4), aircraft(5), aircraft(6), aircraft(8)], "commercial")
    assert [item.category for item in result] == [4, 5, 6]


def test_filter_all_keeps_unknown_categories():
    assert len(filter_aircraft([aircraft(0), aircraft(8)])) == 2


def test_filter_excludes_aircraft_explicitly_reported_on_ground():
    airborne = aircraft(8)
    grounded = AircraftPosition(
        icao24="ground1", callsign="GROUND", origin_country="Brazil",
        time_position=1, last_contact=1, longitude=-46.6, latitude=-23.5,
        baro_altitude_m=0, on_ground=True, velocity_m_s=0, true_track_deg=None,
        vertical_rate_m_s=None, geo_altitude_m=0, squawk=None,
        position_source=0, category=8,
    )
    assert filter_aircraft([airborne, grounded]) == [airborne]
