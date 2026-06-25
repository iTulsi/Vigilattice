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


@lru_cache
def get_settings() -> Settings:
    return Settings()
