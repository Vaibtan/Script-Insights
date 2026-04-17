from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "golden_scripts.json"


def test_golden_fixture_scripts_return_schema_valid_results(client: TestClient) -> None:
    fixture_items = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    for fixture in fixture_items:
        submit_response = client.post("/api/v1/analysis/runs", json=fixture)
        assert submit_response.status_code == 202
        run_handle = submit_response.json()

        detail_response = client.get(f"/api/v1/analysis/runs/{run_handle['run_id']}")
        assert detail_response.status_code == 200
        detail = detail_response.json()
        assert detail["status"] in {"completed", "partial"}
        assert detail["summary"] is not None
        assert detail["emotion"] is not None
        assert detail["engagement"] is not None
        assert detail["cliffhanger"] is not None
        assert isinstance(detail["recommendations"], list)
        assert detail["recommendations"]


def test_health_endpoint_emits_request_id_header(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert "x-request-id" in response.headers
    assert response.headers["x-request-id"] != ""
