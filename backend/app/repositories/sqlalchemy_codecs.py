from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.db.models import AnalysisArtifactModel
from app.db.models import AnalysisRunModel
from app.db.models import NormalizedScriptModel
from app.db.models import ScriptModel
from app.db.models import ScriptRevisionModel
from app.db.models import SourceDocumentModel
from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.analysis_outputs import CliffhangerResult
from app.domain.analysis_outputs import EmotionArcPoint
from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import EngagementResult
from app.domain.analysis_outputs import EvidenceSpan
from app.domain.analysis_outputs import Recommendation
from app.domain.analysis_outputs import SummaryResult
from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.analysis_runs import RunStatus
from app.domain.analysis_runs import SourceType
from app.domain.evaluation import AnalysisWarning
from app.domain.normalization import DialogueBlock
from app.domain.normalization import NormalizationWarning
from app.domain.normalization import NormalizedScript
from app.domain.normalization import SceneBlock


@dataclass(frozen=True)
class SerializedNormalizedScript:
    scenes_json: list[dict[str, object]]
    dialogue_blocks_json: list[dict[str, object]]
    warnings_json: list[dict[str, str]]


@dataclass(frozen=True)
class SerializedAnalysisArtifact:
    normalized_script: SerializedNormalizedScript
    summary_json: dict[str, object] | None
    emotion_json: dict[str, object] | None
    engagement_json: dict[str, object] | None
    recommendations_json: list[dict[str, str]]
    cliffhanger_json: dict[str, object] | None
    warnings_json: list[dict[str, str]]


@dataclass(frozen=True)
class RunGraphModels:
    script: ScriptModel
    revision: ScriptRevisionModel
    run: AnalysisRunModel
    source_document: SourceDocumentModel | None


def _serialize_normalization_warnings(
    warnings: tuple[NormalizationWarning, ...],
) -> list[dict[str, str]]:
    return [{"code": item.code, "message": item.message} for item in warnings]


def _deserialize_normalization_warnings(
    items: list[dict[str, str]] | None,
) -> tuple[NormalizationWarning, ...]:
    return tuple(
        NormalizationWarning(code=item["code"], message=item["message"])
        for item in (items or [])
    )


def _serialize_analysis_warnings(
    warnings: tuple[AnalysisWarning, ...],
) -> list[dict[str, str]]:
    return [
        {
            "code": item.code,
            "message": item.message,
            "component": item.component,
        }
        for item in warnings
    ]


def _deserialize_analysis_warnings(
    items: list[dict[str, str]] | None,
) -> tuple[AnalysisWarning, ...]:
    return tuple(
        AnalysisWarning(
            code=item["code"],
            message=item["message"],
            component=item["component"],
        )
        for item in (items or [])
    )


def _serialize_evidence_spans(
    spans: tuple[EvidenceSpan, ...],
) -> list[dict[str, object]]:
    return [
        {
            "start_offset": item.start_offset,
            "end_offset": item.end_offset,
            "text": item.text,
        }
        for item in spans
    ]


def _deserialize_evidence_spans(
    items: list[dict[str, object]] | None,
) -> tuple[EvidenceSpan, ...]:
    return tuple(
        EvidenceSpan(
            start_offset=int(item["start_offset"]),
            end_offset=int(item["end_offset"]),
            text=str(item["text"]),
        )
        for item in (items or [])
    )


def _serialize_summary(summary: SummaryResult | None) -> dict[str, object] | None:
    if summary is None:
        return None
    return {
        "text": summary.text,
        "evidence_spans": _serialize_evidence_spans(summary.evidence_spans),
    }


def _deserialize_summary(item: dict[str, object] | None) -> SummaryResult | None:
    if item is None:
        return None
    return SummaryResult(
        text=str(item["text"]),
        evidence_spans=_deserialize_evidence_spans(item.get("evidence_spans")),
    )


def _serialize_emotion(emotion: EmotionResult | None) -> dict[str, object] | None:
    if emotion is None:
        return None
    return {
        "dominant_emotions": list(emotion.dominant_emotions),
        "valence": emotion.valence,
        "arousal": emotion.arousal,
        "emotional_arc": [
            {
                "beat_index": point.beat_index,
                "emotion": point.emotion,
                "valence": point.valence,
                "arousal": point.arousal,
            }
            for point in emotion.emotional_arc
        ],
        "evidence_spans": _serialize_evidence_spans(emotion.evidence_spans),
    }


def _deserialize_emotion(item: dict[str, object] | None) -> EmotionResult | None:
    if item is None:
        return None
    emotional_arc = item.get("emotional_arc")
    arc_items = emotional_arc if isinstance(emotional_arc, list) else []
    return EmotionResult(
        dominant_emotions=tuple(str(value) for value in item.get("dominant_emotions", [])),
        valence=float(item["valence"]),
        arousal=float(item["arousal"]),
        emotional_arc=tuple(
            EmotionArcPoint(
                beat_index=int(point["beat_index"]),
                emotion=str(point["emotion"]),
                valence=float(point["valence"]),
                arousal=float(point["arousal"]),
            )
            for point in arc_items
        ),
        evidence_spans=_deserialize_evidence_spans(item.get("evidence_spans")),
    )


def _serialize_engagement(
    engagement: EngagementResult | None,
) -> dict[str, object] | None:
    if engagement is None:
        return None
    return {
        "overall_score": engagement.overall_score,
        "factors": dict(engagement.factors),
        "rationale": engagement.rationale,
    }


def _deserialize_engagement(
    item: dict[str, object] | None,
) -> EngagementResult | None:
    if item is None:
        return None

    factors_json = item.get("factors")
    factors = factors_json if isinstance(factors_json, dict) else {}
    return EngagementResult(
        overall_score=float(item["overall_score"]),
        factors={str(key): float(value) for key, value in factors.items()},
        rationale=str(item["rationale"]),
    )


def _serialize_recommendations(
    recommendations: tuple[Recommendation, ...],
) -> list[dict[str, str]]:
    return [
        {
            "category": item.category,
            "suggestion": item.suggestion,
            "rationale": item.rationale,
        }
        for item in recommendations
    ]


def _deserialize_recommendations(
    items: list[dict[str, str]] | None,
) -> tuple[Recommendation, ...]:
    return tuple(
        Recommendation(
            category=item["category"],
            suggestion=item["suggestion"],
            rationale=item["rationale"],
        )
        for item in (items or [])
    )


def _serialize_cliffhanger(
    cliffhanger: CliffhangerResult | None,
) -> dict[str, object] | None:
    if cliffhanger is None:
        return None
    return {
        "moment_text": cliffhanger.moment_text,
        "why_it_works": cliffhanger.why_it_works,
        "evidence_spans": _serialize_evidence_spans(cliffhanger.evidence_spans),
    }


def _deserialize_cliffhanger(
    item: dict[str, object] | None,
) -> CliffhangerResult | None:
    if item is None:
        return None
    return CliffhangerResult(
        moment_text=str(item["moment_text"]),
        why_it_works=str(item["why_it_works"]),
        evidence_spans=_deserialize_evidence_spans(item.get("evidence_spans")),
    )


def _serialize_normalized_script(
    normalized_script: NormalizedScript,
) -> SerializedNormalizedScript:
    return SerializedNormalizedScript(
        scenes_json=[
            {
                "scene_index": item.scene_index,
                "heading": item.heading,
                "content": item.content,
                "start_offset": item.start_offset,
                "end_offset": item.end_offset,
            }
            for item in normalized_script.scenes
        ],
        dialogue_blocks_json=[
            {
                "scene_index": item.scene_index,
                "speaker": item.speaker,
                "line": item.line,
                "start_offset": item.start_offset,
                "end_offset": item.end_offset,
            }
            for item in normalized_script.dialogue_blocks
        ],
        warnings_json=_serialize_normalization_warnings(normalized_script.warnings),
    )


def _deserialize_normalized_script(
    payload: SerializedNormalizedScript,
) -> NormalizedScript:
    return NormalizedScript(
        scenes=tuple(
            SceneBlock(
                scene_index=int(item["scene_index"]),
                heading=str(item["heading"]),
                content=str(item["content"]),
                start_offset=int(item["start_offset"]),
                end_offset=int(item["end_offset"]),
            )
            for item in payload.scenes_json
        ),
        dialogue_blocks=tuple(
            DialogueBlock(
                scene_index=int(item["scene_index"]),
                speaker=str(item["speaker"]),
                line=str(item["line"]),
                start_offset=int(item["start_offset"]),
                end_offset=int(item["end_offset"]),
            )
            for item in payload.dialogue_blocks_json
        ),
        warnings=_deserialize_normalization_warnings(payload.warnings_json),
    )


class AnalysisArtifactCodec:
    def serialize(self, artifact: AnalysisArtifact) -> SerializedAnalysisArtifact:
        return SerializedAnalysisArtifact(
            normalized_script=_serialize_normalized_script(artifact.normalized_script),
            summary_json=_serialize_summary(artifact.summary),
            emotion_json=_serialize_emotion(artifact.emotion),
            engagement_json=_serialize_engagement(artifact.engagement),
            recommendations_json=_serialize_recommendations(artifact.recommendations),
            cliffhanger_json=_serialize_cliffhanger(artifact.cliffhanger),
            warnings_json=_serialize_analysis_warnings(artifact.warnings),
        )

    def deserialize(self, payload: SerializedAnalysisArtifact) -> AnalysisArtifact:
        return AnalysisArtifact(
            normalized_script=_deserialize_normalized_script(payload.normalized_script),
            summary=_deserialize_summary(payload.summary_json),
            emotion=_deserialize_emotion(payload.emotion_json),
            engagement=_deserialize_engagement(payload.engagement_json),
            recommendations=_deserialize_recommendations(payload.recommendations_json),
            cliffhanger=_deserialize_cliffhanger(payload.cliffhanger_json),
            warnings=_deserialize_analysis_warnings(payload.warnings_json),
        )


class AnalysisRunGraphCodec:
    def serialize(self, run: AnalysisRunRecord) -> RunGraphModels:
        script_id = str(run.script_id)
        revision_id = str(run.revision_id)
        run_id = str(run.run_id)
        source_warnings_json = _serialize_normalization_warnings(run.source_warnings)

        return RunGraphModels(
            script=ScriptModel(id=script_id, created_at=run.created_at),
            revision=ScriptRevisionModel(
                id=revision_id,
                script_id=script_id,
                title=run.title,
                source_type=run.source_type.value,
                script_text=run.script_text,
                source_warnings_json=source_warnings_json,
                created_at=run.created_at,
            ),
            run=AnalysisRunModel(
                run_id=run_id,
                script_id=script_id,
                revision_id=revision_id,
                title=run.title,
                script_text=run.script_text,
                status=run.status.value,
                failure_message=run.failure_message,
                created_at=run.created_at,
            ),
            source_document=(
                SourceDocumentModel(
                    revision_id=revision_id,
                    filename=run.source_document_name,
                    media_type="application/pdf",
                    extracted_text=run.script_text,
                    extraction_warnings_json=source_warnings_json,
                    created_at=run.created_at,
                )
                if run.source_type == SourceType.PDF
                else None
            ),
        )

    def deserialize(
        self,
        run_model: AnalysisRunModel,
        revision_model: ScriptRevisionModel,
        source_document_model: SourceDocumentModel | None,
    ) -> AnalysisRunRecord:
        return AnalysisRunRecord(
            run_id=UUID(run_model.run_id),
            script_id=UUID(run_model.script_id),
            revision_id=UUID(run_model.revision_id),
            title=run_model.title,
            script_text=run_model.script_text,
            status=RunStatus(run_model.status),
            source_type=SourceType(revision_model.source_type),
            source_document_name=(
                source_document_model.filename
                if source_document_model is not None
                else None
            ),
            source_warnings=_deserialize_normalization_warnings(
                revision_model.source_warnings_json
            ),
            failure_message=run_model.failure_message,
            created_at=run_model.created_at,
        )
