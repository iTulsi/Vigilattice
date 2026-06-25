from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_prefix="VIGILATTICE_",
        extra="ignore",
    )

    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]

    scenario_directory: Path = Path(__file__).resolve().parents[1] / "scenarios" / "builtin"
    run_database_path: Path = Path(__file__).resolve().parents[3] / "data" / "vigilattice.db"

    llm_api_key: str = ""
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model: str = "openai/gpt-oss-20b"
    llm_timeout_seconds: float = 30.0
    llm_max_events: int = 12
    llm_max_output_tokens: int = 2400


@lru_cache
def get_settings() -> Settings:
    return Settings()
