"""
main.py – FastAPI application entry point.

Registers all routers and provides a /health endpoint.
Run with:
    uvicorn backend.main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import auth, profile, sentiment

app = FastAPI(
    title="MoodMentor API",
    description=(
        "Backend for MoodMentor – AI-Powered Emotional Tone Analyzer.\n\n"
        "Milestone 1: user management and VADER sentiment analysis."
    ),
    version="1.0.0",
)

# Allow Streamlit (localhost) to call this API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(sentiment.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["meta"], summary="API health check")
def health() -> dict:
    """Return a simple OK response to confirm the API is running."""
    return {"status": "ok", "service": "MoodMentor API"}
