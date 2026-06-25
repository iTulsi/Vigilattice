from pydantic import BaseModel, Field


class ScenarioSpec(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    name: str
    category: str
    description: str
    task: str
    severity: str = "high"
    allowed_resources: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    attack_markers: list[str] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)


class ScenarioSummary(BaseModel):
    id: str
    name: str
    category: str
    description: str
    severity: str
