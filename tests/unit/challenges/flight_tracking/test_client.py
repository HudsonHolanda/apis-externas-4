from unittest.mock import Mock

from apis_externas_4.challenges.flight_tracking.infrastructure.opensky.client import (
    OpenSkyApiClient,
    OpenSkyTokenProvider,
)


def test_anonymous_client_does_not_call_token_endpoint():
    session = Mock()
    response = Mock(status_code=200)
    response.json.return_value = {"time": 1, "states": []}
    session.get.return_value = response
    client = OpenSkyApiClient(session=session)
    payload = client.get_states({"lamin": -33, "lomin": -74, "lamax": 5, "lomax": -34})
    assert payload["states"] == []
    session.post.assert_not_called()
    assert session.get.call_args.kwargs["params"]["extended"] == 1


def test_oauth_token_is_reused_until_expiration():
    session = Mock()
    response = Mock()
    response.json.return_value = {"access_token": "token-123", "expires_in": 1800}
    session.post.return_value = response
    provider = OpenSkyTokenProvider("client", "secret", session=session)
    assert provider.get_token() == "token-123"
    assert provider.get_token() == "token-123"
    session.post.assert_called_once()


def test_unauthenticated_provider_returns_none():
    provider = OpenSkyTokenProvider(None, None, session=Mock())
    assert provider.get_token() is None
