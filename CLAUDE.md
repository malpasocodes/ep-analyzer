# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EP Analyzer is a full-stack web app analyzing earnings premium bias in higher education accountability under the One Big Beautiful Bill Act. It shows how geographic bias in statewide earnings benchmarks affects college program pass/fail outcomes.

## Development Commands

### Backend (Python/FastAPI)
```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (TypeScript/Next.js)
```bash
cd frontend
npm install
npm run dev          # Dev server on port 3000
npm run build        # Production build
npm run lint         # ESLint
```

### Docker (full stack)
```bash
docker compose up --build
```

## Architecture

**Backend** (`backend/app/`): FastAPI REST API serving parquet/CSV data.
- `main.py` — App setup, CORS (localhost:3000 only), router registration
- `routers/` — 4 route modules: overview, states, institutions, analysis
- `services/risk.py` — Risk classification logic, margin calculations, state name mappings
- `services/benchmark.py` — Synthetic local benchmark generation with inequality parameter (0-1 slider) for reclassification modeling
- `models/schemas.py` — Pydantic response models
- `data/loader.py` — LRU-cached parquet/CSV file loaders

**Frontend** (`frontend/src/`): Next.js 16 App Router with React 19.
- `app/` — Pages: overview, states (list + `[state]` detail), institutions (list + `[id]` detail), analysis
- `lib/api.ts` — Type-safe API client; all backend calls go through here. Uses `NEXT_PUBLIC_API_URL` env var (defaults to `http://localhost:8000`)
- `lib/utils.ts` — Formatting helpers (currency, number, percentage) and color/badge definitions
- `components/charts/` — 5 Recharts components: RiskDonut, SectorBreakdown, MarginHistogram, QuadrantScatter, EarningsComparison

**Data** (`data/`): Static data files loaded by the backend.
- `ep_analysis.parquet` — Main institutional analysis (6,429 records)
- `program_counts.parquet` — Program completion counts (3,936 records)
- `scorecard_earnings.csv` — College Scorecard P6/P10 earnings
- `state_thresholds_2024.csv` — State HS earnings thresholds (52 entries)

## Key Patterns

- Backend data loading is LRU-cached; data files are read once and reused across requests
- The analysis router's reclassification endpoint uses a parametric "inequality" slider (0-1) to model how local benchmarks would differ from statewide ones
- Frontend pages fetch data client-side using the API client in `lib/api.ts`
- No test framework is currently configured for either backend or frontend
