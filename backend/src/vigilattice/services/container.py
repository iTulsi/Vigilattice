from functools import lru_cache

from vigilattice.agents.llm import StructuredLLMAgentAdapter
from vigilattice.agents.mock import SafeMockAgent, UnsafeMockAgent
from vigilattice.core.config import get_settings
from vigilattice.evaluation.engine import EvaluationEngine
from vigilattice.scenarios.loader import ScenarioRegistry
from vigilattice.services.arena import ArenaService
from vigilattice.storage.sqlite import SQLiteRunRepository


@lru_cache
def get_arena_service() -> ArenaService:
    settings = get_settings()

    agents = {
        SafeMockAgent.name: SafeMockAgent(),
        UnsafeMockAgent.name: UnsafeMockAgent(),
        StructuredLLMAgentAdapter.name: StructuredLLMAgentAdapter(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            timeout_seconds=settings.llm_timeout_seconds,
            max_events=settings.llm_max_events,
        ),
    }

    return ArenaService(
        registry=ScenarioRegistry(settings.scenario_directory),
        agents=agents,
        evaluator=EvaluationEngine(),
        runs=SQLiteRunRepository(settings.run_database_path),
    )
