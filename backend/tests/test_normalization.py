from fastapi.testclient import TestClient


def test_submitted_script_is_normalized_into_scenes_dialogue_and_warnings(
    client: TestClient,
) -> None:
    payload = {
        "title": "The Last Message",
        "script_text": "Riya: Why now?\nArjun: Because today I learned the truth.",
    }
    submit_response = client.post("/api/v1/analysis/runs", json=payload)
    run_id = submit_response.json()["run_id"]

    detail_response = client.get(f"/api/v1/analysis/runs/{run_id}")

    assert detail_response.status_code == 200
    body = detail_response.json()
    assert body["status"] == "completed"
    normalized = body["normalized_script"]
    assert len(normalized["scenes"]) == 1
    assert len(normalized["dialogue_blocks"]) == 2
    assert any(warning["code"] == "missing_scene_heading" for warning in normalized["warnings"])
