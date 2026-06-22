from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field

from vigilattice.models.trace import AgentTrace


class RunStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class ScoreBreakdown(BaseModel):
    task_completion: float = Field(ge=0, le=100)
    policy_compliance: float = Field(ge=0, le=100)
    injection_resistance: float = Field(ge=0, le=100)
    least_privilege: float = Field(ge=0, le=100)
    overall: float = Field(ge=0, le=100)


class EvaluationFinding(BaseModel):
    code: str
    severity: str
    message: str


class EvaluationReport(BaseModel):
    scores: ScoreBreakdown
    findings: list[EvaluationFinding]
    passed: bool


class EvaluationRun(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    scenario_id: str
    scenario_name: str
    agent: str
    status: RunStatus = RunStatus.COMPLETED
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    trace: AgentTrace
    report: EvaluationReport
