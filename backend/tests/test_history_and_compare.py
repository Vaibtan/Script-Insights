from fastapi.testclient import TestClient


def _submit_run(
    client: TestClient, *, script_text: str, title: str, script_id: str | None = None
) -> dict[str, str]:
    payload: dict[str, str] = {"title": title, "script_text": script_text}
    if script_id is not None:
        payload["script_id"] = script_id
    response = client.post("/api/v1/analysis/runs", json=payload)
    assert response.status_code == 202
    return response.json()


def test_run_history_returns_ordered_runs_with_filters(client: TestClient) -> None:
    first = _submit_run(
        client,
        title="History 1",
        script_text="Scene: First\nA: Why now?\nB: Because the truth matters.",
    )
    second = _submit_run(
        client,
        title="History 2",
        script_id=first["script_id"],
        script_text="Scene: Second\nA: Why now?\nB: Because the truth changed.",
    )

    history = client.get(f"/api/v1/scripts/{first['script_id']}/runs")
    assert history.status_code == 200
    body = history.json()
    assert len(body["runs"]) >= 2
    assert body["runs"][0]["run_id"] == second["run_id"]

    by_revision = client.get(
        f"/api/v1/scripts/{first['script_id']}/runs",
        params={"revision_id": first["revision_id"]},
    )
    assert by_revision.status_code == 200
    filtered = by_revision.json()
    assert len(filtered["runs"]) == 1
    assert filtered["runs"][0]["revision_id"] == first["revision_id"]


def test_compare_returns_deltas_between_two_runs(client: TestClient) -> None:
    base = _submit_run(
        client,
        title="Compare Base",
        script_text="Scene: Base\nA: Why now?\nB: Because this matters.",
    )
    target = _submit_run(
        client,
        title="Compare Target",
        script_id=base["script_id"],
        script_text=(
            "Scene: Target\nA: Why now?\nB: Because the truth changes everything.\n"
            "A: What truth?\nB: The accident was not your fault."
        ),
    )

    comparison = client.get(
        f"/api/v1/scripts/{base['script_id']}/compare",
        params={"base_run_id": base["run_id"], "target_run_id": target["run_id"]},
    )
    assert comparison.status_code == 200
    body = comparison.json()
    assert body["script_id"] == base["script_id"]
    assert body["base_run_id"] == base["run_id"]
    assert body["target_run_id"] == target["run_id"]
    assert "overall_delta" in body["engagement_delta"]
    assert "hook" in body["engagement_delta"]["factor_deltas"]
    assert body["revision_lineage"]["base_revision_id"] == base["revision_id"]
    assert body["revision_lineage"]["target_revision_id"] == target["revision_id"]


def test_compare_includes_changed_non_cliffhanger_evidence(client: TestClient) -> None:
    base = _submit_run(
        client,
        title="Evidence Base",
        script_text=(
            "Scene: A rainy station platform at dusk.\n"
            "Riya: Why now?\n"
            "Arjun: Meet me at midnight."
        ),
    )
    target = _submit_run(
        client,
        title="Evidence Target",
        script_id=base["script_id"],
        script_text=(
            "Scene: A hospital corridor moments before surgery.\n"
            "Riya: Why now?\n"
            "Arjun: Meet me at midnight."
        ),
    )

    comparison = client.get(
        f"/api/v1/scripts/{base['script_id']}/compare",
        params={"base_run_id": base["run_id"], "target_run_id": target["run_id"]},
    )

    assert comparison.status_code == 200
    body = comparison.json()
    assert any("rainy station platform" in item for item in body["changed_evidence"])
    assert any("hospital corridor" in item for item in body["changed_evidence"])
