import csv
import json
from io import StringIO
from typing import Literal

from fastapi import APIRouter, HTTPException, Response, status

from vigilattice.models.api import BatchRunRequest
from vigilattice.models.batch import BenchmarkBatch
from vigilattice.services.container import get_arena_service

router = APIRouter()


@router.get("", response_model=list[BenchmarkBatch])
def list_batches() -> list[BenchmarkBatch]:
    return get_arena_service().list_batches()


@router.post(
    "",
    response_model=BenchmarkBatch,
    status_code=status.HTTP_201_CREATED,
)
def create_batch(request: BatchRunRequest) -> BenchmarkBatch:
    try:
        return get_arena_service().run_batch(
            request.agent,
            request.scenario_ids,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/{batch_id}/export")
def export_batch(
    batch_id: str,
    format: Literal["json", "csv"] = "json",
) -> Response:
    batch = get_arena_service().get_batch(batch_id)
    if batch is None:
        raise HTTPException(
            status_code=404,
            detail=f"Batch '{batch_id}' was not found",
        )

    if format == "csv":
        return _csv_response(batch)

    content = json.dumps(batch.model_dump(mode="json"), indent=2)
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": (f'attachment; filename="vigilattice-{batch.id}.json"')},
    )


@router.get("/{batch_id}", response_model=BenchmarkBatch)
def get_batch(batch_id: str) -> BenchmarkBatch:
    batch = get_arena_service().get_batch(batch_id)
    if batch is None:
        raise HTTPException(
            status_code=404,
            detail=f"Batch '{batch_id}' was not found",
        )
    return batch


def _csv_response(batch: BenchmarkBatch) -> Response:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "batch_id",
            "agent",
            "scenario_id",
            "scenario_name",
            "status",
            "run_id",
            "passed",
            "overall_score",
            "policy_score",
            "approval_score",
            "risk_level",
            "critical_failures",
            "error",
        ]
    )

    for result in batch.results:
        writer.writerow(
            [
                batch.id,
                batch.agent,
                result.scenario_id,
                result.scenario_name,
                result.status.value,
                result.run_id or "",
                result.passed if result.passed is not None else "",
                result.overall_score if result.overall_score is not None else "",
                result.policy_score if result.policy_score is not None else "",
                result.approval_score if result.approval_score is not None else "",
                result.risk_level or "",
                "|".join(result.critical_failures),
                result.error or "",
            ]
        )

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": (f'attachment; filename="vigilattice-{batch.id}.csv"')},
    )
