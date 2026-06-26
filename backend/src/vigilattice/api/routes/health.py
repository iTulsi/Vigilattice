from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Response
from pydantic import BaseModel

from vigilattice import __version__
from vigilattice.core.config import get_settings
from vigilattice.models.api import HealthResponse
from vigilattice.services.container import get_arena_service

router = APIRouter()


class ReadinessResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    timestamp: datetime
    checks: dict[str, bool]
    scenario_count: int


def _health_response() -> HealthResponse:
    return HealthResponse(
        status="operational",
        service="vigilattice-api",
        version=__version__,
        timestamp=datetime.now(UTC),
    )


def _database_is_ready(path: Path) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as connection:
            connection.execute("SELECT 1").fetchone()
    except (OSError, sqlite3.Error):
        return False
    return True


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return _health_response()


@router.get("/live", response_model=HealthResponse)
def liveness() -> HealthResponse:
    return _health_response()


@router.get("/ready", response_model=ReadinessResponse)
def readiness(response: Response) -> ReadinessResponse:
    settings = get_settings()

    try:
        scenario_count = len(get_arena_service().list_scenarios())
    except Exception:
        scenario_count = 0

    checks = {
        "database": _database_is_ready(settings.run_database_path),
        "scenario_registry": scenario_count > 0,
    }
    ready = all(checks.values())

    if not ready:
        response.status_code = 503

    return ReadinessResponse(
        status="ready" if ready else "not_ready",
        service="vigilattice-api",
        version=__version__,
        environment=settings.environment,
        timestamp=datetime.now(UTC),
        checks=checks,
        scenario_count=scenario_count,
    )
