"""Program-level analysis endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..data.loader import has_program_data, load_program_analysis
from ..models.schemas import (
    CipSuppressionRisk,
    CipSummary,
    InstitutionProgramsResponse,
    ProgramBrief,
    ProgramOverview,
    ProgramReclassificationResult,
    ProgramSuppressionSummary,
)
from ..services.program_benchmark import reclassify_programs

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
        "earnings_timeframe": str(row["earnings_timeframe"]) if row.get("earnings_timeframe") and str(row.get("earnings_timeframe")) != "nan" else None,
        "earn_mdn_1yr": _safe_float(row.get("earn_mdn_1yr")),
        "earn_mdn_2yr": _safe_float(row.get("earn_mdn_2yr")),
        "earn_mdn_4yr": _safe_float(row.get("earn_mdn_4yr")),
        "earn_mdn_5yr": _safe_float(row.get("earn_mdn_5yr")),
        "earnings_suppressed": bool(row.get("earnings_suppressed", True)),
        "state_threshold": _safe_float(row.get("state_threshold")),
        "earnings_margin_pct": _safe_float(row.get("earnings_margin_pct")),
        "risk_level": str(row.get("risk_level", "No Cohort")),
        # Per-program MC estimates withheld for privacy — see /suppression-summary for aggregates
        "estimated_earnings": None,
        "earnings_ci_low": None,
        "earnings_ci_high": None,
        "prob_pass_state": None,
        "estimated_risk_level": None,
        "estimation_method": None,
    }


@router.get("/overview", response_model=ProgramOverview)
def get_program_overview():
    """National program-level summary statistics."""
    _require_program_data()
    df = load_program_analysis()

    total = len(df)
    with_earnings = int(df["program_earnings"].notna().sum())
    suppressed = int(df["earnings_suppressed"].sum())
    no_cohort = total - with_earnings - suppressed

    # Build risk distribution that uses estimated risk for suppressed programs
    effective_risk = df["risk_level"].copy()
    has_estimate = df["estimated_risk_level"].notna()
    effective_risk.loc[has_estimate] = df.loc[has_estimate, "estimated_risk_level"]
    risk_dist = effective_risk.value_counts().to_dict()

    # Top CIP codes with highest High Risk rates (min 5 programs with earnings)
    cip_groups = df.groupby(["cipcode", "cip_desc"], observed=True).agg(
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
        no_cohort=no_cohort,
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

    # Exclude No Cohort programs (no earnings and not privacy-suppressed)
    df = df[df["program_earnings"].notna() | df["earnings_suppressed"]]

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

    return [ProgramBrief(**_to_program_brief(row)) for row in df.to_dict(orient="records")]


@router.get("/by-institution/{unit_id}", response_model=InstitutionProgramsResponse)
def get_institution_programs(unit_id: int):
    """All programs for a specific institution."""
    _require_program_data()
    df = load_program_analysis()

    inst_df = df[df["UNITID"] == unit_id]
    if inst_df.empty:
        raise HTTPException(status_code=404, detail=f"No programs found for institution {unit_id}")

    programs = [ProgramBrief(**_to_program_brief(row)) for row in inst_df.to_dict(orient="records")]

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

    cip_df = df[df["cipcode"] == cipcode].copy()
    if cip_df.empty:
        raise HTTPException(status_code=404, detail=f"CIP code {cipcode} not found")

    # Exclude No Cohort programs (no earnings and not privacy-suppressed)
    cip_df = cip_df[cip_df["program_earnings"].notna() | cip_df["earnings_suppressed"]]
    if cip_df.empty:
        raise HTTPException(status_code=404, detail=f"No assessable programs for CIP {cipcode}")

    # Effective risk uses estimates where available
    cip_df["effective_risk"] = cip_df["risk_level"]
    has_est = cip_df["estimated_risk_level"].notna()
    cip_df.loc[has_est, "effective_risk"] = cip_df.loc[has_est, "estimated_risk_level"]

    with_earnings = cip_df["program_earnings"].notna()
    risk_dist = cip_df["effective_risk"].value_counts().to_dict()
    median_earn = float(cip_df.loc[with_earnings, "program_earnings"].median()) if with_earnings.any() else None
    passing = cip_df.loc[with_earnings, "pass_state"]
    pct_passing = float(passing.mean() * 100) if with_earnings.any() and passing.notna().any() else None
    high_risk = (cip_df["effective_risk"] == "High Risk").sum()
    pct_high_risk = float(high_risk / len(cip_df) * 100) if len(cip_df) > 0 else None

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

    # Exclude No Cohort programs (no earnings and not privacy-suppressed)
    df = df[df["program_earnings"].notna() | df["earnings_suppressed"]]

    # Build effective risk column for aggregation
    df = df.copy()
    df["effective_risk"] = df["risk_level"]
    has_est = df["estimated_risk_level"].notna()
    df.loc[has_est, "effective_risk"] = df.loc[has_est, "estimated_risk_level"]

    # Aggregate by CIP code using efficient vectorized groupby
    grouped = df.groupby(["cipcode", "cip_desc"], observed=True)
    agg = grouped.agg(
        total_programs=("UNITID", "size"),
        total_completions=("completions", "sum"),
        with_earnings=("program_earnings", lambda x: x.notna().sum()),
        median_earnings=("program_earnings", "median"),
        high_risk_count=("effective_risk", lambda x: (x == "High Risk").sum()),
    ).reset_index()

    # Compute pass rates and risk distributions separately
    pass_rates = {}
    risk_dists = {}
    for (cipcode, cip_desc), g in grouped:
        with_e = g["program_earnings"].notna()
        if with_e.any() and g.loc[with_e.values, "pass_state"].notna().any():
            pass_rates[cipcode] = float(g.loc[with_e.values, "pass_state"].mean() * 100)
        else:
            pass_rates[cipcode] = None
        risk_dists[cipcode] = g["effective_risk"].value_counts().to_dict()

    result = []
    for row in agg.to_dict(orient="records"):
        cipcode = row["cipcode"]
        total = row["total_programs"]
        result.append(CipSummary(
            cipcode=cipcode,
            cip_desc=row["cip_desc"],
            total_programs=int(total),
            total_completions=int(row["total_completions"]),
            with_earnings=int(row["with_earnings"]),
            median_earnings=_safe_float(row["median_earnings"]),
            pct_passing=round(pass_rates[cipcode], 1) if pass_rates[cipcode] is not None else None,
            pct_high_risk=round(float(row["high_risk_count"]) / total * 100, 1) if total > 0 else None,
            risk_distribution=risk_dists[cipcode],
        ))

    # Sort
    if sort_by == "median_earnings":
        result.sort(key=lambda x: x.median_earnings or 0, reverse=True)
    elif sort_by == "pct_high_risk":
        result.sort(key=lambda x: x.pct_high_risk or 0, reverse=True)
    else:
        result.sort(key=lambda x: x.total_programs, reverse=True)

    return result[:limit]


@router.get("/reclassification", response_model=ProgramReclassificationResult)
def get_program_reclassification(
    state: str = Query(..., min_length=2, max_length=2, description="State abbreviation"),
    inequality: float = Query(0.5, ge=0, le=1, description="Synthetic benchmark inequality (0-1)"),
    seed: int = Query(42, description="Random seed for synthetic benchmarks"),
):
    """Program-level statewide vs local benchmark reclassification.

    Same logic as institution-level reclassification, but applied to
    individual programs. Only includes programs with non-suppressed earnings.
    """
    _require_program_data()
    df = load_program_analysis()

    result = reclassify_programs(df, state.upper(), inequality, seed)
    if result.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No programs with earnings found in state {state.upper()}"
        )

    # Count suppressed programs in this state
    state_df = df[df["state"] == state.upper()]
    suppressed_count = int(state_df["earnings_suppressed"].sum())
    threshold = float(result["state_benchmark"].iloc[0])

    # Classification counts
    classifications = result["classification"].value_counts()
    real_count = int((result["benchmark_source"] == "real").sum())
    synthetic_count = int((result["benchmark_source"] == "synthetic").sum())

    return ProgramReclassificationResult(
        state=state.upper(),
        threshold=threshold,
        inequality=inequality,
        total_programs=len(state_df),
        with_earnings=len(result),
        suppressed=suppressed_count,
        pass_both=int(classifications.get("Pass Both", 0)),
        fail_both=int(classifications.get("Fail Both", 0)),
        pass_local_only=int(classifications.get("Pass Local Only", 0)),
        pass_state_only=int(classifications.get("Pass State Only", 0)),
        real_benchmark_count=real_count,
        synthetic_benchmark_count=synthetic_count,
        programs=result.to_dict(orient="records"),
    )


@router.get("/suppression-summary", response_model=ProgramSuppressionSummary)
def get_suppression_summary():
    """Aggregate Monte Carlo summary for suppressed programs.

    Returns pre-computed aggregate statistics from the parquet dataset
    without exposing per-program estimates, for privacy.
    """
    _require_program_data()
    df = load_program_analysis()

    suppressed = df[df["earnings_suppressed"]]
    total_suppressed = len(suppressed)
    estimable = suppressed["estimated_earnings"].notna()
    n_estimable = int(estimable.sum())
    n_inestimable = total_suppressed - n_estimable

    est_subset = suppressed[estimable]
    risk_dist = est_subset["estimated_risk_level"].value_counts().to_dict()
    prob_mean = float(est_subset["prob_pass_state"].mean()) if not est_subset["prob_pass_state"].isna().all() else None
    median_est = float(est_subset["estimated_earnings"].median()) if n_estimable > 0 else None

    return ProgramSuppressionSummary(
        total_suppressed=total_suppressed,
        estimable=n_estimable,
        inestimable=n_inestimable,
        estimated_risk_distribution=risk_dist,
        prob_pass_state_mean=round(prob_mean, 4) if prob_mean is not None else None,
        median_estimated_earnings=round(median_est) if median_est is not None else None,
    )


@router.get("/suppression-by-cip", response_model=list[CipSuppressionRisk])
def get_suppression_by_cip(
    sort_by: str = Query("high_risk", description="Sort by: high_risk, total, cipcode"),
    limit: int = Query(100, le=500),
):
    """MC risk breakdown by CIP code for suppressed programs."""
    _require_program_data()
    df = load_program_analysis()

    est = df[df["earnings_suppressed"] & df["estimated_earnings"].notna()]
    risk_pivot = (
        est.groupby(["cipcode", "cip_desc", "estimated_risk_level"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    result = []
    for row in risk_pivot.to_dict(orient="records"):
        result.append(CipSuppressionRisk(
            cipcode=str(row["cipcode"]),
            cip_desc=str(row["cip_desc"]),
            total=sum(int(row.get(r, 0)) for r in ["High Risk", "Moderate Risk", "Low Risk", "Very Low Risk"]),
            high_risk=int(row.get("High Risk", 0)),
            moderate_risk=int(row.get("Moderate Risk", 0)),
            low_risk=int(row.get("Low Risk", 0)),
            very_low_risk=int(row.get("Very Low Risk", 0)),
        ))

    if sort_by == "total":
        result.sort(key=lambda x: x.total, reverse=True)
    elif sort_by == "cipcode":
        result.sort(key=lambda x: x.cipcode)
    else:
        result.sort(key=lambda x: x.high_risk, reverse=True)

    return result[:limit]
