from dataclasses import dataclass
from uuid import UUID

from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import SummaryResult
from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.analysis_runs import RunStatus
from app.domain.normalization import NormalizedScript


@dataclass(frozen=True)
class SubmitAnalysisRunCommand:
    script_text: str
    title: str | None


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
