# EP Analyzer

Earnings Premium analysis tool for higher education accountability. Shows how geographic bias in statewide earnings benchmarks affects college program pass/fail outcomes under the One Big Beautiful Bill Act (effective July 2026).

## Architecture

- **Backend**: FastAPI serving parquet data via REST APIs
- **Frontend**: Next.js (App Router) with Recharts visualizations
- **Data**: Real data from College Scorecard, IPEDS, and Census ACS

## Features

| Page | Description |
|------|-------------|
| **Overview** | National risk distribution, sector breakdown, program-level exposure stats |
| **States** | Per-state drill-down with risk distribution, margin histogram, institution table |
| **Institutions** | Search/filter by name, state, sector, risk level; institution detail with peer comparison |
| **Analysis** | Statewide vs. local benchmark reclassification, margin distribution, early vs. late earnings |

## Quick Start

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
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

## Data

All data files are in `data/`:

| File | Records | Source |
|------|---------|--------|
| `ep_analysis.parquet` | 6,429 institutions | College Scorecard + IPEDS + state thresholds |
| `program_counts.parquet` | 3,936 institutions | IPEDS completions |
| `scorecard_earnings.csv` | 6,429 institutions | College Scorecard P6 + P10 earnings |
| `state_thresholds_2024.csv` | 52 | Federal Register / Census ACS |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/overview` | National summary stats |
| `GET /api/states` | All states with risk breakdown |
| `GET /api/states/{state}` | State detail with institutions |
| `GET /api/institutions?search=&state=&risk=` | Search/filter institutions |
| `GET /api/institutions/{id}` | Institution detail |
| `GET /api/institutions/{id}/peers` | Same-state, same-sector peers |
| `GET /api/analysis/reclassification?state=&inequality=` | Statewide vs. local benchmark comparison |
| `GET /api/analysis/sensitivity?unit_id=` | Earnings change scenarios |
| `GET /api/analysis/margins?state=&sector=` | Margin distribution |
| `GET /api/analysis/early-vs-late?state=` | P6 vs P10 earnings comparison |

## License

MIT
