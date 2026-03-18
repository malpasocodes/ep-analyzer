"""Program-level analysis endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..data.loader import has_program_data, load_program_analysis
from ..models.schemas import (
    CipSummary,
    InstitutionProgramsResponse,
    ProgramBrief,
    ProgramOverview,
)

router = APIRouter(prefix="/api/programs", tags=["programs"])


def _require_program_data():
    """Raise 404 if program data hasn't been generated yet."""
    if not has_program_data():
        raise HTTPException(
            status_code=404,
            detail=(
                "Program-level data not available. Run the pipeline:\n"
                "  python -m backend.app.pipelines.fetch_program_earnings\n"
                "  python -m backend.app.pipelines.fetch_ipeds_completions\n"
                "  python -m backend.app.pipelines.build_program_dataset"
            ),
        )


def _safe_float(val) -> float | None:
    """Convert a value to float, returning None for NaN/NA/None."""
    if val is None:
        return None
    try:
        import math
        f = float(val)
        return None if math.isnan(f) else f
    except (ValueError, TypeError):
        return None


def _safe_int(val) -> int | None:
    """Convert a value to int, returning None for NaN/NA/None."""
    f = _safe_float(val)
    return int(f) if f is not None else None


def _to_program_brief(row) -> dict:
    """Convert a DataFrame row to ProgramBrief dict."""
    return {
        "unit_id": int(row.get("UNITID", 0)),
        "institution": str(row.get("institution", "")),
        "state": str(row.get("state", "")),
        "cipcode": str(row.get("cipcode", "")),
        "cip_desc": str(row.get("cip_desc", "")),
        "credential_level": _safe_int(row.get("credential_level")),
        "credential_desc": str(row.get("credential_desc")) if _safe_float(row.get("credential_level")) is not None else None,
        "completions": _safe_int(row.get("completions")),
        "program_earnings": _safe_float(row.get("program_earnings")),
        "earnings_suppressed": bool(row.get("earnings_suppressed", True)),
        "state_threshold": _safe_float(row.get("state_threshold")),
        "earnings_margin_pct": _safe_float(row.get("earnings_margin_pct")),
        "risk_level": str(row.get("risk_level", "Suppressed")),
    }


@router.get("/overview", response_model=ProgramOverview)
def get_program_overview():
    """National program-level summary statistics."""
    _require_program_data()
    df = load_program_analysis()

    total = len(df)
    with_earnings = int(df["program_earnings"].notna().sum())
    suppressed = int(df["earnings_suppressed"].sum())
    risk_dist = df["risk_level"].value_counts().to_dict()

    # Top CIP codes with highest High Risk rates (min 5 programs with earnings)
    cip_groups = df.groupby(["cipcode", "cip_desc"]).agg(
        total=("UNITID", "size"),
        high_risk=("risk_level", lambda x: (x == "High Risk").sum()),
        with_earnings=("program_earnings", lambda x: x.notna().sum()),
    ).reset_index()
    cip_groups = cip_groups[cip_groups["with_earnings"] >= 5]
    cip_groups["pct_high_risk"] = cip_groups["high_risk"] / cip_groups["with_earnings"] * 100
    top_risk = (
        cip_groups.sort_values("pct_high_risk", ascending=False)
        .head(10)
        .apply(lambda r: {
            "cipcode": r["cipcode"],
            "cip_desc": r["cip_desc"],
            "total_programs": int(r["total"]),
            "pct_high_risk": round(float(r["pct_high_risk"]), 1),
        }, axis=1)
        .tolist()
    )

    return ProgramOverview(
        total_programs=total,
        with_earnings=with_earnings,
        earnings_suppressed=suppressed,
        suppression_rate=round(suppressed / total * 100, 1) if total > 0 else 0,
        risk_distribution=risk_dist,
        cip_count=int(df["cipcode"].nunique()),
        institution_count=int(df["UNITID"].nunique()),
        top_risk_cips=top_risk,
    )


@router.get("/search", response_model=list[ProgramBrief])
def search_programs(
    search: Optional[str] = Query(None, description="Search institution or CIP description"),
    state: Optional[str] = Query(None, min_length=2, max_length=2),
    cipcode: Optional[str] = Query(None, description="4-digit CIP code"),
    risk: Optional[str] = Query(None, description="Risk level filter"),
    suppress_filter: str = Query("all", description="all, observed, or suppressed"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    """Search and filter programs."""
    _require_program_data()
    df = load_program_analysis()

    if search:
        mask = (
            df["institution"].str.contains(search, case=False, na=False)
            | df["cip_desc"].str.contains(search, case=False, na=False)
        )
        df = df[mask]

    if state:
        df = df[df["state"] == state.upper()]

    if cipcode:
        df = df[df["cipcode"] == cipcode]

    if risk:
        df = df[df["risk_level"] == risk]

    if suppress_filter == "observed":
        df = df[~df["earnings_suppressed"]]
    elif suppress_filter == "suppressed":
        df = df[df["earnings_suppressed"]]

    total = len(df)
    df = df.iloc[offset : offset + limit]

    return [ProgramBrief(**_to_program_brief(row)) for _, row in df.iterrows()]


@router.get("/by-institution/{unit_id}", response_model=InstitutionProgramsResponse)
def get_institution_programs(unit_id: int):
    """All programs for a specific institution."""
    _require_program_data()
    df = load_program_analysis()

    inst_df = df[df["UNITID"] == unit_id]
    if inst_df.empty:
        raise HTTPException(status_code=404, detail=f"No programs found for institution {unit_id}")

    programs = [ProgramBrief(**_to_program_brief(row)) for _, row in inst_df.iterrows()]

    return InstitutionProgramsResponse(
        unit_id=unit_id,
        institution=str(inst_df["institution"].iloc[0]),
        state=str(inst_df["state"].iloc[0]),
        total_programs=len(programs),
        with_earnings=sum(1 for p in programs if p.program_earnings is not None),
        suppressed=sum(1 for p in programs if p.earnings_suppressed),
        programs=programs,
    )


@router.get("/by-cip/{cipcode}", response_model=CipSummary)
def get_cip_summary(cipcode: str):
    """National summary for a CIP code across all institutions."""
    _require_program_data()
    df = load_program_analysis()

    cip_df = df[df["cipcode"] == cipcode]
    if cip_df.empty:
        raise HTTPException(status_code=404, detail=f"CIP code {cipcode} not found")

    with_earnings = cip_df["program_earnings"].notna()
    risk_dist = cip_df["risk_level"].value_counts().to_dict()
    median_earn = float(cip_df.loc[with_earnings, "program_earnings"].median()) if with_earnings.any() else None
    passing = cip_df.loc[with_earnings, "pass_state"]
    pct_passing = float(passing.mean() * 100) if with_earnings.any() and passing.notna().any() else None
    high_risk = (cip_df["risk_level"] == "High Risk").sum()
    pct_high_risk = float(high_risk / with_earnings.sum() * 100) if with_earnings.sum() > 0 else None

    return CipSummary(
        cipcode=cipcode,
        cip_desc=str(cip_df["cip_desc"].iloc[0]),
        total_programs=len(cip_df),
        total_completions=int(cip_df["completions"].sum()) if "completions" in cip_df.columns else 0,
        with_earnings=int(with_earnings.sum()),
        median_earnings=median_earn,
        pct_passing=round(pct_passing, 1) if pct_passing is not None else None,
        pct_high_risk=round(pct_high_risk, 1) if pct_high_risk is not None else None,
        risk_distribution=risk_dist,
    )


@router.get("/cip-list", response_model=list[CipSummary])
def list_cip_codes(
    sort_by: str = Query("total_programs", description="Sort by: total_programs, median_earnings, pct_high_risk"),
    limit: int = Query(50, le=200),
):
    """List CIP codes with summary statistics."""
    _require_program_data()
    df = load_program_analysis()

    # Aggregate by CIP code
    cip_agg = df.groupby(["cipcode", "cip_desc"]).apply(
        lambda g: {
            "total_programs": len(g),
            "total_completions": int(g["completions"].sum()) if "completions" in g.columns else 0,
            "with_earnings": int(g["program_earnings"].notna().sum()),
            "median_earnings": float(g["program_earnings"].median()) if g["program_earnings"].notna().any() else None,
            "pct_passing": float(g.loc[g["program_earnings"].notna(), "pass_state"].mean() * 100) if g["program_earnings"].notna().any() and g.loc[g["program_earnings"].notna(), "pass_state"].notna().any() else None,
            "pct_high_risk": float((g["risk_level"] == "High Risk").sum() / g["program_earnings"].notna().sum() * 100) if g["program_earnings"].notna().sum() > 0 else None,
            "risk_distribution": g["risk_level"].value_counts().to_dict(),
        },
        include_groups=False,
    ).reset_index(name="stats")

    # Flatten stats dict into columns
    stats_df = cip_agg["stats"].apply(lambda x: x).tolist()
    result = []
    for i, row in cip_agg.iterrows():
        s = stats_df[i]
        result.append(CipSummary(
            cipcode=row["cipcode"],
            cip_desc=row["cip_desc"],
            **s,
        ))

    # Sort
    if sort_by == "median_earnings":
        result.sort(key=lambda x: x.median_earnings or 0, reverse=True)
    elif sort_by == "pct_high_risk":
        result.sort(key=lambda x: x.pct_high_risk or 0, reverse=True)
    else:
        result.sort(key=lambda x: x.total_programs, reverse=True)

    return result[:limit]
