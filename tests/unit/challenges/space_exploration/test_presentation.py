from datetime import UTC, datetime

import pandas as pd

from apis_externas_4.challenges.space_exploration.domain.models import Apod, NaturalEvent
from apis_externas_4.challenges.space_exploration.presentation.charts import create_asteroid_scatter
from apis_externas_4.challenges.space_exploration.presentation.dashboard import create_space_dashboard


def test_asteroid_chart_writes_html(tmp_path):
    frame = pd.DataFrame([{
        "name": "Asteroid A", "approach_date": datetime(2025, 1, 1, tzinfo=UTC),
        "miss_distance_km": 1_000_000, "relative_velocity_km_s": 12.5,
        "diameter_min_km": 0.1, "diameter_max_km": 0.2,
        "potentially_hazardous": False,
    }])
    output = create_asteroid_scatter(frame, tmp_path / "asteroids.html", start_date="2025-01-01", end_date="2025-01-02")
    assert output.exists()
    assert "Asteroid A" in output.read_text(encoding="utf-8")


def test_space_dashboard_contains_three_tabs(tmp_path):
    apod = Apod("2025-01-01", "APOD title", "APOD explanation", "image", "https://example.test/a.jpg", None)
    methods = pd.DataFrame([{"discovery_method": "Transit", "total": 100}])
    events = [NaturalEvent(
        "event-1", "Wildfire", "Description", datetime(2025, 1, 1, tzinfo=UTC),
        ("Wildfires",), 10, 20, "Point", {"type": "Point", "coordinates": [20, 10]},
    )]
    output = create_space_dashboard(apod, methods, events, tmp_path / "dashboard.html")
    html = output.read_text(encoding="utf-8")
    assert "Imagem astronômica" in html
    assert "Exoplanetas" in html
    assert "Eventos naturais" in html
    assert "APOD explanation" in html
    assert "srcdoc=" in html
