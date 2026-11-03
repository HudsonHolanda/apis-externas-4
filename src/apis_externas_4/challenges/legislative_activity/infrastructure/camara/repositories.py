from __future__ import annotations

from datetime import date

from apis_externas_4.challenges.legislative_activity.domain.models import (
    Deputy,
    Party,
    Proposal,
    Theme,
    VoteRecord,
    VoteSession,
)
from apis_externas_4.challenges.legislative_activity.infrastructure.camara import mappers
from apis_externas_4.challenges.legislative_activity.infrastructure.camara.client import (
    CamaraApiClient,
)


class CamaraRepository:
    """Concentra os endpoints da Câmara e entrega modelos normalizados à aplicação."""

    def __init__(self, client: CamaraApiClient) -> None:
        self.client = client

    def list_themes(self) -> list[Theme]:
        rows = self.client.get_paginated("referencias/proposicoes/codTema")
        return [mappers.map_theme(row) for row in rows]

    def list_proposals(
        self, *, theme_code: int, year: int, max_items: int | None = None
    ) -> list[Proposal]:
        rows = self.client.get_paginated(
            "proposicoes",
            {"codTema": theme_code, "ano": year, "ordenarPor": "id", "ordem": "ASC"},
            max_items=max_items,
        )
        return [mappers.map_proposal(row) for row in rows]

    def list_proposal_authors(self, proposal_id: int) -> list[Deputy]:
        rows = self.client.get_paginated(f"proposicoes/{proposal_id}/autores")
        authors: dict[int, Deputy] = {}
        for row in rows:
            deputy = mappers.map_proposal_author(row)
            if deputy is not None:
                authors[deputy.id] = deputy
        return list(authors.values())

    def list_vote_sessions(self, *, year: int, max_items: int | None = None) -> list[VoteSession]:
        rows = self.client.get_paginated(
            "votacoes",
            {"dataInicio": f"{year}-01-01", "dataFim": f"{year}-12-31"},
            max_items=max_items,
        )
        sessions = [mappers.map_vote_session(row) for row in rows]
        return [session for session in sessions if session.date.year == year]

    def list_votes(self, session: VoteSession) -> list[VoteRecord]:
        rows = self.client.get_paginated(f"votacoes/{session.id}/votos")
        records = [mappers.map_vote_record(row, session) for row in rows]
        return [record for record in records if record is not None]

    def list_parties(self) -> list[Party]:
        rows = self.client.get_paginated("partidos")
        return [mappers.map_party(row) for row in rows]

    def list_party_members(self, party_id: int, start: date, end: date) -> set[int]:
        rows = self.client.get_paginated(
            f"partidos/{party_id}/membros",
            {"dataInicio": start.isoformat(), "dataFim": end.isoformat()},
        )
        return {
            member_id
            for row in rows
            if (member_id := mappers.map_party_member_id(row)) is not None
        }
