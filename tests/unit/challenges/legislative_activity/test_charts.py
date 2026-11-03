from pathlib import Path

import pandas as pd

from apis_externas_4.challenges.legislative_activity.presentation.charts import (
    create_ranking_chart,
    create_voting_heatmap,
)


def test_ranking_chart_creates_html(tmp_path: Path):
    frame = pd.DataFrame({"deputy": ["Ana"], "proposals": [3]})
    output = create_ranking_chart(frame, tmp_path / "ranking.html", title="Teste")
    assert output.exists()
    assert "plotly" in output.read_text(encoding="utf-8").lower()


def test_heatmap_creates_html(tmp_path: Path):
    frame = pd.DataFrame({"party": ["ABC"], "month": [1], "value": [5]})
    output = create_voting_heatmap(frame, tmp_path / "heatmap.html", year=2025, metric="volume")
    assert output.exists()
    assert output.stat().st_size > 1000
