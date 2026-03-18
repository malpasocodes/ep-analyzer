"""
Extract real institutional examples from the EP analysis dataset
to support each of the 5 critique problems in EARNINGS_PREMIUM_CRITIQUE.md.
"""

import pandas as pd
import numpy as np
import json
import sys

# ── Load data ──────────────────────────────────────────────────────────────────

df = pd.read_parquet("data/ep_analysis_enriched.parquet")
county_earnings = pd.read_csv("data/county_hs_earnings.csv")
state_thresholds = pd.read_csv("data/state_thresholds_2024.csv")
scorecard = pd.read_csv("data/scorecard_earnings.csv")

# Ensure numeric types
for col in ["median_earnings", "Threshold", "county_hs_earnings", "earnings_margin_pct"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

for col in ["MD_EARN_WNE_P6", "MD_EARN_WNE_P10"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Derived columns
df["fail_state"] = df["median_earnings"] < df["Threshold"]
df["has_county"] = df["county_hs_earnings"].notna()
df["pass_local"] = df["median_earnings"] >= df["county_hs_earnings"]
df["fail_local"] = df["median_earnings"] < df["county_hs_earnings"]

print(f"Total institutions: {len(df)}")
print(f"With county earnings: {df['has_county'].sum()}")
print(f"Fail statewide: {df['fail_state'].sum()}")
print()

# ── PROBLEM 1: Geographic Fallacy ─────────────────────────────────────────────

print("=" * 80)
print("PROBLEM 1: GEOGRAPHIC FALLACY — Punishing Place, Not Quality")
print("=" * 80)

# 1a. Fail statewide BUT pass local (penalized by geography)
penalized = df[df["fail_state"] & df["pass_local"] & df["has_county"]].copy()
penalized["gap"] = penalized["Threshold"] - penalized["county_hs_earnings"]
penalized = penalized.sort_values("gap", ascending=False)

print(f"\n--- 1a. Fail statewide, pass local ({len(penalized)} institutions) ---")
print("Top examples (largest gap between state threshold and county earnings):\n")
for _, r in penalized.head(15).iterrows():
    print(f"  {r['institution']} ({r['STABBR']}, {r.get('county', 'N/A')})")
    print(f"    Earnings: ${r['median_earnings']:,.0f} | State threshold: ${r['Threshold']:,.0f} | County HS: ${r['county_hs_earnings']:,.0f}")
    print(f"    → FAILS state by ${r['Threshold'] - r['median_earnings']:,.0f}, but BEATS county by ${r['median_earnings'] - r['county_hs_earnings']:,.0f}")
    print(f"    Gap (threshold vs county): ${r['gap']:,.0f}")
    print()

# 1b. Pass statewide BUT fail local (masked by geography — high-cost metro)
masked = df[~df["fail_state"] & df["fail_local"] & df["has_county"]].copy()
masked["gap"] = masked["county_hs_earnings"] - masked["median_earnings"]
masked = masked.sort_values("gap", ascending=False)

print(f"\n--- 1b. Pass statewide, fail local ({len(masked)} institutions) ---")
print("Top examples (institutions in high-cost counties that pass state but fail locally):\n")
for _, r in masked.head(10).iterrows():
    print(f"  {r['institution']} ({r['STABBR']}, {r.get('county', 'N/A')})")
    print(f"    Earnings: ${r['median_earnings']:,.0f} | State threshold: ${r['Threshold']:,.0f} | County HS: ${r['county_hs_earnings']:,.0f}")
    print(f"    → PASSES state by ${r['median_earnings'] - r['Threshold']:,.0f}, but FAILS county by ${r['county_hs_earnings'] - r['median_earnings']:,.0f}")
    print()

# 1c. Same-state pairs: one passes, one fails, due to county location
print(f"\n--- 1c. Same-state pairs with divergent outcomes ---\n")
states_with_both = df[df["has_county"]].groupby("STABBR").apply(
    lambda g: g["fail_state"].any() and (~g["fail_state"]).any()
)
pair_states = states_with_both[states_with_both].index.tolist()

for state in pair_states[:5]:
    state_df = df[(df["STABBR"] == state) & df["has_county"]]
    # Find a failing institution with high county HS earnings gap
    failers = state_df[state_df["fail_state"]].sort_values("median_earnings", ascending=False)
    passers = state_df[~state_df["fail_state"]].sort_values("median_earnings")

    if len(failers) == 0 or len(passers) == 0:
        continue

    f = failers.iloc[0]
    p = passers.iloc[0]

    # Only show if the pair is interesting (failer has lower county earnings)
    if pd.notna(f["county_hs_earnings"]) and pd.notna(p["county_hs_earnings"]):
        if f["county_hs_earnings"] < p["county_hs_earnings"]:
            print(f"  State: {state}")
            print(f"    FAILS: {f['institution']} ({f.get('county', 'N/A')})")
            print(f"      Earnings: ${f['median_earnings']:,.0f} | Threshold: ${f['Threshold']:,.0f} | County HS: ${f['county_hs_earnings']:,.0f}")
            print(f"    PASSES: {p['institution']} ({p.get('county', 'N/A')})")
            print(f"      Earnings: ${p['median_earnings']:,.0f} | Threshold: ${p['Threshold']:,.0f} | County HS: ${p['county_hs_earnings']:,.0f}")
            print()


# ── PROBLEM 2: Ecological Fallacy ─────────────────────────────────────────────

print("\n" + "=" * 80)
print("PROBLEM 2: ECOLOGICAL FALLACY — Apples to Averages")
print("=" * 80)

# Small institutions near threshold
near_threshold = df[
    (df["earnings_margin_pct"].abs() <= 10) &
    (df["total_completions"].notna()) &
    (df["total_completions"] > 0)
].copy()
near_threshold = near_threshold.sort_values("total_completions")

print(f"\n--- 2a. Small institutions near threshold ({len(near_threshold)} total) ---")
print("Smallest institutions whose pass/fail hinges on population-level benchmark:\n")
for _, r in near_threshold.head(15).iterrows():
    status = "FAILS" if r["fail_state"] else "PASSES"
    print(f"  {r['institution']} ({r['STABBR']})")
    print(f"    Completions: {r['total_completions']:.0f} | Earnings: ${r['median_earnings']:,.0f} | Threshold: ${r['Threshold']:,.0f}")
    print(f"    Margin: {r['earnings_margin_pct']:.1f}% → {status}")
    print()

# Institutions with very few completions that fail
tiny_failers = df[
    df["fail_state"] &
    (df["total_completions"].notna()) &
    (df["total_completions"] <= 50)
].sort_values("total_completions")

print(f"\n--- 2b. Tiny institutions that fail ({len(tiny_failers)} with ≤50 completions) ---\n")
for _, r in tiny_failers.head(10).iterrows():
    print(f"  {r['institution']} ({r['STABBR']})")
    print(f"    Completions: {r['total_completions']:.0f} | Earnings: ${r['median_earnings']:,.0f} | Threshold: ${r['Threshold']:,.0f}")
    print()


# ── PROBLEM 3: Simpson's Paradox ──────────────────────────────────────────────

print("\n" + "=" * 80)
print("PROBLEM 3: SIMPSON'S PARADOX")
print("=" * 80)

# 3a. States with wide within-state county earnings variation
county_state = county_earnings.copy()
county_state["state_fips"] = county_state["county_fips"].astype(str).str.zfill(5).str[:2]
county_state["hs_median_earnings"] = pd.to_numeric(county_state["hs_median_earnings"], errors="coerce")

county_variation = county_state.groupby("state_fips").agg(
    min_county=("hs_median_earnings", "min"),
    max_county=("hs_median_earnings", "max"),
    median_county=("hs_median_earnings", "median"),
    std_county=("hs_median_earnings", "std"),
    n_counties=("hs_median_earnings", "count"),
).reset_index()
county_variation["range"] = county_variation["max_county"] - county_variation["min_county"]
county_variation = county_variation.sort_values("range", ascending=False)

print(f"\n--- 3a. States with widest county earnings variation ---\n")
for _, r in county_variation.head(10).iterrows():
    print(f"  State FIPS {r['state_fips']}: Range ${r['range']:,.0f} (${r['min_county']:,.0f} – ${r['max_county']:,.0f}), "
          f"Median: ${r['median_county']:,.0f}, Counties: {r['n_counties']:.0f}")

# 3b. Institutions that beat county benchmark but fail statewide
beat_county_fail_state = df[
    df["fail_state"] & df["pass_local"] & df["has_county"]
].copy()
beat_county_fail_state["local_margin"] = beat_county_fail_state["median_earnings"] - beat_county_fail_state["county_hs_earnings"]
beat_county_fail_state["local_margin_pct"] = (beat_county_fail_state["local_margin"] / beat_county_fail_state["county_hs_earnings"] * 100)
beat_county_fail_state = beat_county_fail_state.sort_values("local_margin_pct", ascending=False)

print(f"\n--- 3b. Beat county benchmark by most but still fail state ({len(beat_county_fail_state)} total) ---\n")
for _, r in beat_county_fail_state.head(10).iterrows():
    print(f"  {r['institution']} ({r['STABBR']}, {r.get('county', 'N/A')})")
    print(f"    Earnings: ${r['median_earnings']:,.0f} | County HS: ${r['county_hs_earnings']:,.0f} (+{r['local_margin_pct']:.0f}%) | State threshold: ${r['Threshold']:,.0f}")
    print()

# 3c. Pass rate divergence by sector within states
print(f"\n--- 3c. Pass rate by sector within states (divergent outcomes) ---\n")
sector_state = df.groupby(["STABBR", "sector_name"]).agg(
    n=("fail_state", "count"),
    fail_rate=("fail_state", "mean"),
).reset_index()
sector_state = sector_state[sector_state["n"] >= 5]

# Find states where public schools have very different fail rates from for-profits
for state in df["STABBR"].unique():
    state_sectors = sector_state[sector_state["STABBR"] == state]
    if len(state_sectors) < 2:
        continue
    public = state_sectors[state_sectors["sector_name"].str.contains("Public", na=False)]
    forprofit = state_sectors[state_sectors["sector_name"].str.contains("for-profit", case=False, na=False)]
    if len(public) > 0 and len(forprofit) > 0:
        pub_rate = public["fail_rate"].mean()
        fp_rate = forprofit["fail_rate"].mean()
        if abs(pub_rate - fp_rate) > 0.3:
            print(f"  {state}: Public fail rate {pub_rate:.0%} vs For-profit fail rate {fp_rate:.0%}")


# ── PROBLEM 4: Measurement Error ─────────────────────────────────────────────

print("\n\n" + "=" * 80)
print("PROBLEM 4: MEASUREMENT ERROR")
print("=" * 80)

# 4a. Late bloomers: P6 < Threshold but P10 >= Threshold
late_bloomers = df[
    (df["MD_EARN_WNE_P6"].notna()) &
    (df["MD_EARN_WNE_P10"].notna()) &
    (df["MD_EARN_WNE_P6"] < df["Threshold"]) &
    (df["MD_EARN_WNE_P10"] >= df["Threshold"])
].copy()
late_bloomers["p6_gap"] = late_bloomers["Threshold"] - late_bloomers["MD_EARN_WNE_P6"]
late_bloomers["p10_surplus"] = late_bloomers["MD_EARN_WNE_P10"] - late_bloomers["Threshold"]
late_bloomers = late_bloomers.sort_values("p10_surplus", ascending=False)

print(f"\n--- 4a. Late bloomers: fail P6, pass P10 ({len(late_bloomers)} institutions) ---\n")
for _, r in late_bloomers.head(15).iterrows():
    print(f"  {r['institution']} ({r['STABBR']})")
    print(f"    P6: ${r['MD_EARN_WNE_P6']:,.0f} (fail by ${r['p6_gap']:,.0f}) | P10: ${r['MD_EARN_WNE_P10']:,.0f} (pass by ${r['p10_surplus']:,.0f}) | Threshold: ${r['Threshold']:,.0f}")
    print()

# 4b. Threshold cliff: within ±5% of threshold
cliff = df[
    (df["earnings_margin_pct"].notna()) &
    (df["earnings_margin_pct"].abs() <= 5)
].copy()
cliff = cliff.sort_values("earnings_margin_pct")

print(f"\n--- 4b. Threshold cliff: within ±5% ({len(cliff)} institutions) ---\n")
# Show the narrowest margins
narrowest = cliff.sort_values("earnings_margin_pct", key=abs)
for _, r in narrowest.head(15).iterrows():
    status = "FAILS" if r["fail_state"] else "PASSES"
    print(f"  {r['institution']} ({r['STABBR']})")
    print(f"    Earnings: ${r['median_earnings']:,.0f} | Threshold: ${r['Threshold']:,.0f} | Margin: {r['earnings_margin_pct']:+.1f}% → {status}")
    print()

# 4c. P6 vs P10 growth for institutions near threshold
p6_p10 = df[
    (df["MD_EARN_WNE_P6"].notna()) &
    (df["MD_EARN_WNE_P10"].notna())
].copy()
p6_p10["growth"] = p6_p10["MD_EARN_WNE_P10"] - p6_p10["MD_EARN_WNE_P6"]
p6_p10["growth_pct"] = (p6_p10["growth"] / p6_p10["MD_EARN_WNE_P6"] * 100)

print(f"\n--- 4c. P6→P10 growth statistics ---")
print(f"  Median growth: ${p6_p10['growth'].median():,.0f} ({p6_p10['growth_pct'].median():.1f}%)")
print(f"  Mean growth: ${p6_p10['growth'].mean():,.0f} ({p6_p10['growth_pct'].mean():.1f}%)")
print(f"  Institutions with >20% growth: {(p6_p10['growth_pct'] > 20).sum()}")
print()


# ── PROBLEM 5: What the Metric Doesn't Measure ───────────────────────────────

print("\n" + "=" * 80)
print("PROBLEM 5: WHAT THE METRIC DOESN'T MEASURE")
print("=" * 80)

# 5a. Sector contrasts in same state
print(f"\n--- 5a. Sector fail rates by state (selected states) ---\n")
state_sector_summary = df.groupby(["STABBR", "sector_name"]).agg(
    count=("fail_state", "count"),
    fail_count=("fail_state", "sum"),
    fail_rate=("fail_state", "mean"),
    median_earn=("median_earnings", "median"),
).reset_index()

for state in ["CA", "TX", "NY", "FL", "OH", "PA"]:
    print(f"  {state}:")
    ss = state_sector_summary[state_sector_summary["STABBR"] == state].sort_values("fail_rate", ascending=False)
    for _, r in ss.iterrows():
        print(f"    {r['sector_name']}: {r['fail_rate']:.0%} fail ({r['fail_count']:.0f}/{r['count']:.0f}), median ${r['median_earn']:,.0f}")
    print()

# 5b. Community colleges (2-year public) that fail
comm_colleges = df[
    (df["sector_name"].str.contains("2-year", na=False) | df["sector_name"].str.contains("Public 2", na=False)) &
    df["fail_state"]
].sort_values("earnings_margin_pct")

print(f"\n--- 5b. Public 2-year institutions that fail ({len(comm_colleges)}) ---")
print("Worst margins:\n")
for _, r in comm_colleges.head(10).iterrows():
    print(f"  {r['institution']} ({r['STABBR']})")
    print(f"    Earnings: ${r['median_earnings']:,.0f} | Threshold: ${r['Threshold']:,.0f} | Margin: {r['earnings_margin_pct']:.1f}%")
    if pd.notna(r.get("county_hs_earnings")):
        local_status = "PASSES" if r["median_earnings"] >= r["county_hs_earnings"] else "FAILS"
        print(f"    County HS earnings: ${r['county_hs_earnings']:,.0f} → {local_status} local")
    print()

# 5c. Overall stats for the document
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
print(f"\nTotal institutions: {len(df)}")
print(f"Fail statewide: {df['fail_state'].sum()} ({df['fail_state'].mean():.1%})")
print(f"With county data: {df['has_county'].sum()}")
print(f"Fail state, pass local: {len(penalized)} ({len(penalized)/df['has_county'].sum():.1%} of those with county data)")
print(f"Pass state, fail local: {len(masked)} ({len(masked)/df['has_county'].sum():.1%} of those with county data)")
print(f"Late bloomers (fail P6, pass P10): {len(late_bloomers)}")
print(f"Within ±5% of threshold: {len(cliff)} ({len(cliff)/len(df):.1%})")
print(f"Reclassification rate: {len(penalized)}/{df['fail_state'].sum()} = {len(penalized)/df['fail_state'].sum():.1%} of failures would pass locally")
