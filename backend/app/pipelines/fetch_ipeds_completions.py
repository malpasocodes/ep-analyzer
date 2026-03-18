"""Fetch program-level completion counts from IPEDS Completions survey.

Downloads the IPEDS Completions "A" table (awards by CIP code and award level),
which has 6-digit CIP codes, award levels, and completion counts per institution.

Usage:
    python -m backend.app.pipelines.fetch_ipeds_completions
    python -m backend.app.pipelines.fetch_ipeds_completions --year 2023
    python -m backend.app.pipelines.fetch_ipeds_completions --local /path/to/c2023_a.csv
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

# NCES IPEDS completions data URL pattern
# The "A" table has awards by CIP code and award level
# Format: C{YEAR}_A.zip containing c{year}_a.csv
IPEDS_URL_TEMPLATE = (
    "https://nces.ed.gov/ipeds/datacenter/data/C{year}_A.zip"
)

# Award level mapping (AWLEVEL column in IPEDS completions)
AWARD_LEVEL_MAP = {
    1: "Postsecondary award, certificate, or diploma (< 1 year)",
    2: "Postsecondary award, certificate, or diploma (1-2 years)",
    3: "Associate's degree",
    4: "Postsecondary award, certificate, or diploma (2-4 years)",
    5: "Bachelor's degree",
    6: "Postbaccalaureate certificate",
    7: "Master's degree",
    8: "Post-master's certificate",
    9: "Doctor's degree - research/scholarship",
    10: "Doctor's degree - professional practice",
    11: "Doctor's degree - other",
    12: "Other award",
}

# Map IPEDS AWLEVEL to Scorecard CREDLEV for joining
AWLEVEL_TO_CREDLEV = {
    1: 1,   # < 1 year cert -> Undergrad Certificate
    2: 1,   # 1-2 year cert -> Undergrad Certificate
    3: 2,   # Associate's -> Associate's
    4: 1,   # 2-4 year cert -> Undergrad Certificate
    5: 3,   # Bachelor's -> Bachelor's
    6: 4,   # Post-bacc cert -> Post-bacc Certificate
    7: 5,   # Master's -> Master's
    8: 8,   # Post-master's cert -> Graduate Certificate
    9: 6,   # Doctoral research -> Doctoral
    10: 7,  # Doctoral professional -> First Professional
    11: 6,  # Doctoral other -> Doctoral
    12: 1,  # Other -> Undergrad Certificate (catch-all)
}


def download_ipeds_completions(year: int = 2023) -> pd.DataFrame:
    """Download and extract the IPEDS Completions A table."""
    url = IPEDS_URL_TEMPLATE.format(year=year)
    print(f"Downloading IPEDS Completions data for {year}...")
    print(f"  URL: {url}")

    req = Request(url, headers={"User-Agent": "ep-analyzer/1.0"})
    try:
        with urlopen(req, timeout=120) as resp:
            data = resp.read()
    except HTTPError as e:
        raise RuntimeError(
            f"Failed to download IPEDS completions: HTTP {e.code}\n"
            f"Try a different year with --year, or download manually from\n"
            f"https://nces.ed.gov/ipeds/use-the-data"
        ) from e

    print(f"  Downloaded {len(data) / 1024 / 1024:.1f} MB")

    # Extract CSV from ZIP
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            raise RuntimeError(f"No CSV found in ZIP. Contents: {zf.namelist()}")

        # Prefer the main data file (not the dictionary/metadata)
        data_csvs = [n for n in csv_names if "_a" in n.lower() and "dict" not in n.lower() and "rv" not in n.lower()]
        csv_name = data_csvs[0] if data_csvs else csv_names[0]
        print(f"  Extracting {csv_name}...")
        with zf.open(csv_name) as f:
            df = pd.read_csv(f, encoding="utf-8-sig", low_memory=False)

    print(f"  Raw records: {len(df):,}")
    print(f"  Columns: {list(df.columns)[:15]}...")
    return df


def process_ipeds_completions(raw: pd.DataFrame) -> pd.DataFrame:
    """Clean and aggregate IPEDS completions data."""
    # Standardize column names to uppercase
    raw.columns = raw.columns.str.upper()

    # Required columns
    required = ["UNITID", "CIPCODE", "AWLEVEL", "CTOTALT"]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Available: {list(raw.columns)[:20]}")

    df = raw.copy()

    # Filter: first major only (MAJORNUM=1) if column exists
    if "MAJORNUM" in df.columns:
        before = len(df)
        df = df[df["MAJORNUM"] == 1]
        print(f"  Filtered to first major: {before:,} -> {len(df):,}")

    # Filter: exclude aggregate CIP codes (99.xxxx = grand total rows)
    df["CIPCODE"] = df["CIPCODE"].astype(str).str.strip()
    before = len(df)
    df = df[~df["CIPCODE"].str.startswith("99")]
    print(f"  Excluded aggregate CIP 99: {before:,} -> {len(df):,}")

    # Convert types
    df["UNITID"] = pd.to_numeric(df["UNITID"], errors="coerce")
    df["AWLEVEL"] = pd.to_numeric(df["AWLEVEL"], errors="coerce")
    df["CTOTALT"] = pd.to_numeric(df["CTOTALT"], errors="coerce").fillna(0).astype(int)

    # Optional demographic columns
    demo_cols = {}
    for col in ["CTOTALM", "CTOTALW"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            demo_cols[col] = col.lower()

    # Drop rows with invalid UNITID or AWLEVEL
    df = df.dropna(subset=["UNITID", "AWLEVEL"])
    df["UNITID"] = df["UNITID"].astype(int)
    df["AWLEVEL"] = df["AWLEVEL"].astype(int)

    # Create 4-digit CIP code (for joining with Scorecard)
    # IPEDS CIP is 6-digit like "11.0101", Scorecard uses 4-digit "11.01"
    df["cipcode_6"] = df["CIPCODE"]
    df["cipcode_4"] = df["CIPCODE"].str[:5]  # "11.0101" -> "11.01"

    # Add award level description
    df["award_desc"] = df["AWLEVEL"].map(AWARD_LEVEL_MAP).fillna("Unknown")

    # Map to Scorecard credential level
    df["credential_level"] = df["AWLEVEL"].map(AWLEVEL_TO_CREDLEV)

    # Summary before aggregation
    print(f"\n  Programs (institution-CIP-award): {len(df):,}")
    print(f"  Unique institutions: {df['UNITID'].nunique():,}")
    print(f"  Unique 6-digit CIPs: {df['cipcode_6'].nunique()}")
    print(f"  Unique 4-digit CIPs: {df['cipcode_4'].nunique()}")
    print(f"  Total completions: {df['CTOTALT'].sum():,}")

    # Select output columns
    output_cols = [
        "UNITID", "cipcode_6", "cipcode_4", "AWLEVEL", "award_desc",
        "credential_level", "CTOTALT",
    ]
    if "CTOTALM" in df.columns:
        output_cols.append("CTOTALM")
    if "CTOTALW" in df.columns:
        output_cols.append("CTOTALW")

    result = df[output_cols].rename(columns={
        "CTOTALT": "total_completions",
        "CTOTALM": "male_completions",
        "CTOTALW": "female_completions",
        "AWLEVEL": "award_level",
    })

    return result.reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch IPEDS Completions data by CIP code"
    )
    parser.add_argument(
        "--year", type=int, default=2023,
        help="IPEDS collection year (default: 2023)"
    )
    parser.add_argument(
        "--local", type=str, default=None,
        help="Path to already-downloaded CSV (skip download)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("IPEDS Completions Pipeline")
    print("=" * 60)

    # Step 1: Get raw data
    if args.local:
        print(f"\nLoading local file: {args.local}")
        raw = pd.read_csv(args.local, encoding="utf-8-sig", low_memory=False)
        print(f"  Raw records: {len(raw):,}")
    else:
        raw = download_ipeds_completions(args.year)

    # Step 2: Process
    print("\nProcessing...")
    df = process_ipeds_completions(raw)

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
    output_path = DATA_DIR / "ipeds_completions.parquet"
    df.to_parquet(output_path, index=False)
    print(f"\n  Saved to {output_path}")

    # Summary
    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)
    print(f"\n  {len(df):,} program-award records")
    print(f"  {df['UNITID'].nunique():,} institutions")
    print(f"  {df['cipcode_6'].nunique()} unique 6-digit CIP codes")
    print(f"  {df['cipcode_4'].nunique()} unique 4-digit CIP codes")
    print(f"  {df['total_completions'].sum():,} total completions")

    # Top CIP codes by completions
    top = (
        df.groupby("cipcode_4")["total_completions"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    print(f"\n  Top 10 CIP codes by completions:")
    for cip, count in top.items():
        print(f"    {cip}: {count:,}")


if __name__ == "__main__":
    main()
