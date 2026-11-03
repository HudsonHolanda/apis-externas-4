from __future__ import annotations

import unicodedata

import pandas as pd

from apis_externas_4.challenges.legislative_activity.domain.metrics import (
    build_proposal_ranking,
)
from apis_externas_4.challenges.legislative_activity.domain.models import Theme


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def resolve_theme(themes: list[Theme], query: str) -> Theme:
    """Resolve código, nome exato ou nome parcial não ambíguo."""
    query = query.strip()
    if not query:
        raise ValueError("Informe um tema.")
    if query.isdigit():
        code = int(query)
        for theme in themes:
            if theme.code == code:
                return theme
        raise ValueError(f"Não existe tema com código {code}.")

    normalized = _normalize(query)
    exact = [theme for theme in themes if _normalize(theme.name) == normalized]
    if len(exact) == 1:
        return exact[0]
    matches = [theme for theme in themes if normalized in _normalize(theme.name)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ValueError(f"Nenhum tema corresponde a '{query}'. Use o comando 'themes'.")
    names = ", ".join(f"{item.code}: {item.name}" for item in matches[:10])
    raise ValueError(f"Tema ambíguo: {names}. Informe o código ou um nome mais específico.")


def run_ranking(
    repository,
    *,
    theme_query: str,
    year: int,
    limit: int = 10,
    max_proposals: int | None = None,
) -> tuple[Theme, pd.DataFrame, int]:
    if not 1900 <= year <= 2100:
        raise ValueError("Ano inválido.")
    if limit < 1:
        raise ValueError("--limit precisa ser maior que zero.")
    themes = repository.list_themes()
    theme = resolve_theme(themes, theme_query)
    proposals = repository.list_proposals(
        theme_code=theme.code, year=year, max_items=max_proposals
    )
    authors_by_proposal = {
        proposal.id: repository.list_proposal_authors(proposal.id)
        for proposal in proposals
    }
    ranking = build_proposal_ranking(proposals, authors_by_proposal).head(limit)
    return theme, ranking, len(proposals)
