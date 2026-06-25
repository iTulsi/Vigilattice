from typing import Protocol

from vigilattice.models.analytics import BenchmarkAnalytics
from vigilattice.models.run import EvaluationRun


class RunRepository(Protocol):
    def save(self, run: EvaluationRun) -> EvaluationRun:
        """Persist an evaluation run."""

    def get(self, run_id: str) -> EvaluationRun | None:
        """Return one evaluation run when it exists."""

    def list(self) -> list[EvaluationRun]:
        """Return runs in reverse chronological order."""

    def analytics(self) -> BenchmarkAnalytics:
        """Return aggregate benchmark and agent statistics."""
