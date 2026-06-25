EXPECTED_SCENARIOS = {
    "injected-incident-001",
    "secret-exfiltration-001",
    "approval-bypass-001",
    "cross-tenant-access-001",
    "destructive-tool-001",
    "social-engineering-001",
}


def test_lists_builtin_scenarios(client):
    response = client.get("/api/v1/scenarios")

    assert response.status_code == 200
    scenarios = response.json()

    ids = {scenario["id"] for scenario in scenarios}
    assert ids == EXPECTED_SCENARIOS

    categories = {scenario["category"] for scenario in scenarios}
    assert {
        "prompt-injection",
        "data-exfiltration",
        "approval-bypass",
        "authorization",
        "unsafe-tool-use",
        "social-engineering",
    } <= categories
