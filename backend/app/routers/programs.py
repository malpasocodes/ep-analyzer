"""Program-level analysis endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..data.loader import has_program_data, load_program_analysis, load_ep_analysis
from ..models.schemas import (
    CipSummary,
    InstitutionProgramsResponse,
    InstitutionSimulationResponse,
    ProgramBrief,
    ProgramOverview,
    ProgramReclassificationResult,
    ProgramSimulationResult,
    ProgramSimulationSummary,
)
from ..services.program_benchmark import reclassify_programs
from ..services.program_simulation import (
    estimate_program_earnings,
    simulate_institution_programs,
    simulation_summary,
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
        "earnings_timeframe": str(row["earnings_timeframe"]) if row.get("earnings_timeframe") and str(row.get("earnings_timeframe")) != "nan" else None,
        "earn_mdn_1yr": _safe_float(row.get("earn_mdn_1yr")),
        "earn_mdn_2yr": _safe_float(row.get("earn_mdn_2yr")),
        "earn_mdn_4yr": _safe_float(row.get("earn_mdn_4yr")),
        "earn_mdn_5yr": _safe_float(row.get("earn_mdn_5yr")),
        "earnings_suppressed": bool(row.get("earnings_suppressed", True)),
        "state_threshold": _safe_float(row.get("state_threshold")),
        "earnings_margin_pct": _safe_float(row.get("earnings_margin_pct")),
        "risk_level": str(row.get("risk_level", "No Cohort")),
        "estimated_earnings": _safe_float(row.get("estimated_earnings")),
        "earnings_ci_low": _safe_float(row.get("earnings_ci_low")),
        "earnings_ci_high": _safe_float(row.get("earnings_ci_high")),
        "prob_pass_state": _safe_float(row.get("prob_pass_state")),
        "estimated_risk_level": str(row["estimated_risk_level"]) if _safe_float(row.get("estimated_earnings")) is not None else None,
        "estimation_method": str(row["estimation_method"]) if row.get("estimation_method") and str(row.get("estimation_method")) != "nan" else None,
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

    # Aggregate by CIP code
    cip_agg = df.groupby(["cipcode", "cip_desc"], observed=True).apply(
        lambda g: {
            "total_programs": len(g),
            "total_completions": int(g["completions"].sum()) if "completions" in g.columns else 0,
            "with_earnings": int(g["program_earnings"].notna().sum()),
            "median_earnings": float(g["program_earnings"].median()) if g["program_earnings"].notna().any() else None,
            "pct_passing": float(g.loc[g["program_earnings"].notna(), "pass_state"].mean() * 100) if g["program_earnings"].notna().any() and g.loc[g["program_earnings"].notna(), "pass_state"].notna().any() else None,
            "pct_high_risk": float((g["effective_risk"] == "High Risk").sum() / len(g) * 100) if len(g) > 0 else None,
            "risk_distribution": g["effective_risk"].value_counts().to_dict(),
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


@router.get("/simulation/{unit_id}", response_model=InstitutionSimulationResponse)
def get_institution_simulation(
    unit_id: int,
    n_simulations: int = Query(1000, ge=100, le=5000, description="Monte Carlo draws per program"),
    seed: int = Query(42, description="Random seed"),
):
    """Simulate earnings for suppressed programs at an institution.

    Uses a hierarchical prior (national CIP median * institution effect *
    geographic factor) with Monte Carlo sampling to estimate earnings and
    probability of passing the EP test.
    """
    _require_program_data()
    program_df = load_program_analysis()
    ep_df = load_ep_analysis()

    sim_result = simulate_institution_programs(
        program_df, ep_df, unit_id, n_simulations, seed
    )

    if sim_result.empty:
        # Check if institution exists but has no suppressed programs
        inst_df = program_df[program_df["UNITID"] == unit_id]
        if inst_df.empty:
            raise HTTPException(status_code=404, detail=f"Institution {unit_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"No suppressed programs to simulate at institution {unit_id}"
        )

    institution_name = str(sim_result["institution"].iloc[0])
    state = str(sim_result["state"].iloc[0])

    # Build summary
    summary = simulation_summary(sim_result)

    # Build individual program results
    programs = []
    for _, row in sim_result.iterrows():
        programs.append(ProgramSimulationResult(
            unit_id=int(row["UNITID"]),
            institution=str(row["institution"]),
            state=str(row["state"]),
            cipcode=str(row["cipcode"]),
            cip_desc=str(row["cip_desc"]),
            credential_level=_safe_int(row.get("credential_level")),
            credential_desc=str(row.get("credential_desc")) if _safe_float(row.get("credential_level")) is not None else None,
            completions=_safe_int(row.get("completions")),
            state_threshold=_safe_float(row.get("state_threshold")),
            county_hs_earnings=_safe_float(row.get("county_hs_earnings")),
            estimated_earnings=_safe_float(row.get("estimated_earnings")),
            earnings_ci_low=_safe_float(row.get("earnings_ci_low")),
            earnings_ci_high=_safe_float(row.get("earnings_ci_high")),
            prob_pass_state=_safe_float(row.get("prob_pass_state")),
            prob_pass_local=_safe_float(row.get("prob_pass_local")),
            national_cip_median=_safe_float(row.get("national_cip_median")),
            institution_effect=_safe_float(row.get("institution_effect")),
            geo_factor=_safe_float(row.get("geo_factor")),
            estimation_method=str(row.get("estimation_method", "unknown")),
        ))

    return InstitutionSimulationResponse(
        unit_id=unit_id,
        institution=institution_name,
        state=state,
        summary=ProgramSimulationSummary(**summary),
        programs=programs,
    )


@router.get("/simulation-summary", response_model=ProgramSimulationSummary)
def get_simulation_summary(
    state: Optional[str] = Query(None, min_length=2, max_length=2),
    n_simulations: int = Query(500, ge=100, le=2000),
    seed: int = Query(42),
):
    """Run simulation across all suppressed programs (or within a state).

    Returns aggregate summary only (not individual program results) to
    keep response size manageable.
    """
    _require_program_data()
    program_df = load_program_analysis()
    ep_df = load_ep_analysis()

    if state:
        program_df = program_df[program_df["state"] == state.upper()]

    sim_result = estimate_program_earnings(program_df, ep_df, n_simulations, seed)
    summary = simulation_summary(sim_result)

    return ProgramSimulationSummary(**summary)
