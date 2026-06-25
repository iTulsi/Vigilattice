import pytest

SCENARIO_IDS = [
    "injected-incident-001",
    "secret-exfiltration-001",
    "approval-bypass-001",
    "cross-tenant-access-001",
    "destructive-tool-001",
    "social-engineering-001",
]


@pytest.mark.parametrize("scenario_id", SCENARIO_IDS)
def test_safe_reference_agent_passes_every_builtin_scenario(client, scenario_id):
    response = client.post(
        "/api/v1/runs",
        json={"scenario_id": scenario_id, "agent": "mock-safe"},
    )

    assert response.status_code == 201
    run = response.json()

    assert run["report"]["passed"] is True
    assert run["report"]["risk_level"] == "low"
    assert run["report"]["critical_failures"] == []
    assert run["report"]["scores"]["overall"] == 100.0


@pytest.mark.parametrize("scenario_id", SCENARIO_IDS)
def test_unsafe_reference_agent_fails_every_builtin_scenario(client, scenario_id):
    response = client.post(
        "/api/v1/runs",
        json={"scenario_id": scenario_id, "agent": "mock-unsafe"},
    )

    assert response.status_code == 201
    run = response.json()

    assert run["report"]["passed"] is False
    assert run["report"]["risk_level"] in {"high", "critical"}
    assert run["report"]["critical_failures"]
    assert run["report"]["findings"]
