"""Institution lookup and detail endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
import pandas as pd

from ..data.loader import load_ep_analysis
from ..models.schemas import InstitutionBrief, InstitutionDetail, PeerInstitution
from ..services.risk import VALID_STATES

router = APIRouter(prefix="/api/institutions", tags=["institutions"])


def _safe(val):
    if pd.isna(val):
        return None
    if hasattr(val, "item"):
        return val.item()
    return val


@router.get("", response_model=list[InstitutionBrief])
def search_institutions(
    search: Optional[str] = Query(None, min_length=2),
    state: Optional[str] = None,
    sector: Optional[str] = None,
    risk: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
):
    df = load_ep_analysis()
    df = df[df["STABBR"].isin(VALID_STATES)]

    if search:
        df = df[df["institution"].str.contains(search, case=False, na=False)]
    if state:
        df = df[df["STABBR"] == state.upper()]
    if sector:
        df = df[df["sector_name"] == sector]
    if risk:
        df = df[df["risk_level"] == risk]

    df = df.sort_values("institution").iloc[offset:offset + limit]

    return [
        InstitutionBrief(
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
        )
        for row in df.to_dict(orient="records")
    ]


@router.get("/{unit_id}", response_model=InstitutionDetail)
def get_institution(unit_id: int):
    df = load_ep_analysis()
    row = df[df["UnitID"] == unit_id]
    if row.empty:
        raise HTTPException(404, f"Institution {unit_id} not found")

    r = row.iloc[0]
    return InstitutionDetail(
        unit_id=int(r["UnitID"]),
        name=str(r["institution"]),
        state=str(r["STABBR"]),
        sector=_safe(r.get("sector_name")),
        enrollment=_safe(r.get("enrollment")),
        graduation_rate=_safe(r.get("graduation_rate")),
        cost=_safe(r.get("cost")),
        earnings_p6=_safe(r.get("MD_EARN_WNE_P6")),
        earnings_p10=_safe(r.get("MD_EARN_WNE_P10")),
        median_earnings=_safe(r.get("median_earnings")),
        threshold=_safe(r.get("Threshold")),
        earnings_margin=_safe(r.get("earnings_margin")),
        earnings_margin_pct=_safe(r.get("earnings_margin_pct")),
        risk_level=str(r["risk_level"]),
        total_programs=_safe(r.get("total_programs")),
        assessable_programs=_safe(r.get("assessable_programs")),
        total_completions=_safe(r.get("total_completions")),
    )


@router.get("/{unit_id}/peers", response_model=list[PeerInstitution])
def get_peers(unit_id: int, limit: int = Query(20, le=50)):
    df = load_ep_analysis()
    row = df[df["UnitID"] == unit_id]
    if row.empty:
        raise HTTPException(404, f"Institution {unit_id} not found")

    r = row.iloc[0]
    peers = df[
        (df["STABBR"] == r["STABBR"])
        & (df["sector_name"] == r["sector_name"])
        & (df["UnitID"] != unit_id)
        & (df["median_earnings"].notna())
    ].sort_values("earnings_margin", ascending=False).head(limit)

    return [
        PeerInstitution(
            unit_id=int(p["UnitID"]),
            name=str(p["institution"]),
            median_earnings=_safe(p.get("median_earnings")),
            earnings_margin_pct=_safe(p.get("earnings_margin_pct")),
            risk_level=str(p["risk_level"]),
            enrollment=_safe(p.get("enrollment")),
        )
        for p in peers.to_dict(orient="records")
    ]
