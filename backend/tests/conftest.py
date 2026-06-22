import pytest
from fastapi.testclient import TestClient

from vigilattice.main import create_app
from vigilattice.services.container import get_arena_service


@pytest.fixture(autouse=True)
def reset_service_cache():
    get_arena_service.cache_clear()
    yield
    get_arena_service.cache_clear()


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client
