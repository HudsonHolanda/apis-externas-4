from __future__ import annotations

import calendar
from datetime import date

import pandas as pd

from apis_externas_4.challenges.legislative_activity.domain.metrics import (
    HeatmapMetric,
    build_voting_metrics,
)


def run_voting_heatmap(
    repository,
    *,
    year: int,
    metric: HeatmapMetric = "volume",
    max_votations: int | None = None,
) -> tuple[pd.DataFrame, int, int]:
    if not 1900 <= year <= 2100:
        raise ValueError("Ano inválido.")
    sessions = repository.list_vote_sessions(year=year, max_items=max_votations)
    votes = [vote for session in sessions for vote in repository.list_votes(session)]

    member_rosters: dict[tuple[str, int], set[int]] = {}
    if metric == "rate":
        parties = repository.list_parties()
        observed_siglas = {vote.party_sigla for vote in votes if vote.party_sigla}
        relevant_parties = [party for party in parties if party.sigla.upper() in observed_siglas]
        active_months = sorted({session.date.month for session in sessions})
        for month in active_months:
            start = date(year, month, 1)
            last_day = calendar.monthrange(year, month)[1]
            end = date(year, month, last_day)
            for party in relevant_parties:
                members = repository.list_party_members(party.id, start, end)
                key = (party.sigla.upper(), month)
                member_rosters.setdefault(key, set()).update(members)

    data = build_voting_metrics(
        votes,
        sessions,
        year=year,
        metric=metric,
        member_rosters=member_rosters,
    )
    return data, len(sessions), len(votes)
