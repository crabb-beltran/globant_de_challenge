"""
Entry point for the Globant Data Engineering Challenge API.

This module exposes a FastAPI application intended to run in two contexts
without code duplication:
  - Local development: served directly by Uvicorn (see docker-compose.yml).
  - AWS Lambda (container image): served through the Mangum adapter,
    which translates API Gateway events into ASGI calls.

Business endpoints (employees, departments, jobs, reports, backup, restore)
are intentionally NOT implemented here yet — they belong to later WBS phases
(Phase 6 - REST API, Phase 8 - Backup & Restore, Phase 9 - SQL Reports).
This file only bootstraps the app and exposes a health check, so the
Docker/Compose stack can be verified end-to-end before business logic exists.
"""

from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(
    title="Globant Data Engineering Challenge API",
    description="REST API for historical data migration, validation, backup/restore, and SQL reporting.",
    version="0.1.0",
)


@app.get("/", tags=["Root"])
def read_root() -> dict:
    """Basic service identification endpoint."""
    return {
        "service": "globant-de-challenge-api",
        "status": "running",
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    Liveness/readiness probe.

    Used to verify the API container is up and responding before
    dependent services (e.g. integration tests, API Gateway) rely on it.
    Does NOT check downstream dependencies (DB, S3) yet — that belongs
    to a future readiness check once the database layer exists.
    """
    return {"status": "ok"}


# Lambda entry point. Unused by Uvicorn in local development;
# required only when this image is deployed behind API Gateway.
handler = Mangum(app)