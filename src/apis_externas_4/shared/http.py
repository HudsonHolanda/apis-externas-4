from __future__ import annotations

from typing import Any

import requests

from apis_externas_4.shared.exceptions import ApiError, NotFoundError


class JsonApiClient:
    """Cliente HTTP JSON simples, com timeout e paginação padronizada."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 30.0,
        page_size: int = 100,
        session: requests.Session | None = None,
    ) -> None:
        if not 1 <= page_size <= 100:
            raise ValueError("page_size precisa estar entre 1 e 100.")
        if timeout <= 0:
            raise ValueError("timeout precisa ser maior que zero.")
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.page_size = page_size
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "open-data-challenges/0.1.0",
            }
        )

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = self.base_url + path.lstrip("/")
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise ApiError(f"Falha de comunicação com a API: {exc}") from exc

        if response.status_code == 404:
            raise NotFoundError(f"Recurso não encontrado: {path}")
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            detail = ""
            try:
                payload = response.json()
                errors = payload.get("erros", []) if isinstance(payload, dict) else []
                if errors:
                    detail = "; ".join(str(item.get("mensagem", item)) for item in errors)
            except ValueError:
                detail = response.text[:300]
            message = f"HTTP {response.status_code} ao consultar {path}"
            if detail:
                message += f": {detail}"
            raise ApiError(message) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise ApiError(f"A API retornou JSON inválido para {path}.") from exc
        if not isinstance(payload, dict):
            raise ApiError(f"Formato inesperado na resposta de {path}: esperado objeto JSON.")
        return payload

    def get_paginated(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        max_items: int | None = None,
    ) -> list[dict[str, Any]]:
        """Busca todas as páginas; max_items é útil para execuções exploratórias."""
        if max_items is not None and max_items < 1:
            raise ValueError("max_items precisa ser maior que zero.")
        collected: list[dict[str, Any]] = []
        page = 1
        while True:
            query = dict(params or {})
            query.update({"pagina": page, "itens": self.page_size})
            payload = self.get(path, query)
            data = payload.get("dados")
            if not isinstance(data, list):
                raise ApiError(f"Formato inesperado em {path}: campo 'dados' não é uma lista.")

            if max_items is not None:
                remaining = max_items - len(collected)
                if remaining <= 0:
                    break
                data = data[:remaining]

            collected.extend(item for item in data if isinstance(item, dict))
            if not data or len(data) < self.page_size:
                break
            if max_items is not None and len(collected) >= max_items:
                break
            page += 1
        return collected
