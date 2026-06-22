def test_safe_agent_passes_adversarial_scenario(client):
    response = client.post(
        "/api/v1/runs",
        json={"scenario_id": "injected-incident-001", "agent": "mock-safe"},
    )

    assert response.status_code == 201
    run = response.json()
    assert run["report"]["passed"] is True
    assert run["report"]["scores"]["overall"] == 100.0
    assert run["trace"]["events"][3]["action"] == "reject_prompt_injection"


def test_unsafe_agent_fails_and_produces_findings(client):
    response = client.post(
        "/api/v1/runs",
        json={"scenario_id": "injected-incident-001", "agent": "mock-unsafe"},
    )

    assert response.status_code == 201
    run = response.json()
    assert run["report"]["passed"] is False
    assert run["report"]["scores"]["policy_compliance"] == 0.0
    codes = {finding["code"] for finding in run["report"]["findings"]}
    assert "policy-violation" in codes
    assert "injection-not-rejected" in codes


def test_rejects_unknown_agent(client):
    response = client.post(
        "/api/v1/runs",
        json={"scenario_id": "injected-incident-001", "agent": "unknown"},
    )

    assert response.status_code == 422
