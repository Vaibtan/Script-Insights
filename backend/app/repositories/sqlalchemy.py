from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from datetime import timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

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
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository


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
        evidence_spans=_deserialize_evidence_spans(
            item.get("evidence_spans") if isinstance(item, dict) else None
        ),
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
    arc_items = item.get("emotional_arc") if isinstance(item, dict) else []
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
        evidence_spans=_deserialize_evidence_spans(
            item.get("evidence_spans") if isinstance(item, dict) else None
        ),
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
    return EngagementResult(
        overall_score=float(item["overall_score"]),
        factors={str(key): float(value) for key, value in dict(item["factors"]).items()},
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
        evidence_spans=_deserialize_evidence_spans(
            item.get("evidence_spans") if isinstance(item, dict) else None
        ),
    )


def _serialize_normalized_script(
    normalized_script: NormalizedScript,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, str]]]:
    scenes_json = [
        {
            "scene_index": item.scene_index,
            "heading": item.heading,
            "content": item.content,
            "start_offset": item.start_offset,
            "end_offset": item.end_offset,
        }
        for item in normalized_script.scenes
    ]
    dialogue_blocks_json = [
        {
            "scene_index": item.scene_index,
            "speaker": item.speaker,
            "line": item.line,
            "start_offset": item.start_offset,
            "end_offset": item.end_offset,
        }
        for item in normalized_script.dialogue_blocks
    ]
    return (
        scenes_json,
        dialogue_blocks_json,
        _serialize_normalization_warnings(normalized_script.warnings),
    )


def _deserialize_normalized_script(
    scenes_json: list[dict[str, object]] | None,
    dialogue_blocks_json: list[dict[str, object]] | None,
    warnings_json: list[dict[str, str]] | None,
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
            for item in (scenes_json or [])
        ),
        dialogue_blocks=tuple(
            DialogueBlock(
                scene_index=int(item["scene_index"]),
                speaker=str(item["speaker"]),
                line=str(item["line"]),
                start_offset=int(item["start_offset"]),
                end_offset=int(item["end_offset"]),
            )
            for item in (dialogue_blocks_json or [])
        ),
        warnings=_deserialize_normalization_warnings(warnings_json),
    )


class SqlAlchemyAnalysisRunRepository(AnalysisRunRepository):
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def save(self, run: AnalysisRunRecord) -> None:
        with self._session_factory() as session:
            script_id = str(run.script_id)
            revision_id = str(run.revision_id)
            run_id = str(run.run_id)

            if session.get(ScriptModel, script_id) is None:
                session.add(ScriptModel(id=script_id, created_at=run.created_at))

            session.add(
                ScriptRevisionModel(
                    id=revision_id,
                    script_id=script_id,
                    title=run.title,
                    source_type=run.source_type.value,
                    script_text=run.script_text,
                    source_warnings_json=_serialize_normalization_warnings(
                        run.source_warnings
                    ),
                    created_at=run.created_at,
                )
            )

            if run.source_type == SourceType.PDF:
                session.add(
                    SourceDocumentModel(
                        revision_id=revision_id,
                        filename=run.source_document_name,
                        media_type="application/pdf",
                        extracted_text=run.script_text,
                        extraction_warnings_json=_serialize_normalization_warnings(
                            run.source_warnings
                        ),
                        created_at=run.created_at,
                    )
                )

            session.add(
                AnalysisRunModel(
                    run_id=run_id,
                    script_id=script_id,
                    revision_id=revision_id,
                    title=run.title,
                    script_text=run.script_text,
                    status=run.status.value,
                    failure_message=run.failure_message,
                    created_at=run.created_at,
                )
            )
            session.commit()

    def get(self, run_id: UUID) -> AnalysisRunRecord | None:
        with self._session_factory() as session:
            model = session.get(AnalysisRunModel, str(run_id))
            if model is None:
                return None
            return self._hydrate_run(session, model)

    def update_status(
        self,
        run_id: UUID,
        status: RunStatus,
        failure_message: str | None = None,
    ) -> AnalysisRunRecord | None:
        with self._session_factory() as session:
            model = session.get(AnalysisRunModel, str(run_id))
            if model is None:
                return None
            model.status = status.value
            model.failure_message = failure_message
            session.commit()
            session.refresh(model)
            return self._hydrate_run(session, model)

    def list_by_script(self, script_id: UUID) -> tuple[AnalysisRunRecord, ...]:
        with self._session_factory() as session:
            rows = session.scalars(
                select(AnalysisRunModel)
                .where(AnalysisRunModel.script_id == str(script_id))
                .order_by(AnalysisRunModel.created_at.desc())
            ).all()
            return tuple(self._hydrate_run(session, row) for row in rows)

    def list_queued(self, limit: int | None = None) -> tuple[AnalysisRunRecord, ...]:
        with self._session_factory() as session:
            query = (
                select(AnalysisRunModel)
                .where(AnalysisRunModel.status == RunStatus.QUEUED.value)
                .order_by(AnalysisRunModel.created_at.asc())
            )
            if limit is not None:
                query = query.limit(limit)
            rows = session.scalars(query).all()
            return tuple(self._hydrate_run(session, row) for row in rows)

    def _hydrate_run(
        self,
        session: Session,
        model: AnalysisRunModel,
    ) -> AnalysisRunRecord:
        revision = session.get(ScriptRevisionModel, model.revision_id)
        if revision is None:
            raise ValueError(f"Missing script revision for run {model.run_id}")
        source_document = session.get(SourceDocumentModel, model.revision_id)
        return AnalysisRunRecord(
            run_id=UUID(model.run_id),
            script_id=UUID(model.script_id),
            revision_id=UUID(model.revision_id),
            title=model.title,
            script_text=model.script_text,
            status=RunStatus(model.status),
            source_type=SourceType(revision.source_type),
            source_document_name=(
                source_document.filename if source_document is not None else None
            ),
            source_warnings=_deserialize_normalization_warnings(
                revision.source_warnings_json
            ),
            failure_message=model.failure_message,
            created_at=model.created_at,
        )


class SqlAlchemyAnalysisArtifactRepository(AnalysisArtifactRepository):
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def save(self, run_id: UUID, artifact: AnalysisArtifact) -> None:
        with self._session_factory() as session:
            run_model = session.get(AnalysisRunModel, str(run_id))
            if run_model is None:
                raise ValueError(f"Unknown run_id {run_id}")

            scenes_json, dialogue_blocks_json, warnings_json = (
                _serialize_normalized_script(artifact.normalized_script)
            )
            normalized_model = session.get(NormalizedScriptModel, run_model.revision_id)
            if normalized_model is None:
                normalized_model = NormalizedScriptModel(
                    revision_id=run_model.revision_id,
                    scenes_json=scenes_json,
                    dialogue_blocks_json=dialogue_blocks_json,
                    warnings_json=warnings_json,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(normalized_model)
            else:
                normalized_model.scenes_json = scenes_json
                normalized_model.dialogue_blocks_json = dialogue_blocks_json
                normalized_model.warnings_json = warnings_json

            artifact_model = session.get(AnalysisArtifactModel, str(run_id))
            if artifact_model is None:
                artifact_model = AnalysisArtifactModel(
                    run_id=str(run_id),
                    summary_json=_serialize_summary(artifact.summary),
                    emotion_json=_serialize_emotion(artifact.emotion),
                    engagement_json=_serialize_engagement(artifact.engagement),
                    recommendations_json=_serialize_recommendations(
                        artifact.recommendations
                    ),
                    cliffhanger_json=_serialize_cliffhanger(artifact.cliffhanger),
                    warnings_json=_serialize_analysis_warnings(artifact.warnings),
                )
                session.add(artifact_model)
            else:
                artifact_model.summary_json = _serialize_summary(artifact.summary)
                artifact_model.emotion_json = _serialize_emotion(artifact.emotion)
                artifact_model.engagement_json = _serialize_engagement(
                    artifact.engagement
                )
                artifact_model.recommendations_json = _serialize_recommendations(
                    artifact.recommendations
                )
                artifact_model.cliffhanger_json = _serialize_cliffhanger(
                    artifact.cliffhanger
                )
                artifact_model.warnings_json = _serialize_analysis_warnings(
                    artifact.warnings
                )

            session.commit()

    def get(self, run_id: UUID) -> AnalysisArtifact | None:
        with self._session_factory() as session:
            artifact_model = session.get(AnalysisArtifactModel, str(run_id))
            if artifact_model is None:
                return None

            run_model = session.get(AnalysisRunModel, str(run_id))
            if run_model is None:
                return None
            normalized_model = session.get(NormalizedScriptModel, run_model.revision_id)
            if normalized_model is None:
                return None

            return AnalysisArtifact(
                normalized_script=_deserialize_normalized_script(
                    normalized_model.scenes_json,
                    normalized_model.dialogue_blocks_json,
                    normalized_model.warnings_json,
                ),
                summary=_deserialize_summary(artifact_model.summary_json),
                emotion=_deserialize_emotion(artifact_model.emotion_json),
                engagement=_deserialize_engagement(artifact_model.engagement_json),
                recommendations=_deserialize_recommendations(
                    artifact_model.recommendations_json
                ),
                cliffhanger=_deserialize_cliffhanger(artifact_model.cliffhanger_json),
                warnings=_deserialize_analysis_warnings(artifact_model.warnings_json),
            )
