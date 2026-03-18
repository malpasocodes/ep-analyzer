"""Statewide vs local benchmark reclassification logic.

Uses real county-level HS earnings from Census ACS B20004 when available.
Falls back to synthetic local benchmarks (from ep_sim) when county data
is missing for an institution.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# CZ type multipliers for synthetic fallback (same as ep_sim config)
CZ_TYPE_MULTIPLIERS = {
    "urban": (0.90, 1.25),
    "suburban": (0.85, 1.10),
    "rural": (0.70, 1.00),
}
CZ_TYPE_WEIGHTS = [0.35, 0.40, 0.25]  # urban, suburban, rural


def generate_synthetic_benchmarks(
    state_threshold: float,
    n_institutions: int,
    inequality: float = 0.5,
    seed: int = 42,
) -> np.ndarray:
    """Generate synthetic local benchmarks around a real state threshold.

    Used as fallback when real county earnings data is not available.
    """
    rng = np.random.default_rng(seed)
    sigma = 1500 + inequality * 6500

    cz_types = rng.choice(
        ["urban", "suburban", "rural"],
        size=n_institutions,
        p=CZ_TYPE_WEIGHTS,
    )

    local_benchmarks = np.empty(n_institutions)
    for i, cz_type in enumerate(cz_types):
        lo, hi = CZ_TYPE_MULTIPLIERS[cz_type]
        multiplier = rng.uniform(lo, hi)
        noise = rng.normal(0, sigma)
        local_benchmarks[i] = state_threshold * multiplier + noise

    return local_benchmarks


def reclassify(
    df: pd.DataFrame,
    state: str,
    inequality: float = 0.5,
    seed: int = 42,
    earnings_metric: str = "P10",
) -> pd.DataFrame:
    """Run statewide-vs-local reclassification on real institutions.

    Uses real county HS earnings (from Census ACS B20004) as local benchmarks
    when available. Falls back to synthetic benchmarks for institutions
    without county data.

    Returns DataFrame with columns:
        unit_id, name, earnings, state_benchmark, local_benchmark,
        pass_state, pass_local, classification, benchmark_source
    """
    earnings_col = "MD_EARN_WNE_P6" if earnings_metric == "P6" else "MD_EARN_WNE_P10"

    state_df = df[df["STABBR"] == state].copy()
    if state_df.empty:
        return pd.DataFrame()

    state_df = state_df.dropna(subset=[earnings_col])
    if state_df.empty:
        return pd.DataFrame()

    threshold = state_df["Threshold"].iloc[0]
    if pd.isna(threshold):
        return pd.DataFrame()

    # Determine local benchmarks: real county data or synthetic
    has_county = "county_hs_earnings" in state_df.columns
    if has_county:
        real_mask = state_df["county_hs_earnings"].notna()
        real_count = real_mask.sum()
        synthetic_count = len(state_df) - real_count
    else:
        real_mask = pd.Series(False, index=state_df.index)
        real_count = 0
        synthetic_count = len(state_df)

    # Build local benchmarks array
    local_benchmarks = np.empty(len(state_df))
    benchmark_source = np.empty(len(state_df), dtype=object)

    if real_count > 0:
        real_indices = np.where(real_mask.values)[0]
        local_benchmarks[real_indices] = state_df.loc[real_mask, "county_hs_earnings"].values
        benchmark_source[real_indices] = "real"

    if synthetic_count > 0:
        synthetic_indices = np.where(~real_mask.values)[0]
        synthetic_values = generate_synthetic_benchmarks(
            threshold, synthetic_count, inequality, seed
        )
        local_benchmarks[synthetic_indices] = synthetic_values
        benchmark_source[synthetic_indices] = "synthetic"

    # Build county name column
    county_names = np.empty(len(state_df), dtype=object)
    if has_county and "county" in state_df.columns:
        county_names = state_df["county"].values
    else:
        county_names[:] = None

    result = pd.DataFrame({
        "unit_id": state_df["UnitID"].values,
        "name": state_df["institution"].values,
        "sector": state_df["sector_name"].values,
        "county": county_names,
        "earnings": state_df[earnings_col].values,
        "state_benchmark": threshold,
        "local_benchmark": local_benchmarks,
        "distance_state": state_df[earnings_col].values - threshold,
        "distance_local": state_df[earnings_col].values - local_benchmarks,
        "benchmark_source": benchmark_source,
    })

    result["pass_state"] = result["earnings"] >= result["state_benchmark"]
    result["pass_local"] = result["earnings"] >= result["local_benchmark"]

    def classify(row):
        if row["pass_state"] and row["pass_local"]:
            return "Pass Both"
        if not row["pass_state"] and not row["pass_local"]:
            return "Fail Both"
        if row["pass_local"] and not row["pass_state"]:
            return "Pass Local Only"
        return "Pass State Only"

    result["classification"] = result.apply(classify, axis=1)
    return result
