from fastapi import APIRouter

from vigilattice.api.routes import (
    analytics,
    batches,
    health,
    regressions,
    runs,
    scenarios,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["system"])
api_router.include_router(
    scenarios.router,
    prefix="/scenarios",
    tags=["scenarios"],
)
api_router.include_router(runs.router, prefix="/runs", tags=["runs"])
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"],
)
api_router.include_router(
    batches.router,
    prefix="/batches",
    tags=["batches"],
)
api_router.include_router(
    regressions.router,
    prefix="/regressions",
    tags=["regressions"],
)
