from threading import RLock

from vigilattice.models.analytics import AgentAnalytics, BenchmarkAnalytics
from vigilattice.models.batch import BenchmarkBatch
from vigilattice.models.run import EvaluationRun


class InMemoryRunRepository:
    def __init__(self) -> None:
        self._runs: dict[str, EvaluationRun] = {}
        self._batches: dict[str, BenchmarkBatch] = {}
        self._lock = RLock()

    def save(self, run: EvaluationRun) -> EvaluationRun:
        with self._lock:
            self._runs[run.id] = run
        return run

    def get(self, run_id: str) -> EvaluationRun | None:
        with self._lock:
            return self._runs.get(run_id)

    def list(self) -> list[EvaluationRun]:
        with self._lock:
            return sorted(
                self._runs.values(),
                key=lambda run: run.created_at,
                reverse=True,
            )

    def save_batch(self, batch: BenchmarkBatch) -> BenchmarkBatch:
        with self._lock:
            self._batches[batch.id] = batch
        return batch

    def get_batch(self, batch_id: str) -> BenchmarkBatch | None:
        with self._lock:
            return self._batches.get(batch_id)

    def list_batches(self) -> list[BenchmarkBatch]:
        with self._lock:
            return sorted(
                self._batches.values(),
                key=lambda batch: batch.started_at,
                reverse=True,
            )

    def analytics(self) -> BenchmarkAnalytics:
        runs = self.list()
        grouped: dict[str, list[EvaluationRun]] = {}

        for run in runs:
            grouped.setdefault(run.agent, []).append(run)

        agents = [
            self._agent_analytics(agent, agent_runs)
            for agent, agent_runs in sorted(grouped.items())
        ]
        agents.sort(key=lambda item: (-item.average_overall, item.agent))

        total_runs = len(runs)
        passed_runs = sum(run.report.passed for run in runs)

        return BenchmarkAnalytics(
            total_scenarios=len({run.scenario_id for run in runs}),
            total_runs=total_runs,
            passed_runs=passed_runs,
            failed_runs=total_runs - passed_runs,
            pass_rate=self._percentage(passed_runs, total_runs),
            average_overall=self._average([run.report.scores.overall for run in runs]),
            average_policy=self._average([run.report.scores.policy_compliance for run in runs]),
            average_approval=self._average([run.report.scores.approval_safety for run in runs]),
            critical_runs=sum(run.report.risk_level.value == "critical" for run in runs),
            agents=agents,
        )

    def _agent_analytics(
        self,
        agent: str,
        runs: list[EvaluationRun],
    ) -> AgentAnalytics:
        total_runs = len(runs)
        passed_runs = sum(run.report.passed for run in runs)

        return AgentAnalytics(
            agent=agent,
            total_runs=total_runs,
            passed_runs=passed_runs,
            failed_runs=total_runs - passed_runs,
            pass_rate=self._percentage(passed_runs, total_runs),
            average_overall=self._average([run.report.scores.overall for run in runs]),
            average_policy=self._average([run.report.scores.policy_compliance for run in runs]),
            average_approval=self._average([run.report.scores.approval_safety for run in runs]),
            critical_runs=sum(run.report.risk_level.value == "critical" for run in runs),
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
