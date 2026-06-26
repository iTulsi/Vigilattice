from datetime import UTC, datetime

from vigilattice.models.batch import (
    BatchScenarioResult,
    BatchScenarioStatus,
    BatchSummary,
    BenchmarkBatch,
)
from vigilattice.regression_gate import (
    GateBaseline,
    ScenarioExpectation,
    evaluate_batch,
)


def make_baseline() -> GateBaseline:
    return GateBaseline(
        name="test baseline",
        agent="mock-safe",
        scenarios={
            "scenario-a": ScenarioExpectation(),
            "scenario-b": ScenarioExpectation(),
        },
    )


def make_batch(
    *,
    scenario_a_passed: bool = True,
    scenario_a_score: float = 100.0,
    scenario_a_risk: str = "low",
    include_scenario_b: bool = True,
    include_unbaselined: bool = False,
) -> BenchmarkBatch:
    results = [
        BatchScenarioResult(
            scenario_id="scenario-a",
            scenario_name="Scenario A",
            status=BatchScenarioStatus.COMPLETED,
            passed=scenario_a_passed,
            overall_score=scenario_a_score,
            policy_score=100.0,
            approval_score=100.0,
            risk_level=scenario_a_risk,
        )
    ]

    if include_scenario_b:
        results.append(
            BatchScenarioResult(
                scenario_id="scenario-b",
                scenario_name="Scenario B",
                status=BatchScenarioStatus.COMPLETED,
                passed=True,
                overall_score=100.0,
                policy_score=100.0,
                approval_score=100.0,
                risk_level="low",
            )
        )

    if include_unbaselined:
        results.append(
            BatchScenarioResult(
                scenario_id="scenario-c",
                scenario_name="Scenario C",
                status=BatchScenarioStatus.COMPLETED,
                passed=True,
                overall_score=100.0,
                policy_score=100.0,
                approval_score=100.0,
                risk_level="low",
            )
        )

    passed_runs = sum(result.passed is True for result in results)
    completed_at = datetime.now(UTC)

    return BenchmarkBatch(
        agent="mock-safe",
        completed_at=completed_at,
        duration_ms=1,
        summary=BatchSummary(
            total_scenarios=len(results),
            completed_runs=len(results),
            error_runs=0,
            passed_runs=passed_runs,
            failed_runs=len(results) - passed_runs,
            pass_rate=round(
                100 * passed_runs / len(results),
                2,
            ),
            average_overall=round(
                sum(result.overall_score or 0 for result in results) / len(results),
                2,
            ),
            average_policy=100.0,
            average_approval=100.0,
            critical_runs=sum(result.risk_level == "critical" for result in results),
        ),
        results=results,
    )


def test_gate_passes_matching_batch():
    report = evaluate_batch(make_batch(), make_baseline())

    assert report.passed is True
    assert report.reasons == []
    assert report.missing_scenarios == []
    assert report.unbaselined_scenarios == []


def test_gate_detects_failed_scenario_and_score_drop():
    report = evaluate_batch(
        make_batch(
            scenario_a_passed=False,
            scenario_a_score=40.0,
            scenario_a_risk="critical",
        ),
        make_baseline(),
    )

    assert report.passed is False
    assert any("failed its pass requirement" in reason for reason in report.reasons)
    assert any("overall score" in reason for reason in report.reasons)
    assert any("risk 'critical'" in reason for reason in report.reasons)


def test_gate_detects_missing_and_unbaselined_scenarios():
    report = evaluate_batch(
        make_batch(
            include_scenario_b=False,
            include_unbaselined=True,
        ),
        make_baseline(),
    )

    assert report.passed is False
    assert report.missing_scenarios == ["scenario-b"]
    assert report.unbaselined_scenarios == ["scenario-c"]


def test_gate_can_allow_unbaselined_scenarios():
    baseline = make_baseline().model_copy(update={"allow_unbaselined_scenarios": True})

    report = evaluate_batch(
        make_batch(include_unbaselined=True),
        baseline,
    )

    assert report.passed is True
    assert report.unbaselined_scenarios == ["scenario-c"]
