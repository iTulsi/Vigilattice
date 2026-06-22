from pathlib import Path

import yaml

from vigilattice.models.scenario import ScenarioSpec


class ScenarioRegistry:
    def __init__(self, directory: Path):
        self.directory = directory
        self._scenarios: dict[str, ScenarioSpec] = {}

    def load(self) -> None:
        scenarios: dict[str, ScenarioSpec] = {}
        for path in sorted(self.directory.glob("*.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            scenario = ScenarioSpec.model_validate(raw)
            if scenario.id in scenarios:
                raise ValueError(f"Duplicate scenario id: {scenario.id}")
            scenarios[scenario.id] = scenario
        if not scenarios:
            raise RuntimeError(f"No scenarios found in {self.directory}")
        self._scenarios = scenarios

    def list(self) -> list[ScenarioSpec]:
        return list(self._scenarios.values())

    def get(self, scenario_id: str) -> ScenarioSpec:
        try:
            return self._scenarios[scenario_id]
        except KeyError as exc:
            raise KeyError(f"Scenario '{scenario_id}' was not found") from exc
