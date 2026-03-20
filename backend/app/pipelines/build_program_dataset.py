"""Build the enriched program-level analysis dataset.

Merges College Scorecard field-of-study earnings with IPEDS completions
and institution-level context (state, county, thresholds, sector).

Prerequisite pipelines:
    python -m backend.app.pipelines.fetch_program_earnings
    python -m backend.app.pipelines.fetch_ipeds_completions

Usage:
    python -m backend.app.pipelines.build_program_dataset
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


def load_inputs(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame | None, pd.DataFrame]:
    """Load the three input datasets.

    Returns:
        (scorecard_fos, ipeds_completions_or_None, ep_analysis)
    """
    # Scorecard Field-of-Study earnings (required)
    fos_path = data_dir / "scorecard_fos_earnings.parquet"
    if not fos_path.exists():
        raise FileNotFoundError(
            f"{fos_path} not found. Run:\n"
            "  python -m backend.app.pipelines.fetch_program_earnings"
        )
    fos = pd.read_parquet(fos_path)
    print(f"  Scorecard FoS: {len(fos):,} records")

    # IPEDS Completions (optional — enriches but not required)
    ipeds_path = data_dir / "ipeds_completions.parquet"
    ipeds = None
    if ipeds_path.exists():
        ipeds = pd.read_parquet(ipeds_path)
        print(f"  IPEDS Completions: {len(ipeds):,} records")
    else:
        print(f"  IPEDS Completions: not found (will use Scorecard counts only)")

    # EP Analysis (institution-level context)
    ep_path = data_dir / "ep_analysis_enriched.parquet"
    if not ep_path.exists():
        ep_path = data_dir / "ep_analysis.parquet"
    if not ep_path.exists():
        raise FileNotFoundError(f"No EP analysis file found in {data_dir}")
    ep = pd.read_parquet(ep_path)
    print(f"  EP Analysis: {len(ep):,} institutions ({ep_path.name})")

    return fos, ipeds, ep


def normalize_cip4(cip: str) -> str:
    """Normalize a CIP code to 4-digit dotted format: XX.XX

    Handles various formats:
        '0100' -> '01.00'  (Scorecard, no dot)
        '1.01' -> '01.01'  (IPEDS, missing leading zero)
        '01.01' -> '01.01' (already normalized)
        '11.0101' -> '11.01' (6-digit, truncate)
    """
    cip = str(cip).strip()
    if "." in cip:
        parts = cip.split(".")
        major = parts[0].zfill(2)
        minor = parts[1][:2].ljust(2, "0")
        return f"{major}.{minor}"
    else:
        # No dot: assume XXYY or XXXY format
        cip = cip.zfill(4)
        return f"{cip[:2]}.{cip[2:4]}"


def merge_ipeds_completions(
    fos: pd.DataFrame, ipeds: pd.DataFrame
) -> pd.DataFrame:
    """Enrich Scorecard FoS with IPEDS completion counts.

    Joins on UNITID + normalized 4-digit CIP code + credential level.
    IPEDS has finer 6-digit CIP codes, so we aggregate to 4-digit first.
    """
    # Normalize CIP codes in both datasets for joining
    fos = fos.copy()
    fos["cip_join"] = fos["cipcode"].apply(normalize_cip4)

    ipeds = ipeds.copy()
    ipeds["cip_join"] = ipeds["cipcode_4"].apply(normalize_cip4)

    # Normalize credential level types for joining
    ipeds["credential_level"] = pd.to_numeric(ipeds["credential_level"], errors="coerce").astype("Int64")

    # Aggregate IPEDS completions to 4-digit CIP + credential level
    agg_dict = {"total_completions": ("total_completions", "sum")}
    if "male_completions" in ipeds.columns:
        agg_dict["ipeds_male"] = ("male_completions", "sum")
    if "female_completions" in ipeds.columns:
        agg_dict["ipeds_female"] = ("female_completions", "sum")
    agg_dict["n_6digit_programs"] = ("cipcode_6", "nunique")

    ipeds_agg = (
        ipeds.groupby(["UNITID", "cip_join", "credential_level"])
        .agg(**agg_dict)
        .reset_index()
        .rename(columns={"total_completions": "ipeds_completions"})
    )

    print(f"  IPEDS aggregated: {len(ipeds_agg):,} groups")
    print(f"  Sample FoS cip_join: {fos['cip_join'].head(5).tolist()}")
    print(f"  Sample IPEDS cip_join: {ipeds_agg['cip_join'].head(5).tolist()}")

    # Join
    merged = fos.merge(
        ipeds_agg,
        on=["UNITID", "cip_join", "credential_level"],
        how="left",
    )

    matched = merged["ipeds_completions"].notna().sum()
    print(f"  IPEDS match: {matched:,}/{len(merged):,} ({matched/len(merged)*100:.1f}%)")

    # Use IPEDS completions where available, fall back to Scorecard
    if "completions" in merged.columns:
        merged["completions"] = merged["ipeds_completions"].fillna(merged["completions"])
    else:
        merged["completions"] = merged["ipeds_completions"]

    # Drop helper columns
    drop_cols = ["cip_join", "ipeds_male", "ipeds_female"]
    merged = merged.drop(columns=[c for c in drop_cols if c in merged.columns])

    return merged


def merge_institution_context(
    programs: pd.DataFrame, ep: pd.DataFrame
) -> pd.DataFrame:
    """Add institution-level context: state, county, thresholds, sector."""
    # Select institution-level columns
    inst_cols = ["UnitID", "STABBR", "sector_name", "Threshold", "median_earnings"]

    # Add county columns if available (enriched dataset)
    for col in ["county_fips", "county", "county_hs_earnings"]:
        if col in ep.columns:
            inst_cols.append(col)

    inst = ep[inst_cols].drop_duplicates(subset=["UnitID"]).rename(columns={
        "UnitID": "UNITID",
        "STABBR": "state",
        "Threshold": "state_threshold",
        "median_earnings": "institution_earnings",
    })

    merged = programs.merge(inst, on="UNITID", how="left")

    matched = merged["state"].notna().sum()
    print(f"  Institution context match: {matched:,}/{len(merged):,}")

    return merged


def compute_ep_test(df: pd.DataFrame) -> pd.DataFrame:
    """Compute program-level EP test outcomes where earnings are available."""
    # Pass state EP test: program earnings >= state threshold
    has_earnings = df["program_earnings"].notna() & df["state_threshold"].notna()
    df["pass_state"] = pd.NA
    df.loc[has_earnings, "pass_state"] = (
        df.loc[has_earnings, "program_earnings"] >= df.loc[has_earnings, "state_threshold"]
    )

    # Pass county benchmark: program earnings >= county HS earnings
    if "county_hs_earnings" in df.columns:
        has_county = has_earnings & df["county_hs_earnings"].notna()
        df["pass_county"] = pd.NA
        df.loc[has_county, "pass_county"] = (
            df.loc[has_county, "program_earnings"] >= df.loc[has_county, "county_hs_earnings"]
        )
    else:
        df["pass_county"] = pd.NA

    # Earnings margin (percentage above/below state threshold)
    df["earnings_margin_pct"] = pd.NA
    mask = df["program_earnings"].notna() & df["state_threshold"].notna() & (df["state_threshold"] > 0)
    df.loc[mask, "earnings_margin_pct"] = (
        (df.loc[mask, "program_earnings"] - df.loc[mask, "state_threshold"])
        / df.loc[mask, "state_threshold"]
        * 100
    )

    # Risk level — distinguish privacy-suppressed (<30 cohort) from no data (no cohort)
    df["risk_level"] = "No Cohort"
    df.loc[df["earnings_suppressed"] == True, "risk_level"] = "Privacy Suppressed"  # noqa: E712
    df.loc[df["earnings_margin_pct"].notna() & (df["earnings_margin_pct"] >= 50), "risk_level"] = "Very Low Risk"
    df.loc[df["earnings_margin_pct"].notna() & (df["earnings_margin_pct"] >= 20) & (df["earnings_margin_pct"] < 50), "risk_level"] = "Low Risk"
    df.loc[df["earnings_margin_pct"].notna() & (df["earnings_margin_pct"] >= 0) & (df["earnings_margin_pct"] < 20), "risk_level"] = "Moderate Risk"
    df.loc[df["earnings_margin_pct"].notna() & (df["earnings_margin_pct"] < 0), "risk_level"] = "High Risk"

    # Summary
    risk_counts = df["risk_level"].value_counts()
    print(f"\n  Program risk distribution:")
    for level in ["Very Low Risk", "Low Risk", "Moderate Risk", "High Risk", "Privacy Suppressed", "No Cohort"]:
        count = risk_counts.get(level, 0)
        pct = count / len(df) * 100
        print(f"    {level}: {count:,} ({pct:.1f}%)")

    return df


def run_simulation(df: pd.DataFrame, ep: pd.DataFrame) -> pd.DataFrame:
    """Run Monte Carlo simulation and bake estimated fields into the DataFrame."""
    from backend.app.services.program_simulation import (
        build_national_cip_priors,
        compute_institution_effects,
        compute_geographic_factors,
    )

    # Initialize estimated columns
    df["estimated_earnings"] = pd.NA
    df["earnings_ci_low"] = pd.NA
    df["earnings_ci_high"] = pd.NA
    df["prob_pass_state"] = pd.NA
    df["prob_pass_local"] = pd.NA
    df["estimated_risk_level"] = pd.NA
    df["estimation_method"] = pd.NA

    # Build priors and factors
    priors = build_national_cip_priors(df)
    inst_effects = compute_institution_effects(ep)
    geo_factors = compute_geographic_factors(df)

    if priors.empty:
        print("  No priors available — skipping simulation")
        return df

    # Get suppressed programs
    suppressed_mask = df["earnings_suppressed"] == True  # noqa: E712
    suppressed = df.loc[suppressed_mask].copy()
    print(f"  Suppressed programs to simulate: {len(suppressed):,}")

    if suppressed.empty:
        return df

    # Preserve original df index through merges
    suppressed["_orig_idx"] = suppressed.index

    # Merge priors and factors
    suppressed = suppressed.merge(
        priors[["cipcode", "credential_level", "national_median", "national_std",
                "cip_median", "cip_std", "n_observed"]],
        on=["cipcode", "credential_level"],
        how="left",
    )
    suppressed = suppressed.merge(inst_effects, on="UNITID", how="left")
    suppressed = suppressed.merge(geo_factors, on="UNITID", how="left")

    suppressed["institution_effect"] = suppressed["institution_effect"].fillna(1.0)
    suppressed["geo_factor"] = suppressed["geo_factor"].fillna(1.0)

    # CIP-only fallback
    no_prior = suppressed["national_median"].isna()
    if no_prior.any():
        suppressed.loc[no_prior, "national_median"] = suppressed.loc[no_prior, "cip_median"]
        suppressed.loc[no_prior, "national_std"] = suppressed.loc[no_prior, "cip_std"]

    has_prior = suppressed["national_median"].notna()
    estimable = suppressed[has_prior]
    n_estimable = len(estimable)
    n_inestimable = (~has_prior).sum()
    print(f"  Estimable: {n_estimable:,} | Inestimable: {n_inestimable:,}")

    if n_estimable > 0:
        rng = np.random.default_rng(42)
        n_sims = 1000

        medians = estimable["national_median"].values
        stds = estimable["national_std"].values
        inst_effs = estimable["institution_effect"].values
        geo_facs = estimable["geo_factor"].values

        sigma_rel = np.minimum(stds / np.maximum(medians, 1), 0.5)
        noise = rng.normal(1.0, sigma_rel[:, np.newaxis], size=(n_estimable, n_sims))
        draws = medians[:, np.newaxis] * inst_effs[:, np.newaxis] * geo_facs[:, np.newaxis] * noise
        draws = np.maximum(draws, 0)

        point_estimates = np.median(draws, axis=1)
        ci_low = np.percentile(draws, 10, axis=1)
        ci_high = np.percentile(draws, 90, axis=1)

        # Probability of passing
        thresholds = estimable["state_threshold"].values
        valid_thresh = ~np.isnan(thresholds)
        prob_pass_state = np.full(n_estimable, np.nan)
        if valid_thresh.any():
            prob_pass_state[valid_thresh] = (
                draws[valid_thresh] >= thresholds[valid_thresh, np.newaxis]
            ).mean(axis=1)

        county_earnings = estimable["county_hs_earnings"].values if "county_hs_earnings" in estimable.columns else np.full(n_estimable, np.nan)
        valid_county = ~np.isnan(county_earnings)
        prob_pass_local = np.full(n_estimable, np.nan)
        if valid_county.any():
            prob_pass_local[valid_county] = (
                draws[valid_county] >= county_earnings[valid_county, np.newaxis]
            ).mean(axis=1)

        # Estimated risk level based on point estimate vs threshold
        est_margin = np.full(n_estimable, np.nan)
        if valid_thresh.any():
            est_margin[valid_thresh] = (
                (point_estimates[valid_thresh] - thresholds[valid_thresh])
                / thresholds[valid_thresh] * 100
            )

        est_risk = np.where(
            np.isnan(est_margin), "Privacy Suppressed",
            np.where(est_margin >= 50, "Very Low Risk",
            np.where(est_margin >= 20, "Low Risk",
            np.where(est_margin >= 0, "Moderate Risk", "High Risk")))
        )

        # Write back to main DataFrame using preserved original index
        idx = estimable["_orig_idx"].values
        df.loc[idx, "estimated_earnings"] = np.round(point_estimates).astype(int)
        df.loc[idx, "earnings_ci_low"] = np.round(ci_low).astype(int)
        df.loc[idx, "earnings_ci_high"] = np.round(ci_high).astype(int)
        df.loc[idx, "prob_pass_state"] = np.round(prob_pass_state, 3)
        df.loc[idx, "prob_pass_local"] = np.round(prob_pass_local, 3)
        df.loc[idx, "estimated_risk_level"] = est_risk
        df.loc[idx, "estimation_method"] = "national_cip_prior"

    # Mark inestimable
    inestimable_idx = suppressed.loc[~has_prior, "_orig_idx"].values
    if len(inestimable_idx) > 0:
        df.loc[inestimable_idx, "estimation_method"] = "no_estimate"

    # Summary
    est_risk_counts = df.loc[df["estimated_risk_level"].notna(), "estimated_risk_level"].value_counts()
    print(f"\n  Estimated risk distribution (from simulation):")
    for level in ["Very Low Risk", "Low Risk", "Moderate Risk", "High Risk"]:
        count = est_risk_counts.get(level, 0)
        print(f"    {level}: {count:,}")

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Build enriched program-level analysis dataset"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Program Dataset Builder")
    print("=" * 60)

    # Load inputs
    print("\nLoading input datasets...")
    fos, ipeds, ep = load_inputs(DATA_DIR)

    # Step 1: Merge IPEDS completions (if available)
    if ipeds is not None:
        print("\nMerging IPEDS completions...")
        programs = merge_ipeds_completions(fos, ipeds)
    else:
        programs = fos.copy()

    # Step 2: Merge institution context
    print("\nMerging institution context...")
    programs = merge_institution_context(programs, ep)

    # Step 3: Compute EP test outcomes
    print("\nComputing EP test outcomes...")
    programs = compute_ep_test(programs)

    # Normalize cipcode to dotted format (XX.XX) for consistency
    programs["cipcode"] = programs["cipcode"].apply(normalize_cip4)

    # Step 4: Monte Carlo simulation for suppressed programs
    print("\nRunning Monte Carlo simulation for suppressed programs...")
    programs = run_simulation(programs, ep)

    # Step 5: Clean up and select final columns
    final_cols = [
        "UNITID", "institution", "state", "sector_name",
        "cipcode", "cip_desc", "credential_level", "credential_desc",
        "completions", "program_earnings", "earnings_timeframe",
        "earnings_suppressed", "state_threshold",
        "institution_earnings", "earnings_margin_pct",
        "pass_state", "pass_county", "risk_level",
        "estimated_earnings", "earnings_ci_low", "earnings_ci_high",
        "prob_pass_state", "prob_pass_local", "estimated_risk_level",
        "estimation_method",
    ]

    # Add optional columns if present
    for col in ["county_fips", "county", "county_hs_earnings",
                "ipeds_completions", "n_6digit_programs",
                "earn_mdn_1yr", "earn_mdn_2yr", "earn_mdn_4yr", "earn_mdn_5yr"]:
        if col in programs.columns:
            final_cols.append(col)

    programs = programs[[c for c in final_cols if c in programs.columns]]

    # Sort
    programs = programs.sort_values(["state", "UNITID", "cipcode"]).reset_index(drop=True)

    # Save
    output_path = DATA_DIR / "program_analysis.parquet"
    programs.to_parquet(output_path, index=False)
    print(f"\n  Saved to {output_path}")

    # Final summary
    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)
    print(f"\n  {len(programs):,} program records")
    print(f"  {programs['UNITID'].nunique():,} institutions")
    print(f"  {programs['cipcode'].nunique()} CIP codes")
    print(f"  {programs['program_earnings'].notna().sum():,} with earnings")
    print(f"  {programs['earnings_suppressed'].sum():,} suppressed")

    if "completions" in programs.columns:
        total_comp = programs["completions"].sum()
        print(f"  {total_comp:,} total completions across all programs")

    # Top CIP codes at risk
    at_risk = programs[programs["risk_level"] == "High Risk"]
    if len(at_risk) > 0:
        top_risk_cips = (
            at_risk.groupby(["cipcode", "cip_desc"])
            .size()
            .sort_values(ascending=False)
            .head(10)
        )
        print(f"\n  Top 10 CIP codes with High Risk programs:")
        for (cip, desc), count in top_risk_cips.items():
            print(f"    {cip} {desc}: {count} programs")


if __name__ == "__main__":
    main()
