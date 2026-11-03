from __future__ import annotations

import pandas as pd


def format_ranking_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "Nenhuma proposição com autoria de deputado foi encontrada."
    return frame[["position", "deputy", "proposals"]].to_string(
        index=False,
        header=["POSIÇÃO", "DEPUTADO", "PROPOSIÇÕES"],
    )


def format_heatmap_summary(frame: pd.DataFrame, metric: str) -> str:
    if frame.empty:
        return "Não há registros suficientes para montar o heatmap."
    if metric == "volume":
        return frame.groupby("party")["value"].sum().sort_values(ascending=False).to_string()
    return (
        frame.groupby("party")["value"]
        .mean()
        .sort_values(ascending=False)
        .map(lambda value: f"{value:.1f}%")
        .to_string()
    )
