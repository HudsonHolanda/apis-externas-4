from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pandas as pd

from apis_externas_4.challenges.space_exploration.domain.models import Apod, NaturalEvent


def split_date_range(start_date: str, end_date: str, *, max_days: int = 7) -> list[tuple[str, str]]:
    """Divide intervalo inclusivo em chamadas NeoWs de no máximo max_days dias."""
    if max_days < 1 or max_days > 7:
        raise ValueError("max_days precisa estar entre 1 e 7 para respeitar o limite NeoWs.")
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Datas devem utilizar o formato YYYY-MM-DD.") from exc
    if start > end:
        raise ValueError("A data inicial não pode ser posterior à data final.")

    chunks = []
    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=max_days - 1), end)
        chunks.append((current.isoformat(), chunk_end.isoformat()))
        current = chunk_end + timedelta(days=1)
    return chunks


def map_neo_feeds(payloads: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for payload in payloads:
        grouped = payload.get("near_earth_objects", {})
        if not isinstance(grouped, dict):
            continue
        for asteroids in grouped.values():
            if not isinstance(asteroids, list):
                continue
            for asteroid in asteroids:
                if not isinstance(asteroid, dict):
                    continue
                diameter = (asteroid.get("estimated_diameter") or {}).get("kilometers") or {}
                for approach in asteroid.get("close_approach_data") or []:
                    if not isinstance(approach, dict):
                        continue
                    try:
                        raw_date = approach.get("close_approach_date_full") or approach["close_approach_date"]
                        try:
                            approach_date = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
                        except ValueError:
                            # NeoWs usa, em alguns registros, o formato "YYYY-Mon-DD HH:MM".
                            approach_date = datetime.strptime(str(raw_date), "%Y-%b-%d %H:%M")
                        if approach_date.tzinfo is None:
                            approach_date = approach_date.replace(tzinfo=UTC)
                        distance = float((approach.get("miss_distance") or {})["kilometers"])
                        velocity_kmh = float(
                            (approach.get("relative_velocity") or {})["kilometers_per_hour"]
                        )
                    except (KeyError, TypeError, ValueError):
                        continue
                    rows.append(
                        {
                            "asteroid_id": str(asteroid.get("id", "")),
                            "name": str(asteroid.get("name", "Unknown")),
                            "approach_date": approach_date,
                            "miss_distance_km": distance,
                            "relative_velocity_km_s": velocity_kmh / 3600.0,
                            "diameter_min_km": _to_float(diameter.get("estimated_diameter_min")),
                            "diameter_max_km": _to_float(diameter.get("estimated_diameter_max")),
                            "potentially_hazardous": bool(
                                asteroid.get("is_potentially_hazardous_asteroid", False)
                            ),
                            "nasa_jpl_url": asteroid.get("nasa_jpl_url"),
                        }
                    )
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.drop_duplicates(subset=["asteroid_id", "approach_date"])
        frame = frame.sort_values("approach_date").reset_index(drop=True)
    return frame


def _to_float(value: Any) -> float | None:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def map_apod(payload: dict[str, Any]) -> Apod:
    media_type = str(payload.get("media_type", "image"))
    # No endpoint WordPress atual, url/permalink apontam para a página; hdurl é o arquivo de mídia.
    image_url = payload.get("hdurl") if media_type == "image" else None
    return Apod(
        date=str(payload.get("date", "")),
        title=str(payload.get("title", "Sem título")),
        explanation=str(payload.get("explanation", "")),
        media_type=media_type,
        image_url=image_url,
        page_url=payload.get("permalink") or payload.get("url"),
        credit=payload.get("credit") or payload.get("copyright"),
    )


def map_exoplanet_methods(payload: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for item in payload:
        method = item.get("discoverymethod")
        total = _to_float(item.get("total"))
        if method and total is not None:
            rows.append({"discovery_method": str(method), "total": int(total)})
    frame = pd.DataFrame(rows, columns=["discovery_method", "total"])
    if not frame.empty:
        frame = frame.sort_values("total", ascending=False).reset_index(drop=True)
    return frame


def _representative_coordinate(geometry: dict[str, Any]) -> tuple[float, float] | None:
    kind = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if kind == "Point" and isinstance(coordinates, list) and len(coordinates) >= 2:
        try:
            return float(coordinates[1]), float(coordinates[0])
        except (TypeError, ValueError):
            return None

    points: list[list[Any]] = []
    if kind == "LineString" and isinstance(coordinates, list):
        points = coordinates
    elif kind == "Polygon" and isinstance(coordinates, list) and coordinates:
        points = coordinates[0]
    elif kind == "MultiPoint" and isinstance(coordinates, list):
        points = coordinates
    elif kind == "MultiPolygon" and isinstance(coordinates, list):
        points = [ring[0] for polygon in coordinates if polygon for ring in polygon if ring]
    valid = []
    for point in points:
        if not isinstance(point, list) or len(point) < 2:
            continue
        try:
            valid.append((float(point[1]), float(point[0])))
        except (TypeError, ValueError):
            continue
    if not valid:
        return None
    return sum(item[0] for item in valid) / len(valid), sum(item[1] for item in valid) / len(valid)


def map_eonet_events(
    payload: dict[str, Any], *, now: datetime | None = None, hours: int = 48
) -> list[NaturalEvent]:
    if hours <= 0:
        raise ValueError("hours precisa ser maior que zero.")
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    cutoff = current - timedelta(hours=hours)
    events: list[NaturalEvent] = []
    for event in payload.get("events") or []:
        if not isinstance(event, dict):
            continue
        candidates = []
        for geometry in event.get("geometry") or []:
            if not isinstance(geometry, dict):
                continue
            try:
                event_date = datetime.fromisoformat(str(geometry.get("date", "")).replace("Z", "+00:00"))
                if event_date.tzinfo is None:
                    event_date = event_date.replace(tzinfo=UTC)
            except ValueError:
                continue
            if event_date >= cutoff:
                coordinate = _representative_coordinate(geometry)
                if coordinate:
                    candidates.append((event_date, geometry, coordinate))
        if not candidates:
            continue
        event_date, geometry, (latitude, longitude) = max(candidates, key=lambda item: item[0])
        categories = tuple(
            str(category.get("title"))
            for category in event.get("categories", [])
            if isinstance(category, dict) and category.get("title")
        )
        events.append(
            NaturalEvent(
                event_id=str(event.get("id", "")),
                title=str(event.get("title", "Evento natural")),
                description=event.get("description"),
                date=event_date,
                category_names=categories,
                latitude=latitude,
                longitude=longitude,
                geometry_type=str(geometry.get("type", "Point")),
                geometry=geometry,
                url=event.get("link"),
            )
        )
    return sorted(events, key=lambda item: item.date, reverse=True)
