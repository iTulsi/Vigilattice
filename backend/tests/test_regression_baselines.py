from datetime import UTC, datetime
from uuid import uuid4

from vigilattice.services.container import get_arena_service


def create_batch(client, agent: str = "mock-safe"):
    response = client.post("/api/v1/batches", json={"agent": agent})
    assert response.status_code == 201
    return response.json()


def set_baseline(client, batch_id: str):
    response = client.post(f"/api/v1/regressions/baselines/{batch_id}")
    assert response.status_code == 201
    return response.json()


def test_regression_baseline_survives_service_reinitialization(client):
    batch = create_batch(client)
    baseline = set_baseline(client, batch["id"])

    get_arena_service.cache_clear()

    response = client.get("/api/v1/regressions/baselines/mock-safe")
    assert response.status_code == 200
    assert response.json()["id"] == baseline["id"]
    assert response.json()["batch_id"] == batch["id"]


def test_same_batch_has_no_regression(client):
    batch = create_batch(client)
    set_baseline(client, batch["id"])

    response = client.get(f"/api/v1/regressions/compare/{batch['id']}")

    assert response.status_code == 200
    comparison = response.json()
    assert comparison["regressed"] is False
    assert comparison["reasons"] == []
    assert comparison["deltas"]["pass_rate"] == 0.0
    assert comparison["newly_failing_scenarios"] == []


def test_comparison_detects_new_failure_and_score_drop(client):
    batch = create_batch(client)
    set_baseline(client, batch["id"])

    service = get_arena_service()
    original = service.get_batch(batch["id"])
    assert original is not None

    candidate = original.model_copy(deep=True)
    candidate.id = str(uuid4())
    candidate.started_at = datetime.now(UTC)
    candidate.completed_at = datetime.now(UTC)
    candidate.summary.passed_runs -= 1
    candidate.summary.failed_runs += 1
    candidate.summary.pass_rate = round(
        100 * candidate.summary.passed_runs / candidate.summary.total_scenarios,
        2,
    )
    candidate.summary.average_overall = 80.0
    candidate.summary.critical_runs += 1

    failed = candidate.results[0]
    failed.passed = False
    failed.overall_score = 0.0
    failed.risk_level = "critical"
    failed.critical_failures = ["Synthetic regression for test"]

    service.runs.save_batch(candidate)

    response = client.get(
        f"/api/v1/regressions/compare/{candidate.id}?max_score_drop=5&max_pass_rate_drop=0"
    )

    assert response.status_code == 200
    comparison = response.json()
    assert comparison["regressed"] is True
    assert failed.scenario_id in comparison["newly_failing_scenarios"]
    assert comparison["deltas"]["average_overall"] == -20.0
    assert comparison["deltas"]["critical_runs"] == 1
    assert comparison["reasons"]


def test_comparison_requires_agent_baseline(client):
    batch = create_batch(client, "mock-unsafe")

    response = client.get(f"/api/v1/regressions/compare/{batch['id']}")

    assert response.status_code == 404
    assert "baseline" in response.json()["detail"].lower()


def test_regression_comparison_exports_json_and_csv(client):
    batch = create_batch(client)
    set_baseline(client, batch["id"])

    json_response = client.get(f"/api/v1/regressions/compare/{batch['id']}/export?format=json")
    csv_response = client.get(f"/api/v1/regressions/compare/{batch['id']}/export?format=csv")

    assert json_response.status_code == 200
    assert json_response.json()["candidate_batch_id"] == batch["id"]
    assert "attachment;" in json_response.headers["content-disposition"]

    assert csv_response.status_code == 200
    assert csv_response.headers["content-type"].startswith("text/csv")
    assert "candidate_batch_id" in csv_response.text
    assert "unchanged_pass" in csv_response.text
    assert "attachment;" in csv_response.headers["content-disposition"]
