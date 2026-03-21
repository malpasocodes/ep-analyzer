"""Monte Carlo simulation engine for privacy-suppressed program earnings.

~72% of College Scorecard program records lack earnings data due to
privacy suppression (<30 students in cohort). This module estimates
likely earnings using a hierarchical prior approach:

1. National CIP prior   — median earnings for this CIP + credential level
                          from all non-suppressed programs nationally
2. Institution effect   — ratio of this institution's median earnings to
                          the national median (captures school quality/selectivity)
3. Geographic factor    — ratio of county HS earnings to state threshold
                          (captures local labor market conditions)

For each suppressed program, N Monte Carlo draws produce:
- Point estimate (median of draws)
- 80% confidence interval
- Probability of passing the state EP test
- Probability of passing the local (county) benchmark
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def build_national_cip_priors(program_df: pd.DataFrame) -> pd.DataFrame:
    """Compute national earnings distribution by CIP + credential level.

    Uses only non-suppressed programs to build priors.

    Returns DataFrame with columns:
        cipcode, credential_level, national_median, national_p25,
        national_p75, national_std, n_observed
    """
    observed = program_df[program_df["program_earnings"].notna()].copy()

    if observed.empty:
        return pd.DataFrame()

    priors = (
        observed.groupby(["cipcode", "credential_level"], observed=True)["program_earnings"]
        .agg(
            national_median="median",
            national_p25=lambda x: x.quantile(0.25),
            national_p75=lambda x: x.quantile(0.75),
            national_std="std",
            national_mean="mean",
            n_observed="count",
        )
        .reset_index()
    )

    # Fill NaN std (CIP codes with only 1 observed program) with global std
    global_std = observed["program_earnings"].std()
    priors["national_std"] = priors["national_std"].fillna(global_std)

    # Also compute a CIP-only prior (ignoring credential level) for fallback
    cip_priors = (
        observed.groupby("cipcode", observed=True)["program_earnings"]
        .agg(
            cip_median="median",
            cip_std="std",
            cip_n_observed="count",
        )
        .reset_index()
    )
    cip_priors["cip_std"] = cip_priors["cip_std"].fillna(global_std)

    priors = priors.merge(cip_priors, on="cipcode", how="left")

    return priors


def compute_institution_effects(ep_df: pd.DataFrame) -> pd.DataFrame:
    """Compute institution-level earnings effect ratios.

    The institution effect captures whether a school's graduates generally
    earn more or less than the national average.

    Returns DataFrame with columns:
        UNITID, institution_effect
    """
    # National median across all institutions
    national_median = ep_df["median_earnings"].median()
    if pd.isna(national_median) or national_median <= 0:
        national_median = 35000  # Fallback

    inst = ep_df[["UnitID", "median_earnings"]].dropna(subset=["median_earnings"]).copy()
    inst = inst.rename(columns={"UnitID": "UNITID"})
    inst["institution_effect"] = inst["median_earnings"] / national_median

    # Clip extreme effects to [0.3, 3.0] to prevent wild estimates
    inst["institution_effect"] = inst["institution_effect"].clip(0.3, 3.0)

    return inst[["UNITID", "institution_effect"]]


def compute_geographic_factors(program_df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-institution geographic labor market factor.

    Geographic factor = county_hs_earnings / state_threshold.
    Values > 1 indicate a high-cost/high-wage area.

    Returns DataFrame with columns:
        UNITID, geo_factor
    """
    inst = program_df[["UNITID", "county_hs_earnings", "state_threshold"]].drop_duplicates("UNITID").copy()

    has_both = inst["county_hs_earnings"].notna() & inst["state_threshold"].notna() & (inst["state_threshold"] > 0)
    inst["geo_factor"] = 1.0  # default: neutral
    inst.loc[has_both, "geo_factor"] = (
        inst.loc[has_both, "county_hs_earnings"] / inst.loc[has_both, "state_threshold"]
    )

    # Clip to [0.5, 2.0] to prevent extreme geographic adjustments
    inst["geo_factor"] = inst["geo_factor"].clip(0.5, 2.0)

    return inst[["UNITID", "geo_factor"]]


def estimate_program_earnings(
    program_df: pd.DataFrame,
    ep_df: pd.DataFrame,
    n_simulations: int = 1000,
    seed: int = 42,
    priors_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Monte Carlo simulation for suppressed program earnings.

    For each suppressed program, draws from:
        estimated = national_cip_median * institution_effect * geo_factor * N(1, σ)

    where σ is calibrated from within-CIP variance of observed programs.

    Args:
        program_df: Program analysis DataFrame (programs to simulate)
        ep_df: Institution-level EP analysis DataFrame (from load_ep_analysis)
        n_simulations: Number of Monte Carlo draws per program
        seed: Random seed for reproducibility
        priors_df: Optional separate DataFrame for building national CIP priors.
                   If None, uses program_df. Pass the full dataset here when
                   program_df is filtered to a subset (e.g. single institution).

    Returns DataFrame with columns for suppressed programs:
        UNITID, institution, cipcode, cip_desc, credential_desc,
        completions, state_threshold, county_hs_earnings,
        estimated_earnings, earnings_ci_low, earnings_ci_high,
        prob_pass_state, prob_pass_local, estimation_method
    """
    rng = np.random.default_rng(seed)

    # Build priors from full dataset, adjustment factors from target programs
    base_df = priors_df if priors_df is not None else program_df
    priors = build_national_cip_priors(base_df)
    inst_effects = compute_institution_effects(ep_df)
    geo_factors = compute_geographic_factors(program_df)

    if priors.empty:
        return pd.DataFrame()

    # Get suppressed programs
    suppressed = program_df[program_df["earnings_suppressed"]].copy()
    if suppressed.empty:
        return pd.DataFrame()

    # Merge in priors, institution effects, and geographic factors
    suppressed = suppressed.merge(
        priors[["cipcode", "credential_level", "national_median", "national_std",
                "cip_median", "cip_std", "n_observed"]],
        on=["cipcode", "credential_level"],
        how="left",
    )
    suppressed = suppressed.merge(inst_effects, on="UNITID", how="left")
    suppressed = suppressed.merge(geo_factors, on="UNITID", how="left")

    # Fill missing factors with defaults
    suppressed["institution_effect"] = suppressed["institution_effect"].fillna(1.0)
    suppressed["geo_factor"] = suppressed["geo_factor"].fillna(1.0)

    # For programs without a CIP+credential prior, try CIP-only prior
    no_prior = suppressed["national_median"].isna()
    if no_prior.any():
        # Use CIP-only median as fallback
        suppressed.loc[no_prior, "national_median"] = suppressed.loc[no_prior, "cip_median"]
        suppressed.loc[no_prior, "national_std"] = suppressed.loc[no_prior, "cip_std"]

    # Separate: programs with a prior vs no prior at all
    has_prior = suppressed["national_median"].notna()
    estimable = suppressed[has_prior].copy()
    no_estimate = suppressed[~has_prior].copy()

    results = []

    if not estimable.empty:
        # Vectorized Monte Carlo simulation — chunked to cap memory usage.
        # Each chunk processes at most CHUNK_SIZE programs at a time,
        # keeping peak array memory under ~150MB even at 1000 simulations.
        CHUNK_SIZE = 10_000  # 10k × 1000 sims × 8 bytes ≈ 80MB per array
        n_programs = len(estimable)
        medians = estimable["national_median"].values
        stds = estimable["national_std"].values
        inst_effs = estimable["institution_effect"].values
        geo_facs = estimable["geo_factor"].values
        thresholds = estimable["state_threshold"].values
        county_earnings = estimable["county_hs_earnings"].values if "county_hs_earnings" in estimable.columns else np.full(n_programs, np.nan)

        # Coefficient of variation from observed data, capped
        sigma_rel = np.minimum(stds / np.maximum(medians, 1), 0.5)

        # Pre-allocate output arrays
        point_estimates = np.empty(n_programs)
        ci_low = np.empty(n_programs)
        ci_high = np.empty(n_programs)
        prob_pass_state = np.full(n_programs, np.nan)
        prob_pass_local = np.full(n_programs, np.nan)

        for start in range(0, n_programs, CHUNK_SIZE):
            end = min(start + CHUNK_SIZE, n_programs)
            chunk_size = end - start

            # Draw N simulations for this chunk: shape (chunk_size, n_simulations)
            noise = rng.normal(1.0, sigma_rel[start:end, np.newaxis],
                               size=(chunk_size, n_simulations))

            draws = (
                medians[start:end, np.newaxis]
                * inst_effs[start:end, np.newaxis]
                * geo_facs[start:end, np.newaxis]
                * noise
            )
            del noise  # free immediately

            np.maximum(draws, 0, out=draws)

            point_estimates[start:end] = np.median(draws, axis=1)
            ci_low[start:end] = np.percentile(draws, 10, axis=1)
            ci_high[start:end] = np.percentile(draws, 90, axis=1)

            # Probability of passing EP test
            chunk_thresh = thresholds[start:end]
            valid_t = ~np.isnan(chunk_thresh)
            if valid_t.any():
                prob_pass_state[start:end][valid_t] = (
                    (draws[valid_t] >= chunk_thresh[valid_t, np.newaxis]).mean(axis=1)
                )

            # Probability of passing local benchmark
            chunk_county = county_earnings[start:end]
            valid_c = ~np.isnan(chunk_county)
            if valid_c.any():
                prob_pass_local[start:end][valid_c] = (
                    (draws[valid_c] >= chunk_county[valid_c, np.newaxis]).mean(axis=1)
                )

            del draws  # free chunk memory

        # Build result DataFrame
        est_df = pd.DataFrame({
            "UNITID": estimable["UNITID"].values,
            "institution": estimable["institution"].values,
            "state": estimable["state"].values,
            "cipcode": estimable["cipcode"].values,
            "cip_desc": estimable["cip_desc"].values,
            "credential_level": estimable["credential_level"].values,
            "credential_desc": estimable["credential_desc"].values if "credential_desc" in estimable.columns else None,
            "completions": estimable["completions"].values if "completions" in estimable.columns else None,
            "state_threshold": thresholds,
            "county_hs_earnings": county_earnings,
            "estimated_earnings": np.round(point_estimates).astype(int),
            "earnings_ci_low": np.round(ci_low).astype(int),
            "earnings_ci_high": np.round(ci_high).astype(int),
            "prob_pass_state": np.round(prob_pass_state, 3),
            "prob_pass_local": np.round(prob_pass_local, 3),
            "national_cip_median": medians,
            "institution_effect": inst_effs,
            "geo_factor": geo_facs,
            "estimation_method": "national_cip_prior",
        })
        results.append(est_df)

    if not no_estimate.empty:
        # Programs with no CIP prior at all — mark as inestimable
        noest_df = pd.DataFrame({
            "UNITID": no_estimate["UNITID"].values,
            "institution": no_estimate["institution"].values,
            "state": no_estimate["state"].values,
            "cipcode": no_estimate["cipcode"].values,
            "cip_desc": no_estimate["cip_desc"].values,
            "credential_level": no_estimate["credential_level"].values,
            "credential_desc": no_estimate["credential_desc"].values if "credential_desc" in no_estimate.columns else None,
            "completions": no_estimate["completions"].values if "completions" in no_estimate.columns else None,
            "state_threshold": no_estimate["state_threshold"].values,
            "county_hs_earnings": no_estimate["county_hs_earnings"].values if "county_hs_earnings" in no_estimate.columns else np.nan,
            "estimated_earnings": np.nan,
            "earnings_ci_low": np.nan,
            "earnings_ci_high": np.nan,
            "prob_pass_state": np.nan,
            "prob_pass_local": np.nan,
            "national_cip_median": np.nan,
            "institution_effect": np.nan,
            "geo_factor": np.nan,
            "estimation_method": "no_estimate",
        })
        results.append(noest_df)

    if not results:
        return pd.DataFrame()

    return pd.concat(results, ignore_index=True)


def simulate_institution_programs(
    program_df: pd.DataFrame,
    ep_df: pd.DataFrame,
    unit_id: int,
    n_simulations: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    """Simulate earnings for suppressed programs at a single institution.

    Builds priors from the full dataset but only runs Monte Carlo draws
    for programs at the target institution, keeping memory usage minimal.
    """
    inst_programs = program_df[program_df["UNITID"] == unit_id]
    if inst_programs.empty:
        return pd.DataFrame()

    # Only simulate if there are suppressed programs
    suppressed = inst_programs[inst_programs["earnings_suppressed"]]
    if suppressed.empty:
        return pd.DataFrame()

    # Build priors from full dataset (cheap — just aggregation)
    # but only simulate the target institution's programs
    inst_only_df = program_df[program_df["UNITID"] == unit_id]
    result = estimate_program_earnings(inst_only_df, ep_df, n_simulations, seed,
                                       priors_df=program_df)

    if result.empty:
        return pd.DataFrame()

    return result.reset_index(drop=True)


def simulation_summary(sim_df: pd.DataFrame) -> dict:
    """Summarize simulation results.

    Returns dict with aggregate statistics about the simulation.
    """
    if sim_df.empty:
        return {
            "total_simulated": 0,
            "estimable": 0,
            "inestimable": 0,
            "prob_pass_state_mean": None,
            "prob_pass_local_mean": None,
            "estimated_high_risk": 0,
            "estimated_moderate_risk": 0,
            "estimated_low_risk": 0,
            "estimated_very_low_risk": 0,
        }

    estimable = sim_df[sim_df["estimation_method"] == "national_cip_prior"]
    inestimable = sim_df[sim_df["estimation_method"] == "no_estimate"]

    # Classify simulated programs by estimated risk
    est_with_thresh = estimable[estimable["state_threshold"].notna() & estimable["estimated_earnings"].notna()]
    if not est_with_thresh.empty:
        margin_pct = (
            (est_with_thresh["estimated_earnings"] - est_with_thresh["state_threshold"])
            / est_with_thresh["state_threshold"] * 100
        )
        high_risk = (margin_pct < 0).sum()
        moderate = ((margin_pct >= 0) & (margin_pct < 20)).sum()
        low = ((margin_pct >= 20) & (margin_pct < 50)).sum()
        very_low = (margin_pct >= 50).sum()
    else:
        high_risk = moderate = low = very_low = 0

    return {
        "total_simulated": len(sim_df),
        "estimable": len(estimable),
        "inestimable": len(inestimable),
        "prob_pass_state_mean": round(float(estimable["prob_pass_state"].mean()), 3) if not estimable.empty and estimable["prob_pass_state"].notna().any() else None,
        "prob_pass_local_mean": round(float(estimable["prob_pass_local"].mean()), 3) if not estimable.empty and estimable["prob_pass_local"].notna().any() else None,
        "estimated_high_risk": int(high_risk),
        "estimated_moderate_risk": int(moderate),
        "estimated_low_risk": int(low),
        "estimated_very_low_risk": int(very_low),
    }
