from app.api.schemas import AnalysisRunDetailResponse
from app.api.schemas import DialogueBlockResponse
from app.api.schemas import EngagementResponse
from app.api.schemas import EngagementDeltaResponse
from app.api.schemas import EmotionArcPointResponse
from app.api.schemas import EmotionResponse
from app.api.schemas import EvidenceSpanResponse
from app.api.schemas import RecommendationResponse
from app.api.schemas import CliffhangerResponse
from app.api.schemas import NormalizationWarningResponse
from app.api.schemas import NormalizedScriptResponse
from app.api.schemas import SceneBlockResponse
from app.api.schemas import AnalysisWarningResponse
from app.api.schemas import RevisionLineageResponse
from app.api.schemas import RunComparisonResponse
from app.api.schemas import RunHistoryEntryResponse
from app.api.schemas import RunHistoryResponse
from app.api.schemas import SubmitAnalysisRunResponse
from app.api.schemas import SummaryResponse
from app.domain.run_views import AnalysisRunDetail
from app.domain.run_views import AnalysisRunHandle
from app.domain.run_views import RunComparison
from app.domain.run_views import RunHistory


def to_submit_analysis_run_response(
    handle: AnalysisRunHandle,
) -> SubmitAnalysisRunResponse:
    return SubmitAnalysisRunResponse(
        result_version=handle.result_version,
        run_id=handle.run_id,
        script_id=handle.script_id,
        revision_id=handle.revision_id,
        status=handle.status,
        failure_message=handle.failure_message,
    )


def to_analysis_run_detail_response(
    detail: AnalysisRunDetail,
) -> AnalysisRunDetailResponse:
    normalized_script_response: NormalizedScriptResponse | None = None
    if detail.normalized_script is not None:
        normalized_script_response = NormalizedScriptResponse(
            scenes=[
                SceneBlockResponse(
                    scene_index=scene.scene_index,
                    heading=scene.heading,
                    content=scene.content,
                    start_offset=scene.start_offset,
                    end_offset=scene.end_offset,
                )
                for scene in detail.normalized_script.scenes
            ],
            dialogue_blocks=[
                DialogueBlockResponse(
                    scene_index=dialogue.scene_index,
                    speaker=dialogue.speaker,
                    line=dialogue.line,
                    start_offset=dialogue.start_offset,
                    end_offset=dialogue.end_offset,
                )
                for dialogue in detail.normalized_script.dialogue_blocks
            ],
            warnings=[
                NormalizationWarningResponse(
                    code=warning.code,
                    message=warning.message,
                )
                for warning in detail.normalized_script.warnings
            ],
        )

    summary_response: SummaryResponse | None = None
    if detail.summary is not None:
        summary_response = SummaryResponse(
            text=detail.summary.text,
            evidence_spans=[
                EvidenceSpanResponse(
                    start_offset=span.start_offset,
                    end_offset=span.end_offset,
                    text=span.text,
                )
                for span in detail.summary.evidence_spans
            ],
        )

    emotion_response: EmotionResponse | None = None
    if detail.emotion is not None:
        emotion_response = EmotionResponse(
            dominant_emotions=list(detail.emotion.dominant_emotions),
            valence=detail.emotion.valence,
            arousal=detail.emotion.arousal,
            emotional_arc=[
                EmotionArcPointResponse(
                    beat_index=point.beat_index,
                    emotion=point.emotion,
                    valence=point.valence,
                    arousal=point.arousal,
                )
                for point in detail.emotion.emotional_arc
            ],
            evidence_spans=[
                EvidenceSpanResponse(
                    start_offset=span.start_offset,
                    end_offset=span.end_offset,
                    text=span.text,
                )
                for span in detail.emotion.evidence_spans
            ],
        )

    engagement_response: EngagementResponse | None = None
    if detail.engagement is not None:
        engagement_response = EngagementResponse(
            overall_score=detail.engagement.overall_score,
            factors=dict(detail.engagement.factors),
            rationale=detail.engagement.rationale,
        )

    cliffhanger_response: CliffhangerResponse | None = None
    if detail.cliffhanger is not None:
        cliffhanger_response = CliffhangerResponse(
            moment_text=detail.cliffhanger.moment_text,
            why_it_works=detail.cliffhanger.why_it_works,
            evidence_spans=[
                EvidenceSpanResponse(
                    start_offset=span.start_offset,
                    end_offset=span.end_offset,
                    text=span.text,
                )
                for span in detail.cliffhanger.evidence_spans
            ],
        )

    return AnalysisRunDetailResponse(
        result_version=detail.result_version,
        run_id=detail.run.run_id,
        script_id=detail.run.script_id,
        revision_id=detail.run.revision_id,
        status=detail.run.status,
        failure_message=detail.run.failure_message,
        normalized_script=normalized_script_response,
        summary=summary_response,
        emotion=emotion_response,
        engagement=engagement_response,
        recommendations=[
            RecommendationResponse(
                category=item.category,
                suggestion=item.suggestion,
                rationale=item.rationale,
            )
            for item in detail.recommendations
        ],
        cliffhanger=cliffhanger_response,
        warnings=[
            AnalysisWarningResponse(
                code=item.code,
                message=item.message,
                component=item.component,
            )
            for item in detail.warnings
        ],
    )


def to_run_history_response(history: RunHistory) -> RunHistoryResponse:
    return RunHistoryResponse(
        result_version=history.result_version,
        script_id=history.script_id,
        runs=[
            RunHistoryEntryResponse(
                run_id=item.run_id,
                revision_id=item.revision_id,
                status=item.status,
                created_at=item.created_at.isoformat(),
            )
            for item in history.runs
        ],
    )


def to_run_comparison_response(comparison: RunComparison) -> RunComparisonResponse:
    return RunComparisonResponse(
        result_version=comparison.result_version,
        script_id=comparison.script_id,
        base_run_id=comparison.base_run_id,
        target_run_id=comparison.target_run_id,
        engagement_delta=EngagementDeltaResponse(
            overall_delta=comparison.engagement_delta.overall_delta,
            factor_deltas=dict(comparison.engagement_delta.factor_deltas),
        ),
        changed_recommendations=list(comparison.changed_recommendations),
        changed_evidence=list(comparison.changed_evidence),
        revision_lineage=RevisionLineageResponse(
            base_revision_id=comparison.revision_lineage.base_revision_id,
            target_revision_id=comparison.revision_lineage.target_revision_id,
        ),
    )
