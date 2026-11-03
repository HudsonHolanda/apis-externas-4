from __future__ import annotations

from pathlib import Path

from apis_externas_4.challenges.legislative_activity.application.ranking import run_ranking
from apis_externas_4.challenges.legislative_activity.application.voting_heatmap import (
    run_voting_heatmap,
)
from apis_externas_4.challenges.legislative_activity.infrastructure.camara.client import (
    CamaraApiClient,
)
from apis_externas_4.challenges.legislative_activity.infrastructure.camara.repositories import (
    CamaraRepository,
)
from apis_externas_4.challenges.legislative_activity.presentation.charts import (
    create_ranking_chart,
    create_voting_heatmap,
)
from apis_externas_4.challenges.legislative_activity.presentation.tables import (
    format_heatmap_summary,
    format_ranking_table,
)


def _repository(timeout: float, page_size: int) -> CamaraRepository:
    return CamaraRepository(CamaraApiClient(timeout=timeout, page_size=page_size))


def command_themes(args) -> int:
    repository = _repository(args.timeout, args.page_size)
    themes = repository.list_themes()
    for theme in sorted(themes, key=lambda item: item.name.casefold()):
        print(f"{theme.code:>4}  {theme.name}")
    print(f"\nTotal: {len(themes)} temas")
    return 0


def command_ranking(args) -> int:
    repository = _repository(args.timeout, args.page_size)
    theme, ranking, total = run_ranking(
        repository,
        theme_query=args.theme,
        year=args.year,
        limit=args.limit,
        max_proposals=args.max_proposals,
    )
    print(f"\nAtividade legislativa — {theme.name} ({args.year})")
    print(format_ranking_table(ranking))
    print(f"\nProposições consultadas: {total}")
    if args.max_proposals is not None:
        print("AVISO: resultado limitado por --max-proposals; não representa o universo completo.")
    if not ranking.empty:
        output = Path(args.output_dir) / f"ranking-{args.year}-{theme.code}.html"
        create_ranking_chart(ranking, output, title=f"Proposições por deputado — {theme.name} ({args.year})")
        print(f"Gráfico salvo em: {output}")
    return 0


def command_voting_heatmap(args) -> int:
    repository = _repository(args.timeout, args.page_size)
    frame, sessions_count, votes_count = run_voting_heatmap(
        repository,
        year=args.year,
        metric=args.metric,
        max_votations=args.max_votations,
    )
    print(f"\nAtividade de votação — Câmara dos Deputados ({args.year})")
    print(f"Votações consultadas: {sessions_count}")
    print(f"Registros individuais de voto: {votes_count}")
    print(format_heatmap_summary(frame, args.metric))
    if args.max_votations is not None:
        print("AVISO: resultado limitado por --max-votations; não representa o universo completo.")
    if not frame.empty:
        output = Path(args.output_dir) / f"voting-heatmap-{args.year}-{args.metric}.html"
        create_voting_heatmap(frame, output, year=args.year, metric=args.metric)
        print(f"Heatmap salvo em: {output}")
    if args.metric == "rate":
        print(
            "\nNota: a taxa representa membros do partido com ao menos um voto registrado no mês. "
            "Não equivale à presença em cada votação."
        )
    return 0
