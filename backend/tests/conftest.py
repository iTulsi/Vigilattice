import pytest
from fastapi.testclient import TestClient

from vigilattice.core.config import get_settings
from vigilattice.main import create_app
from vigilattice.services.container import get_arena_service


@pytest.fixture(autouse=True)
def reset_service_cache(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "VIGILATTICE_RUN_DATABASE_PATH",
        str(tmp_path / "vigilattice-test.db"),
    )
    get_settings.cache_clear()
    get_arena_service.cache_clear()

    yield

    get_arena_service.cache_clear()
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
