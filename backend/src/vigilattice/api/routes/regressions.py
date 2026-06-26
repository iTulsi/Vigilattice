import csv
import json
from io import StringIO
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Response, status

from vigilattice.models.regression import (
    RegressionBaseline,
    RegressionComparison,
)
from vigilattice.services.container import get_arena_service

router = APIRouter()


@router.post(
    "/baselines/{batch_id}",
    response_model=RegressionBaseline,
    status_code=status.HTTP_201_CREATED,
)
def set_baseline(batch_id: str) -> RegressionBaseline:
    try:
        return get_arena_service().set_regression_baseline(batch_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get(
    "/baselines/{agent}",
    response_model=RegressionBaseline,
)
def get_baseline(agent: str) -> RegressionBaseline:
    baseline = get_arena_service().get_regression_baseline(agent)
    if baseline is None:
        raise HTTPException(
            status_code=404,
            detail=f"No regression baseline exists for agent '{agent}'",
        )
    return baseline


@router.get(
    "/compare/{batch_id}",
    response_model=RegressionComparison,
)
def compare_batch(
    batch_id: str,
    max_score_drop: float = Query(default=0.0, ge=0, le=100),
    max_pass_rate_drop: float = Query(default=0.0, ge=0, le=100),
) -> RegressionComparison:
    try:
        return get_arena_service().compare_batch_to_baseline(
            batch_id,
            max_score_drop=max_score_drop,
            max_pass_rate_drop=max_pass_rate_drop,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/compare/{batch_id}/export")
def export_comparison(
    batch_id: str,
    format: Literal["json", "csv"] = "json",
    max_score_drop: float = Query(default=0.0, ge=0, le=100),
    max_pass_rate_drop: float = Query(default=0.0, ge=0, le=100),
) -> Response:
    try:
        comparison = get_arena_service().compare_batch_to_baseline(
            batch_id,
            max_score_drop=max_score_drop,
            max_pass_rate_drop=max_pass_rate_drop,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if format == "csv":
        return _csv_response(comparison)

    content = json.dumps(comparison.model_dump(mode="json"), indent=2)
    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition": (
                f'attachment; filename="vigilattice-regression-{batch_id}.json"'
            )
        },
    )


def _csv_response(comparison: RegressionComparison) -> Response:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "baseline_id",
            "baseline_batch_id",
            "candidate_batch_id",
            "agent",
            "regressed",
            "scenario_id",
            "scenario_name",
            "status",
            "baseline_passed",
            "candidate_passed",
            "baseline_score",
            "candidate_score",
            "score_delta",
            "baseline_risk",
            "candidate_risk",
        ]
    )

    for scenario in comparison.scenarios:
        writer.writerow(
            [
                comparison.baseline_id,
                comparison.baseline_batch_id,
                comparison.candidate_batch_id,
                comparison.agent,
                comparison.regressed,
                scenario.scenario_id,
                scenario.scenario_name,
                scenario.status.value,
                (scenario.baseline_passed if scenario.baseline_passed is not None else ""),
                (scenario.candidate_passed if scenario.candidate_passed is not None else ""),
                (scenario.baseline_score if scenario.baseline_score is not None else ""),
                (scenario.candidate_score if scenario.candidate_score is not None else ""),
                scenario.score_delta if scenario.score_delta is not None else "",
                scenario.baseline_risk or "",
                scenario.candidate_risk or "",
            ]
        )

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                f'attachment; filename="vigilattice-regression-{comparison.candidate_batch_id}.csv"'
            )
        },
    )
