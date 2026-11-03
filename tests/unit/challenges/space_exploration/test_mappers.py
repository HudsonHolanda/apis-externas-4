from datetime import UTC, datetime

from apis_externas_4.challenges.space_exploration.infrastructure.nasa.mappers import (
    map_apod,
    map_eonet_events,
    map_exoplanet_methods,
    map_neo_feeds,
    split_date_range,
)


def test_split_date_range_respects_seven_day_neo_window():
    result = split_date_range("2025-01-01", "2025-01-10")
    assert result == [("2025-01-01", "2025-01-07"), ("2025-01-08", "2025-01-10")]


def test_split_date_range_rejects_invalid_interval():
    try:
        split_date_range("2025-02-01", "2025-01-01")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_map_neo_feeds_flattens_nested_json_and_converts_kmh_to_km_s():
    frame = map_neo_feeds([{
        "near_earth_objects": {
            "2025-01-01": [{
                "id": "123", "name": "Asteroid A",
                "estimated_diameter": {"kilometers": {
                    "estimated_diameter_min": 0.1, "estimated_diameter_max": 0.2
                }},
                "is_potentially_hazardous_asteroid": True,
                "nasa_jpl_url": "https://example.test/asteroid",
                "close_approach_data": [{
                    "close_approach_date": "2025-01-01",
                    "close_approach_date_full": "2025-Jan-01 12:00",
                    "miss_distance": {"kilometers": "1000000"},
                    "relative_velocity": {"kilometers_per_hour": "36000"},
                }],
            }]
        }
    }])
    assert len(frame) == 1
    assert frame.iloc[0]["miss_distance_km"] == 1_000_000
    assert frame.iloc[0]["relative_velocity_km_s"] == 10
    assert bool(frame.iloc[0]["potentially_hazardous"]) is True


def test_map_apod_uses_hd_image_url_and_new_api_fields():
    apod = map_apod({
        "date": "2026-11-02", "title": "Deep sky", "explanation": "Text",
        "media_type": "image", "hdurl": "https://example.test/image.jpg",
        "permalink": "https://science.nasa.gov/apod/example", "credit": "NASA",
    })
    assert apod.image_url == "https://example.test/image.jpg"
    assert apod.page_url.endswith("example")


def test_map_exoplanet_methods_sorts_by_count():
    frame = map_exoplanet_methods([
        {"discoverymethod": "Transit", "total": 100},
        {"discoverymethod": "Radial Velocity", "total": 20},
        {"discoverymethod": None, "total": 5},
    ])
    assert frame.iloc[0]["discovery_method"] == "Transit"
    assert len(frame) == 2


def test_map_eonet_filters_last_48_hours_and_handles_polygon_centroid():
    now = datetime(2025, 1, 3, 12, tzinfo=UTC)
    events = map_eonet_events({"events": [
        {
            "id": "old", "title": "Old event", "categories": [],
            "geometry": [{"date": "2025-01-01T00:00:00Z", "type": "Point", "coordinates": [10, 20]}],
        },
        {
            "id": "new", "title": "New event", "categories": [{"title": "Wildfires"}],
            "geometry": [{"date": "2025-01-03T10:00:00Z", "type": "Polygon", "coordinates": [[[10, 20], [12, 20], [12, 22], [10, 22], [10, 20]]]}],
        },
    ]}, now=now, hours=48)
    assert len(events) == 1
    assert events[0].event_id == "new"
    assert events[0].latitude == 20.8
    assert events[0].longitude == 10.8


def test_eonet_includes_event_exactly_at_48_hour_cutoff():
    now = datetime(2025, 1, 3, 12, tzinfo=UTC)
    events = map_eonet_events({"events": [
        {
            "id": "cutoff", "title": "At cutoff", "categories": [],
            "geometry": [{
                "date": "2025-01-01T12:00:00Z",
                "type": "Point",
                "coordinates": [-46.6, -23.5],
            }],
        },
    ]}, now=now, hours=48)
    assert [event.event_id for event in events] == ["cutoff"]


def test_eonet_rejects_non_positive_window():
    try:
        map_eonet_events({"events": []}, hours=0)
    except ValueError as exc:
        assert "maior que zero" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
