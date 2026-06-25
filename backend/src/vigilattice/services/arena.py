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
            pass_rate=ArenaService._percentage(passed_runs, total_scenarios),
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
