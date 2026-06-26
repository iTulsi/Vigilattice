from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_liveness_endpoint(client):
    response = client.get("/api/v1/live")

    assert response.status_code == 200
    assert response.json()["status"] == "operational"


def test_readiness_endpoint(client):
    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["environment"] == "development"
    assert payload["scenario_count"] > 0
    assert payload["checks"] == {
        "database": True,
        "scenario_registry": True,
    }


def test_free_render_blueprint_is_wired_for_public_demo():
    blueprint = yaml.safe_load((ROOT / "render.yaml").read_text(encoding="utf-8"))
    services = {service["name"]: service for service in blueprint["services"]}

    api = services["vigilattice-api-itulsi"]
    web = services["vigilattice-itulsi"]

    assert api["runtime"] == "python"
    assert api["plan"] == "free"
    assert api["rootDir"] == "backend"
    assert api["healthCheckPath"] == "/api/v1/ready"
    assert "$PORT" in api["startCommand"]

    api_env = {item["key"]: item["value"] for item in api["envVars"]}
    assert api_env["VIGILATTICE_ENVIRONMENT"] == "production"
    assert api_env["VIGILATTICE_RUN_DATABASE_PATH"] == "/tmp/vigilattice.db"

    assert web["runtime"] == "static"
    assert web["rootDir"] == "frontend"
    assert web["staticPublishPath"] == "./dist"

    web_env = {item["key"]: item["value"] for item in web["envVars"]}
    assert web_env["VITE_API_BASE_URL"].endswith("/api/v1")


def test_persistent_blueprint_uses_paid_disk_path():
    blueprint = yaml.safe_load(
        (ROOT / "infra" / "render-persistent.yaml").read_text(encoding="utf-8")
    )
    api = next(
        service for service in blueprint["services"] if service["name"] == "vigilattice-api-itulsi"
    )
    api_env = {item["key"]: item["value"] for item in api["envVars"]}

    assert api["plan"] == "starter"
    assert api["disk"]["mountPath"] == "/var/data"
    assert api["disk"]["sizeGB"] == 1
    assert api_env["VIGILATTICE_RUN_DATABASE_PATH"] == "/var/data/vigilattice.db"
