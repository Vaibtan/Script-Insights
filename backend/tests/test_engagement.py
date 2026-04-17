from fastapi.testclient import TestClient


def test_completed_run_returns_engagement_score_and_factor_breakdown(
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
    engagement = body["engagement"]
    assert engagement is not None
    assert 0.0 <= engagement["overall_score"] <= 100.0
    factors = engagement["factors"]
    for factor in ("hook", "conflict", "tension", "pacing", "stakes", "payoff"):
        assert factor in factors
        assert 0.0 <= factors[factor] <= 100.0
