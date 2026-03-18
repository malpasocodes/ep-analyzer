# EP Analyzer: Analysis of Geographic Bias in the Earnings Premium Test

## What This Application Does

EP Analyzer examines how the **Earnings Premium (EP) test** — a core accountability mechanism in the [One Big Beautiful Bill Act](https://www.congress.gov/bill/119th-congress/house-bill/1) — creates geographic winners and losers among college programs. The law requires that a program's median graduate earnings exceed a statewide high-school-graduate earnings threshold to maintain federal financial aid eligibility.

This application compares that **statewide benchmark** against **county-level benchmarks** derived from real Census data to reveal where the uniform threshold produces outcomes that don't reflect local economic reality.

### Data Sources

- **Census ACS Table B20004**: County-level median earnings for high school graduates (the local benchmark)
- **IPEDS**: Institution-to-county FIPS code mappings via the Integrated Postsecondary Education Data System
- **College Scorecard**: Institutional median graduate earnings at 6 years (P6) and 10 years (P10) post-enrollment
- **State HS earnings thresholds**: The statewide benchmarks each program must beat (52 entries covering 50 states + DC)

The dataset covers **6,429 institutional records** across all 50 states and DC.

## Level of Analysis

This application analyzes **institution-level** median graduate earnings from College Scorecard (P6 and P10 measures), not individual program-level earnings. Each record represents an institution's overall median graduate earnings compared against the applicable threshold.

The OBBB law, however, will apply the earnings premium test at the **program level** — each program's median graduate earnings must independently exceed the threshold to maintain eligibility. Program-level public earnings data remains limited, making institution-level analysis the best available proxy for studying the threshold's structural effects.

Critically, the geographic bias demonstrated here at the institutional level applies equally — and likely more acutely — at the program level. If an institution's blended median earnings face geographic distortion from a uniform statewide threshold, individual programs within that institution will face it even more sharply. Lower-earning fields like education, social work, and the arts will be hit hardest, since their program-level medians sit well below the institutional blend that already struggles to clear the bar in low-wage regions.

## The Core Problem

The EP test uses a single statewide earnings threshold per state. A nursing program in rural Mississippi and a finance program in Manhattan must each clear their respective state's one number. But labor markets are local: the cost of living, prevailing wages, and economic opportunity vary enormously within a state.

This means:

- **A program producing graduates who out-earn every local high school graduate could still fail** if its county's wages fall below the state average.
- **A program in a wealthy metro could pass the statewide bar while its graduates actually underperform relative to local non-college workers.**

The EP test as designed measures geography as much as it measures program quality.

## Key Analytical Findings

### 1. Geographic Bias — "Pass Local Only" Institutions

The reclassification analysis compares each institution's outcome under the statewide threshold versus a local (county-level) threshold. Institutions are classified into four groups:

| Classification | Statewide | Local | Interpretation |
|---|---|---|---|
| **Pass Both** | Pass | Pass | Genuinely above threshold regardless of benchmark |
| **Fail Both** | Fail | Fail | Genuinely below threshold regardless of benchmark |
| **Pass Local Only** | Fail | Pass | Geographic bias victim — graduates out-earn local HS grads but fail the statewide bar |
| **Pass State Only** | Pass | Fail | Masked underperformance — passes statewide but graduates earn less than local HS grads |

**"Pass Local Only"** institutions are the clearest evidence of geographic bias. These institutions deliver economic value relative to their local labor market but would lose federal aid eligibility under the uniform threshold. They tend to be concentrated in lower-wage rural areas.

**"Pass State Only"** institutions represent the opposite distortion: institutions that appear successful by statewide standards but whose graduates actually earn less than local high school graduates. A uniform threshold masks this underperformance in high-wage areas.

### 2. Threshold Fragility

The margin analysis reveals that many institutions cluster near the pass/fail boundary. The application computes each institution's **earnings margin** — how far above or below the threshold its graduates fall, as a percentage.

Institutions with small positive margins (0–20% above threshold) are classified as **near-threshold**. For these institutions, normal year-to-year earnings fluctuations, small changes in graduate mix, or minor data revisions could flip their outcome from pass to fail. This fragility means the EP test's binary pass/fail determination overstates the precision of the underlying earnings data.

The sensitivity analysis lets users model this directly: for any institution, it shows how earnings changes of ±50% affect pass/fail status, revealing how thin the margin really is.

### 3. Measurement Timing Bias — P6 vs. P10

The early-vs-late analysis compares institutional outcomes using earnings measured at **6 years** post-enrollment (P6) versus **10 years** (P10). Some institutions show a pattern where graduates fail the threshold at P6 but pass at P10 — their earnings trajectory crosses the bar later.

These "late bloomer" institutions are penalized not for poor quality but for **timing**. Institutions concentrated in fields where earnings growth is back-loaded (e.g., education, social work, some healthcare fields) are systematically disadvantaged by a P6-based measurement, even though their graduates ultimately achieve strong earnings outcomes.

Institutions where P6 and P10 produce **different pass/fail outcomes** (`changed = true` in the analysis) highlight where measurement timing — not program quality — drives the result.

### 4. Sector and Regional Patterns

Risk classification (High Risk, Moderate Risk, Low Risk, Insufficient Data) is not distributed evenly:

- **Community colleges and public 2-year institutions** face disproportionate risk, as their graduates' earnings reflect local labor markets that may sit below the statewide average.
- **For-profit institutions** show mixed patterns — some in metro areas benefit from the statewide threshold while others in lower-wage areas are penalized.
- **States with high intra-state inequality** (e.g., New York, California, Texas) show the largest divergence between statewide and local outcomes, producing the most reclassification changes.

## Policy Implications

### Local Benchmarks Would Be More Equitable

When county-level earnings are used as the benchmark, outcomes better reflect whether a program delivers value relative to the alternative of not attending college *in that labor market*. The application demonstrates this by letting users compare statewide vs. local reclassification results state by state.

### Rural and Community College Programs Are Disproportionately Affected

Programs serving students in lower-wage areas face a structural disadvantage under a uniform statewide bar. These are often the programs serving students with the fewest alternatives — precisely the populations the accountability framework should protect, not penalize.

### Benchmark Transparency Matters

The application distinguishes between **real** county earnings data (from Census ACS B20004) and **synthetic** benchmarks (used when county data is unavailable). This distinction matters for policy credibility: conclusions drawn from real local data are stronger than those from modeled estimates. The `benchmark_source` field in every reclassification result makes this transparent.

### The Binary Pass/Fail Design Overstates Precision

Given the clustering of institutions near the threshold and the sensitivity of outcomes to small earnings changes, a binary pass/fail determination converts continuous, noisy data into a bright-line rule with significant consequences. Margin-aware or graduated approaches would better match the precision of the underlying data.

## How to Explore These Findings

| Application Section | What It Shows |
|---|---|
| **Overview** | National risk distribution and sector breakdown |
| **States** | Per-state institution counts, risk levels, and threshold values |
| **Institutions** | Individual institution detail — earnings, margins, risk classification |
| **Analysis** | Reclassification (statewide vs. local), margin distributions, sensitivity modeling, P6 vs. P10 comparison |

The analysis page's **inequality slider** (0–1) controls the variance of synthetic local benchmarks — higher values model greater within-state inequality. This only affects institutions without real county data; institutions with Census-sourced county earnings always use the real value.
