from pathlib import Path

from fastapi.testclient import TestClient

from app.core.container import build_container
from app.core.settings import get_settings
from app.main import create_app


def test_queued_mode_preserves_status_transitions_and_final_retrieval(
    tmp_path: Path,
) -> None:
    settings = get_settings().model_copy(
        update={
            "execution_mode": "queued",
            "database_url": f"sqlite:///{tmp_path / 'queued-execution.db'}",
        }
    )
    app = create_app(container=build_container(settings=settings))
    client = TestClient(app)

    submit = client.post(
        "/api/v1/analysis/runs",
        json={
            "title": "Queued Run",
            "script_text": "Scene: queued path\nA: Why now?\nB: Because this is queued.",
        },
    )
    assert submit.status_code == 202
    handle = submit.json()
    assert handle["status"] == "queued"

    before = client.get(f"/api/v1/analysis/runs/{handle['run_id']}")
    assert before.status_code == 200
    assert before.json()["status"] == "queued"
    assert before.json()["normalized_script"] is None

    drain = client.post("/api/v1/analysis/workers/drain")
    assert drain.status_code == 200
    assert drain.json()["processed"] == 1

    after = client.get(f"/api/v1/analysis/runs/{handle['run_id']}")
    assert after.status_code == 200
    assert after.json()["status"] in {"completed", "partial"}
    assert after.json()["normalized_script"] is not None
