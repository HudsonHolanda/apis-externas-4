from __future__ import annotations

import os
import time
from pathlib import Path

from apis_externas_4.challenges.flight_tracking.application.aircraft import (
    run_brazil_aircraft_map,
)
from apis_externas_4.challenges.flight_tracking.application.track import run_aircraft_track
from apis_externas_4.challenges.flight_tracking.infrastructure.opensky.client import (
    OpenSkyApiClient,
)
from apis_externas_4.challenges.flight_tracking.infrastructure.opensky.repositories import (
    OpenSkyRepository,
)
from apis_externas_4.challenges.flight_tracking.presentation.maps import (
    create_brazil_aircraft_map,
    create_track_map,
)
from apis_externas_4.challenges.flight_tracking.presentation.tables import (
    format_airport_flights,
)


def _repository(timeout: float) -> OpenSkyRepository:
    return OpenSkyRepository(
        OpenSkyApiClient(
            timeout=timeout,
            client_id=os.getenv("OPENSKY_CLIENT_ID"),
            client_secret=os.getenv("OPENSKY_CLIENT_SECRET"),
        )
    )


def command_brazil_map(args) -> int:
    repository = _repository(args.timeout)
    aircraft = run_brazil_aircraft_map(repository, args.category)
    output = Path(args.output)
    create_brazil_aircraft_map(aircraft, output, category=args.category)
    print(f"Aeronaves encontradas: {len(aircraft)}")
    print(f"Categoria: {args.category}")
    print(f"Mapa salvo em: {output}")
    if args.category == "commercial":
        print(
            "Nota: 'commercial' é uma aproximação baseada nas categorias ADS-B de aeronaves "
            "grandes/pesadas; não identifica com certeza a operação comercial."
        )
    return 0


def command_track(args) -> int:
    repository = _repository(args.timeout)
    track = run_aircraft_track(
        repository,
        args.icao24,
        hours=args.hours,
        timestamp=args.timestamp,
    )
    output = Path(args.output)
    create_track_map(track, output)
    print(f"Aeronave: {track.icao24}")
    print(f"Indicativo: {track.callsign or 'não informado'}")
    print(f"Pontos da trajetória: {len(track.path)}")
    print(f"Mapa salvo em: {output}")
    if args.timestamp == 0:
        print(f"Trajetória ao vivo; valida atividade dentro das últimas {args.hours:g} hora(s) e mantém o percurso completo.")
    else:
        print("Trajetória consultada no instante Unix informado.")
    print("Nota: o endpoint de trajetórias é experimental e o acesso histórico é limitado a 30 dias.")
    return 0


def command_airport_flights(args) -> int:
    if not 0 < args.hours <= 48:
        raise ValueError("--hours deve estar entre 0 e 48 para consultas por aeroporto.")
    repository = _repository(args.timeout)
    end = int(time.time())
    begin = end - int(args.hours * 3600)
    direction = "arrival" if args.direction == "arrivals" else "departure"
    flights = repository.list_airport_flights(args.airport, direction, begin, end)
    print(f"{args.direction.title()} em {args.airport.upper()} — últimos {args.hours:g} hora(s)")
    print(format_airport_flights(flights))
    print(
        "Nota: os endpoints de chegadas/partidas são atualizados em lote durante a noite; "
        "os dados mais recentes podem ainda não estar disponíveis."
    )
    return 0
