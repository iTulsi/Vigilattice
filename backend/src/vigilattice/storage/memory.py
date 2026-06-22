from threading import RLock

from vigilattice.models.run import EvaluationRun


class InMemoryRunRepository:
    def __init__(self) -> None:
        self._runs: dict[str, EvaluationRun] = {}
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
            return sorted(self._runs.values(), key=lambda run: run.created_at, reverse=True)
