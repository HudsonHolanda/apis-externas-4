from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px


def create_ranking_chart(frame: pd.DataFrame, output_path: Path, *, title: str) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if frame.empty:
        raise ValueError("Não é possível gerar um gráfico sem resultados.")
    chart = px.bar(
        frame.sort_values("proposals"),
        x="proposals",
        y="deputy",
        orientation="h",
        text="proposals",
        title=title,
        labels={"proposals": "Proposições", "deputy": "Deputado"},
    )
    chart.update_layout(yaxis={"categoryorder": "total ascending"})
    chart.write_html(output_path, include_plotlyjs=True, auto_open=False)
    return output_path


def create_voting_heatmap(
    frame: pd.DataFrame,
    output_path: Path,
    *,
    year: int,
    metric: str,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if frame.empty:
        raise ValueError("Não é possível gerar um heatmap sem resultados.")
    pivot = frame.pivot(index="party", columns="month", values="value")
    pivot = pivot.reindex(columns=range(1, 13))
    pivot.columns = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    if metric == "rate":
        colorbar_title = "Cobertura (%)"
        zmin, zmax = 0, 100
        title = f"Cobertura mensal de membros com voto registrado por partido — {year}"
    else:
        colorbar_title = "Votos registrados"
        zmin, zmax = 0, None
        title = f"Votos individuais registrados por partido — {year}"
    chart = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Blues",
        zmin=zmin,
        zmax=zmax,
        labels={"x": "Mês", "y": "Partido", "color": colorbar_title},
        title=title,
    )
    chart.write_html(output_path, include_plotlyjs=True, auto_open=False)
    return output_path
