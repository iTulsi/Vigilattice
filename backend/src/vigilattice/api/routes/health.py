from datetime import UTC, datetime

from fastapi import APIRouter

from vigilattice import __version__
from vigilattice.models.api import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="operational",
        service="vigilattice-api",
        version=__version__,
        timestamp=datetime.now(UTC),
    )
