"""Claude Agent SDK adapter boundary.

This module intentionally avoids importing optional Anthropic dependencies until the
adapter is used. Phase two will map SDK messages and MCP tool events into AgentTrace.
"""

from vigilattice.agents.base import AgentAdapter
from vigilattice.models.scenario import ScenarioSpec
from vigilattice.models.trace import AgentTrace


class ClaudeAgentAdapter(AgentAdapter):
    name = "claude"

    def execute(self, scenario: ScenarioSpec) -> AgentTrace:
        raise NotImplementedError(
            "Claude execution is the next milestone. Install the 'agents' extra and "
            "configure ANTHROPIC_API_KEY before enabling this adapter."
        )
