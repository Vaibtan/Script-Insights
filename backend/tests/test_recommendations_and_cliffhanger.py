from fastapi.testclient import TestClient


def test_completed_run_returns_recommendations_and_cliffhanger(
    client: TestClient,
) -> None:
    payload = {
        "title": "The Last Message",
        "script_text": (
            "Scene: Riya receives a message from her ex-boyfriend after five years.\n"
            "Riya: Why now?\n"
            "Arjun: Because today I learned the truth.\n"
            "Riya: What truth?\n"
            "Arjun: That the accident was not your fault."
        ),
    }
    submit_response = client.post("/api/v1/analysis/runs", json=payload)
    run_id = submit_response.json()["run_id"]

    detail_response = client.get(f"/api/v1/analysis/runs/{run_id}")

    assert detail_response.status_code == 200
    body = detail_response.json()
    recommendations = body["recommendations"]
    assert recommendations is not None
    assert len(recommendations) >= 1
    assert recommendations[0]["category"] in {
        "pacing",
        "dialogue",
        "conflict",
        "emotional_impact",
    }
    assert recommendations[0]["suggestion"] != ""

    cliffhanger = body["cliffhanger"]
    assert cliffhanger is not None
    assert cliffhanger["moment_text"] != ""
    assert cliffhanger["why_it_works"] != ""
    assert len(cliffhanger["evidence_spans"]) >= 1
