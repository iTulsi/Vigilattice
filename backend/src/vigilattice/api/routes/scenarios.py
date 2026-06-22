from fastapi import APIRouter

from vigilattice.models.scenario import ScenarioSummary
from vigilattice.services.container import get_arena_service

router = APIRouter()


@router.get("", response_model=list[ScenarioSummary])
def list_scenarios() -> list[ScenarioSummary]:
    return get_arena_service().list_scenarios()
