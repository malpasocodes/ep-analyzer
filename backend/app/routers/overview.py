"""National overview endpoint."""

from fastapi import APIRouter

from ..data.loader import load_ep_analysis, has_program_data, load_program_analysis, get_phase1_unitids
from ..models.schemas import OverviewResponse
from ..services.risk import risk_distribution, sector_distribution, VALID_STATES

router = APIRouter(prefix="/api", tags=["overview"])

# Phase 1: Only Associates (2) and Bachelors (3)
PHASE1_CREDENTIAL_LEVELS = {2, 3}


@router.get("/overview", response_model=OverviewResponse)
def get_overview():
    df = load_ep_analysis()
    df_states = df[df["STABBR"].isin(VALID_STATES)]

    # Derive program-level stats from Phase 1 credential levels if available
    if has_program_data():
        prog = load_program_analysis()
        prog = prog[prog["credential_level"].isin(PHASE1_CREDENTIAL_LEVELS)]
        prog = prog[prog["state"].isin(VALID_STATES)]

        # Build risk distribution from program data
        effective_risk = prog["risk_level"].copy()
        has_estimate = prog["estimated_risk_level"].notna()
        effective_risk.loc[has_estimate] = prog.loc[has_estimate, "estimated_risk_level"]
        prog_risk_dist = effective_risk.value_counts().to_dict()

        # Institution counts derived from Phase 1 programs
        total_institutions = int(prog["UNITID"].nunique())
        with_earnings = int(prog[prog["program_earnings"].notna()]["UNITID"].nunique())

        return OverviewResponse(
            total_institutions=total_institutions,
            with_earnings=with_earnings,
            states_covered=int(prog["state"].nunique()),
            risk_distribution=prog_risk_dist,
            sector_distribution=sector_distribution(df_states),
            total_programs=len(prog),
            assessable_programs=int(prog[prog["program_earnings"].notna() | prog["earnings_suppressed"]].shape[0]),
        )

    # Fallback to institution-level data
    df_states = df_states[df_states["UnitID"].isin(get_phase1_unitids())]
    return OverviewResponse(
        total_institutions=len(df_states),
        with_earnings=int(df_states["median_earnings"].notna().sum()),
        states_covered=int(df_states["STABBR"].nunique()),
        risk_distribution=risk_distribution(df_states),
        sector_distribution=sector_distribution(df_states),
        total_programs=int(df_states["total_programs"].sum()),
        assessable_programs=int(df_states["assessable_programs"].sum()),
    )
