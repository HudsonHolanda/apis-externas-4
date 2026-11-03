from datetime import date

from apis_externas_4.challenges.legislative_activity.infrastructure.camara.repositories import (
    CamaraRepository,
)


class FakeClient:
    def get_paginated(self, path, params=None, **kwargs):
        if path == "referencias/proposicoes/codTema":
            return [{"cod": 1, "nome": "Saúde"}]
        if path == "proposicoes":
            assert params["codTema"] == 1
            assert params["ano"] == 2025
            return [{"id": 10, "siglaTipo": "PL", "numero": 2, "ano": 2025}]
        if path == "partidos/7/membros":
            assert params == {"dataInicio": "2025-01-01", "dataFim": "2025-01-31"}
            return [{"id": 100}, {"id": 101}]
        return []


def test_repository_maps_themes_and_proposals():
    repository = CamaraRepository(FakeClient())
    assert repository.list_themes()[0].name == "Saúde"
    proposals = repository.list_proposals(theme_code=1, year=2025)
    assert proposals[0].id == 10


def test_repository_reads_historical_party_members():
    repository = CamaraRepository(FakeClient())
    members = repository.list_party_members(7, date(2025, 1, 1), date(2025, 1, 31))
    assert members == {100, 101}
