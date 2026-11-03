from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd

from apis_externas_4.challenges.space_exploration.domain.models import Apod, NaturalEvent
from apis_externas_4.challenges.space_exploration.presentation.charts import (
    create_exoplanet_bar_chart,
)
from apis_externas_4.challenges.space_exploration.presentation.maps import create_eonet_map


def create_space_dashboard(
    apod: Apod,
    exoplanet_methods: pd.DataFrame,
    events: list[NaturalEvent],
    output: str | Path,
) -> Path:
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if apod.media_type == "image" and apod.image_url:
        apod_media = (
            f'<img class="apod-image" src="{escape(apod.image_url, quote=True)}" '
            f'alt="{escape(apod.title, quote=True)}">'
        )
    elif apod.page_url:
        apod_media = (
            f'<p>O conteúdo do APOD é do tipo {escape(apod.media_type)}. '
            f'<a href="{escape(apod.page_url, quote=True)}" target="_blank" rel="noopener">Abrir mídia</a>.</p>'
        )
    else:
        apod_media = "<p>Mídia não disponível para incorporação.</p>"

    credit = f'<p class="credit">Crédito: {escape(apod.credit)}</p>' if apod.credit else ""
    apod_panel = (
        f'<p class="date">{escape(apod.date)}</p><h2>{escape(apod.title)}</h2>'
        f'{apod_media}<p class="explanation">{escape(apod.explanation)}</p>{credit}'
    )

    chart_html = create_exoplanet_bar_chart(exoplanet_methods).to_html(
        full_html=False, include_plotlyjs="cdn"
    )
    map_html = create_eonet_map(events).get_root().render()
    iframe_srcdoc = escape(map_html, quote=True)
    map_panel = (
        f'<p class="date">Eventos com geometria registrada nas últimas 48 horas: {len(events)}</p>'
        f'<iframe class="map-frame" title="Mapa de eventos naturais" srcdoc="{iframe_srcdoc}"></iframe>'
    )

    document = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard de Exploração Espacial</title>
<style>
:root {{ color-scheme: light; font-family: system-ui, sans-serif; background: #f4f6fb; color: #182230; }}
body {{ margin: 0; padding: 28px; }}
main {{ max-width: 1200px; margin: 0 auto; background: white; padding: 24px; border-radius: 14px; box-shadow: 0 8px 30px #17203314; }}
h1 {{ margin-top: 0; }}
.subtitle,.date,.credit {{ color: #667085; }}
.tabs {{ display: flex; flex-wrap: wrap; gap: 8px; border-bottom: 1px solid #dfe3eb; margin: 22px 0; }}
.tabs button {{ border: 0; background: #eef1f6; padding: 11px 16px; border-radius: 8px 8px 0 0; cursor: pointer; font: inherit; }}
.tabs button.active {{ background: #172033; color: white; }}
.panel {{ display: none; }}
.panel.active {{ display: block; }}
.apod-image {{ max-width: 100%; max-height: 560px; object-fit: contain; display: block; margin: 16px auto; }}
.explanation {{ line-height: 1.65; white-space: pre-wrap; }}
.map-frame {{ width: 100%; height: 620px; border: 0; border-radius: 10px; }}
.chart {{ width: 100%; min-height: 520px; }}
a {{ color: #1769aa; }}
</style>
</head>
<body><main>
<h1>Dashboard de Exploração Espacial</h1>
<p class="subtitle">NASA APOD · NASA Exoplanet Archive · Earth Observatory Natural Event Tracker</p>
<nav class="tabs" role="tablist">
<button class="active" role="tab" aria-selected="true" onclick="showTab('apod', this)">Imagem astronômica</button>
<button role="tab" aria-selected="false" onclick="showTab('exoplanets', this)">Exoplanetas</button>
<button role="tab" aria-selected="false" onclick="showTab('events', this)">Eventos naturais</button>
</nav>
<section id="apod" class="panel active">{apod_panel}</section>
<section id="exoplanets" class="panel"><div class="chart">{chart_html}</div></section>
<section id="events" class="panel">{map_panel}</section>
</main>
<script>
function showTab(id, button) {{
  document.querySelectorAll('.panel').forEach(panel => panel.classList.remove('active'));
  document.querySelectorAll('.tabs button').forEach(tab => {{ tab.classList.remove('active'); tab.setAttribute('aria-selected','false'); }});
  document.getElementById(id).classList.add('active');
  button.classList.add('active'); button.setAttribute('aria-selected','true');
  window.dispatchEvent(new Event('resize'));
}}
</script>
</body></html>"""
    output_path.write_text(document, encoding="utf-8")
    return output_path
