from dataclasses import dataclass
from dataclasses import replace
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
from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import Recommendation
from app.domain.analysis_outputs import SummaryResult
from app.domain.normalization import NormalizedScript
from app.main import create_app


@dataclass(slots=True)
class MalformedEngagementProgram(EngagementProgram):
    def score_engagement(self, normalized_script: NormalizedScript) -> EngagementResult:
        _ = normalized_script
        return EngagementResult(
            overall_score=120.0,
            factors={
                "hook": 150.0,
                "conflict": -5.0,
                "tension": 85.0,
                "pacing": 70.0,
                "stakes": 92.0,
                "payoff": 88.0,
            },
            rationale="synthetic malformed score",
        )


@dataclass(slots=True)
class GuardrailTestProgramRegistry(ProgramRegistry):
    summary_program: SummaryProgram
    emotion_program: EmotionProgram
    recommendation_program: RecommendationProgram
    cliffhanger_program: CliffhangerProgram

    def create_summary_program(self) -> SummaryProgram:
        return self.summary_program

    def create_emotion_program(self) -> EmotionProgram:
        return self.emotion_program

    def create_engagement_program(self) -> EngagementProgram:
        return MalformedEngagementProgram()

    def create_recommendation_program(self) -> RecommendationProgram:
        return self.recommendation_program

    def create_cliffhanger_program(self) -> CliffhangerProgram:
        return self.cliffhanger_program


def test_malformed_agent_output_yields_partial_result_with_warnings(
    tmp_path: Path,
) -> None:
    from app.agents.heuristic_programs import HeuristicCliffhangerProgram
    from app.agents.heuristic_programs import HeuristicEmotionProgram
    from app.agents.heuristic_programs import HeuristicRecommendationProgram
    from app.agents.heuristic_programs import HeuristicSummaryProgram

    registry = GuardrailTestProgramRegistry(
        summary_program=HeuristicSummaryProgram(),
        emotion_program=HeuristicEmotionProgram(),
        recommendation_program=HeuristicRecommendationProgram(),
        cliffhanger_program=HeuristicCliffhangerProgram(),
    )
    settings = replace(
        get_settings(),
        database_url=f"sqlite:///{tmp_path / 'guardrails.db'}",
    )
    app = create_app(
        container=build_container(settings=settings, program_registry=registry)
    )
    client = TestClient(app)

    payload = {
        "title": "Guardrail Case",
        "script_text": "Scene: tense reveal.\nA: Why?\nB: The truth is out.",
    }

    submit = client.post("/api/v1/analysis/runs", json=payload)
    assert submit.status_code == 202
    handle = submit.json()
    assert handle["status"] == "partial"

    detail = client.get(f"/api/v1/analysis/runs/{handle['run_id']}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["status"] == "partial"
    assert body["engagement"] is None
    assert any(w["component"] == "engagement" for w in body["warnings"])
