from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from apis_externas_4.challenges.space_exploration.domain.models import Apod, NaturalEvent
from apis_externas_4.challenges.space_exploration.infrastructure.nasa.client import NASAApiClient
from apis_externas_4.challenges.space_exploration.infrastructure.nasa.mappers import (
    map_apod,
    map_eonet_events,
    map_exoplanet_methods,
    map_neo_feeds,
    split_date_range,
)


class NASARepository:
    def __init__(self, client: NASAApiClient) -> None:
        self.client = client

    def list_asteroid_approaches(self, start_date: str, end_date: str) -> pd.DataFrame:
        payloads = [
            self.client.get_neo_feed(start, end)
            for start, end in split_date_range(start_date, end_date)
        ]
        return map_neo_feeds(payloads)

    def get_apod(self, date: str) -> Apod:
        return map_apod(self.client.get_apod(date))

    def list_exoplanet_methods(self) -> pd.DataFrame:
        return map_exoplanet_methods(self.client.get_exoplanet_discovery_methods())

    def list_recent_events(
        self, *, now: datetime | None = None, hours: int = 48
    ) -> list[NaturalEvent]:
        current = now or datetime.now(UTC)
        # Busca três datas UTC para cobrir qualquer janela móvel de 48h; o mapper aplica o corte exato.
        return map_eonet_events(self.client.get_eonet_events(days=3), now=current, hours=hours)
