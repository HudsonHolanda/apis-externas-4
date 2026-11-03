from __future__ import annotations

from html import escape

import folium
from folium.plugins import MarkerCluster

from apis_externas_4.challenges.space_exploration.domain.models import NaturalEvent


def create_eonet_map(events: list[NaturalEvent]) -> folium.Map:
    map_view = folium.Map(location=[10, 0], zoom_start=2, control_scale=True)
    cluster = MarkerCluster(name="Eventos naturais").add_to(map_view)
    for event in events:
        categories = ", ".join(event.category_names) or "Categoria não informada"
        popup_text = (
            f"<b>{escape(event.title)}</b><br>"
            f"Categoria: {escape(categories)}<br>"
            f"Data: {event.date.isoformat()}"
        )
        folium.Marker(
            location=[event.latitude, event.longitude],
            popup=folium.Popup(popup_text, max_width=360),
            tooltip=event.title,
        ).add_to(cluster)
    folium.LayerControl().add_to(map_view)
    return map_view
