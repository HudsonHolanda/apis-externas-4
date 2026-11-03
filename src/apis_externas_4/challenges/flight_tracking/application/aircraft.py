from __future__ import annotations

from collections.abc import Iterable

from apis_externas_4.challenges.flight_tracking.domain.models import AircraftPosition


COMMERCIAL_LIKE_CATEGORIES = {4, 5, 6}


def filter_aircraft(
    aircraft: Iterable[AircraftPosition], category: str = "all"
) -> list[AircraftPosition]:
    """Filtra categorias ADS-B; commercial é apenas uma aproximação por porte."""
    category = category.casefold()
    if category not in {"all", "rotorcraft", "commercial"}:
        raise ValueError("Categoria deve ser all, rotorcraft ou commercial.")
    # Vetores explicitamente marcados como em solo não representam aeronaves em voo.
    # Estados sem informação sobre on_ground são mantidos, pois não provam que a aeronave
    # esteja em solo.
    items = [item for item in aircraft if item.on_ground is not True]
    if category == "rotorcraft":
        return [item for item in items if item.category == 8]
    if category == "commercial":
        return [item for item in items if item.category in COMMERCIAL_LIKE_CATEGORIES]
    return items


def run_brazil_aircraft_map(repository, category: str = "all") -> list[AircraftPosition]:
    return filter_aircraft(repository.list_aircraft_over_brazil(), category)
