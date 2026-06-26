from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field

from vigilattice.models.batch import BenchmarkBatch


class ScenarioRegressionStatus(StrEnum):
    NEW_FAILURE = "new_failure"
    RECOVERED = "recovered"
    UNCHANGED_PASS = "unchanged_pass"
    UNCHANGED_FAIL = "unchanged_fail"
    MISSING = "missing"
    NEW_SCENARIO = "new_scenario"


class RegressionBaseline(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent: str
    batch_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    batch: BenchmarkBatch


class RegressionThresholds(BaseModel):
    max_score_drop: float = Field(default=0.0, ge=0, le=100)
    max_pass_rate_drop: float = Field(default=0.0, ge=0, le=100)


class RegressionDeltas(BaseModel):
    pass_rate: float
    average_overall: float
    average_policy: float
    average_approval: float
    critical_runs: int
    error_runs: int


class ScenarioRegression(BaseModel):
    scenario_id: str
    scenario_name: str
    status: ScenarioRegressionStatus
    baseline_passed: bool | None
    candidate_passed: bool | None
    baseline_score: float | None
    candidate_score: float | None
    score_delta: float | None
    baseline_risk: str | None
    candidate_risk: str | None


class RegressionComparison(BaseModel):
    baseline_id: str
    baseline_batch_id: str
    candidate_batch_id: str
    agent: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    thresholds: RegressionThresholds
    deltas: RegressionDeltas
    regressed: bool
    reasons: list[str]
    newly_failing_scenarios: list[str]
    recovered_scenarios: list[str]
    missing_scenarios: list[str]
    scenarios: list[ScenarioRegression]
