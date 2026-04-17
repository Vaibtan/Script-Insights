from fastapi.testclient import TestClient


def test_completed_run_returns_structured_summary_with_evidence_spans(
    client: TestClient,
) -> None:
    payload = {
        "title": "The Last Message",
        "script_text": (
            "Scene: Riya receives a message from her ex-boyfriend after five years.\n"
            "Riya: Why now?\n"
            "Arjun: Because today I learned the truth."
        ),
    }
    submit_response = client.post("/api/v1/analysis/runs", json=payload)
    run_id = submit_response.json()["run_id"]

    detail_response = client.get(f"/api/v1/analysis/runs/{run_id}")

    assert detail_response.status_code == 200
    body = detail_response.json()
    summary = body["summary"]
    assert summary is not None
    assert isinstance(summary["text"], str)
    assert summary["text"].strip() != ""
    assert len(summary["evidence_spans"]) >= 1
    first_span = summary["evidence_spans"][0]
    assert first_span["start_offset"] >= 0
    assert first_span["end_offset"] > first_span["start_offset"]
    assert first_span["text"].strip() != ""
