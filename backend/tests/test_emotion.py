from fastapi.testclient import TestClient


def test_completed_run_returns_emotion_analysis_with_arc(client: TestClient) -> None:
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
    emotion = body["emotion"]
    assert emotion is not None
    assert len(emotion["dominant_emotions"]) >= 1
    assert isinstance(emotion["valence"], float)
    assert isinstance(emotion["arousal"], float)
    assert len(emotion["emotional_arc"]) >= 1
    first_point = emotion["emotional_arc"][0]
    assert first_point["beat_index"] == 0
    assert first_point["emotion"] != ""
