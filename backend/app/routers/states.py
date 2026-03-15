"""State-level endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
import pandas as pd

from ..data.loader import load_ep_analysis
from ..models.schemas import StateSummary, StateDetail, InstitutionBrief
from ..services.risk import risk_distribution, get_state_name, VALID_STATES

router = APIRouter(prefix="/api/states", tags=["states"])


def _safe(val):
    """Convert pandas/numpy value to Python native, handling NaN."""
    if pd.isna(val):
        return None
    if hasattr(val, "item"):
        return val.item()
    return val


@router.get("", response_model=list[StateSummary])
def list_states():
    df = load_ep_analysis()
    df = df[df["STABBR"].isin(VALID_STATES)]
    results = []
    for state, group in df.groupby("STABBR"):
        threshold = group["Threshold"].dropna()
        results.append(StateSummary(
            state=str(state),
            state_name=get_state_name(str(state)),
            threshold=float(threshold.iloc[0]) if len(threshold) > 0 else 0,
            institution_count=len(group),
            risk_distribution=risk_distribution(group),
        ))
    results.sort(key=lambda s: s.state)
    return results


@router.get("/{state}", response_model=StateDetail)
def get_state(state: str):
    state = state.upper()
    if state not in VALID_STATES:
        raise HTTPException(404, f"State '{state}' not found")

    df = load_ep_analysis()
    state_df = df[df["STABBR"] == state]
    if state_df.empty:
        raise HTTPException(404, f"No data for state '{state}'")

    threshold = state_df["Threshold"].dropna()
    threshold_val = float(threshold.iloc[0]) if len(threshold) > 0 else 0

    institutions = []
    for _, row in state_df.iterrows():
        institutions.append(InstitutionBrief(
            unit_id=int(row["UnitID"]),
            name=str(row["institution"]),
            state=str(row["STABBR"]),
            sector=_safe(row.get("sector_name")),
            enrollment=_safe(row.get("enrollment")),
            median_earnings=_safe(row.get("median_earnings")),
            threshold=_safe(row.get("Threshold")),
            earnings_margin_pct=_safe(row.get("earnings_margin_pct")),
            risk_level=str(row["risk_level"]),
            total_programs=_safe(row.get("total_programs")),
        ))

    margins = state_df["earnings_margin_pct"].dropna().tolist()

    return StateDetail(
        state=state,
        state_name=get_state_name(state),
        threshold=threshold_val,
        institution_count=len(state_df),
        risk_distribution=risk_distribution(state_df),
        institutions=institutions,
        margin_histogram=[float(m) for m in margins],
    )
