from datetime import date

from apis_externas_4.challenges.legislative_activity.domain.metrics import (
    build_proposal_ranking,
    build_voting_metrics,
)
from apis_externas_4.challenges.legislative_activity.domain.models import (
    Deputy,
    Proposal,
    VoteRecord,
    VoteSession,
)


def test_ranking_counts_coauthors_and_deduplicates_same_deputy():
    proposals = [
        Proposal(id=1, type="PL", number=10, year=2025),
        Proposal(id=2, type="PL", number=11, year=2025),
    ]
    authors = {
        1: [Deputy(1, "Ana"), Deputy(2, "Bruno"), Deputy(1, "Ana")],
        2: [Deputy(1, "Ana")],
    }
    result = build_proposal_ranking(proposals, authors)
    assert result.iloc[0]["deputy"] == "Ana"
    assert result.iloc[0]["proposals"] == 2
    assert result.iloc[1]["proposals"] == 1


def test_ranking_returns_empty_frame_with_expected_columns():
    result = build_proposal_ranking([], {})
    assert result.empty
    assert list(result.columns) == ["position", "deputy_id", "deputy", "proposals"]


def test_voting_volume_groups_by_party_and_month():
    session = VoteSession("1", date(2025, 1, 4))
    votes = [
        VoteRecord("1", session.date, 10, "A", "ABC", "Sim"),
        VoteRecord("1", session.date, 11, "B", "ABC", "Não"),
        VoteRecord("1", session.date, 12, "C", "XYZ", "Sim"),
    ]
    result = build_voting_metrics(votes, [session], year=2025, metric="volume")
    counts = dict(zip(result["party"], result["value"], strict=True))
    assert counts == {"ABC": 2, "XYZ": 1}


def test_voting_rate_is_monthly_member_coverage():
    session = VoteSession("1", date(2025, 1, 4))
    votes = [
        VoteRecord("1", session.date, 10, "A", "ABC", "Sim"),
        VoteRecord("1", session.date, 11, "B", "ABC", "Não"),
    ]
    rosters = {("ABC", 1): {10, 11, 12, 13}}
    result = build_voting_metrics(
        votes, [session], year=2025, metric="rate", member_rosters=rosters
    )
    assert result.iloc[0]["value"] == 50.0
    assert result.iloc[0]["members_with_recorded_vote"] == 2


def test_voting_metrics_ignore_records_outside_requested_year():
    session = VoteSession("1", date(2025, 1, 4))
    vote = VoteRecord("1", date(2024, 1, 4), 10, "A", "ABC", "Sim")
    result = build_voting_metrics([vote], [session], year=2025, metric="volume")
    assert result.empty
