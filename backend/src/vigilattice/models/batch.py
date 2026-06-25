from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class BatchScenarioStatus(StrEnum):
    COMPLETED = "completed"
    ERROR = "error"


class BatchScenarioResult(BaseModel):
    scenario_id: str
    scenario_name: str
    status: BatchScenarioStatus
    run_id: str | None = None
    passed: bool | None = None
    overall_score: float | None = Field(default=None, ge=0, le=100)
    policy_score: float | None = Field(default=None, ge=0, le=100)
    approval_score: float | None = Field(default=None, ge=0, le=100)
    risk_level: str | None = None
    critical_failures: list[str] = Field(default_factory=list)
    error: str | None = None


class BatchSummary(BaseModel):
    total_scenarios: int = Field(ge=0)
    completed_runs: int = Field(ge=0)
    error_runs: int = Field(ge=0)
    passed_runs: int = Field(ge=0)
    failed_runs: int = Field(ge=0)
    pass_rate: float = Field(ge=0, le=100)
    average_overall: float = Field(ge=0, le=100)
    average_policy: float = Field(ge=0, le=100)
    average_approval: float = Field(ge=0, le=100)
    critical_runs: int = Field(ge=0)


class BenchmarkBatch(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime
    duration_ms: int = Field(ge=0)
    summary: BatchSummary
    results: list[BatchScenarioResult]
