from __future__ import annotations

import time
from typing import Any

import requests

from apis_externas_4.shared.exceptions import ApiError


class OpenSkyTokenProvider:
    """Obtém e renova token OAuth2 quando credenciais OpenSky são fornecidas."""

    TOKEN_URL = (
        "https://auth.opensky-network.org/auth/realms/opensky-network/"
        "protocol/openid-connect/token"
    )

    def __init__(
        self,
        client_id: str | None,
        client_secret: str | None,
        *,
        session: requests.Session | None = None,
        timeout: float = 30.0,
    ) -> None:
        if bool(client_id) != bool(client_secret):
            raise ValueError("Defina OPENSKY_CLIENT_ID e OPENSKY_CLIENT_SECRET em conjunto.")
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = session or requests.Session()
        self.timeout = timeout
        self._token: str | None = None
        self._expires_at = 0.0

    @property
    def authenticated(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def get_token(self, *, force_refresh: bool = False) -> str | None:
        if not self.authenticated:
            return None
        if not force_refresh and self._token and time.monotonic() < self._expires_at:
            return self._token
        try:
            response = self.session.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise ApiError(f"Não foi possível obter token OAuth2 da OpenSky: {exc}") from exc

        token = payload.get("access_token") if isinstance(payload, dict) else None
        if not token:
            raise ApiError("A autenticação OpenSky não retornou access_token.")
        expires_in = int(payload.get("expires_in", 1800))
        self._token = str(token)
        self._expires_at = time.monotonic() + max(1, expires_in - 30)
        return self._token


class OpenSkyApiClient:
    """Cliente REST OpenSky. Sem credenciais, utiliza a cota anônima por IP."""

    BASE_URL = "https://opensky-network.org/api"

    def __init__(
        self,
        *,
        timeout: float = 30.0,
        client_id: str | None = None,
        client_secret: str | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.headers.update(
            {"Accept": "application/json", "User-Agent": "open-data-challenges/0.1.0"}
        )
        self.tokens = OpenSkyTokenProvider(
            client_id, client_secret, session=self.session, timeout=timeout
        )

    def _get(self, path: str, params: dict[str, Any], *, allow_not_found: bool = False) -> Any:
        headers: dict[str, str] = {}
        token = self.tokens.get_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            response = self.session.get(
                f"{self.BASE_URL}/{path.lstrip('/')}",
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            if response.status_code == 404 and allow_not_found:
                return [] if path.startswith("flights/") else None
            if response.status_code == 401 and self.tokens.authenticated:
                token = self.tokens.get_token(force_refresh=True)
                response = self.session.get(
                    f"{self.BASE_URL}/{path.lstrip('/')}",
                    params=params,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=self.timeout,
                )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status == 429:
                raise ApiError("Limite de créditos da OpenSky atingido. Tente novamente mais tarde.") from exc
            raise ApiError(f"Falha ao consultar OpenSky ({path}): {exc}") from exc
        except ValueError as exc:
            raise ApiError(f"A OpenSky retornou JSON inválido para {path}.") from exc

    def get_states(self, bounding_box: dict[str, float], *, extended: bool = True) -> dict[str, Any]:
        params: dict[str, Any] = {**bounding_box, "extended": int(extended)}
        payload = self._get("states/all", params)
        if not isinstance(payload, dict):
            raise ApiError("Formato inesperado em states/all: esperado objeto JSON.")
        return payload

    def get_track(self, icao24: str, timestamp: int = 0) -> dict[str, Any] | None:
        payload = self._get(
            "tracks/all", {"icao24": icao24.lower(), "time": timestamp}, allow_not_found=True
        )
        if payload is not None and not isinstance(payload, dict):
            raise ApiError("Formato inesperado em tracks/all: esperado objeto JSON.")
        return payload

    def get_airport_flights(
        self, airport: str, direction: str, begin: int, end: int
    ) -> list[dict[str, Any]]:
        if direction not in {"arrival", "departure"}:
            raise ValueError("direction deve ser 'arrival' ou 'departure'.")
        payload = self._get(
            f"flights/{direction}",
            {"airport": airport.upper(), "begin": begin, "end": end},
            allow_not_found=True,
        )
        if not isinstance(payload, list):
            raise ApiError(f"Formato inesperado em flights/{direction}: esperado lista JSON.")
        return [item for item in payload if isinstance(item, dict)]
