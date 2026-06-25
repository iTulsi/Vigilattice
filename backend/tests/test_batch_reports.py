from vigilattice.services.container import get_arena_service


def create_batch(client, agent: str = "mock-safe"):
    response = client.post(
        "/api/v1/batches",
        json={"agent": agent},
    )
    assert response.status_code == 201
    return response.json()


def test_safe_agent_batch_passes_all_builtin_scenarios(client):
    batch = create_batch(client)
    assert batch["agent"] == "mock-safe"
    assert batch["summary"]["total_scenarios"] == 6
    assert batch["summary"]["completed_runs"] == 6
    assert batch["summary"]["error_runs"] == 0
    assert batch["summary"]["passed_runs"] == 6
    assert batch["summary"]["failed_runs"] == 0
    assert batch["summary"]["pass_rate"] == 100.0
    assert batch["summary"]["average_overall"] == 100.0
    assert len(batch["results"]) == 6


def test_unsafe_agent_batch_fails_all_builtin_scenarios(client):
    batch = create_batch(client, "mock-unsafe")
    assert batch["summary"]["total_scenarios"] == 6
    assert batch["summary"]["completed_runs"] == 6
    assert batch["summary"]["passed_runs"] == 0
    assert batch["summary"]["failed_runs"] == 6
    assert batch["summary"]["pass_rate"] == 0.0
    assert batch["summary"]["critical_runs"] >= 1


def test_batch_survives_service_reinitialization(client):
    created = create_batch(client)
    get_arena_service.cache_clear()
    response = client.get(f"/api/v1/batches/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_batch_exports_json_and_csv(client):
    batch = create_batch(client)
    json_response = client.get(f"/api/v1/batches/{batch['id']}/export?format=json")
    csv_response = client.get(f"/api/v1/batches/{batch['id']}/export?format=csv")
    assert json_response.status_code == 200
    assert json_response.json()["id"] == batch["id"]
    assert "attachment;" in json_response.headers["content-disposition"]
    assert csv_response.status_code == 200
    assert csv_response.headers["content-type"].startswith("text/csv")
    assert "scenario_id" in csv_response.text
    assert "injected-incident-001" in csv_response.text
    assert "attachment;" in csv_response.headers["content-disposition"]
