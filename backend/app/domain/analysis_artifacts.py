from dataclasses import dataclass

from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import SummaryResult
from app.domain.normalization import NormalizedScript


@dataclass(frozen=True)
class AnalysisArtifact:
    normalized_script: NormalizedScript
    summary: SummaryResult | None = None
    emotion: EmotionResult | None = None
