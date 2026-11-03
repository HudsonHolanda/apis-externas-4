from __future__ import annotations

from html import escape
from pathlib import Path

import folium
from folium.plugins import MarkerCluster

from apis_externas_4.challenges.flight_tracking.domain.models import (
    AircraftPosition,
    FlightTrack,
)


def create_brazil_aircraft_map(
    aircraft: list[AircraftPosition], output: str | Path, *, category: str = "all"
) -> Path:
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    map_view = folium.Map(location=[-10.0, -52.0], zoom_start=4, control_scale=True)
    cluster = MarkerCluster(name="Aeronaves").add_to(map_view)
    for item in aircraft:
        if item.latitude is None or item.longitude is None:
            continue
        callsign = escape(item.callsign or "Sem indicativo")
        popup = (
            f"<b>{callsign}</b><br>ICAO24: {escape(item.icao24)}<br>"
            f"Origem: {escape(item.origin_country or 'Não informada')}<br>"
            f"Categoria: {escape(item.category_name)}<br>"
            f"Altitude: {item.baro_altitude_m if item.baro_altitude_m is not None else 'N/D'} m<br>"
            f"Velocidade: {item.velocity_m_s if item.velocity_m_s is not None else 'N/D'} m/s"
        )
        folium.CircleMarker(
            location=[item.latitude, item.longitude],
            radius=5,
            color="#1f77b4",
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(popup, max_width=320),
            tooltip=f"{callsign} · {item.icao24}",
        ).add_to(cluster)
    folium.LayerControl().add_to(map_view)
    map_view.get_root().html.add_child(
        folium.Element(f"<h3 style='font-family: sans-serif'>Aeronaves sobre o Brasil · {escape(category)}</h3>")
    )
    map_view.save(str(output_path))
    return output_path


def create_track_map(track: FlightTrack, output: str | Path) -> Path:
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    points = [point for point in track.path if point.latitude is not None and point.longitude is not None]
    if not points:
        raise ValueError("A trajetória não possui coordenadas válidas.")
    center = [points[len(points) // 2].latitude, points[len(points) // 2].longitude]
    map_view = folium.Map(location=center, zoom_start=5, control_scale=True)
    coordinates = [[point.latitude, point.longitude] for point in points]
    folium.PolyLine(coordinates, color="#e63946", weight=4, opacity=0.85, tooltip="Trajetória").add_to(map_view)
    first, last = points[0], points[-1]
    folium.Marker(
        [first.latitude, first.longitude],
        tooltip="Início da trajetória",
        icon=folium.Icon(color="green", icon="play"),
    ).add_to(map_view)
    folium.Marker(
        [last.latitude, last.longitude],
        tooltip="Última posição",
        icon=folium.Icon(color="red", icon="flag"),
    ).add_to(map_view)
    title = f"Trajetória {escape(track.icao24)} · {escape(track.callsign or 'sem callsign')}"
    map_view.get_root().html.add_child(
        folium.Element(f"<h3 style='font-family: sans-serif'>{title}</h3>")
    )
    map_view.fit_bounds(coordinates)
    map_view.save(str(output_path))
    return output_path
