from typing import Protocol

from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import SummaryResult
from app.domain.normalization import NormalizedScript


class SummaryProgram(Protocol):
    def summarize(self, normalized_script: NormalizedScript) -> SummaryResult:
        ...


class EmotionProgram(Protocol):
    def analyze_emotion(self, normalized_script: NormalizedScript) -> EmotionResult:
        ...
