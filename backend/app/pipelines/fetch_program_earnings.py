"""Fetch program-level earnings from College Scorecard Field-of-Study data.

Downloads the bulk "Most Recent Cohorts - Field of Study" dataset, which
contains earnings by institution + 4-digit CIP code + credential level.

~75% of program-level earnings are privacy-suppressed (<30 student cohort).

Usage:
    python -m backend.app.pipelines.fetch_program_earnings
    python -m backend.app.pipelines.fetch_program_earnings --url <custom_url>
"""

from __future__ import annotations

import argparse
import io
import sys
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"

# College Scorecard bulk download — Field of Study level
# Updated periodically; check https://collegescorecard.ed.gov/data/ for latest
SCORECARD_FOS_URL = (
    "https://ed-public-download.scorecard.network/downloads/"
    "Most-Recent-Cohorts-Field-of-Study_04172025.zip"
)

# Columns to extract from the ~300+ column Scorecard FoS file
KEEP_COLUMNS = {
    "UNITID": "UNITID",
    "OPEID6": "opeid6",
    "INSTNM": "institution",
    "CIPCODE": "cipcode",
    "CIPDESC": "cip_desc",
    "CREDLEV": "credential_level",
    "CREDDESC": "credential_desc",
    "IPEDSCOUNT1": "completions_yr1",
    "IPEDSCOUNT2": "completions_yr2",
    "EARN_MDN_HI_1YR": "earn_mdn_1yr",
    "EARN_MDN_HI_2YR": "earn_mdn_2yr",
    "EARN_MDN_4YR": "earn_mdn_4yr",
    "EARN_MDN_5YR": "earn_mdn_5yr",
}

# Fallback column names — Scorecard has changed naming across releases
EARNINGS_FALLBACKS = {
    "earn_mdn_1yr": ["EARN_MDN_HI_1YR", "EARN_MDN_1YR", "MD_EARN_WNE_INDEP0_P6"],
    "earn_mdn_2yr": ["EARN_MDN_HI_2YR", "EARN_MDN_2YR", "MD_EARN_WNE_INDEP1_P6"],
    "earn_mdn_4yr": ["EARN_MDN_4YR", "EARN_MDN_HI_4YR"],
    "earn_mdn_5yr": ["EARN_MDN_5YR", "EARN_MDN_HI_5YR"],
}


def download_scorecard_fos(url: str = SCORECARD_FOS_URL) -> pd.DataFrame:
    """Download and extract the Scorecard Field-of-Study CSV from a ZIP."""
    print(f"Downloading College Scorecard Field-of-Study data...")
    print(f"  URL: {url[:80]}...")

    req = Request(url, headers={"User-Agent": "ep-analyzer/1.0"})
    try:
        with urlopen(req, timeout=120) as resp:
            data = resp.read()
    except HTTPError as e:
        raise RuntimeError(
            f"Failed to download Scorecard FoS data: HTTP {e.code}\n"
            f"URL may have changed — check https://collegescorecard.ed.gov/data/"
        ) from e

    print(f"  Downloaded {len(data) / 1024 / 1024:.1f} MB")

    # Extract CSV from ZIP
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        csv_names = [n for n in zf.namelist() if n.endswith(".csv")]
        if not csv_names:
            raise RuntimeError(f"No CSV found in ZIP. Contents: {zf.namelist()}")
        csv_name = csv_names[0]
        print(f"  Extracting {csv_name}...")
        with zf.open(csv_name) as f:
            df = pd.read_csv(f, dtype=str, low_memory=False)

    print(f"  Raw records: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")
    return df


def process_scorecard_fos(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean and select columns from the raw Scorecard FoS data."""
    # Find available columns (Scorecard naming varies across releases)
    available = set(raw.columns)
    print(f"\n  Selecting columns...")

    # Build column mapping from what's available
    col_map = {}
    for target, source in KEEP_COLUMNS.items():
        if target in available:
            col_map[target] = source
        else:
            print(f"    Warning: {target} not found in data")

    # Handle earnings columns with fallbacks
    for target_name, candidates in EARNINGS_FALLBACKS.items():
        found = False
        for candidate in candidates:
            if candidate in available:
                col_map[candidate] = target_name
                found = True
                print(f"    Using {candidate} for {target_name}")
                break
        if not found:
            print(f"    Warning: No column found for {target_name}")

    # Select and rename
    select_cols = [c for c in col_map if c in available]
    df = raw[select_cols].rename(columns=col_map).copy()

    # Convert types
    df["UNITID"] = pd.to_numeric(df["UNITID"], errors="coerce").astype("Int64")
    df["credential_level"] = pd.to_numeric(df["credential_level"], errors="coerce").astype("Int64")

    for col in ["completions_yr1", "completions_yr2"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Handle earnings: detect "PrivacySuppressed" before numeric conversion
    all_earn_cols = [c for c in ["earn_mdn_1yr", "earn_mdn_2yr", "earn_mdn_4yr", "earn_mdn_5yr"] if c in df.columns]
    suppressed_any = pd.Series(False, index=df.index)
    for col in all_earn_cols:
        suppressed_mask = df[col].astype(str).str.strip().str.lower() == "privacysuppressed"
        suppressed_any = suppressed_any | suppressed_mask
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Compute best available earnings (prefer 4yr > 5yr > 2yr > 1yr)
    # 4yr is the default — closest to mid-career while still available for
    # most recent cohorts. Falls back through 5yr, 2yr, 1yr as needed.
    preference_order = [
        ("earn_mdn_4yr", "4yr"),
        ("earn_mdn_5yr", "5yr"),
        ("earn_mdn_2yr", "2yr"),
        ("earn_mdn_1yr", "1yr"),
    ]
    available_earn = [(col, label) for col, label in preference_order if col in df.columns]

    if available_earn:
        # Start with the highest-priority column
        best_col, best_label = available_earn[0]
        df["program_earnings"] = df[best_col].copy()
        df["earnings_timeframe"] = pd.Series(None, index=df.index, dtype="object")
        df.loc[df["program_earnings"].notna(), "earnings_timeframe"] = best_label

        # Fill from lower-priority columns
        for col, label in available_earn[1:]:
            missing = df["program_earnings"].isna() & df[col].notna()
            df.loc[missing, "program_earnings"] = df.loc[missing, col]
            df.loc[missing, "earnings_timeframe"] = label

        df.loc[df["program_earnings"].isna(), "earnings_timeframe"] = None
    else:
        df["program_earnings"] = pd.NA
        df["earnings_timeframe"] = None

    # Suppressed = had PrivacySuppressed flag OR has no earnings despite having
    # completions (Scorecard suppresses programs with <30 students in cohort)
    has_completions = False
    for col in ["completions_yr1", "completions_yr2"]:
        if col in df.columns:
            has_completions = has_completions | (df[col].notna() & (df[col] > 0))
    df["earnings_suppressed"] = (
        suppressed_any | (df["program_earnings"].isna() & has_completions)
    )

    # Compute average completions
    comp_cols = [c for c in ["completions_yr1", "completions_yr2"] if c in df.columns]
    if comp_cols:
        df["completions"] = df[comp_cols].mean(axis=1).round().astype("Int64")
    else:
        df["completions"] = pd.NA

    # Drop rows without a UNITID or CIP code
    df = df.dropna(subset=["UNITID", "cipcode"])
    df["UNITID"] = df["UNITID"].astype(int)

    # Clean CIP codes — ensure 4-digit XX.XX format
    df["cipcode"] = df["cipcode"].str.strip()

    # Summary
    total = len(df)
    with_earnings = df["program_earnings"].notna().sum()
    suppressed = df["earnings_suppressed"].sum()
    print(f"\n  Processed: {total:,} programs")
    print(f"  With earnings: {with_earnings:,} ({with_earnings/total*100:.1f}%)")
    print(f"  Suppressed: {suppressed:,} ({suppressed/total*100:.1f}%)")
    if with_earnings > 0:
        print(f"  Earnings range: ${df['program_earnings'].min():,.0f} - ${df['program_earnings'].max():,.0f}")
        print(f"  Median: ${df['program_earnings'].median():,.0f}")

    # Unique CIP codes and credential levels
    print(f"  Unique CIP codes: {df['cipcode'].nunique()}")
    print(f"  Unique institutions: {df['UNITID'].nunique()}")

    # Select final columns
    final_cols = [
        "UNITID", "institution", "cipcode", "cip_desc",
        "credential_level", "credential_desc", "completions",
        "program_earnings", "earnings_timeframe", "earnings_suppressed",
    ]
    # Add raw earnings if available (all timeframes for comparative analysis)
    for col in ["earn_mdn_1yr", "earn_mdn_2yr", "earn_mdn_4yr", "earn_mdn_5yr"]:
        if col in df.columns:
            final_cols.append(col)

    return df[[c for c in final_cols if c in df.columns]]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch College Scorecard Field-of-Study program earnings"
    )
    parser.add_argument(
        "--url", type=str, default=SCORECARD_FOS_URL,
        help="Override download URL (if Scorecard URL has changed)"
    )
    parser.add_argument(
        "--local", type=str, default=None,
        help="Path to already-downloaded CSV (skip download)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("College Scorecard Field-of-Study Pipeline")
    print("=" * 60)

    # Step 1: Get raw data
    if args.local:
        print(f"\nLoading local file: {args.local}")
        raw = pd.read_csv(args.local, dtype=str, low_memory=False)
        print(f"  Raw records: {len(raw):,}")
    else:
        raw = download_scorecard_fos(args.url)

    # Step 2: Process
    print("\nProcessing...")
    df = process_scorecard_fos(raw)

    # Step 3: Filter to institutions in our EP analysis dataset
    ep_path = DATA_DIR / "ep_analysis_enriched.parquet"
    if not ep_path.exists():
        ep_path = DATA_DIR / "ep_analysis.parquet"

    if ep_path.exists():
        ep = pd.read_parquet(ep_path, columns=["UnitID"])
        ep_unitids = set(ep["UnitID"].dropna().astype(int))
        before = len(df)
        df = df[df["UNITID"].isin(ep_unitids)]
        print(f"\n  Filtered to EP analysis institutions: {before:,} -> {len(df):,}")
    else:
        print(f"\n  Warning: {ep_path} not found, keeping all institutions")

    # Step 4: Save
    output_path = DATA_DIR / "scorecard_fos_earnings.parquet"
    df.to_parquet(output_path, index=False)
    print(f"\n  Saved to {output_path}")

    # Summary
    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)
    print(f"\n  {len(df):,} program records")
    print(f"  {df['program_earnings'].notna().sum():,} with earnings data")
    print(f"  {df['UNITID'].nunique():,} institutions")
    print(f"  {df['cipcode'].nunique()} CIP codes")


if __name__ == "__main__":
    main()
