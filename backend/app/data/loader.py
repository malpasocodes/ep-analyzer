"""Load and cache parquet/CSV data files at startup."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


@lru_cache(maxsize=1)
def load_ep_analysis() -> pd.DataFrame:
    return pd.read_parquet(DATA_DIR / "ep_analysis.parquet")


@lru_cache(maxsize=1)
def load_program_counts() -> pd.DataFrame:
    return pd.read_parquet(DATA_DIR / "program_counts.parquet")


@lru_cache(maxsize=1)
def load_scorecard_earnings() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "scorecard_earnings.csv")


@lru_cache(maxsize=1)
def load_state_thresholds() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "state_thresholds_2024.csv")
