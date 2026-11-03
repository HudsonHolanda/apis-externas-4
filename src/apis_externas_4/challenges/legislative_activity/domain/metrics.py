from __future__ import annotations

import calendar
from collections import defaultdict
from typing import Literal

import pandas as pd

from apis_externas_4.challenges.legislative_activity.domain.models import (
    Deputy,
    Proposal,
    VoteRecord,
    VoteSession,
)

HeatmapMetric = Literal["volume", "rate"]


def build_proposal_ranking(
    proposals: list[Proposal], authors_by_proposal: dict[int, list[Deputy]]
) -> pd.DataFrame:
    """Conta uma proposição por deputado, deduplicando autores repetidos."""
    proposal_ids_by_deputy: dict[int, set[int]] = defaultdict(set)
    names_by_deputy: dict[int, str] = {}
    for proposal in proposals:
        for deputy in authors_by_proposal.get(proposal.id, []):
            proposal_ids_by_deputy[deputy.id].add(proposal.id)
            names_by_deputy[deputy.id] = deputy.name

    rows = [
        {
            "deputy_id": deputy_id,
            "deputy": names_by_deputy[deputy_id],
            "proposals": len(proposal_ids),
        }
        for deputy_id, proposal_ids in proposal_ids_by_deputy.items()
    ]
    frame = pd.DataFrame(rows, columns=["deputy_id", "deputy", "proposals"])
    if frame.empty:
        frame["position"] = pd.Series(dtype="int64")
        return frame[["position", "deputy_id", "deputy", "proposals"]]
    frame = frame.sort_values(
        ["proposals", "deputy"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    frame.insert(0, "position", range(1, len(frame) + 1))
    return frame


def build_voting_metrics(
    votes: list[VoteRecord],
    sessions: list[VoteSession],
    *,
    year: int,
    metric: HeatmapMetric,
    member_rosters: dict[tuple[str, int], set[int]] | None = None,
) -> pd.DataFrame:
    """Cria dados longos por partido/mês para volume ou cobertura mensal de membros."""
    if metric not in ("volume", "rate"):
        raise ValueError("Métrica inválida. Use 'volume' ou 'rate'.")

    month_sessions = {session.date.month for session in sessions if session.date.year == year}
    volume: dict[tuple[str, int], int] = defaultdict(int)
    deputies: dict[tuple[str, int], set[int]] = defaultdict(set)
    for vote in votes:
        if vote.date.year != year or not vote.party_sigla:
            continue
        key = (vote.party_sigla.upper(), vote.date.month)
        volume[key] += 1
        deputies[key].add(vote.deputy_id)

    rows: list[dict] = []
    if metric == "volume":
        for (party, month), count in sorted(volume.items()):
            rows.append(
                {"party": party, "month": month, "value": count, "volume": count}
            )
    else:
        rosters = member_rosters or {}
        observed_parties = {party for party, _ in volume}
        for (party, month), members in sorted(rosters.items()):
            if month not in month_sessions or party not in observed_parties:
                continue
            member_count = len(members)
            if member_count == 0:
                rate = float("nan")
                participating = 0
            else:
                participating = len(deputies.get((party, month), set()) & members)
                rate = participating / member_count * 100
            rows.append(
                {
                    "party": party,
                    "month": month,
                    "value": rate,
                    "volume": volume.get((party, month), 0),
                    "members": member_count,
                    "members_with_recorded_vote": participating,
                }
            )

    frame = pd.DataFrame(rows)
    if frame.empty:
        columns = ["party", "month", "value", "volume"]
        if metric == "rate":
            columns += ["members", "members_with_recorded_vote"]
        return pd.DataFrame(columns=columns)
    frame["month_name"] = frame["month"].map(lambda number: calendar.month_abbr[number])
    return frame.sort_values(["party", "month"]).reset_index(drop=True)
