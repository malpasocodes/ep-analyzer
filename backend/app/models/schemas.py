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


# Needed for forward reference resolution
StateDetail.model_rebuild()
