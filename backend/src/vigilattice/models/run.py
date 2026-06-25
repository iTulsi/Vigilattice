from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field

from vigilattice.models.trace import AgentTrace


class RunStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


class FindingSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScoreBreakdown(BaseModel):
    task_completion: float = Field(ge=0, le=100)
    policy_compliance: float = Field(ge=0, le=100)
    injection_resistance: float = Field(ge=0, le=100)
    least_privilege: float = Field(ge=0, le=100)
    approval_safety: float = Field(ge=0, le=100)
    overall: float = Field(ge=0, le=100)


class EvaluationFinding(BaseModel):
    code: str
    severity: FindingSeverity
    message: str
    evidence: str
    event_sequences: list[int] = Field(default_factory=list)
    recommendation: str
    penalty: float = Field(default=0, ge=0, le=100)


class EvaluationReport(BaseModel):
    scores: ScoreBreakdown
    findings: list[EvaluationFinding]
    passed: bool
    risk_level: RiskLevel
    critical_failures: list[str] = Field(default_factory=list)
    evaluation_version: str = "1.0"


class EvaluationRun(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    scenario_id: str
    scenario_name: str
    agent: str
    status: RunStatus = RunStatus.COMPLETED
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    trace: AgentTrace
    report: EvaluationReport
