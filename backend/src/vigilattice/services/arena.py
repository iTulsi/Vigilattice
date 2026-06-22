from vigilattice.agents.base import AgentAdapter
from vigilattice.evaluation.engine import EvaluationEngine
from vigilattice.models.run import EvaluationRun
from vigilattice.models.scenario import ScenarioSummary
from vigilattice.scenarios.loader import ScenarioRegistry
from vigilattice.storage.memory import InMemoryRunRepository


class ArenaService:
    def __init__(
        self,
        registry: ScenarioRegistry,
        agents: dict[str, AgentAdapter],
        evaluator: EvaluationEngine,
        runs: InMemoryRunRepository,
    ) -> None:
        self.registry = registry
        self.agents = agents
        self.evaluator = evaluator
        self.runs = runs

    def load_scenarios(self) -> None:
        self.registry.load()

    def list_scenarios(self) -> list[ScenarioSummary]:
        return [
            ScenarioSummary(
                id=scenario.id,
                name=scenario.name,
                category=scenario.category,
                description=scenario.description,
                severity=scenario.severity,
            )
            for scenario in self.registry.list()
        ]

    def run(self, scenario_id: str, agent_name: str) -> EvaluationRun:
        scenario = self.registry.get(scenario_id)
        agent = self.agents.get(agent_name)
        if agent is None:
            supported = ", ".join(sorted(self.agents))
            raise ValueError(f"Unknown agent '{agent_name}'. Supported agents: {supported}")
        trace = agent.execute(scenario)
        report = self.evaluator.evaluate(scenario, trace)
        run = EvaluationRun(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            agent=agent.name,
            trace=trace,
            report=report,
        )
        return self.runs.save(run)

    def list_runs(self) -> list[EvaluationRun]:
        return self.runs.list()

    def get_run(self, run_id: str) -> EvaluationRun | None:
        return self.runs.get(run_id)
