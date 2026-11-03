from datetime import date

from apis_externas_4.challenges.legislative_activity.domain.models import VoteSession
from apis_externas_4.challenges.legislative_activity.infrastructure.camara.mappers import (
    map_proposal_author,
    map_vote_record,
    map_vote_session,
)


def test_map_proposal_author_accepts_deputy_uri():
    author = {
        "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/123",
        "nome": "Maria Silva",
        "tipo": "Deputado Federal",
    }
    result = map_proposal_author(author)
    assert result.id == 123
    assert result.name == "Maria Silva"


def test_map_proposal_author_ignores_non_deputy():
    assert map_proposal_author({"nome": "Senado Federal", "tipo": "Órgão"}) is None


def test_map_vote_session_parses_date():
    session = map_vote_session({"id": "123-1", "data": "2025-03-12", "descricao": "Teste"})
    assert session.date == date(2025, 3, 12)


def test_map_vote_record_reads_nested_deputy_and_party():
    session = VoteSession(id="123-1", date=date(2025, 3, 12))
    vote = map_vote_record(
        {
            "tipoVoto": "Sim",
            "deputado_": {"id": 123, "nome": "Maria Silva", "siglaPartido": "abc"},
        },
        session,
    )
    assert vote is not None
    assert vote.deputy_id == 123
    assert vote.party_sigla == "ABC"
    assert vote.vote == "Sim"
