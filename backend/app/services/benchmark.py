"""Statewide vs local benchmark reclassification logic.

Ports the parametric local-benchmark model from ep_sim, but applies it
to real institutions from ep_analysis data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# CZ type multipliers (same as ep_sim config)
CZ_TYPE_MULTIPLIERS = {
    "urban": (0.90, 1.25),
    "suburban": (0.85, 1.10),
    "rural": (0.70, 1.00),
}
CZ_TYPE_WEIGHTS = [0.35, 0.40, 0.25]  # urban, suburban, rural


def generate_local_benchmarks(
    state_threshold: float,
    n_institutions: int,
    inequality: float = 0.5,
    seed: int = 42,
) -> np.ndarray:
    """Generate synthetic local benchmarks around a real state threshold.

    Args:
        state_threshold: Real state HS earnings threshold.
        n_institutions: Number of institutions to generate benchmarks for.
        inequality: 0-1 slider controlling local variation spread.
            0 = tight ($1,500 std), 1 = wide ($8,000 std).
        seed: Random seed for reproducibility.

    Returns:
        Array of local benchmark values, one per institution.
    """
    rng = np.random.default_rng(seed)
    sigma = 1500 + inequality * 6500  # maps 0->1500, 1->8000

    # Assign CZ types
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
) -> pd.DataFrame:
    """Run statewide-vs-local reclassification on real institutions.

    Takes real institutions from a state, generates synthetic local benchmarks,
    and classifies each into the 4 quadrants.

    Returns DataFrame with columns:
        unit_id, name, earnings, state_benchmark, local_benchmark,
        pass_state, pass_local, classification
    """
    state_df = df[df["STABBR"] == state].copy()
    if state_df.empty:
        return pd.DataFrame()

    # Drop institutions without earnings
    state_df = state_df.dropna(subset=["median_earnings"])
    if state_df.empty:
        return pd.DataFrame()

    threshold = state_df["Threshold"].iloc[0]
    if pd.isna(threshold):
        return pd.DataFrame()

    local_benchmarks = generate_local_benchmarks(
        threshold, len(state_df), inequality, seed
    )

    result = pd.DataFrame({
        "unit_id": state_df["UnitID"].values,
        "name": state_df["institution"].values,
        "sector": state_df["sector_name"].values,
        "earnings": state_df["median_earnings"].values,
        "state_benchmark": threshold,
        "local_benchmark": local_benchmarks,
        "distance_state": state_df["median_earnings"].values - threshold,
        "distance_local": state_df["median_earnings"].values - local_benchmarks,
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
