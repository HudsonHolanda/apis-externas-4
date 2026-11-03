import pytest
import requests

from apis_externas_4.shared.exceptions import ApiError, NotFoundError
from apis_externas_4.shared.http import JsonApiClient


class FakeResponse:
    def __init__(self, payload=None, status_code=200, text=""):
        self.payload = payload
        self.status_code = status_code
        self.text = text

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.headers = {}
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params, timeout))
        return self.responses.pop(0)


def test_get_paginated_collects_all_pages():
    session = FakeSession(
        [
            FakeResponse({"dados": [{"id": 1}, {"id": 2}]}),
            FakeResponse({"dados": [{"id": 3}]}),
        ]
    )
    client = JsonApiClient("https://example.test", page_size=2, session=session)
    result = client.get_paginated("items")
    assert result == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert [call[1]["pagina"] for call in session.calls] == [1, 2]


def test_get_paginated_respects_max_items():
    session = FakeSession([FakeResponse({"dados": [{"id": 1}, {"id": 2}]})])
    client = JsonApiClient("https://example.test", page_size=2, session=session)
    result = client.get_paginated("items", max_items=1)
    assert result == [{"id": 1}]
    assert len(session.calls) == 1


def test_get_raises_api_error_for_http_error():
    session = FakeSession([FakeResponse({"erros": []}, status_code=500)])
    client = JsonApiClient("https://example.test", session=session)
    with pytest.raises(ApiError, match="HTTP 500"):
        client.get("items")


def test_get_raises_not_found_for_404():
    session = FakeSession([FakeResponse(status_code=404)])
    client = JsonApiClient("https://example.test", session=session)
    with pytest.raises(NotFoundError):
        client.get("items/1")


def test_get_raises_error_for_invalid_json():
    session = FakeSession([FakeResponse(ValueError("bad json"))])
    client = JsonApiClient("https://example.test", session=session)
    with pytest.raises(ApiError, match="JSON inválido"):
        client.get("items")


def test_page_size_is_limited_to_api_maximum():
    with pytest.raises(ValueError):
        JsonApiClient("https://example.test", page_size=101)
