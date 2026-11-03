from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path


def run_space_dashboard(repository, output: str | Path, apod_date: str | None = None) -> Path:
    selected_date = apod_date or datetime.now(UTC).date().isoformat()
    apod = repository.get_apod(selected_date)
    exoplanet_methods = repository.list_exoplanet_methods()
    events = repository.list_recent_events(now=datetime.now(UTC), hours=48)

    from apis_externas_4.challenges.space_exploration.presentation.dashboard import (
        create_space_dashboard,
    )

    return create_space_dashboard(apod, exoplanet_methods, events, output)
