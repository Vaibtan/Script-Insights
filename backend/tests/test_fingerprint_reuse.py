from dataclasses import dataclass
from pathlib import Path

from fastapi.testclient import TestClient

from app.agents.heuristic_programs import HeuristicCliffhangerProgram
from app.agents.heuristic_programs import HeuristicEngagementProgram
from app.agents.heuristic_programs import HeuristicEmotionProgram
from app.agents.heuristic_programs import HeuristicRecommendationProgram
from app.agents.heuristic_programs import HeuristicSummaryProgram
from app.core.container import build_container
from app.core.settings import get_settings
from app.main import create_app
from app.services.normalization import ScriptNormalizer
from app.services.workflow import AnalysisWorkflow


@dataclass(slots=True)
class CountingWorkflow:
    delegate: AnalysisWorkflow
    calls: int = 0

    def execute(self, run: object):  # type: ignore[no-untyped-def]
        self.calls += 1
        return self.delegate.execute(run)  # type: ignore[arg-type]


def _build_counting_workflow() -> CountingWorkflow:
    return CountingWorkflow(
        delegate=AnalysisWorkflow(
            normalizer=ScriptNormalizer(),
            summary_program=HeuristicSummaryProgram(),
            emotion_program=HeuristicEmotionProgram(),
            engagement_program=HeuristicEngagementProgram(),
            recommendation_program=HeuristicRecommendationProgram(),
            cliffhanger_program=HeuristicCliffhangerProgram(),
        )
    )


def _build_client(database_path: Path, *, execution_mode: str = "inline") -> TestClient:
    settings = get_settings().model_copy(
        update={
            "execution_mode": execution_mode,
            "database_url": f"sqlite:///{database_path}",
        }
    )
    return TestClient(create_app(container=build_container(settings=settings)))


def test_inline_duplicate_submission_reuses_prior_artifact_without_reexecution(
    tmp_path: Path,
) -> None:
    settings = get_settings().model_copy(
        update={"database_url": f"sqlite:///{tmp_path / 'reuse-inline.db'}"}
    )
    workflow = _build_counting_workflow()
    client = TestClient(
        create_app(container=build_container(settings=settings, workflow=workflow))
    )

    payload = {
        "title": "First Pass",
        "script_text": "Scene: Reuse\nRiya: Why now?\nArjun: Because the truth changed.",
    }

    first = client.post("/api/v1/analysis/runs", json=payload)
    assert first.status_code == 202
    first_handle = first.json()
    assert first_handle["status"] in {"completed", "partial"}

    second = client.post(
        "/api/v1/analysis/runs",
        json={**payload, "title": "Second Pass"},
    )
    assert second.status_code == 202
    second_handle = second.json()
    assert second_handle["run_id"] != first_handle["run_id"]
    assert second_handle["revision_id"] != first_handle["revision_id"]
    assert second_handle["status"] == first_handle["status"]
    assert second_handle["reused_from_run_id"] == first_handle["run_id"]

    first_detail = client.get(f"/api/v1/analysis/runs/{first_handle['run_id']}")
    second_detail = client.get(f"/api/v1/analysis/runs/{second_handle['run_id']}")
    assert first_detail.status_code == 200
    assert second_detail.status_code == 200
    assert second_detail.json()["summary"] == first_detail.json()["summary"]
    assert second_detail.json()["normalized_script"] == first_detail.json()["normalized_script"]
    assert second_detail.json()["reused_from_run_id"] == first_handle["run_id"]
    assert second_detail.json()["normalized_candidate_run_id"] is None
    assert workflow.calls == 1


def test_persisted_duplicate_submission_skips_queue_after_prior_completion(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "reuse-queued.db"
    submit_client = _build_client(database_path, execution_mode="queued")

    payload = {
        "title": "Queued Reuse",
        "script_text": "Scene: Queue reuse\nA: Why now?\nB: Because we already analyzed this.",
    }

    first = submit_client.post("/api/v1/analysis/runs", json=payload)
    assert first.status_code == 202
    first_handle = first.json()
    assert first_handle["status"] == "queued"

    worker_client = _build_client(database_path, execution_mode="queued")
    drain = worker_client.post("/api/v1/analysis/workers/drain")
    assert drain.status_code == 200
    assert drain.json()["processed"] == 1

    reuse_client = _build_client(database_path, execution_mode="queued")
    second = reuse_client.post(
        "/api/v1/analysis/runs",
        json={**payload, "title": "Queued Reuse Duplicate"},
    )
    assert second.status_code == 202
    second_handle = second.json()
    assert second_handle["status"] in {"completed", "partial"}
    assert second_handle["reused_from_run_id"] == first_handle["run_id"]

    second_drain = reuse_client.post("/api/v1/analysis/workers/drain")
    assert second_drain.status_code == 200
    assert second_drain.json()["processed"] == 0

    first_detail = reuse_client.get(f"/api/v1/analysis/runs/{first_handle['run_id']}")
    second_detail = reuse_client.get(f"/api/v1/analysis/runs/{second_handle['run_id']}")
    assert first_detail.status_code == 200
    assert second_detail.status_code == 200
    assert second_detail.json()["summary"] == first_detail.json()["summary"]
    assert second_detail.json()["reused_from_run_id"] == first_handle["run_id"]


def test_queued_duplicate_submission_collapses_onto_single_in_flight_execution(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "reuse-single-flight.db"
    submit_client = _build_client(database_path, execution_mode="queued")

    payload = {
        "title": "Single Flight",
        "script_text": "Scene: Single flight\nA: Why now?\nB: Because we only run once.",
    }

    first = submit_client.post("/api/v1/analysis/runs", json=payload)
    assert first.status_code == 202
    first_handle = first.json()
    assert first_handle["status"] == "queued"
    assert first_handle["reused_from_run_id"] is None

    second = submit_client.post(
        "/api/v1/analysis/runs",
        json={**payload, "title": "Single Flight Duplicate"},
    )
    assert second.status_code == 202
    second_handle = second.json()
    assert second_handle["run_id"] != first_handle["run_id"]
    assert second_handle["status"] == "queued"
    assert second_handle["reused_from_run_id"] == first_handle["run_id"]

    worker_client = _build_client(database_path, execution_mode="queued")
    drain = worker_client.post("/api/v1/analysis/workers/drain")
    assert drain.status_code == 200
    assert drain.json()["processed"] == 1

    first_detail = worker_client.get(f"/api/v1/analysis/runs/{first_handle['run_id']}")
    second_detail = worker_client.get(f"/api/v1/analysis/runs/{second_handle['run_id']}")
    assert first_detail.status_code == 200
    assert second_detail.status_code == 200
    assert second_detail.json()["summary"] == first_detail.json()["summary"]
    assert second_detail.json()["normalized_script"] == first_detail.json()["normalized_script"]
    assert second_detail.json()["reused_from_run_id"] == first_handle["run_id"]

    second_drain = worker_client.post("/api/v1/analysis/workers/drain")
    assert second_drain.status_code == 200
    assert second_drain.json()["processed"] == 0


def test_normalized_candidate_is_recorded_but_run_is_recomputed(
    tmp_path: Path,
) -> None:
    settings = get_settings().model_copy(
        update={"database_url": f"sqlite:///{tmp_path / 'normalized-candidate.db'}"}
    )
    workflow = _build_counting_workflow()
    client = TestClient(
        create_app(container=build_container(settings=settings, workflow=workflow))
    )

    base_payload = {
        "title": "Base Script",
        "script_text": "Scene: Candidate\nRiya: Why now?\nArjun: Because the truth changed.",
    }
    base_response = client.post("/api/v1/analysis/runs", json=base_payload)
    assert base_response.status_code == 202
    base_handle = base_response.json()

    candidate_response = client.post(
        "/api/v1/analysis/runs",
        json={
            "title": "Whitespace Variant",
            "script_text": (
                "Scene: Candidate\nRiya: Why now?   \nArjun: Because the truth changed."
            ),
        },
    )
    assert candidate_response.status_code == 202
    candidate_handle = candidate_response.json()
    assert candidate_handle["reused_from_run_id"] is None

    candidate_detail = client.get(
        f"/api/v1/analysis/runs/{candidate_handle['run_id']}"
    )
    assert candidate_detail.status_code == 200
    detail_body = candidate_detail.json()
    assert detail_body["reused_from_run_id"] is None
    assert detail_body["normalized_candidate_run_id"] == base_handle["run_id"]
    assert workflow.calls == 2
