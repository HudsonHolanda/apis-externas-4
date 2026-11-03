from __future__ import annotations

from typing import Any

import requests

from apis_externas_4.shared.exceptions import ApiError


class NASAApiClient:
    """Cliente das APIs NASA, EONET e NASA Exoplanet Archive."""

    NASA_BASE_URL = "https://api.nasa.gov"
    APOD_BASE_URL = "https://science.nasa.gov/wp-json/wp/v2/apod-basic"
    EONET_BASE_URL = "https://eonet.gsfc.nasa.gov/api/v3"
    EXOPLANET_TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout: float = 45.0,
        session: requests.Session | None = None,
    ) -> None:
        self.api_key = api_key or "DEMO_KEY"
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(
            {"Accept": "application/json", "User-Agent": "open-data-challenges/0.1.0"}
        )

    def _get_json(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        *,
        context: str,
    ) -> Any:
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status == 429:
                raise ApiError(f"Limite de requisições atingido em {context}.") from exc
            raise ApiError(f"Falha ao consultar {context}: {exc}") from exc
        except ValueError as exc:
            raise ApiError(f"A fonte {context} retornou JSON inválido.") from exc

    def get_neo_feed(self, start_date: str, end_date: str) -> dict[str, Any]:
        payload = self._get_json(
            f"{self.NASA_BASE_URL}/neo/rest/v1/feed",
            {"start_date": start_date, "end_date": end_date, "api_key": self.api_key},
            context="NASA NeoWs",
        )
        if not isinstance(payload, dict):
            raise ApiError("Formato inesperado do NeoWs: esperado objeto JSON.")
        return payload

    def get_apod(self, date: str) -> dict[str, Any]:
        payload = self._get_json(
            self.APOD_BASE_URL,
            {"date": date, "api_key": self.api_key},
            context="NASA APOD",
        )
        if isinstance(payload, list):
            payload = payload[0] if payload else None
        if not isinstance(payload, dict):
            raise ApiError("Formato inesperado do APOD: esperado objeto JSON.")
        return payload

    def get_eonet_events(self, *, days: int = 2) -> dict[str, Any]:
        payload = self._get_json(
            f"{self.EONET_BASE_URL}/events",
            {"days": days, "status": "all"},
            context="NASA EONET",
        )
        if not isinstance(payload, dict):
            raise ApiError("Formato inesperado do EONET: esperado objeto JSON.")
        return payload

    def get_exoplanet_discovery_methods(self) -> list[dict[str, Any]]:
        query = (
            "select discoverymethod, count(*) as total "
            "from pscomppars where discoverymethod is not null "
            "group by discoverymethod order by total desc"
        )
        payload = self._get_json(
            self.EXOPLANET_TAP_URL,
            {"query": query, "format": "json"},
            context="NASA Exoplanet Archive TAP",
        )
        if not isinstance(payload, list):
            raise ApiError("Formato inesperado do Exoplanet Archive: esperado lista JSON.")
        return [item for item in payload if isinstance(item, dict)]
