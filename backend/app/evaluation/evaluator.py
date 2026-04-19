from dataclasses import dataclass, replace

from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.evaluation import AnalysisWarning
from app.evaluation.critic import CriticEvaluator

_ENGAGEMENT_FACTORS = {"hook", "conflict", "tension", "pacing", "stakes", "payoff"}
_RECOMMENDATION_CATEGORIES = {"pacing", "dialogue", "conflict", "emotional_impact"}


@dataclass(slots = True)
class AnalysisEvaluator:
    critic: CriticEvaluator | None = None

    def evaluate(self, artifact: AnalysisArtifact) -> AnalysisArtifact:
        warnings = list(artifact.warnings)
        evaluated = artifact

        if artifact.engagement is not None:
            if not self._is_valid_engagement(artifact.engagement.overall_score, artifact.engagement.factors):
                warnings.append(
                    AnalysisWarning(
                        code="invalid_engagement",
                        message="Engagement output failed schema or range validation.",
                        component="engagement",
                    )
                )
                evaluated = replace(evaluated, engagement=None)

        filtered_recommendations = tuple(
            item
            for item in evaluated.recommendations
            if item.category in _RECOMMENDATION_CATEGORIES and bool(item.suggestion.strip())
        )
        if len(filtered_recommendations) != len(evaluated.recommendations):
            warnings.append(
                AnalysisWarning(
                    code="invalid_recommendations",
                    message="Some recommendations were dropped due to validation failures.",
                    component="recommendations",
                )
            )
        evaluated = replace(evaluated, recommendations=filtered_recommendations)

        if evaluated.cliffhanger is not None and not evaluated.cliffhanger.evidence_spans:
            warnings.append(
                AnalysisWarning(
                    code="invalid_cliffhanger",
                    message="Cliffhanger output is missing evidence spans.",
                    component="cliffhanger",
                )
            )
            evaluated = replace(evaluated, cliffhanger=None)

        if evaluated.summary is not None and not evaluated.summary.evidence_spans:
            warnings.append(
                AnalysisWarning(
                    code="invalid_summary",
                    message="Summary output is missing evidence spans.",
                    component="summary",
                )
            )
            evaluated = replace(evaluated, summary=None)

        if evaluated.emotion is not None:
            if not (-1.0 <= evaluated.emotion.valence <= 1.0 and 0.0 <= evaluated.emotion.arousal <= 1.0):
                warnings.append(
                    AnalysisWarning(
                        code="invalid_emotion",
                        message="Emotion output contains out-of-range values.",
                        component="emotion",
                    )
                )
                evaluated = replace(evaluated, emotion=None)

        evaluated = replace(evaluated, warnings=tuple(warnings))
        if self.critic is None:
            return evaluated
        return replace(
            evaluated,
            critic_assessment=self.critic.assess(evaluated),
        )

    @staticmethod
    def _is_valid_engagement(overall_score: float, factors: dict[str, float]) -> bool:
        if not 0.0 <= overall_score <= 100.0:
            return False
        if set(factors.keys()) != _ENGAGEMENT_FACTORS:
            return False
        return all(0.0 <= value <= 100.0 for value in factors.values())
