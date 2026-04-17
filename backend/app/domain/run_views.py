from datetime import datetime
from dataclasses import dataclass
from uuid import UUID

from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import EngagementResult
from app.domain.analysis_outputs import Recommendation
from app.domain.analysis_outputs import SummaryResult
from app.domain.analysis_outputs import CliffhangerResult
from app.domain.evaluation import AnalysisWarning
from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.analysis_runs import RunStatus
from app.domain.analysis_runs import SourceType
from app.domain.normalization import NormalizedScript
from app.domain.normalization import NormalizationWarning


@dataclass(frozen=True)
class SubmitAnalysisRunCommand:
    script_text: str
    title: str | None
    script_id: UUID | None = None
    source_type: SourceType = SourceType.TEXT
    source_document_name: str | None = None
    source_warnings: tuple[NormalizationWarning, ...] = ()


@dataclass(frozen=True)
class AnalysisRunHandle:
    result_version: str
    run_id: UUID
    script_id: UUID
    revision_id: UUID
    status: RunStatus
    failure_message: str | None


@dataclass(frozen=True)
class AnalysisRunDetail:
    result_version: str
    run: AnalysisRunRecord
    normalized_script: NormalizedScript | None
    summary: SummaryResult | None
    emotion: EmotionResult | None
    engagement: EngagementResult | None
    recommendations: tuple[Recommendation, ...]
    cliffhanger: CliffhangerResult | None
    warnings: tuple[AnalysisWarning, ...]


@dataclass(frozen=True)
class RunHistoryEntry:
    run_id: UUID
    revision_id: UUID
    status: RunStatus
    created_at: datetime


@dataclass(frozen=True)
class RunHistory:
    result_version: str
    script_id: UUID
    runs: tuple[RunHistoryEntry, ...]


@dataclass(frozen=True)
class EngagementDelta:
    overall_delta: float
    factor_deltas: dict[str, float]


@dataclass(frozen=True)
class RevisionLineage:
    base_revision_id: UUID
    target_revision_id: UUID


@dataclass(frozen=True)
class RunComparison:
    result_version: str
    script_id: UUID
    base_run_id: UUID
    target_run_id: UUID
    engagement_delta: EngagementDelta
    changed_recommendations: tuple[str, ...]
    changed_evidence: tuple[str, ...]
    revision_lineage: RevisionLineage
