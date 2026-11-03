from unittest.mock import Mock

from apis_externas_4.challenges.space_exploration.infrastructure.nasa.client import NASAApiClient


def test_neo_client_passes_api_key_and_dates():
    session = Mock()
    response = Mock()
    response.json.return_value = {"near_earth_objects": {}}
    session.get.return_value = response
    client = NASAApiClient(api_key="test-key", session=session)
    result = client.get_neo_feed("2025-01-01", "2025-01-03")
    assert result == {"near_earth_objects": {}}
    params = session.get.call_args.kwargs["params"]
    assert params == {"start_date": "2025-01-01", "end_date": "2025-01-03", "api_key": "test-key"}


def test_exoplanet_query_uses_pscomppars():
    session = Mock()
    response = Mock()
    response.json.return_value = [{"discoverymethod": "Transit", "total": 12}]
    session.get.return_value = response
    client = NASAApiClient(session=session)
    rows = client.get_exoplanet_discovery_methods()
    assert rows[0]["total"] == 12
    query = session.get.call_args.kwargs["params"]["query"]
    assert "from pscomppars" in query
    assert session.get.call_args.kwargs["params"]["format"] == "json"
