"""National overview endpoint."""

from fastapi import APIRouter

from ..data.loader import load_ep_analysis
from ..models.schemas import OverviewResponse
from ..services.risk import risk_distribution, sector_distribution, VALID_STATES

router = APIRouter(prefix="/api", tags=["overview"])


@router.get("/overview", response_model=OverviewResponse)
def get_overview():
    df = load_ep_analysis()
    df_states = df[df["STABBR"].isin(VALID_STATES)]
    return OverviewResponse(
        total_institutions=len(df_states),
        with_earnings=int(df_states["median_earnings"].notna().sum()),
        states_covered=int(df_states["STABBR"].nunique()),
        risk_distribution=risk_distribution(df_states),
        sector_distribution=sector_distribution(df_states),
        total_programs=int(df_states["total_programs"].sum()),
        assessable_programs=int(df_states["assessable_programs"].sum()),
    )
