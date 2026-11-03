from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Theme:
    code: int
    name: str


@dataclass(frozen=True)
class Deputy:
    id: int
    name: str


@dataclass(frozen=True)
class Proposal:
    id: int
    type: str
    number: int | None
    year: int
    summary: str = ""


@dataclass(frozen=True)
class VoteSession:
    id: str
    date: date
    description: str = ""


@dataclass(frozen=True)
class VoteRecord:
    session_id: str
    date: date
    deputy_id: int
    deputy_name: str
    party_sigla: str | None
    vote: str


@dataclass(frozen=True)
class Party:
    id: int
    name: str
    sigla: str
