from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.analysis_runs import RunStatus


class SubmitAnalysisRunRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    script_text: str = Field(min_length=1)
    title: str | None = Field(default=None, min_length=1)
    script_id: UUID | None = None


class SubmitAnalysisRunResponse(BaseModel):
    result_version: str
    run_id: UUID
    script_id: UUID
    revision_id: UUID
    status: RunStatus
    failure_message: str | None = None


class NormalizationWarningResponse(BaseModel):
    code: str
    message: str


class SceneBlockResponse(BaseModel):
    scene_index: int
    heading: str
    content: str
    start_offset: int
    end_offset: int


class DialogueBlockResponse(BaseModel):
    scene_index: int
    speaker: str
    line: str
    start_offset: int
    end_offset: int


class NormalizedScriptResponse(BaseModel):
    scenes: list[SceneBlockResponse]
    dialogue_blocks: list[DialogueBlockResponse]
    warnings: list[NormalizationWarningResponse]


class EvidenceSpanResponse(BaseModel):
    start_offset: int
    end_offset: int
    text: str


class SummaryResponse(BaseModel):
    text: str
    evidence_spans: list[EvidenceSpanResponse]


class EmotionArcPointResponse(BaseModel):
    beat_index: int
    emotion: str
    valence: float
    arousal: float


class EmotionResponse(BaseModel):
    dominant_emotions: list[str]
    valence: float
    arousal: float
    emotional_arc: list[EmotionArcPointResponse]
    evidence_spans: list[EvidenceSpanResponse]


class EngagementResponse(BaseModel):
    overall_score: float
    factors: dict[str, float]
    rationale: str


class RecommendationResponse(BaseModel):
    category: str
    suggestion: str
    rationale: str


class CliffhangerResponse(BaseModel):
    moment_text: str
    why_it_works: str
    evidence_spans: list[EvidenceSpanResponse]


class AnalysisWarningResponse(BaseModel):
    code: str
    message: str
    component: str


class AnalysisRunDetailResponse(BaseModel):
    result_version: str
    run_id: UUID
    script_id: UUID
    revision_id: UUID
    status: RunStatus
    failure_message: str | None
    normalized_script: NormalizedScriptResponse | None
    summary: SummaryResponse | None
    emotion: EmotionResponse | None
    engagement: EngagementResponse | None
    recommendations: list[RecommendationResponse]
    cliffhanger: CliffhangerResponse | None
    warnings: list[AnalysisWarningResponse]


class RunHistoryEntryResponse(BaseModel):
    run_id: UUID
    revision_id: UUID
    status: RunStatus
    created_at: str


class RunHistoryResponse(BaseModel):
    result_version: str
    script_id: UUID
    runs: list[RunHistoryEntryResponse]


class EngagementDeltaResponse(BaseModel):
    overall_delta: float
    factor_deltas: dict[str, float]


class RevisionLineageResponse(BaseModel):
    base_revision_id: UUID
    target_revision_id: UUID


class RunComparisonResponse(BaseModel):
    result_version: str
    script_id: UUID
    base_run_id: UUID
    target_run_id: UUID
    engagement_delta: EngagementDeltaResponse
    changed_recommendations: list[str]
    changed_evidence: list[str]
    revision_lineage: RevisionLineageResponse


class QueueDrainResponse(BaseModel):
    processed: int
