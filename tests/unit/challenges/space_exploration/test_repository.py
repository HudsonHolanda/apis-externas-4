from unittest.mock import Mock

from apis_externas_4.challenges.space_exploration.infrastructure.nasa.repositories import NASARepository


def test_repository_splits_neo_range_into_valid_api_windows():
    client = Mock()
    client.get_neo_feed.side_effect = [
        {"near_earth_objects": {"2025-01-01": []}},
        {"near_earth_objects": {"2025-01-08": []}},
    ]
    repository = NASARepository(client)
    frame = repository.list_asteroid_approaches("2025-01-01", "2025-01-08")
    assert frame.empty
    assert client.get_neo_feed.call_count == 2
    assert client.get_neo_feed.call_args_list[0].args == ("2025-01-01", "2025-01-07")
    assert client.get_neo_feed.call_args_list[1].args == ("2025-01-08", "2025-01-08")


def test_repository_maps_apod_and_eonet_data():
    client = Mock()
    client.get_apod.return_value = {
        "date": "2025-01-01", "title": "APOD", "explanation": "Text",
        "media_type": "image", "hdurl": "https://example.test/image.jpg",
    }
    client.get_eonet_events.return_value = {"events": []}
    repository = NASARepository(client)
    assert repository.get_apod("2025-01-01").title == "APOD"
    assert repository.list_recent_events(hours=48) == []
    client.get_eonet_events.assert_called_once_with(days=3)
