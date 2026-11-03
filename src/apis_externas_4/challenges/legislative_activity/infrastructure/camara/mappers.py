from __future__ import annotations

import re
from datetime import date
from urllib.parse import urlparse

from apis_externas_4.challenges.legislative_activity.domain.models import (
    Deputy,
    Party,
    Proposal,
    Theme,
    VoteRecord,
    VoteSession,
)


def _as_int(value: object) -> int | None:
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _id_from_uri(uri: object) -> int | None:
    if not isinstance(uri, str) or not uri:
        return None
    path = urlparse(uri).path.rstrip("/")
    match = re.search(r"/(?:deputados|partidos)/(\d+)$", path)
    if match:
        return int(match.group(1))
    return None


def map_theme(raw: dict) -> Theme:
    code = _as_int(raw.get("cod", raw.get("id")))
    name = raw.get("nome") or raw.get("descricao")
    if code is None or not name:
        raise ValueError(f"Tema sem código ou nome: {raw!r}")
    return Theme(code=code, name=str(name))


def map_proposal(raw: dict) -> Proposal:
    proposal_id = _as_int(raw.get("id"))
    year = _as_int(raw.get("ano"))
    if proposal_id is None or year is None:
        raise ValueError(f"Proposição sem identificador ou ano: {raw!r}")
    return Proposal(
        id=proposal_id,
        type=str(raw.get("siglaTipo") or raw.get("codTipo") or ""),
        number=_as_int(raw.get("numero")),
        year=year,
        summary=str(raw.get("ementa") or ""),
    )


def map_proposal_author(raw: dict) -> Deputy | None:
    uri = raw.get("uri") or raw.get("uriAutor")
    deputy_id = _id_from_uri(uri)
    author_type = str(raw.get("tipo") or raw.get("tipoAutor") or "").casefold()
    if deputy_id is None and "deputad" in author_type:
        deputy_id = _as_int(raw.get("id"))
    if deputy_id is None:
        return None
    name = raw.get("nome") or raw.get("nomeAutor") or f"Deputado {deputy_id}"
    return Deputy(id=deputy_id, name=str(name))


def map_vote_session(raw: dict) -> VoteSession:
    session_id = raw.get("id")
    raw_date = raw.get("data") or raw.get("dataHoraRegistro")
    if not session_id or not raw_date:
        raise ValueError(f"Votação sem identificador ou data: {raw!r}")
    try:
        parsed_date = date.fromisoformat(str(raw_date)[:10])
    except ValueError as exc:
        raise ValueError(f"Data inválida na votação {session_id}: {raw_date}") from exc
    return VoteSession(
        id=str(session_id),
        date=parsed_date,
        description=str(raw.get("descricao") or ""),
    )


def map_vote_record(raw: dict, session: VoteSession) -> VoteRecord | None:
    deputy = raw.get("deputado_") or raw.get("deputado") or {}
    if not isinstance(deputy, dict):
        deputy = {}
    deputy_id = _as_int(deputy.get("id")) or _id_from_uri(deputy.get("uri"))
    if deputy_id is None:
        return None
    party = deputy.get("siglaPartido") or raw.get("siglaPartido")
    vote_value = raw.get("tipoVoto") or raw.get("voto") or "Não informado"
    return VoteRecord(
        session_id=session.id,
        date=session.date,
        deputy_id=deputy_id,
        deputy_name=str(deputy.get("nome") or f"Deputado {deputy_id}"),
        party_sigla=str(party).strip().upper() if party else None,
        vote=str(vote_value),
    )


def map_party(raw: dict) -> Party:
    party_id = _as_int(raw.get("id"))
    if party_id is None:
        raise ValueError(f"Partido sem identificador: {raw!r}")
    return Party(
        id=party_id,
        name=str(raw.get("nome") or raw.get("sigla") or f"Partido {party_id}"),
        sigla=str(raw.get("sigla") or raw.get("nome") or f"PARTIDO-{party_id}").upper(),
    )


def map_party_member_id(raw: dict) -> int | None:
    member_id = _as_int(raw.get("id")) or _id_from_uri(raw.get("uri"))
    return member_id
