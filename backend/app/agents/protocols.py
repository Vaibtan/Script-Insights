from typing import Protocol

from collections.abc import Sequence

from app.domain.analysis_outputs import CliffhangerResult
from app.domain.analysis_outputs import EngagementResult
from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import Recommendation
from app.domain.analysis_outputs import SummaryResult
from app.domain.normalization import NormalizedScript


class SummaryProgram(Protocol):
    def summarize(self, normalized_script: NormalizedScript) -> SummaryResult:
        ...


class EmotionProgram(Protocol):
    def analyze_emotion(self, normalized_script: NormalizedScript) -> EmotionResult:
        ...


class EngagementProgram(Protocol):
    def score_engagement(self, normalized_script: NormalizedScript) -> EngagementResult:
        ...


class RecommendationProgram(Protocol):
    def suggest_improvements(
        self, normalized_script: NormalizedScript
    ) -> Sequence[Recommendation]:
        ...


class CliffhangerProgram(Protocol):
    def detect_cliffhanger(
        self, normalized_script: NormalizedScript
    ) -> CliffhangerResult:
        ...
