from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px


def create_asteroid_scatter(frame: pd.DataFrame, output: str | Path, *, start_date: str, end_date: str) -> Path:
    if frame.empty:
        raise ValueError("Não há aproximações de asteroides para o intervalo informado.")
    data = frame.copy()
    data["miss_distance_million_km"] = data["miss_distance_km"] / 1_000_000
    figure = px.scatter(
        data,
        x="miss_distance_million_km",
        y="relative_velocity_km_s",
        color="potentially_hazardous",
        size="diameter_max_km",
        log_x=True,
        hover_name="name",
        hover_data={
            "approach_date": True,
            "diameter_min_km": ":.4f",
            "diameter_max_km": ":.4f",
            "miss_distance_million_km": ":.4f",
            "relative_velocity_km_s": ":.3f",
        },
        labels={
            "miss_distance_million_km": "Distância mínima da Terra (milhões de km, escala logarítmica)",
            "relative_velocity_km_s": "Velocidade relativa (km/s)",
            "potentially_hazardous": "Potencialmente perigoso",
        },
        title=f"Asteroides próximos da Terra · {start_date} a {end_date}",
    )
    figure.update_layout(template="plotly_white")
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(str(output_path), include_plotlyjs="cdn", full_html=True)
    return output_path


def create_exoplanet_bar_chart(frame: pd.DataFrame):
    if frame.empty:
        figure = px.bar(title="Nenhum método de descoberta encontrado")
    else:
        figure = px.bar(
            frame.head(15).sort_values("total"),
            x="total",
            y="discovery_method",
            orientation="h",
            labels={"total": "Exoplanetas confirmados", "discovery_method": "Método de descoberta"},
            title="Exoplanetas confirmados por método de descoberta (15 principais)",
        )
    figure.update_layout(template="plotly_white")
    return figure
