from fastapi import APIRouter, HTTPException, status

from vigilattice.models.api import RunRequest
from vigilattice.models.run import EvaluationRun
from vigilattice.services.container import get_arena_service

router = APIRouter()


@router.get("", response_model=list[EvaluationRun])
def list_runs() -> list[EvaluationRun]:
    return get_arena_service().list_runs()


@router.post("", response_model=EvaluationRun, status_code=status.HTTP_201_CREATED)
def create_run(request: RunRequest) -> EvaluationRun:
    try:
        return get_arena_service().run(request.scenario_id, request.agent)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{run_id}", response_model=EvaluationRun)
def get_run(run_id: str) -> EvaluationRun:
    run = get_arena_service().get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' was not found")
    return run
