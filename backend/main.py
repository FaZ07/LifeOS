"""Uvicorn entry point: `uvicorn backend.main:app --reload`."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .memory import storage


def create_app() -> FastAPI:
    app = FastAPI(
        title="LifeOS — Counterfactual Decision Engine",
        version="2.0.0",
        description=(
            "Deterministic, Monte-Carlo-based life-trajectory simulator. "
            "No ML, no external AI — just physics-style modelling of behaviour."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    storage.init_db()
    app.include_router(router, prefix="/api")

    @app.get("/")
    def root() -> dict[str, str]:
        return {"service": "LifeOS", "docs": "/docs", "health": "/api/health"}

    return app


app = create_app()
