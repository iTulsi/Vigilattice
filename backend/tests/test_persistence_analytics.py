from vigilattice.services.container import get_arena_service


def create_run(client, agent: str = "mock-safe"):
    response = client.post(
        "/api/v1/runs",
        json={
            "scenario_id": "injected-incident-001",
            "agent": agent,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_run_survives_service_reinitialization(client):
    created = create_run(client)

    get_arena_service.cache_clear()

    response = client.get(f"/api/v1/runs/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_empty_analytics_summary(client):
    response = client.get("/api/v1/analytics/summary")

    assert response.status_code == 200
    summary = response.json()

    assert summary["total_runs"] == 0
    assert summary["pass_rate"] == 0.0
    assert summary["agents"] == []


def test_analytics_compare_safe_and_unsafe_agents(client):
    create_run(client, "mock-safe")
    create_run(client, "mock-unsafe")

    response = client.get("/api/v1/analytics/summary")

    assert response.status_code == 200
    summary = response.json()

    assert summary["total_scenarios"] == 1
    assert summary["total_runs"] == 2
    assert summary["passed_runs"] == 1
    assert summary["failed_runs"] == 1
    assert summary["pass_rate"] == 50.0

    agents = {agent["agent"]: agent for agent in summary["agents"]}

    assert agents["mock-safe"]["pass_rate"] == 100.0
    assert agents["mock-safe"]["average_overall"] == 100.0
    assert agents["mock-unsafe"]["pass_rate"] == 0.0
    assert agents["mock-unsafe"]["critical_runs"] == 1
