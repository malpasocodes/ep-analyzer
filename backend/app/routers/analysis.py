"""Analysis endpoints: reclassification, sensitivity, margins, early-vs-late."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from ..data.loader import load_ep_analysis, load_scorecard_earnings
from ..models.schemas import (
    ReclassificationResult,
    SensitivityResult,
    MarginDistribution,
    EarlyVsLate,
)
from ..services.benchmark import reclassify
from ..services.risk import VALID_STATES

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def _safe(val):
    if pd.isna(val):
        return None
    if hasattr(val, "item"):
        return val.item()
    return val


@router.get("/reclassification", response_model=ReclassificationResult)
def get_reclassification(
    state: str = Query(..., min_length=2, max_length=2),
    inequality: float = Query(0.5, ge=0, le=1),
    seed: int = 42,
):
    state = state.upper()
    if state not in VALID_STATES:
        raise HTTPException(404, f"State '{state}' not found")

    df = load_ep_analysis()
    result = reclassify(df, state, inequality, seed)
    if result.empty:
        raise HTTPException(404, f"No data for state '{state}'")

    counts = result["classification"].value_counts().to_dict()
    threshold = float(result["state_benchmark"].iloc[0])

    programs = result.to_dict(orient="records")
    # Convert numpy types to native Python
    for p in programs:
        for k, v in p.items():
            p[k] = _safe(v)

    # Count real vs synthetic benchmarks
    source_counts = result["benchmark_source"].value_counts().to_dict() if "benchmark_source" in result.columns else {}

    return ReclassificationResult(
        state=state,
        threshold=threshold,
        inequality=inequality,
        total_programs=len(result),
        pass_both=counts.get("Pass Both", 0),
        fail_both=counts.get("Fail Both", 0),
        pass_local_only=counts.get("Pass Local Only", 0),
        pass_state_only=counts.get("Pass State Only", 0),
        real_benchmark_count=source_counts.get("real", 0),
        synthetic_benchmark_count=source_counts.get("synthetic", 0),
        programs=programs,
    )


@router.get("/sensitivity", response_model=SensitivityResult)
def get_sensitivity(
    unit_id: int = Query(...),
    steps: int = Query(11, ge=3, le=21),
):
    df = load_ep_analysis()
    row = df[df["UnitID"] == unit_id]
    if row.empty:
        raise HTTPException(404, f"Institution {unit_id} not found")

    r = row.iloc[0]
    earnings = _safe(r.get("median_earnings"))
    threshold = _safe(r.get("Threshold"))

    scenarios = []
    if earnings is not None and threshold is not None:
        for pct in range(-50, 55, int(100 / (steps - 1))):
            adjusted = earnings * (1 + pct / 100)
            margin = (adjusted - threshold) / threshold * 100
            scenarios.append({
                "change_pct": pct,
                "adjusted_earnings": round(adjusted, 0),
                "margin_pct": round(margin, 1),
                "passes": adjusted >= threshold,
            })

    return SensitivityResult(
        unit_id=int(r["UnitID"]),
        name=str(r["institution"]),
        current_earnings=earnings,
        threshold=threshold,
        current_margin_pct=_safe(r.get("earnings_margin_pct")),
        scenarios=scenarios,
    )


@router.get("/margins", response_model=MarginDistribution)
def get_margins(
    state: Optional[str] = None,
    sector: Optional[str] = None,
):
    df = load_ep_analysis()
    df = df[df["STABBR"].isin(VALID_STATES)]

    if state:
        df = df[df["STABBR"] == state.upper()]
    if sector:
        df = df[df["sector_name"] == sector]

    margins = df["earnings_margin_pct"].dropna().tolist()
    risk_counts = df["risk_level"].value_counts().to_dict()
    near_threshold = df[
        (df["earnings_margin_pct"].notna())
        & (df["earnings_margin_pct"] >= 0)
        & (df["earnings_margin_pct"] <= 20)
    ]

    return MarginDistribution(
        state=state,
        sector=sector,
        margins=[float(m) for m in margins],
        risk_counts={k: int(v) for k, v in risk_counts.items()},
        near_threshold_count=len(near_threshold),
        total_count=len(df),
    )


@router.get("/early-vs-late", response_model=EarlyVsLate)
def get_early_vs_late(
    state: Optional[str] = None,
    limit: int = Query(100, le=500),
):
    df = load_ep_analysis()
    df = df[df["STABBR"].isin(VALID_STATES)]

    if state:
        df = df[df["STABBR"] == state.upper()]

    # Only institutions with both P6 and P10
    df = df.dropna(subset=["MD_EARN_WNE_P6", "MD_EARN_WNE_P10"])
    df = df.head(limit)

    institutions = []
    for _, row in df.iterrows():
        threshold = _safe(row.get("Threshold"))
        p6 = float(row["MD_EARN_WNE_P6"])
        p10 = float(row["MD_EARN_WNE_P10"])
        institutions.append({
            "unit_id": int(row["UnitID"]),
            "name": str(row["institution"]),
            "state": str(row["STABBR"]),
            "sector": _safe(row.get("sector_name")),
            "earnings_p6": p6,
            "earnings_p10": p10,
            "threshold": threshold,
            "pass_p6": p6 >= threshold if threshold else None,
            "pass_p10": p10 >= threshold if threshold else None,
            "changed": (p6 >= threshold) != (p10 >= threshold) if threshold else None,
        })

    return EarlyVsLate(state=state, institutions=institutions)
