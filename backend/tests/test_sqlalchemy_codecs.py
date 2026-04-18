from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.analysis_outputs import CliffhangerResult
from app.domain.analysis_outputs import EmotionArcPoint
from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import EngagementResult
from app.domain.analysis_outputs import EvidenceSpan
from app.domain.analysis_outputs import Recommendation
from app.domain.analysis_outputs import SummaryResult
from app.domain.evaluation import AnalysisWarning
from app.domain.normalization import DialogueBlock
from app.domain.normalization import NormalizationWarning
from app.domain.normalization import NormalizedScript
from app.domain.normalization import SceneBlock
from app.repositories.sqlalchemy_codecs import AnalysisArtifactCodec


def test_analysis_artifact_codec_round_trips_full_artifact() -> None:
    artifact = AnalysisArtifact(
        normalized_script=NormalizedScript(
            scenes=(
                SceneBlock(
                    scene_index=0,
                    heading="Scene 1",
                    content="Scene 1\nA: Hello",
                    start_offset=0,
                    end_offset=17,
                ),
            ),
            dialogue_blocks=(
                DialogueBlock(
                    scene_index=0,
                    speaker="A",
                    line="Hello",
                    start_offset=9,
                    end_offset=17,
                ),
            ),
            warnings=(
                NormalizationWarning(
                    code="missing_scene_heading",
                    message="No explicit scene heading detected.",
                ),
            ),
        ),
        summary=SummaryResult(
            text="Short summary.",
            evidence_spans=(EvidenceSpan(start_offset=0, end_offset=17, text="A: Hello"),),
        ),
        emotion=EmotionResult(
            dominant_emotions=("tense",),
            valence=-0.2,
            arousal=0.7,
            emotional_arc=(
                EmotionArcPoint(
                    beat_index=0,
                    emotion="tense",
                    valence=-0.2,
                    arousal=0.7,
                ),
            ),
            evidence_spans=(EvidenceSpan(start_offset=0, end_offset=17, text="A: Hello"),),
        ),
        engagement=EngagementResult(
            overall_score=72.5,
            factors={
                "hook": 75.0,
                "conflict": 70.0,
                "tension": 74.0,
                "pacing": 68.0,
                "stakes": 73.0,
                "payoff": 75.0,
            },
            rationale="Balanced engagement profile.",
        ),
        recommendations=(
            Recommendation(
                category="hook",
                suggestion="Raise the opening question earlier.",
                rationale="Front-load intrigue.",
            ),
        ),
        cliffhanger=CliffhangerResult(
            moment_text="A: Hello",
            why_it_works="Leaves the scene unresolved.",
            evidence_spans=(EvidenceSpan(start_offset=0, end_offset=17, text="A: Hello"),),
        ),
        warnings=(
            AnalysisWarning(
                code="guardrail_partial",
                message="One agent degraded to fallback.",
                component="emotion",
            ),
        ),
    )

    codec = AnalysisArtifactCodec()

    payload = codec.serialize(artifact)
    round_tripped = codec.deserialize(payload)

    assert round_tripped == artifact
