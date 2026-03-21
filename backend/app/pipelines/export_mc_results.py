"""Export per-program Monte Carlo estimates to CSV for local analysis.

The output file contains individual program risk estimates and is NOT
intended for public distribution (privacy of small cohorts).

Usage:
    python -m backend.app.pipelines.export_mc_results
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"

EXPORT_COLS = [
    "UNITID", "institution", "state", "sector_name",
    "cipcode", "cip_desc", "credential_level", "credential_desc",
    "completions", "state_threshold", "county_hs_earnings",
    "estimated_earnings", "earnings_ci_low", "earnings_ci_high",
    "prob_pass_state", "prob_pass_local", "estimated_risk_level",
    "estimation_method",
]


def main():
    path = DATA_DIR / "program_analysis.parquet"
    if not path.exists():
        print(f"Error: {path} not found. Run build_program_dataset first.")
        return

    print("Loading program analysis...")
    df = pd.read_parquet(path)

    # Filter to suppressed programs with MC estimates
    est = df[df["earnings_suppressed"] & df["estimated_earnings"].notna()]
    cols = [c for c in EXPORT_COLS if c in est.columns]
    out = est[cols].sort_values(["state", "UNITID", "cipcode"]).reset_index(drop=True)

    output_path = DATA_DIR / "mc_program_estimates.csv"
    out.to_csv(output_path, index=False)

    print(f"\nExported {len(out):,} program estimates to {output_path}")
    print(f"  States: {out['state'].nunique()}")
    print(f"  Institutions: {out['UNITID'].nunique():,}")
    print(f"  CIP codes: {out['cipcode'].nunique()}")
    print()
    print("Risk distribution:")
    print(out["estimated_risk_level"].value_counts().to_string())


if __name__ == "__main__":
    main()
