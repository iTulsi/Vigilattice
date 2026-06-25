from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class EventKind(StrEnum):
    TOOL_CALL = "tool_call"
    MODEL_DECISION = "model_decision"
    SECURITY_DECISION = "security_decision"
    APPROVAL = "approval"
    OBSERVATION = "observation"
    ERROR = "error"
    FINAL = "final"


class TraceEvent(BaseModel):
    sequence: int = Field(ge=1)
    kind: EventKind
    action: str
    resource: str | None = None
    detail: str
    payload: dict[str, Any] = Field(default_factory=dict)
    policy_tags: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentTrace(BaseModel):
    agent: str
    final_answer: str
    events: list[TraceEvent]
    token_count: int = Field(default=0, ge=0)
    duration_ms: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
