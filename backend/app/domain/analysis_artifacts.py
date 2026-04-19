from dataclasses import dataclass

from app.domain.agent_runs import AgentRunRecord
from app.domain.analysis_outputs import CliffhangerResult
from app.domain.analysis_outputs import EngagementResult
from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import Recommendation
from app.domain.analysis_outputs import SummaryResult
from app.domain.evaluation import CriticAssessment
from app.domain.evaluation import AnalysisWarning
from app.domain.normalization import NormalizedScript


@dataclass(frozen=True)
class AnalysisArtifact:
    normalized_script: NormalizedScript
    summary: SummaryResult | None = None
    emotion: EmotionResult | None = None
    engagement: EngagementResult | None = None
    recommendations: tuple[Recommendation, ...] = ()
    cliffhanger: CliffhangerResult | None = None
    critic_assessment: CriticAssessment | None = None
    agent_runs: tuple[AgentRunRecord, ...] = ()
    warnings: tuple[AnalysisWarning, ...] = ()
