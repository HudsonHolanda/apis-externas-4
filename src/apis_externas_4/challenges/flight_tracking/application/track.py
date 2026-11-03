from __future__ import annotations

import time

from apis_externas_4.challenges.flight_tracking.domain.models import FlightTrack


def run_aircraft_track(
    repository,
    icao24: str,
    *,
    hours: float = 6,
    timestamp: int = 0,
    now: int | None = None,
) -> FlightTrack:
    if len(icao24) != 6 or any(char not in "0123456789abcdefABCDEF" for char in icao24):
        raise ValueError("ICAO24 deve conter exatamente 6 caracteres hexadecimais.")
    if hours <= 0:
        raise ValueError("hours precisa ser maior que zero.")
    if timestamp < 0:
        raise ValueError("timestamp não pode ser negativo.")
    track = repository.get_track(icao24.lower(), timestamp)
    if track is None or not track.path:
        raise ValueError("Nenhuma trajetória encontrada para essa aeronave e instante.")
    if timestamp == 0:
        cutoff = (now if now is not None else int(time.time())) - int(hours * 3600)
        last_seen = track.end_time or track.path[-1].timestamp
        if last_seen < cutoff:
            raise ValueError(f"A trajetória não possui atividade nas últimas {hours:g} hora(s).")
    # O mapa mantém todos os waypoints retornados para preservar o percurso completo do voo.
    return track
