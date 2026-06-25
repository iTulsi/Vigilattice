from pydantic import BaseModel, Field


class AgentAnalytics(BaseModel):
    agent: str
    total_runs: int = Field(ge=0)
    passed_runs: int = Field(ge=0)
    failed_runs: int = Field(ge=0)
    pass_rate: float = Field(ge=0, le=100)
    average_overall: float = Field(ge=0, le=100)
    average_policy: float = Field(ge=0, le=100)
    average_approval: float = Field(ge=0, le=100)
    critical_runs: int = Field(ge=0)


class BenchmarkAnalytics(BaseModel):
    total_scenarios: int = Field(ge=0)
    total_runs: int = Field(ge=0)
    passed_runs: int = Field(ge=0)
    failed_runs: int = Field(ge=0)
    pass_rate: float = Field(ge=0, le=100)
    average_overall: float = Field(ge=0, le=100)
    average_policy: float = Field(ge=0, le=100)
    average_approval: float = Field(ge=0, le=100)
    critical_runs: int = Field(ge=0)
    agents: list[AgentAnalytics]
