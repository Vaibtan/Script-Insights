from dataclasses import dataclass
from pathlib import Path

from fastapi.testclient import TestClient

from app.agents.protocols import CliffhangerProgram
from app.agents.protocols import EngagementProgram
from app.agents.protocols import EmotionProgram
from app.agents.protocols import RecommendationProgram
from app.agents.protocols import SummaryProgram
from app.agents.registry import ProgramRegistry
from app.core.container import build_container
from app.core.settings import get_settings
from app.domain.analysis_outputs import CliffhangerResult
from app.domain.analysis_outputs import EngagementResult
from app.domain.analysis_outputs import Recommendation
from app.domain.analysis_outputs import SummaryResult
from app.domain.normalization import NormalizedScript
from app.main import create_app


def test_completed_run_includes_agent_runs_and_critic_assessment(
    client: TestClient,
) -> None:
    payload = {
        "title": "Critic Case",
        "script_text": (
            "Scene: Riya receives a message from her ex-boyfriend after five years.\n"
            "Riya: Why now?\n"
            "Arjun: Because today I learned the truth."
        ),
    }

    submit_response = client.post("/api/v1/analysis/runs", json=payload)
    assert submit_response.status_code == 202
    run_id = submit_response.json()["run_id"]

    detail_response = client.get(f"/api/v1/analysis/runs/{run_id}")
    assert detail_response.status_code == 200
    body = detail_response.json()

    assert body["critic_assessment"] is not None
    assert body["critic_assessment"]["score"] >= 0
    assert body["critic_assessment"]["summary"].strip() != ""
    assert len(body["agent_runs"]) == 5
    assert {item["agent_name"] for item in body["agent_runs"]} == {
        "summary",
        "emotion",
        "engagement",
        "recommendations",
        "cliffhanger",
    }
    summary_run = next(item for item in body["agent_runs"] if item["agent_name"] == "summary")
    assert summary_run["status"] == "completed"
    assert summary_run["latency_ms"] >= 0


@dataclass(slots=True)
class FailingEmotionProgram(EmotionProgram):
    def analyze_emotion(self, normalized_script: NormalizedScript):
        _ = normalized_script
        raise RuntimeError("emotion stage failed")


@dataclass(slots=True)
class AgentRunFailureRegistry(ProgramRegistry):
    summary_program: SummaryProgram
    engagement_program: EngagementProgram
    recommendation_program: RecommendationProgram
    cliffhanger_program: CliffhangerProgram

    def create_summary_program(self) -> SummaryProgram:
        return self.summary_program

    def create_emotion_program(self) -> EmotionProgram:
        return FailingEmotionProgram()

    def create_engagement_program(self) -> EngagementProgram:
        return self.engagement_program

    def create_recommendation_program(self) -> RecommendationProgram:
        return self.recommendation_program

    def create_cliffhanger_program(self) -> CliffhangerProgram:
        return self.cliffhanger_program


def test_failed_agent_yields_partial_run_and_is_persisted_in_agent_run_history(
    tmp_path: Path,
) -> None:
    from app.agents.heuristic_programs import HeuristicCliffhangerProgram
    from app.agents.heuristic_programs import HeuristicEngagementProgram
    from app.agents.heuristic_programs import HeuristicRecommendationProgram
    from app.agents.heuristic_programs import HeuristicSummaryProgram

    registry = AgentRunFailureRegistry(
        summary_program=HeuristicSummaryProgram(),
        engagement_program=HeuristicEngagementProgram(),
        recommendation_program=HeuristicRecommendationProgram(),
        cliffhanger_program=HeuristicCliffhangerProgram(),
    )
    settings = get_settings().model_copy(
        update={"database_url": f"sqlite:///{tmp_path / 'agent-runs.db'}"}
    )
    app = create_app(
        container=build_container(settings=settings, program_registry=registry)
    )
    client = TestClient(app)

    submit_response = client.post(
        "/api/v1/analysis/runs",
        json={
            "title": "Agent Failure",
            "script_text": "Scene: Failure\nRiya: Why now?\nArjun: Because the stage breaks.",
        },
    )

    assert submit_response.status_code == 202
    handle = submit_response.json()
    assert handle["status"] == "partial"
    assert handle["failure_message"] is None

    detail_response = client.get(f"/api/v1/analysis/runs/{handle['run_id']}")
    assert detail_response.status_code == 200
    body = detail_response.json()
    assert body["status"] == "partial"
    assert body["summary"] is not None
    assert body["emotion"] is None
    assert body["critic_assessment"] is not None
    assert any(item["component"] == "emotion" for item in body["warnings"])
    assert any(
        item["agent_name"] == "summary" and item["status"] == "completed"
        for item in body["agent_runs"]
    )
    assert any(
        item["agent_name"] == "emotion"
        and item["status"] == "failed"
        and item["failure_message"] == "emotion stage failed"
        for item in body["agent_runs"]
    )
