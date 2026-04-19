from uuid import UUID

from fastapi.testclient import TestClient


def test_submit_analysis_run_returns_accepted_with_stable_identifiers(
    client: TestClient,
) -> None:
    payload = {
        "title": "The Last Message",
        "script_text": (
            "Scene: Riya receives a message from her ex-boyfriend after five years."
        ),
    }

    response = client.post("/api/v1/analysis/runs", json=payload)

    assert response.status_code == 202
    body = response.json()
    assert body["result_version"] == "v1"
    assert body["status"] == "completed"
    assert body["failure_message"] is None
    assert body["reused_from_run_id"] is None
    assert UUID(body["run_id"])
    assert UUID(body["script_id"])
    assert UUID(body["revision_id"])
