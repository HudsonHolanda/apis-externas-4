from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class AsteroidApproach:
    asteroid_id: str
    name: str
    approach_date: datetime
    miss_distance_km: float
    relative_velocity_km_s: float
    diameter_min_km: float | None
    diameter_max_km: float | None
    potentially_hazardous: bool
    nasa_jpl_url: str | None


@dataclass(frozen=True, slots=True)
class Apod:
    date: str
    title: str
    explanation: str
    media_type: str
    image_url: str | None
    page_url: str | None
    credit: str | None = None


@dataclass(frozen=True, slots=True)
class NaturalEvent:
    event_id: str
    title: str
    description: str | None
    date: datetime
    category_names: tuple[str, ...]
    latitude: float
    longitude: float
    geometry_type: str
    geometry: dict[str, Any]
    url: str | None = None
