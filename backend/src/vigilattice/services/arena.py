from datetime import UTC, datetime

from vigilattice.agents.base import AgentAdapter
from vigilattice.evaluation.engine import EvaluationEngine
from vigilattice.models.analytics import BenchmarkAnalytics
from vigilattice.models.batch import (
    BatchScenarioResult,
    BatchScenarioStatus,
    BatchSummary,
    BenchmarkBatch,
)
from vigilattice.models.regression import (
    RegressionBaseline,
    RegressionComparison,
    RegressionDeltas,
    RegressionThresholds,
    ScenarioRegression,
    ScenarioRegressionStatus,
)
from vigilattice.models.run import EvaluationRun
from vigilattice.models.scenario import ScenarioSpec, ScenarioSummary
from vigilattice.scenarios.loader import ScenarioRegistry
from vigilattice.storage.base import RunRepository


class ArenaService:
    def __init__(
        self,
        registry: ScenarioRegistry,
        agents: dict[str, AgentAdapter],
        evaluator: EvaluationEngine,
        runs: RunRepository,
    ) -> None:
        self.registry = registry
        self.agents = agents
        self.evaluator = evaluator
        self.runs = runs

    def load_scenarios(self) -> None:
        self.registry.load()

    def list_scenarios(self) -> list[ScenarioSummary]:
        return [
            ScenarioSummary(
                id=scenario.id,
                name=scenario.name,
                category=scenario.category,
                description=scenario.description,
                severity=scenario.severity,
            )
            for scenario in self.registry.list()
        ]

    def run(self, scenario_id: str, agent_name: str) -> EvaluationRun:
        scenario = self.registry.get(scenario_id)
        agent = self._get_agent(agent_name)
        trace = agent.execute(scenario)
        report = self.evaluator.evaluate(scenario, trace)
        run = EvaluationRun(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            agent=agent.name,
            trace=trace,
            report=report,
        )
        return self.runs.save(run)

    def run_batch(
        self,
        agent_name: str,
        scenario_ids: list[str] | None = None,
    ) -> BenchmarkBatch:
        self._get_agent(agent_name)
        scenarios = self._resolve_batch_scenarios(scenario_ids)
        started_at = datetime.now(UTC)
        results: list[BatchScenarioResult] = []

        for scenario in scenarios:
            try:
                run = self.run(scenario.id, agent_name)
            except ValueError as exc:
                results.append(
                    BatchScenarioResult(
                        scenario_id=scenario.id,
                        scenario_name=scenario.name,
                        status=BatchScenarioStatus.ERROR,
                        error=str(exc),
                    )
                )
                continue

            results.append(
                BatchScenarioResult(
                    scenario_id=scenario.id,
                    scenario_name=scenario.name,
                    status=BatchScenarioStatus.COMPLETED,
                    run_id=run.id,
                    passed=run.report.passed,
                    overall_score=run.report.scores.overall,
                    policy_score=run.report.scores.policy_compliance,
                    approval_score=run.report.scores.approval_safety,
                    risk_level=run.report.risk_level.value,
                    critical_failures=run.report.critical_failures,
                )
            )

        completed_at = datetime.now(UTC)
        batch = BenchmarkBatch(
            agent=agent_name,
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=max(
                0,
                round((completed_at - started_at).total_seconds() * 1000),
            ),
            summary=self._build_batch_summary(results),
            results=results,
        )
        return self.runs.save_batch(batch)

    def list_runs(self) -> list[EvaluationRun]:
        return self.runs.list()

    def get_run(self, run_id: str) -> EvaluationRun | None:
        return self.runs.get(run_id)

    def get_analytics(self) -> BenchmarkAnalytics:
        return self.runs.analytics()

    def list_batches(self) -> list[BenchmarkBatch]:
        return self.runs.list_batches()

    def get_batch(self, batch_id: str) -> BenchmarkBatch | None:
        return self.runs.get_batch(batch_id)

    def set_regression_baseline(
        self,
        batch_id: str,
    ) -> RegressionBaseline:
        batch = self.get_batch(batch_id)
        if batch is None:
            raise KeyError(f"Batch '{batch_id}' was not found")
        if batch.summary.completed_runs == 0:
            raise ValueError("A baseline must contain completed evaluations")
        if batch.summary.error_runs > 0:
            raise ValueError("A baseline cannot contain scenario execution errors")

        baseline = RegressionBaseline(
            agent=batch.agent,
            batch_id=batch.id,
            batch=batch.model_copy(deep=True),
        )
        return self.runs.save_baseline(baseline)

    def get_regression_baseline(
        self,
        agent: str,
    ) -> RegressionBaseline | None:
        return self.runs.get_baseline(agent)

    def compare_batch_to_baseline(
        self,
        batch_id: str,
        *,
        max_score_drop: float = 0.0,
        max_pass_rate_drop: float = 0.0,
    ) -> RegressionComparison:
        candidate = self.get_batch(batch_id)
        if candidate is None:
            raise KeyError(f"Batch '{batch_id}' was not found")

        baseline = self.get_regression_baseline(candidate.agent)
        if baseline is None:
            raise KeyError(f"No regression baseline exists for agent '{candidate.agent}'")

        thresholds = RegressionThresholds(
            max_score_drop=max_score_drop,
            max_pass_rate_drop=max_pass_rate_drop,
        )
        return self._compare_batches(
            baseline,
            candidate,
            thresholds,
        )

    @staticmethod
    def _compare_batches(
        baseline: RegressionBaseline,
        candidate: BenchmarkBatch,
        thresholds: RegressionThresholds,
    ) -> RegressionComparison:
        baseline_batch = baseline.batch
        baseline_results = {result.scenario_id: result for result in baseline_batch.results}
        candidate_results = {result.scenario_id: result for result in candidate.results}

        scenarios: list[ScenarioRegression] = []
        newly_failing: list[str] = []
        recovered: list[str] = []
        missing: list[str] = []

        for scenario_id in sorted(baseline_results.keys() | candidate_results.keys()):
            baseline_result = baseline_results.get(scenario_id)
            candidate_result = candidate_results.get(scenario_id)

            if baseline_result is None and candidate_result is not None:
                scenario_status = ScenarioRegressionStatus.NEW_SCENARIO
                scenario_name = candidate_result.scenario_name
            elif candidate_result is None and baseline_result is not None:
                scenario_status = ScenarioRegressionStatus.MISSING
                scenario_name = baseline_result.scenario_name
                missing.append(scenario_id)
            else:
                assert baseline_result is not None
                assert candidate_result is not None
                scenario_name = candidate_result.scenario_name

                if baseline_result.passed is True and candidate_result.passed is not True:
                    scenario_status = ScenarioRegressionStatus.NEW_FAILURE
                    newly_failing.append(scenario_id)
                elif baseline_result.passed is not True and candidate_result.passed is True:
                    scenario_status = ScenarioRegressionStatus.RECOVERED
                    recovered.append(scenario_id)
                elif candidate_result.passed is True:
                    scenario_status = ScenarioRegressionStatus.UNCHANGED_PASS
                else:
                    scenario_status = ScenarioRegressionStatus.UNCHANGED_FAIL

            baseline_score = baseline_result.overall_score if baseline_result is not None else None
            candidate_score = (
                candidate_result.overall_score if candidate_result is not None else None
            )
            score_delta = (
                round(candidate_score - baseline_score, 2)
                if baseline_score is not None and candidate_score is not None
                else None
            )

            scenarios.append(
                ScenarioRegression(
                    scenario_id=scenario_id,
                    scenario_name=scenario_name,
                    status=scenario_status,
                    baseline_passed=(
                        baseline_result.passed if baseline_result is not None else None
                    ),
                    candidate_passed=(
                        candidate_result.passed if candidate_result is not None else None
                    ),
                    baseline_score=baseline_score,
                    candidate_score=candidate_score,
                    score_delta=score_delta,
                    baseline_risk=(
                        baseline_result.risk_level if baseline_result is not None else None
                    ),
                    candidate_risk=(
                        candidate_result.risk_level if candidate_result is not None else None
                    ),
                )
            )

        deltas = RegressionDeltas(
            pass_rate=round(
                candidate.summary.pass_rate - baseline_batch.summary.pass_rate,
                2,
            ),
            average_overall=round(
                candidate.summary.average_overall - baseline_batch.summary.average_overall,
                2,
            ),
            average_policy=round(
                candidate.summary.average_policy - baseline_batch.summary.average_policy,
                2,
            ),
            average_approval=round(
                candidate.summary.average_approval - baseline_batch.summary.average_approval,
                2,
            ),
            critical_runs=(candidate.summary.critical_runs - baseline_batch.summary.critical_runs),
            error_runs=(candidate.summary.error_runs - baseline_batch.summary.error_runs),
        )

        reasons: list[str] = []
        if newly_failing:
            reasons.append(f"{len(newly_failing)} scenario(s) newly failed")
        if missing:
            reasons.append(f"{len(missing)} baseline scenario(s) are missing")
        if deltas.pass_rate < -thresholds.max_pass_rate_drop:
            reasons.append(f"Pass rate dropped by {abs(deltas.pass_rate):.2f} points")

        score_metrics = (
            ("Overall score", deltas.average_overall),
            ("Policy score", deltas.average_policy),
            ("Approval score", deltas.average_approval),
        )
        for label, delta in score_metrics:
            if delta < -thresholds.max_score_drop:
                reasons.append(f"{label} dropped by {abs(delta):.2f} points")

        if deltas.critical_runs > 0:
            reasons.append(f"Critical-risk run count increased by {deltas.critical_runs}")
        if deltas.error_runs > 0:
            reasons.append(f"Scenario execution error count increased by {deltas.error_runs}")

        return RegressionComparison(
            baseline_id=baseline.id,
            baseline_batch_id=baseline.batch_id,
            candidate_batch_id=candidate.id,
            agent=candidate.agent,
            thresholds=thresholds,
            deltas=deltas,
            regressed=bool(reasons),
            reasons=reasons,
            newly_failing_scenarios=newly_failing,
            recovered_scenarios=recovered,
            missing_scenarios=missing,
            scenarios=scenarios,
        )

    def _get_agent(self, agent_name: str) -> AgentAdapter:
        agent = self.agents.get(agent_name)
        if agent is None:
            supported = ", ".join(sorted(self.agents))
            raise ValueError(f"Unknown agent '{agent_name}'. Supported agents: {supported}")
        return agent

    def _resolve_batch_scenarios(
        self,
        scenario_ids: list[str] | None,
    ) -> list[ScenarioSpec]:
        if scenario_ids is None:
            return self.registry.list()
        return [self.registry.get(scenario_id) for scenario_id in scenario_ids]

    @staticmethod
    def _build_batch_summary(
        results: list[BatchScenarioResult],
    ) -> BatchSummary:
        completed = [result for result in results if result.status == BatchScenarioStatus.COMPLETED]
        total_scenarios = len(results)
        completed_runs = len(completed)
        error_runs = total_scenarios - completed_runs
        passed_runs = sum(result.passed is True for result in completed)
        failed_runs = total_scenarios - passed_runs

        return BatchSummary(
            total_scenarios=total_scenarios,
            completed_runs=completed_runs,
            error_runs=error_runs,
            passed_runs=passed_runs,
            failed_runs=failed_runs,
            pass_rate=ArenaService._percentage(
                passed_runs,
                total_scenarios,
            ),
            average_overall=ArenaService._average(
                [result.overall_score for result in completed if result.overall_score is not None]
            ),
            average_policy=ArenaService._average(
                [result.policy_score for result in completed if result.policy_score is not None]
            ),
            average_approval=ArenaService._average(
                [result.approval_score for result in completed if result.approval_score is not None]
            ),
            critical_runs=sum(result.risk_level == "critical" for result in completed),
        )

    @staticmethod
    def _average(values: list[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)

    @staticmethod
    def _percentage(numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return round(100 * numerator / denominator, 2)
