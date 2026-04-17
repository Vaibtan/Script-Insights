from dataclasses import dataclass
from typing import Protocol

from app.agents.protocols import CliffhangerProgram
from app.agents.protocols import EngagementProgram
from app.agents.protocols import EmotionProgram
from app.agents.protocols import RecommendationProgram
from app.agents.protocols import SummaryProgram
from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.normalization import NormalizedScript
from app.evaluation.evaluator import AnalysisEvaluator
from app.services.normalization import ScriptNormalizer


class AnalysisWorkflowExecutor(Protocol):
    def execute(self, run: AnalysisRunRecord) -> AnalysisArtifact:
        ...


@dataclass(slots=True)
class AnalysisWorkflow:
    normalizer: ScriptNormalizer
    summary_program: SummaryProgram | None = None
    emotion_program: EmotionProgram | None = None
    engagement_program: EngagementProgram | None = None
    recommendation_program: RecommendationProgram | None = None
    cliffhanger_program: CliffhangerProgram | None = None
    evaluator: AnalysisEvaluator | None = None

    def execute(self, run: AnalysisRunRecord) -> AnalysisArtifact:
        normalized_script = self.normalizer.normalize(run.script_text)
        if run.source_warnings:
            normalized_script = NormalizedScript(
                scenes=normalized_script.scenes,
                dialogue_blocks=normalized_script.dialogue_blocks,
                warnings=normalized_script.warnings + run.source_warnings,
            )
        summary = (
            self.summary_program.summarize(normalized_script)
            if self.summary_program is not None
            else None
        )
        emotion = (
            self.emotion_program.analyze_emotion(normalized_script)
            if self.emotion_program is not None
            else None
        )
        engagement = (
            self.engagement_program.score_engagement(normalized_script)
            if self.engagement_program is not None
            else None
        )
        recommendations = (
            tuple(self.recommendation_program.suggest_improvements(normalized_script))
            if self.recommendation_program is not None
            else ()
        )
        cliffhanger = (
            self.cliffhanger_program.detect_cliffhanger(normalized_script)
            if self.cliffhanger_program is not None
            else None
        )
        artifact = AnalysisArtifact(
            normalized_script=normalized_script,
            summary=summary,
            emotion=emotion,
            engagement=engagement,
            recommendations=recommendations,
            cliffhanger=cliffhanger,
        )
        if self.evaluator is not None:
            return self.evaluator.evaluate(artifact)
        return artifact
