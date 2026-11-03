class OpenDataError(Exception):
    """Erro conhecido que pode ser apresentado de forma amigável na CLI."""


class ApiError(OpenDataError):
    """Falha ao consultar ou interpretar a API externa."""


class NotFoundError(OpenDataError):
    """Recurso não encontrado na fonte externa."""
