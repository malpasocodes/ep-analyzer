# We Built a Tool to Stress-Test the Earnings Premium — Now With 213,000 Programs

The One Big Beautiful Bill proposes a simple test for higher education accountability: if a college's graduates don't out-earn high school graduates in their state, the institution loses access to federal financial aid. It's called the Earnings Premium (EP) test.

Simple in theory. In practice, it's a blunt instrument — and we built a tool to show exactly where it breaks.

**The EP Analyzer is now live with program-level data.** You can explore it at [ep-analyzer.onrender.com](https://ep-analyzer.onrender.com).

---

## What's New: Program-Level Analysis

The original EP Analyzer worked at the institution level — one earnings figure per school, one pass/fail verdict. But the bill is written to evaluate programs, not institutions. This update brings the tool closer to the actual intent of the legislation, applying the EP test where it's meant to land: at the individual program level.

We've now integrated College Scorecard field-of-study data, covering **213,711 individual programs** across **5,762 institutions** and **424 fields of study**. Each program now carries its own earnings figure, its own margin relative to the state threshold, and its own risk classification.

The headline numbers:

- **63,582 programs** (29.8%) have reportable earnings from the College Scorecard
- **107,804 programs** (50.4%) have earnings suppressed for privacy — their cohorts are too small to report

That last number is worth sitting with. The Department of Education would evaluate these programs using IRS tax filings — data that is not publicly available. Half of all programs in higher education would have their fate decided by a black box: pass/fail verdicts derived from data that neither the institutions, their students, nor independent researchers can see or verify.

So we built a Monte Carlo simulation engine to fill the gap. For each suppressed program, the model draws from a hierarchical prior — national field-of-study median earnings, adjusted for the institution's overall performance and local labor market conditions — across thousands of simulations. The result is an estimated earnings figure, an 80% confidence interval, and a probability of passing the EP test.

This approach let us generate risk estimates for an additional **100,862 suppressed programs**, bringing total risk coverage to **164,444 programs — 76.9% of all programs in the dataset**.

The combined picture:

- **16,417 programs** are likely failing the EP test (9,380 from reported earnings + 7,037 from Monte Carlo estimates)
- **13,792 programs** sit in the moderate risk zone — passing today, but within 20% of the threshold (7,256 reported + 6,536 estimated)
- Together, that's **over 30,000 programs** either failing or at risk of failing

### Earnings Trajectories

We now track earnings at four post-completion timepoints from the College Scorecard: 1-year, 2-year, 4-year, and 5-year. The tool defaults to 4-year earnings when available (the most complete mid-career measure), falling back through 5-year, 2-year, and 1-year as needed.

Of the 63,582 programs with earnings:
- **47,445** (74.6%) use 4-year post-completion earnings
- **7,768** (12.2%) use 2-year
- **5,499** (8.6%) use 1-year
- **2,870** (4.5%) use 5-year

Every program in the tool now shows which timeframe is being used, plus a trajectory column displaying all available data points — so you can see whether a program's graduates are on an upward earnings path or stagnating.

---

## What the EP Analyzer Shows

The tool has five major sections:

### 1. Overview
A dashboard showing the full landscape: 6,429 institutions across 52 states, with risk distributions at both the institution and program level. This is your entry point for understanding the scale of the problem.

### 2. States
Browse all 52 states and their EP thresholds — the statewide median earnings for high school graduates that each institution must beat. Thresholds vary significantly by state, which is the core of the geographic bias problem. Drill into any state to see its institutions ranked by earnings margin, with risk donut charts and margin histograms.

### 3. Institutions
Search and filter 6,429 institutions by name, state, or risk level. Each institution detail page shows:
- Earnings vs. threshold with a visual gauge
- Early (6-year) vs. late (10-year) earnings comparison
- All programs offered at that institution, with individual risk classifications
- Monte Carlo estimates for privacy-suppressed programs, including estimated earnings, 80% confidence intervals, and probability of passing

### 4. Programs
The new centerpiece. Three ways to explore:
- **CIP Explorer**: Browse all 424 fields of study, sorted by risk. See which fields have the highest failure rates across all institutions.
- **Program Search**: Find specific programs by institution or field name. Filter by state and risk level.
- **Most At-Risk**: The fields with the highest concentration of failing programs.

### 5. Benchmark Analysis
The analytical core. This section asks: *what if we used local benchmarks instead of statewide ones?*

Using county-level high school earnings from the Census Bureau (ACS table B20004), the tool reclassifies every institution and program against their local labor market. The results fall into four categories:

- **Pass Both**: safe under either benchmark
- **Fail Both**: genuinely underperforming
- **Pass Local, Fail State**: penalized by geography — graduates out-earn local HS grads but not the statewide average
- **Pass State, Fail Local**: masked by geography — graduates look fine statewide but underperform locally

This is where the geographic bias becomes visible. An institution in rural Appalachia faces the same statewide threshold as one in suburban DC, despite dramatically different local labor markets.

---

## Key Findings

### The fields that fail most often aren't surprising — but the scale is

The programs most likely to fail the EP test read like a list of vocational and creative fields:

| Field | High Risk Programs |
|-------|-------------------|
| Cosmetology | 1,146 |
| Allied Health/Medical Assisting | 716 |
| Health Administration | 610 |
| Dental Support | 336 |
| Liberal Arts | 321 |
| Drama/Theatre | 275 |
| Massage/Bodywork | 271 |
| Fine Arts | 260 |
| Business Support | 230 |
| Music | 225 |

Cosmetology alone accounts for over 12% of all high-risk programs. These are predominantly certificate and associate-level programs at community colleges and for-profit schools — institutions that serve students who often have the fewest alternatives.

### Failing programs aren't empty classrooms

The 9,380 programs with reported earnings that fail the EP test represent **342,692 annual completions** — 7% of all program completions in the dataset. Factor in the 7,037 suppressed programs our Monte Carlo model estimates would also fail, and the true number of affected students is likely far higher. These are real people who chose these programs, completed them, and are working. Under the EP test as proposed, their programs would be flagged for elimination.

### The moderate risk zone is crowded

Another 13,792 programs (7,256 reported + 6,536 estimated) sit between 0% and +20% above their state's threshold. They pass today, but a minor economic shift, a bad cohort year, or a threshold recalculation could push them into failure. These programs represent systemic fragility — they're one recession away from losing eligibility.

### Half of higher education is invisible to policymakers — but not to us

The College Scorecard suppresses earnings for 50.4% of programs. Without our Monte Carlo estimates, policymakers would be making high-stakes funding decisions with no visibility into the majority of programs. Our simulation engine recovers risk estimates for 100,862 of those suppressed programs — but roughly 49,000 remain truly invisible, with neither reported earnings nor enough contextual data to model. The EP test would simply have nothing to say about them.

### At the institution level, 1 in 5 schools fail

Of 6,429 institutions:
- **1,264** (19.7%) are High Risk — currently failing
- **885** (13.8%) are Moderate Risk — vulnerable
- **1,029** (16.0%) have no reportable data at all

That's a third of all institutions either failing or too close to the line for comfort, and another sixth completely invisible to the metric.

---

## Why This Matters

The Earnings Premium test treats higher education as a simple investment calculation: did your degree earn more than a high school diploma? But earnings are shaped by geography, field of study, credential level, local labor markets, and the demographics of who enrolls. A single statewide threshold flattens all of that complexity into a binary pass/fail.

The EP Analyzer doesn't argue that accountability is wrong. It argues that *this particular metric* is too crude for the decisions it's being asked to make. When a cosmetology program in rural Mississippi is measured against the same benchmark as an engineering program in suburban Boston, the test isn't measuring institutional quality — it's measuring zip codes.

Explore the data yourself: [ep-analyzer.onrender.com](https://ep-analyzer.onrender.com)

---

*The EP Analyzer is an independent research tool. It is not affiliated with the Department of Education. All data comes from publicly available sources: the College Scorecard, IPEDS, and the Census Bureau's American Community Survey. Methodology and source code are available on GitHub.*
