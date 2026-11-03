from apis_externas_4.shared.http import JsonApiClient


class CamaraApiClient(JsonApiClient):
    """Cliente específico da API REST de Dados Abertos da Câmara."""

    def __init__(self, *, timeout: float = 30.0, page_size: int = 100) -> None:
        super().__init__(
            "https://dadosabertos.camara.leg.br/api/v2/",
            timeout=timeout,
            page_size=page_size,
        )
