"""Program-level risk classification and aggregation.

Same threshold logic as institution-level risk.py, with an additional
"Suppressed" category for programs whose earnings are privacy-suppressed
by the College Scorecard (<30 student cohort).
"""

from __future__ import annotations

import pandas as pd


def classify_program_risk(
    program_earnings: float | None,
    threshold: float | None,
    earnings_suppressed: bool = False,
) -> str:
    """Classify a single program's risk level.

    Returns one of:
        "Very Low Risk"       — earnings >= 50% above threshold
        "Low Risk"            — earnings 20-50% above threshold
        "Moderate Risk"       — earnings 0-20% above threshold
        "High Risk"           — earnings below threshold
        "Privacy Suppressed"  — earnings suppressed (cohort <30)
        "No Cohort"           — no earnings or threshold data
    """
    if earnings_suppressed or program_earnings is None:
        return "Privacy Suppressed"
    if threshold is None or threshold <= 0:
        return "No Cohort"

    margin_pct = (program_earnings - threshold) / threshold * 100

    if margin_pct >= 50:
        return "Very Low Risk"
    if margin_pct >= 20:
        return "Low Risk"
    if margin_pct >= 0:
        return "Moderate Risk"
    return "High Risk"


def program_risk_distribution(df: pd.DataFrame) -> dict[str, int]:
    """Count programs by risk level."""
    counts = df["risk_level"].value_counts().to_dict()
    return {k: int(v) for k, v in counts.items()}


def cip_risk_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate risk by CIP code across all institutions.

    Returns DataFrame with per-CIP summary:
        cipcode, cip_desc, total_programs, total_completions,
        with_earnings, pct_high_risk, pct_suppressed, median_earnings
    """
    def _summarize(g):
        total = len(g)
        with_earn = g["program_earnings"].notna().sum()
        high_risk = (g["risk_level"] == "High Risk").sum()
        suppressed = (g["risk_level"] == "Privacy Suppressed").sum()
        completions = g["completions"].sum() if "completions" in g.columns else 0

        return pd.Series({
            "total_programs": total,
            "total_completions": int(completions) if pd.notna(completions) else 0,
            "with_earnings": int(with_earn),
            "pct_high_risk": round(high_risk / with_earn * 100, 1) if with_earn > 0 else None,
            "pct_suppressed": round(suppressed / total * 100, 1) if total > 0 else 0,
            "median_earnings": float(g["program_earnings"].median()) if with_earn > 0 else None,
        })

    summary = (
        df.groupby(["cipcode", "cip_desc"])
        .apply(_summarize, include_groups=False)
        .reset_index()
    )

    return summary.sort_values("total_programs", ascending=False)


def state_program_risk_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate program risk by state.

    Returns DataFrame with per-state summary:
        state, total_programs, with_earnings, pct_high_risk,
        pct_suppressed, risk_distribution
    """
    def _summarize(g):
        total = len(g)
        with_earn = g["program_earnings"].notna().sum()
        high_risk = (g["risk_level"] == "High Risk").sum()
        suppressed = (g["risk_level"] == "Privacy Suppressed").sum()
        risk_dist = g["risk_level"].value_counts().to_dict()

        return pd.Series({
            "total_programs": total,
            "with_earnings": int(with_earn),
            "pct_high_risk": round(high_risk / with_earn * 100, 1) if with_earn > 0 else None,
            "pct_suppressed": round(suppressed / total * 100, 1) if total > 0 else 0,
            "risk_distribution": risk_dist,
        })

    summary = (
        df.groupby("state")
        .apply(_summarize, include_groups=False)
        .reset_index()
    )

    return summary.sort_values("total_programs", ascending=False)
