from fastapi import APIRouter

from vigilattice.models.analytics import BenchmarkAnalytics
from vigilattice.services.container import get_arena_service

router = APIRouter()


@router.get("/summary", response_model=BenchmarkAnalytics)
def get_analytics() -> BenchmarkAnalytics:
    return get_arena_service().get_analytics()
