from __future__ import annotations

from typing import Protocol

from vigilattice.models.analytics import BenchmarkAnalytics
from vigilattice.models.batch import BenchmarkBatch
from vigilattice.models.regression import RegressionBaseline
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

    def save_batch(self, batch: BenchmarkBatch) -> BenchmarkBatch:
        """Persist a complete benchmark batch."""

    def get_batch(self, batch_id: str) -> BenchmarkBatch | None:
        """Return one benchmark batch when it exists."""

    def list_batches(self) -> list[BenchmarkBatch]:
        """Return benchmark batches in reverse chronological order."""

    def save_baseline(
        self,
        baseline: RegressionBaseline,
    ) -> RegressionBaseline:
        """Persist the current regression baseline for an agent."""

    def get_baseline(self, agent: str) -> RegressionBaseline | None:
        """Return the current regression baseline for an agent."""
