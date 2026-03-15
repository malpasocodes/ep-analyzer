"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import overview, states, institutions, analysis

app = FastAPI(
    title="EP Analyzer API",
    description="Earnings Premium analysis for higher education accountability",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(overview.router)
app.include_router(states.router)
app.include_router(institutions.router)
app.include_router(analysis.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
