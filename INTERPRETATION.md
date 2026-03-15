# INTERPRETATION.md — Metric Documentation

Reference for how EP Analyzer metrics are calculated and what they mean.

---

## Risk

### Definition

Risk level classifies institutions by how far their median graduate earnings sit relative to their state's high school earnings threshold (the Earnings Premium benchmark).

### Formula

```
earnings_margin = median_earnings - state_threshold
earnings_margin_pct = (earnings_margin / state_threshold) × 100
```

### Classification Thresholds

| Risk Level | Earnings Margin % | Meaning |
|---|---|---|
| Very Low Risk | ≥ +50% | Earnings comfortably exceed the benchmark |
| Low Risk | +20% to +49.9% | Solid margin above the benchmark |
| Moderate Risk | 0% to +19.9% | Passes but vulnerable — one bad cohort could flip outcome |
| High Risk | < 0% (negative) | Below the benchmark — fails the EP test |
| No Data | N/A | Institution has no reported median earnings |

### Data Sources

- **`median_earnings`**: Uses College Scorecard P10 (`MD_EARN_WNE_P10`, 10-year post-enrollment median earnings) when available (5,280 institutions). Falls back to P6 (`MD_EARN_WNE_P6`, 6-year) for the remaining 262 institutions that lack P10 data. 887 institutions have no earnings data at all ("No Data" risk level).
- **`state_threshold`**: State-level HS graduate median earnings from `data/state_thresholds_2024.csv` (52 entries: 50 states + DC + national).

### Caveats

- Risk is pre-computed in the parquet file, not calculated at runtime.
- The threshold is a single statewide number — it does not reflect county-level variation (see the "State vs. Local" analysis tab for that comparison).
- "Moderate Risk" institutions are the most policy-sensitive: they technically pass but are close enough to the threshold that normal earnings fluctuation could cause them to fail.
