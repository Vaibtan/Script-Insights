from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.container import build_container
from app.core.settings import get_settings
from app.main import create_app


@dataclass(slots=True)
class FailingWorkflow:
    error_message: str = "synthetic workflow failure"

    def execute(self, run: object) -> object:
        _ = run
        raise RuntimeError(self.error_message)


def test_get_unknown_run_returns_404(client: TestClient) -> None:
    response = client.get(f"/api/v1/analysis/runs/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Run not found."}


def test_failed_workflow_marks_run_failed_and_surfaces_failure_message(
    tmp_path: Path,
) -> None:
    settings = replace(
        get_settings(),
        database_url=f"sqlite:///{tmp_path / 'run-errors.db'}",
    )
    app = create_app(
        container=build_container(settings=settings, workflow=FailingWorkflow())
    )
    client = TestClient(app)

    payload = {
        "title": "Failure Case",
        "script_text": "Scene: Something goes wrong.\nAsha: This should fail.",
    }

    submit_response = client.post("/api/v1/analysis/runs", json=payload)

    assert submit_response.status_code == 202
    body = submit_response.json()
    assert body["status"] == "failed"
    assert body["failure_message"] == "synthetic workflow failure"

    detail_response = client.get(f"/api/v1/analysis/runs/{body['run_id']}")

    assert detail_response.status_code == 200
    detail_body = detail_response.json()
    assert detail_body["status"] == "failed"
    assert detail_body["failure_message"] == "synthetic workflow failure"
    assert detail_body["normalized_script"] is None
    assert detail_body["summary"] is None
    assert detail_body["emotion"] is None
