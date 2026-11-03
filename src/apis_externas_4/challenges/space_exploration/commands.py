from __future__ import annotations

import os
from pathlib import Path

from apis_externas_4.challenges.space_exploration.application.asteroids import (
    run_asteroid_analysis,
)
from apis_externas_4.challenges.space_exploration.application.dashboard import (
    run_space_dashboard,
)
from apis_externas_4.challenges.space_exploration.infrastructure.nasa.client import NASAApiClient
from apis_externas_4.challenges.space_exploration.infrastructure.nasa.repositories import (
    NASARepository,
)
from apis_externas_4.challenges.space_exploration.presentation.charts import (
    create_asteroid_scatter,
)


def _repository(timeout: float) -> NASARepository:
    return NASARepository(
        NASAApiClient(api_key=os.getenv("NASA_API_KEY"), timeout=timeout)
    )


def command_asteroids(args) -> int:
    repository = _repository(args.timeout)
    frame = run_asteroid_analysis(repository, args.start_date, args.end_date)
    print(f"Aproximações encontradas: {len(frame)}")
    if frame.empty:
        print("Nenhum dado disponível para o intervalo informado.")
        return 0
    print(
        frame[["name", "approach_date", "miss_distance_km", "relative_velocity_km_s"]]
        .to_string(index=False)
    )
    output = Path(args.output)
    create_asteroid_scatter(frame, output, start_date=args.start_date, end_date=args.end_date)
    print(f"Gráfico salvo em: {output}")
    return 0


def command_space_dashboard(args) -> int:
    repository = _repository(args.timeout)
    output = Path(args.output)
    run_space_dashboard(repository, output, args.apod_date)
    print(f"Dashboard salvo em: {output}")
    print("Abre o arquivo HTML em um navegador para navegar pelas abas.")
    if os.getenv("NASA_API_KEY") is None:
        print("Aviso: usando DEMO_KEY da NASA, sujeito a limites menores de requisições.")
    return 0


def command_apod(args) -> int:
    repository = _repository(args.timeout)
    apod = repository.get_apod(args.date)
    print(f"{apod.date} — {apod.title}")
    print(apod.explanation)
    print(f"Mídia: {apod.page_url or apod.image_url or 'não disponível'}")
    return 0
