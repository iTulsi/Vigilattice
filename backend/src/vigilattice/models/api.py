from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime


class RunRequest(BaseModel):
    scenario_id: str = Field(min_length=1)
    agent: str = Field(default="mock-safe", pattern=r"^[a-z0-9-]+$")


class BatchRunRequest(BaseModel):
    agent: str = Field(default="mock-safe", pattern=r"^[a-z0-9-]+$")
    scenario_ids: list[str] | None = Field(
        default=None,
        min_length=1,
    )
