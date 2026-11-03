from __future__ import annotations

import pandas as pd


def run_asteroid_analysis(repository, start_date: str, end_date: str) -> pd.DataFrame:
    return repository.list_asteroid_approaches(start_date, end_date)
