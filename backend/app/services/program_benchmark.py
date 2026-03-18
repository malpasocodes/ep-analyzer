"""Program-level statewide vs local benchmark reclassification.

Adapts the institution-level benchmark.reclassify() for program-level rows.
The EP test threshold is still the state/county HS earnings benchmark —
only the earnings being compared change (from institution median to
program-level median).

Operates only on programs with non-suppressed earnings.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .benchmark import generate_synthetic_benchmarks


def reclassify_programs(
    program_df: pd.DataFrame,
    state: str,
    inequality: float = 0.5,
    seed: int = 42,
) -> pd.DataFrame:
    """Run statewide-vs-local reclassification on programs in a state.

    Uses real county HS earnings as local benchmarks when available.
    Falls back to synthetic benchmarks for programs at institutions
    without county data.

    Only includes programs with non-suppressed earnings.

    Returns DataFrame with columns:
        unit_id, institution, cipcode, cip_desc, credential_desc,
        completions, earnings, state_benchmark, local_benchmark,
        distance_state, distance_local, pass_state, pass_local,
        classification, benchmark_source, county
    """
    # Filter to state + non-suppressed earnings
    state_df = program_df[program_df["state"] == state].copy()
    if state_df.empty:
        return pd.DataFrame()

    state_df = state_df[state_df["program_earnings"].notna()]
    if state_df.empty:
        return pd.DataFrame()

    threshold = state_df["state_threshold"].iloc[0]
    if pd.isna(threshold):
        return pd.DataFrame()

    # Determine local benchmarks per program
    # Each program inherits its institution's county benchmark
    has_county = "county_hs_earnings" in state_df.columns
    if has_county:
        real_mask = state_df["county_hs_earnings"].notna()
        real_count = real_mask.sum()
        synthetic_count = len(state_df) - real_count
    else:
        real_mask = pd.Series(False, index=state_df.index)
        real_count = 0
        synthetic_count = len(state_df)

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
        "unit_id": state_df["UNITID"].values,
        "institution": state_df["institution"].values,
        "cipcode": state_df["cipcode"].values,
        "cip_desc": state_df["cip_desc"].values,
        "credential_desc": state_df["credential_desc"].values if "credential_desc" in state_df.columns else None,
        "completions": state_df["completions"].values if "completions" in state_df.columns else None,
        "county": county_names,
        "earnings": state_df["program_earnings"].values,
        "state_benchmark": threshold,
        "local_benchmark": local_benchmarks,
        "distance_state": state_df["program_earnings"].values - threshold,
        "distance_local": state_df["program_earnings"].values - local_benchmarks,
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
