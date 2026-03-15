"""Risk classification and margin calculation helpers."""

from __future__ import annotations

import pandas as pd

STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}

# Only include the 50 states + DC for the dashboard
VALID_STATES = set(STATE_NAMES.keys())


def get_state_name(abbr: str) -> str:
    return STATE_NAMES.get(abbr, abbr)


def risk_distribution(df: pd.DataFrame) -> dict[str, int]:
    counts = df["risk_level"].value_counts().to_dict()
    return {k: int(v) for k, v in counts.items()}


def sector_distribution(df: pd.DataFrame) -> dict[str, int]:
    counts = df["sector_name"].value_counts(dropna=False).to_dict()
    result = {}
    for k, v in counts.items():
        key = str(k) if pd.notna(k) else "Unknown"
        result[key] = int(v)
    return result
