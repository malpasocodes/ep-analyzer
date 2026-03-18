"""Pydantic response models."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class OverviewResponse(BaseModel):
    total_institutions: int
    with_earnings: int
    states_covered: int
    risk_distribution: dict[str, int]
    sector_distribution: dict[str, int]
    total_programs: int
    assessable_programs: int


class StateSummary(BaseModel):
    state: str
    state_name: str
    threshold: float
    institution_count: int
    risk_distribution: dict[str, int]


class StateDetail(BaseModel):
    state: str
    state_name: str
    threshold: float
    institution_count: int
    risk_distribution: dict[str, int]
    institutions: list[InstitutionBrief]
    margin_histogram: list[float]


class InstitutionBrief(BaseModel):
    unit_id: int
    name: str
    state: str
    sector: Optional[str] = None
    enrollment: Optional[float] = None
    median_earnings: Optional[float] = None
    threshold: Optional[float] = None
    earnings_margin_pct: Optional[float] = None
    risk_level: str
    total_programs: Optional[int] = None


class InstitutionDetail(BaseModel):
    unit_id: int
    name: str
    state: str
    sector: Optional[str] = None
    enrollment: Optional[float] = None
    graduation_rate: Optional[float] = None
    cost: Optional[float] = None
    earnings_p6: Optional[float] = None
    earnings_p10: Optional[float] = None
    median_earnings: Optional[float] = None
    threshold: Optional[float] = None
    earnings_margin: Optional[float] = None
    earnings_margin_pct: Optional[float] = None
    risk_level: str
    total_programs: Optional[int] = None
    assessable_programs: Optional[int] = None
    total_completions: Optional[int] = None


class PeerInstitution(BaseModel):
    unit_id: int
    name: str
    median_earnings: Optional[float] = None
    earnings_margin_pct: Optional[float] = None
    risk_level: str
    enrollment: Optional[float] = None


class ReclassificationResult(BaseModel):
    state: str
    threshold: float
    inequality: float
    total_programs: int
    pass_both: int
    fail_both: int
    pass_local_only: int
    pass_state_only: int
    real_benchmark_count: int = 0
    synthetic_benchmark_count: int = 0
    programs: list[dict]


class SensitivityResult(BaseModel):
    unit_id: int
    name: str
    current_earnings: Optional[float] = None
    threshold: Optional[float] = None
    current_margin_pct: Optional[float] = None
    scenarios: list[dict]


class MarginDistribution(BaseModel):
    state: Optional[str] = None
    sector: Optional[str] = None
    margins: list[float]
    risk_counts: dict[str, int]
    near_threshold_count: int
    total_count: int


class EarlyVsLate(BaseModel):
    state: Optional[str] = None
    institutions: list[dict]


class ProgramBrief(BaseModel):
    """Single program in a list context."""
    unit_id: int
    institution: str
    state: str
    cipcode: str
    cip_desc: str
    credential_level: Optional[int] = None
    credential_desc: Optional[str] = None
    completions: Optional[int] = None
    program_earnings: Optional[float] = None
    earnings_suppressed: bool
    state_threshold: Optional[float] = None
    earnings_margin_pct: Optional[float] = None
    risk_level: str


class ProgramOverview(BaseModel):
    """Summary stats for program-level analysis."""
    total_programs: int
    with_earnings: int
    earnings_suppressed: int
    suppression_rate: float
    risk_distribution: dict[str, int]
    cip_count: int
    institution_count: int
    top_risk_cips: list[dict]


class CipSummary(BaseModel):
    """Aggregated summary for a CIP code nationally."""
    cipcode: str
    cip_desc: str
    total_programs: int
    total_completions: int
    with_earnings: int
    median_earnings: Optional[float] = None
    pct_passing: Optional[float] = None
    pct_high_risk: Optional[float] = None
    risk_distribution: dict[str, int]


class InstitutionProgramsResponse(BaseModel):
    """Programs for a specific institution."""
    unit_id: int
    institution: str
    state: str
    total_programs: int
    with_earnings: int
    suppressed: int
    programs: list[ProgramBrief]


# Needed for forward reference resolution
StateDetail.model_rebuild()
