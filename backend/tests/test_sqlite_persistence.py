from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.container import build_container
from app.core.settings import get_settings
from app.main import create_app


def _build_client(database_path: Path, *, execution_mode: str = "inline") -> TestClient:
    settings = replace(
        get_settings(),
        execution_mode=execution_mode,
        database_url=f"sqlite:///{database_path}",
    )
    return TestClient(create_app(container=build_container(settings=settings)))


def test_sqlite_persistence_survives_new_app_instances(tmp_path: Path) -> None:
    database_path = tmp_path / "script-insights.db"
    first_client = _build_client(database_path)

    first = first_client.post(
        "/api/v1/analysis/runs",
        json={
            "title": "Persistent Base",
            "script_text": "Scene: Base\nRiya: Why now?\nArjun: Because it changed.",
        },
    )
    assert first.status_code == 202
    first_body = first.json()

    second = first_client.post(
        "/api/v1/analysis/runs",
        json={
            "title": "Persistent Revision",
            "script_id": first_body["script_id"],
            "script_text": (
                "Scene: Revision\nRiya: Why now?\nArjun: Because the truth changes everything."
            ),
        },
    )
    assert second.status_code == 202
    second_body = second.json()

    second_client = _build_client(database_path)

    detail = second_client.get(f"/api/v1/analysis/runs/{second_body['run_id']}")
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["summary"] is not None
    assert detail_body["summary"]["evidence_spans"]
    assert detail_body["normalized_script"] is not None
    assert detail_body["normalized_script"]["scenes"]

    history = second_client.get(f"/api/v1/scripts/{first_body['script_id']}/runs")
    assert history.status_code == 200
    history_body = history.json()
    assert [item["run_id"] for item in history_body["runs"]][:2] == [
        second_body["run_id"],
        first_body["run_id"],
    ]

    comparison = second_client.get(
        f"/api/v1/scripts/{first_body['script_id']}/compare",
        params={
            "base_run_id": first_body["run_id"],
            "target_run_id": second_body["run_id"],
        },
    )
    assert comparison.status_code == 200
    assert comparison.json()["revision_lineage"]["base_revision_id"] == first_body["revision_id"]


def test_queued_processing_can_resume_from_persisted_storage(tmp_path: Path) -> None:
    database_path = tmp_path / "queued-script-insights.db"
    submit_client = _build_client(database_path, execution_mode="queued")

    submit = submit_client.post(
        "/api/v1/analysis/runs",
        json={
            "title": "Queued Persistent Run",
            "script_text": "Scene: queued persistence\nA: Why now?\nB: Because it can resume.",
        },
    )
    assert submit.status_code == 202
    handle = submit.json()
    assert handle["status"] == "queued"

    worker_client = _build_client(database_path, execution_mode="queued")
    drain = worker_client.post("/api/v1/analysis/workers/drain")
    assert drain.status_code == 200
    assert drain.json()["processed"] == 1

    detail = worker_client.get(f"/api/v1/analysis/runs/{handle['run_id']}")
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["status"] in {"completed", "partial"}
    assert detail_body["summary"] is not None
