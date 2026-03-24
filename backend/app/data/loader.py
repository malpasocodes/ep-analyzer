"""Load and cache parquet/CSV data files at startup."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(os.environ.get("DATA_DIR", Path(__file__).resolve().parent.parent.parent.parent / "data"))


_SKIP_CATEGORY = {"risk_level", "estimated_risk_level", "pass_state", "pass_county"}


def _optimize_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Convert object columns to category dtype to reduce memory usage.

    Skips columns used in cross-category assignment or arithmetic.
    """
    for col in df.select_dtypes(include="object").columns:
        if col not in _SKIP_CATEGORY:
            df[col] = df[col].astype("category")
    return df


def has_enriched_data() -> bool:
    """Check if the enriched dataset with real county earnings exists."""
    return (DATA_DIR / "ep_analysis_enriched.parquet").exists()


@lru_cache(maxsize=1)
def load_ep_analysis() -> pd.DataFrame:
    """Load EP analysis data, preferring enriched version with county earnings."""
    enriched = DATA_DIR / "ep_analysis_enriched.parquet"
    if enriched.exists():
        return _optimize_strings(pd.read_parquet(enriched))
    return _optimize_strings(pd.read_parquet(DATA_DIR / "ep_analysis.parquet"))


@lru_cache(maxsize=1)
def load_county_earnings() -> pd.DataFrame:
    """Load county-level HS graduate earnings from Census ACS B20004."""
    path = DATA_DIR / "county_hs_earnings.csv"
    if path.exists():
        return pd.read_csv(path, dtype={"county_fips": str, "state_fips": str})
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_state_bachelor_earnings() -> pd.DataFrame:
    """Load state-level Bachelor's degree median earnings from Census ACS B20004.

    Used as EP test threshold for graduate programs (credential levels 4-8).
    Built by: python -m backend.app.pipelines.fetch_county_earnings
    """
    path = DATA_DIR / "state_bachelor_earnings.csv"
    if path.exists():
        return pd.read_csv(path, dtype={"state_fips": str})
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_program_counts() -> pd.DataFrame:
    return pd.read_parquet(DATA_DIR / "program_counts.parquet")


@lru_cache(maxsize=1)
def load_scorecard_earnings() -> pd.DataFrame:
    return _optimize_strings(pd.read_csv(DATA_DIR / "scorecard_earnings.csv"))


@lru_cache(maxsize=1)
def load_state_thresholds() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "state_thresholds_2024.csv")


def has_program_data() -> bool:
    """Check if the program-level analysis dataset exists."""
    return (DATA_DIR / "program_analysis.parquet").exists()


@lru_cache(maxsize=1)
def load_program_analysis() -> pd.DataFrame:
    """Load program-level analysis with earnings, EP test results.

    Built by: python -m backend.app.pipelines.build_program_dataset
    """
    path = DATA_DIR / "program_analysis.parquet"
    if path.exists():
        return _optimize_strings(pd.read_parquet(path))
    return pd.DataFrame()


# Phase 1: Only Associates (2) and Bachelors (3)
_PHASE1_CREDENTIAL_LEVELS = {2, 3}


@lru_cache(maxsize=1)
def get_phase1_unitids() -> frozenset:
    """Return UNITIDs that have at least one Phase 1 program with data.

    An institution qualifies if it has any Associates/Bachelors program
    with reported earnings or privacy-suppressed earnings.
    """
    df = load_program_analysis()
    if df.empty:
        return frozenset()
    df = df[df["credential_level"].isin(_PHASE1_CREDENTIAL_LEVELS)]
    has_data = df["program_earnings"].notna() | df["earnings_suppressed"]
    return frozenset(df.loc[has_data, "UNITID"].unique())


@lru_cache(maxsize=1)
def load_scorecard_fos() -> pd.DataFrame:
    """Load raw Scorecard field-of-study earnings.

    Built by: python -m backend.app.pipelines.fetch_program_earnings
    """
    path = DATA_DIR / "scorecard_fos_earnings.parquet"
    if path.exists():
        return _optimize_strings(pd.read_parquet(path))
    return pd.DataFrame()


@lru_cache(maxsize=1)
def load_ipeds_completions() -> pd.DataFrame:
    """Load IPEDS completions by CIP code.

    Built by: python -m backend.app.pipelines.fetch_ipeds_completions
    """
    path = DATA_DIR / "ipeds_completions.parquet"
    if path.exists():
        return _optimize_strings(pd.read_parquet(path))
    return pd.DataFrame()
