from app.api.schemas import AnalysisRunDetailResponse
from app.api.schemas import DialogueBlockResponse
from app.api.schemas import EmotionArcPointResponse
from app.api.schemas import EmotionResponse
from app.api.schemas import EvidenceSpanResponse
from app.api.schemas import NormalizationWarningResponse
from app.api.schemas import NormalizedScriptResponse
from app.api.schemas import SceneBlockResponse
from app.api.schemas import SubmitAnalysisRunResponse
from app.api.schemas import SummaryResponse
from app.domain.run_views import AnalysisRunDetail
from app.domain.run_views import AnalysisRunHandle


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
    )
