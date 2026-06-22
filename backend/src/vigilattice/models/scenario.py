from pydantic import BaseModel, Field


class ScenarioSpec(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9-]+$")
    name: str
    category: str
    description: str
    task: str
    severity: str = "high"
    allowed_resources: list[str]
    required_actions: list[str]
    forbidden_actions: list[str]
    attack_markers: list[str] = []
    metadata: dict[str, str] = {}


class ScenarioSummary(BaseModel):
    id: str
    name: str
    category: str
    description: str
    severity: str
