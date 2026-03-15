"""Load and cache parquet/CSV data files at startup."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


def has_enriched_data() -> bool:
    """Check if the enriched dataset with real county earnings exists."""
    return (DATA_DIR / "ep_analysis_enriched.parquet").exists()


@lru_cache(maxsize=1)
def load_ep_analysis() -> pd.DataFrame:
    """Load EP analysis data, preferring enriched version with county earnings."""
    enriched = DATA_DIR / "ep_analysis_enriched.parquet"
    if enriched.exists():
        return pd.read_parquet(enriched)
    return pd.read_parquet(DATA_DIR / "ep_analysis.parquet")


@lru_cache(maxsize=1)
def load_county_earnings() -> pd.DataFrame:
    """Load county-level HS graduate earnings from Census ACS B20004."""
    path = DATA_DIR / "county_hs_earnings.csv"
    if path.exists():
        return pd.read_csv(path, dtype={"county_fips": str, "state_fips": str})
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_program_counts() -> pd.DataFrame:
    return pd.read_parquet(DATA_DIR / "program_counts.parquet")


@lru_cache(maxsize=1)
def load_scorecard_earnings() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "scorecard_earnings.csv")


@lru_cache(maxsize=1)
def load_state_thresholds() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "state_thresholds_2024.csv")
