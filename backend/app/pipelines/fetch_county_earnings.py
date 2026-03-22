"""Fetch county-level HS graduate median earnings from Census ACS API.

Uses table B20004_003E (Median Earnings, HS graduate including equivalency,
population 25+) from the ACS 5-Year estimates for all U.S. counties.

Also fetches state-level Bachelor's degree median earnings (B20004_005E)
for use as graduate program thresholds.

Usage:
    python -m backend.app.pipelines.fetch_county_earnings
    python -m backend.app.pipelines.fetch_county_earnings --year 2022
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"

# ACS 5-Year API base
ACS_BASE = "https://api.census.gov/data/{year}/acs/acs5"

# B20004_003E = Median earnings, HS graduate (includes equivalency), 25+
# B20004_003M = Margin of error for the same
VARIABLES = "NAME,B20004_003E,B20004_003M"


def fetch_county_earnings(year: int = 2023, api_key: str | None = None) -> pd.DataFrame:
    """Fetch median HS graduate earnings for all U.S. counties.

    Args:
        year: ACS 5-year vintage (e.g., 2023 = 2019-2023 estimates).
        api_key: Census API key. Optional but recommended for higher rate limits.
            Get one free at https://api.census.gov/data/key_signup.html

    Returns:
        DataFrame with columns: county_fips, state_fips, county_name,
        hs_median_earnings, margin_of_error
    """
    url = (
        f"{ACS_BASE.format(year=year)}"
        f"?get={VARIABLES}"
        f"&for=county:*&in=state:*"
    )
    if api_key:
        url += f"&key={api_key}"

    print(f"Fetching ACS {year} 5-Year county earnings data...")
    print(f"  URL: {url[:80]}...")

    # Retry with exponential backoff
    for attempt in range(4):
        try:
            req = Request(url, headers={"User-Agent": "ep-analyzer/1.0"})
            with urlopen(req, timeout=60) as resp:
                raw = json.loads(resp.read().decode())
            break
        except HTTPError as e:
            if attempt < 3:
                wait = 2 ** (attempt + 1)
                print(f"  Attempt {attempt + 1} failed ({e.code}), retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Census API failed after 4 attempts: {e}") from e

    # First row is headers
    headers = raw[0]
    rows = raw[1:]

    df = pd.DataFrame(rows, columns=headers)

    # Build 5-digit county FIPS
    df["county_fips"] = df["state"].str.zfill(2) + df["county"].str.zfill(3)
    df["state_fips"] = df["state"].str.zfill(2)

    # Rename and convert types
    df = df.rename(columns={
        "NAME": "county_name",
        "B20004_003E": "hs_median_earnings",
        "B20004_003M": "margin_of_error",
    })

    # Convert to numeric (some counties may have null/-666666666 for suppressed data)
    df["hs_median_earnings"] = pd.to_numeric(df["hs_median_earnings"], errors="coerce")
    df["margin_of_error"] = pd.to_numeric(df["margin_of_error"], errors="coerce")

    # Drop rows with suppressed/missing earnings
    total = len(df)
    df = df[df["hs_median_earnings"].notna() & (df["hs_median_earnings"] > 0)]
    dropped = total - len(df)

    df = df[["county_fips", "state_fips", "county_name", "hs_median_earnings", "margin_of_error"]]
    df = df.sort_values("county_fips").reset_index(drop=True)

    print(f"  Fetched {total} counties, {dropped} suppressed/missing, {len(df)} usable")
    print(f"  Earnings range: ${df['hs_median_earnings'].min():,.0f} - ${df['hs_median_earnings'].max():,.0f}")
    print(f"  Median: ${df['hs_median_earnings'].median():,.0f}")

    return df


def fetch_state_bachelor_earnings(year: int = 2023, api_key: str | None = None) -> pd.DataFrame:
    """Fetch median Bachelor's degree earnings for all U.S. states.

    Uses B20004_005E (Median Earnings, Bachelor's degree, population 25+).
    These serve as the EP test threshold for graduate-level programs
    (credential levels 4-8: post-bac certificates, Master's, Doctoral,
    First Professional, and Graduate/Professional certificates).

    Args:
        year: ACS 5-year vintage (e.g., 2023 = 2019-2023 estimates).
        api_key: Census API key (optional).

    Returns:
        DataFrame with columns: state_fips, state_name,
        bachelor_median_earnings, bachelor_margin_of_error
    """
    variables = "NAME,B20004_005E,B20004_005M"
    url = (
        f"{ACS_BASE.format(year=year)}"
        f"?get={variables}"
        f"&for=state:*"
    )
    if api_key:
        url += f"&key={api_key}"

    print(f"Fetching ACS {year} 5-Year state-level Bachelor's degree earnings...")
    print(f"  URL: {url[:80]}...")

    for attempt in range(4):
        try:
            req = Request(url, headers={"User-Agent": "ep-analyzer/1.0"})
            with urlopen(req, timeout=60) as resp:
                raw = json.loads(resp.read().decode())
            break
        except HTTPError as e:
            if attempt < 3:
                wait = 2 ** (attempt + 1)
                print(f"  Attempt {attempt + 1} failed ({e.code}), retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Census API failed after 4 attempts: {e}") from e

    headers = raw[0]
    rows = raw[1:]
    df = pd.DataFrame(rows, columns=headers)

    df["state_fips"] = df["state"].str.zfill(2)
    df = df.rename(columns={
        "NAME": "state_name",
        "B20004_005E": "bachelor_median_earnings",
        "B20004_005M": "bachelor_margin_of_error",
    })

    df["bachelor_median_earnings"] = pd.to_numeric(df["bachelor_median_earnings"], errors="coerce")
    df["bachelor_margin_of_error"] = pd.to_numeric(df["bachelor_margin_of_error"], errors="coerce")

    total = len(df)
    df = df[df["bachelor_median_earnings"].notna() & (df["bachelor_median_earnings"] > 0)]
    dropped = total - len(df)

    df = df[["state_fips", "state_name", "bachelor_median_earnings", "bachelor_margin_of_error"]]
    df = df.sort_values("state_fips").reset_index(drop=True)

    print(f"  Fetched {total} states, {dropped} suppressed/missing, {len(df)} usable")
    print(f"  Earnings range: ${df['bachelor_median_earnings'].min():,.0f} - ${df['bachelor_median_earnings'].max():,.0f}")
    print(f"  Median: ${df['bachelor_median_earnings'].median():,.0f}")

    return df


def build_institution_county_mapping() -> pd.DataFrame:
    """Build UnitID -> county FIPS mapping from IPEDS institutions data.

    Tries to load from edu-accountability IPEDS data, falls back to
    scorecard data if available.
    """
    # Try IPEDS institutions file (has FIPS column = county FIPS)
    ipeds_paths = [
        DATA_DIR / "ipeds_institutions.csv",
        Path("/tmp/edu-accountability/data/raw/ipeds/2023/institutions.csv"),
    ]

    for path in ipeds_paths:
        if path.exists():
            print(f"  Loading institution-county mapping from {path.name}...")
            df = pd.read_csv(path, usecols=["UnitID", "INSTITUTION", "STATE", "FIPS"])
            df = df.rename(columns={"FIPS": "county_fips_raw"})
            df = df.dropna(subset=["county_fips_raw"])
            df = df[df["county_fips_raw"] > 0]
            df["county_fips"] = df["county_fips_raw"].astype(int).astype(str).str.zfill(5)
            df = df[["UnitID", "county_fips"]].drop_duplicates(subset=["UnitID"])
            print(f"  Mapped {len(df)} institutions to counties")
            return df

    raise FileNotFoundError(
        "IPEDS institutions file not found. Copy it to data/ipeds_institutions.csv"
    )


def main():
    parser = argparse.ArgumentParser(description="Fetch county-level HS earnings from Census ACS")
    parser.add_argument("--year", type=int, default=2023, help="ACS vintage year (default: 2023)")
    parser.add_argument("--api-key", type=str, default=None, help="Census API key (optional)")
    args = parser.parse_args()

    print("=" * 60)
    print("County-Level HS Graduate Earnings Pipeline")
    print("=" * 60)

    # Step 1: Fetch county HS earnings
    earnings = fetch_county_earnings(args.year, args.api_key)

    # Save county earnings
    output_path = DATA_DIR / "county_hs_earnings.csv"
    earnings.to_csv(output_path, index=False)
    print(f"\n  Saved to {output_path}")

    # Step 1b: Fetch state-level Bachelor's degree earnings (for graduate thresholds)
    print("\nFetching state-level Bachelor's degree earnings...")
    bachelor = fetch_state_bachelor_earnings(args.year, args.api_key)
    bachelor_path = DATA_DIR / "state_bachelor_earnings.csv"
    bachelor.to_csv(bachelor_path, index=False)
    print(f"  Saved to {bachelor_path}")

    # Step 2: Build institution-county mapping
    print("\nBuilding institution-county mapping...")
    try:
        mapping = build_institution_county_mapping()
        mapping_path = DATA_DIR / "institution_county_mapping.csv"
        mapping.to_csv(mapping_path, index=False)
        print(f"  Saved to {mapping_path}")
    except FileNotFoundError as e:
        print(f"  Warning: {e}")
        print("  Skipping mapping step. You can add it later.")
        mapping = None

    # Step 3: Merge and create enriched dataset
    if mapping is not None:
        print("\nMerging institution earnings with county benchmarks...")
        ep = pd.read_parquet(DATA_DIR / "ep_analysis.parquet")

        # Add county FIPS to ep_analysis
        ep = ep.merge(mapping, on="UnitID", how="left")

        # Add county earnings
        ep = ep.merge(
            earnings[["county_fips", "hs_median_earnings", "county_name"]],
            on="county_fips",
            how="left",
        )

        # Rename for clarity
        ep = ep.rename(columns={
            "hs_median_earnings": "county_hs_earnings",
            "county_name": "county",
        })

        matched = ep["county_hs_earnings"].notna().sum()
        total = len(ep)
        print(f"  {matched}/{total} institutions matched to county earnings ({matched/total*100:.1f}%)")

        # Save enriched dataset
        enriched_path = DATA_DIR / "ep_analysis_enriched.parquet"
        ep.to_parquet(enriched_path, index=False)
        print(f"  Saved enriched dataset to {enriched_path}")

    # Summary
    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)
    print(f"\nFiles created:")
    print(f"  data/county_hs_earnings.csv          ({len(earnings)} counties)")
    print(f"  data/state_bachelor_earnings.csv     ({len(bachelor)} states)")
    if mapping is not None:
        print(f"  data/institution_county_mapping.csv  ({len(mapping)} institutions)")
        print(f"  data/ep_analysis_enriched.parquet    ({total} institutions, {matched} with county data)")
    print(f"\nNote: B20004 covers ages 25+, not 25-34 specifically.")
    print(f"This is the best available pre-tabulated county/state-level data.")


if __name__ == "__main__":
    main()
