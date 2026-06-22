from abc import ABC, abstractmethod

from vigilattice.models.scenario import ScenarioSpec
from vigilattice.models.trace import AgentTrace


class AgentAdapter(ABC):
    name: str

    @abstractmethod
    def execute(self, scenario: ScenarioSpec) -> AgentTrace:
        """Execute one scenario and return an auditable trace."""
