from __future__ import annotations

import argparse
import sys

from apis_externas_4.challenges.flight_tracking.commands import (
    command_airport_flights,
    command_brazil_map,
    command_track,
)
from apis_externas_4.challenges.space_exploration.commands import (
    command_apod,
    command_asteroids,
    command_space_dashboard,
)
from apis_externas_4.challenges.legislative_activity.commands import (
    command_ranking,
    command_themes,
    command_voting_heatmap,
)
from apis_externas_4.shared.exceptions import OpenDataError


def _add_connection_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="Timeout HTTP em segundos (padrão: 30)."
    )
    parser.add_argument(
        "--page-size", type=int, default=100, help="Itens por página, de 1 a 100 (padrão: 100)."
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="open-data-challenges",
        description="Suíte CLI modular para explorar conjuntos de dados públicos.",
    )
    challenge_parsers = parser.add_subparsers(dest="challenge", required=True)

    legislative = challenge_parsers.add_parser(
        "legislative", help="Desafio de atividade legislativa da Câmara dos Deputados."
    )
    commands = legislative.add_subparsers(dest="command", required=True)

    themes = commands.add_parser("themes", help="Lista os temas oficiais de proposições.")
    _add_connection_options(themes)
    themes.set_defaults(handler=command_themes)

    ranking = commands.add_parser("ranking", help="Ranking de deputados por tema e ano.")
    ranking.add_argument("--theme", required=True, help="Nome ou código do tema (ex.: saúde).")
    ranking.add_argument("--year", required=True, type=int, help="Ano de apresentação das proposições.")
    ranking.add_argument("--limit", type=int, default=10, help="Quantidade de deputados exibidos (padrão: 10).")
    ranking.add_argument(
        "--max-proposals",
        type=int,
        help="Limita proposições para execução exploratória; torna o resultado parcial.",
    )
    ranking.add_argument("--output-dir", default="artifacts", help="Diretório dos gráficos HTML.")
    _add_connection_options(ranking)
    ranking.set_defaults(handler=command_ranking)

    heatmap = commands.add_parser(
        "voting-heatmap", help="Heatmap mensal de votos registrados por partido."
    )
    heatmap.add_argument("--year", required=True, type=int, help="Ano das votações.")
    heatmap.add_argument(
        "--metric",
        choices=("volume", "rate"),
        default="volume",
        help="volume: quantidade de votos registrados; rate: cobertura mensal de membros.",
    )
    heatmap.add_argument(
        "--max-votations",
        type=int,
        help="Limita votações para execução exploratória; torna o resultado parcial.",
    )
    heatmap.add_argument("--output-dir", default="artifacts", help="Diretório dos gráficos HTML.")
    _add_connection_options(heatmap)
    heatmap.set_defaults(handler=command_voting_heatmap)

    flights = challenge_parsers.add_parser(
        "flights", help="Rastreamento de aeronaves com dados OpenSky Network."
    )
    flight_commands = flights.add_subparsers(dest="command", required=True)

    brazil_map = flight_commands.add_parser(
        "brazil-map", help="Gera mapa de aeronaves sobre a bounding box do Brasil."
    )
    brazil_map.add_argument(
        "--category",
        choices=("all", "rotorcraft", "commercial"),
        default="all",
        help="Categoria ADS-B; commercial é uma aproximação por porte da aeronave.",
    )
    brazil_map.add_argument("--output", default="artifacts/flights-brazil.html")
    brazil_map.add_argument("--timeout", type=float, default=30.0)
    brazil_map.set_defaults(handler=command_brazil_map)

    track = flight_commands.add_parser(
        "track", help="Gera mapa da trajetória de uma aeronave identificada por ICAO24."
    )
    track.add_argument(
        "--icao24", required=True, help="Endereço transponder ICAO24 de 6 dígitos hexadecimais."
    )
    track.add_argument(
        "--hours", type=float, default=6,
        help="Recência mínima do track ao vivo em horas (padrão: 6).",
    )
    track.add_argument(
        "--timestamp", type=int, default=0,
        help="Instante Unix dentro de um voo conhecido; 0 solicita o track ao vivo.",
    )
    track.add_argument("--output", default="artifacts/flight-track.html")
    track.add_argument("--timeout", type=float, default=30.0)
    track.set_defaults(handler=command_track)

    airport = flight_commands.add_parser(
        "airport-flights", help="Consulta chegadas ou partidas registradas para um aeroporto."
    )
    airport.add_argument("--airport", required=True, help="Código ICAO do aeroporto (ex.: SBGR).")
    airport.add_argument("--direction", choices=("arrivals", "departures"), required=True)
    airport.add_argument(
        "--hours", type=float, default=24, help="Janela de consulta, entre 0 e 48 horas."
    )
    airport.add_argument("--timeout", type=float, default=30.0)
    airport.set_defaults(handler=command_airport_flights)

    space = challenge_parsers.add_parser(
        "space", help="Exploração espacial com APIs NASA e NASA Exoplanet Archive."
    )
    space_commands = space.add_subparsers(dest="command", required=True)

    asteroids = space_commands.add_parser(
        "asteroids", help="Gráfico de distância e velocidade de asteroides próximos da Terra."
    )
    asteroids.add_argument("--start-date", required=True, help="Data inicial (YYYY-MM-DD).")
    asteroids.add_argument("--end-date", required=True, help="Data final (YYYY-MM-DD).")
    asteroids.add_argument("--output", default="artifacts/asteroid-approaches.html")
    asteroids.add_argument("--timeout", type=float, default=45.0)
    asteroids.set_defaults(handler=command_asteroids)

    dashboard = space_commands.add_parser(
        "dashboard", help="Gera dashboard HTML com APOD, exoplanetas e eventos EONET."
    )
    dashboard.add_argument("--apod-date", help="Data APOD (YYYY-MM-DD); padrão: data UTC atual.")
    dashboard.add_argument("--output", default="artifacts/space-dashboard.html")
    dashboard.add_argument("--timeout", type=float, default=45.0)
    dashboard.set_defaults(handler=command_space_dashboard)

    apod = space_commands.add_parser("apod", help="Consulta o Astronomy Picture of the Day.")
    apod.add_argument("--date", required=True, help="Data APOD (YYYY-MM-DD).")
    apod.add_argument("--timeout", type=float, default=45.0)
    apod.set_defaults(handler=command_apod)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (OpenDataError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Operação interrompida.", file=sys.stderr)
        return 130
