# EP Analyzer

Analyzes geographic bias in the **Earnings Premium (EP) test** — a higher education accountability mechanism in the [One Big Beautiful Bill Act](https://www.congress.gov/bill/119th-congress/house-bill/1) (effective July 2026). The law requires that a program's median graduate earnings exceed a statewide high-school-graduate earnings threshold to maintain federal financial aid eligibility. This tool reveals where that uniform statewide threshold produces outcomes that don't reflect local economic reality.

## The Core Problem

The EP test uses a single statewide earnings threshold per state, but labor markets are local. A program producing graduates who out-earn every local high school graduate can still fail if its county's wages fall below the state average. Conversely, a program in a wealthy metro can pass the statewide bar while its graduates actually underperform relative to local non-college workers. The EP test as designed measures geography as much as it measures program quality.

## Level of Analysis

This application analyzes **institution-level** median graduate earnings (College Scorecard P6/P10), not individual program-level earnings. The OBBB law will apply the EP test at the program level, but program-level public earnings data remains limited. The geographic bias demonstrated at the institutional level applies equally — and likely more acutely — at the program level, since lower-earning fields like education and social work sit well below the institutional blend.

## Architecture

- **Backend**: FastAPI (Python) serving parquet data via REST APIs
- **Frontend**: Next.js (App Router) with Recharts visualizations
- **Data**: College Scorecard, IPEDS, and Census ACS

## Features

| Page | Description |
|------|-------------|
| **Overview** | National risk distribution, sector breakdown, risk calculation explainer |
| **States** | Per-state drill-down with risk distribution, margin histogram, institution table |
| **Institutions** | Search/filter by name, state, sector, risk level; institution detail with peer comparison |
| **Analysis** | Statewide vs. local benchmark reclassification, state vs. local divergent institution view, margin distribution, early vs. late earnings |

### Risk Levels

| Risk Level | Earnings Margin % | Meaning |
|---|---|---|
| Very Low Risk | >= +50% | Earnings comfortably exceed the benchmark |
| Low Risk | +20% to +49.9% | Solid margin above the benchmark |
| Moderate Risk | 0% to +19.9% | Passes but vulnerable — one bad cohort could flip outcome |
| High Risk | < 0% (negative) | Below the benchmark — fails the EP test |
| No Data | N/A | No reported median earnings |

### Reclassification Categories

The analysis page compares statewide vs. county-level thresholds, classifying institutions into four groups:

| Classification | Statewide | Local | Interpretation |
|---|---|---|---|
| **Pass Both** | Pass | Pass | Above threshold regardless of benchmark |
| **Fail Both** | Fail | Fail | Below threshold regardless of benchmark |
| **Pass Local Only** | Fail | Pass | Geographic bias victim — out-earns local HS grads but fails statewide bar |
| **Pass State Only** | Pass | Fail | Masked underperformance — passes statewide but earns less than local HS grads |

## Quick Start

### Local Development

```bash
# Backend
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### Docker

```bash
docker compose up --build
```

### Data Pipeline

```bash
# Fetch county-level HS earnings from Census ACS and build enriched dataset
python -m backend.app.pipelines.fetch_county_earnings
```

This generates `data/county_hs_earnings.csv`, `data/institution_county_mapping.csv`, and `data/ep_analysis_enriched.parquet`. The enriched parquet is auto-detected by the backend at startup.

## Data

All data files are in `data/`:

| File | Records | Source |
|------|---------|--------|
| `ep_analysis.parquet` | 6,429 institutions | College Scorecard + IPEDS + state thresholds |
| `ep_analysis_enriched.parquet` | 6,429 institutions | Above + county FIPS/earnings (generated, not checked in) |
| `program_counts.parquet` | 3,936 institutions | IPEDS completions |
| `scorecard_earnings.csv` | 6,429 institutions | College Scorecard P6 + P10 earnings |
| `state_thresholds_2024.csv` | 52 | Federal Register / Census ACS |
| `county_hs_earnings.csv` | County-level | Census ACS B20004 HS graduate median earnings |
| `institution_county_mapping.csv` | Institution-level | UnitID to county FIPS mapping from IPEDS |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `GET /api/overview` | National summary stats |
| `GET /api/states` | All states with risk breakdown |
| `GET /api/states/{state}` | State detail with institutions |
| `GET /api/institutions?search=&state=&sector=&risk=&limit=&offset=` | Search/filter institutions |
| `GET /api/institutions/{id}` | Institution detail |
| `GET /api/institutions/{id}/peers?limit=` | Same-state, same-sector peers |
| `GET /api/analysis/reclassification?state=&inequality=&seed=` | Statewide vs. local benchmark comparison |
| `GET /api/analysis/sensitivity?unit_id=&steps=` | Earnings change scenarios |
| `GET /api/analysis/margins?state=&sector=` | Margin distribution |
| `GET /api/analysis/early-vs-late?state=&limit=` | P6 vs P10 earnings comparison |

## Key Findings

- **Geographic bias is structural**: Institutions in low-wage counties fail the statewide bar even when their graduates significantly out-earn local high school graduates. States with high intra-state inequality (NY, CA, TX) show the largest divergence between statewide and local outcomes.
- **Thresholds are fragile**: Many institutions cluster near the pass/fail boundary. Normal year-to-year earnings fluctuations can flip outcomes, making the binary determination more volatile than it appears.
- **Measurement timing matters**: Some institutions fail at P6 (6-year earnings) but pass at P10 (10-year). Fields with back-loaded earnings growth — education, social work, healthcare — are systematically disadvantaged by early measurement.
- **Sector patterns are uneven**: Community colleges and public 2-year institutions face disproportionate risk, as their graduates' earnings reflect local labor markets below the statewide average. For-profit institutions show mixed patterns depending on geography.

## Further Reading

- **[ANALYSIS.md](ANALYSIS.md)** — Full analytical findings, policy implications, and methodology
- **[INTERPRETATION.md](INTERPRETATION.md)** — Metric definitions, formulas, and classification thresholds

## License

MIT
