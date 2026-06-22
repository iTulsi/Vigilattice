def test_lists_builtin_scenarios(client):
    response = client.get("/api/v1/scenarios")

    assert response.status_code == 200
    scenarios = response.json()
    assert scenarios[0]["id"] == "injected-incident-001"
    assert scenarios[0]["category"] == "prompt-injection"
