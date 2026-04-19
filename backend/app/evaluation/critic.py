from dataclasses import dataclass

from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.evaluation import CriticAssessment
from app.domain.evaluation import CriticIssue


@dataclass(slots=True)
class CriticEvaluator:
    def assess(self, artifact: AnalysisArtifact) -> CriticAssessment:
        issues: list[CriticIssue] = []
        score = 100.0

        if artifact.summary is None:
            issues.append(
                CriticIssue(
                    code="missing_summary",
                    message="Summary is missing or failed validation.",
                    component="summary",
                )
            )
            score -= 25.0

        if artifact.cliffhanger is None:
            issues.append(
                CriticIssue(
                    code="missing_cliffhanger",
                    message="Cliffhanger moment is missing or unsupported.",
                    component="cliffhanger",
                )
            )
            score -= 15.0

        if not artifact.recommendations:
            issues.append(
                CriticIssue(
                    code="missing_recommendations",
                    message="No actionable recommendations survived evaluation.",
                    component="recommendations",
                )
            )
            score -= 15.0

        if artifact.engagement is not None and artifact.engagement.factors:
            average_factor = sum(artifact.engagement.factors.values()) / len(
                artifact.engagement.factors
            )
            if abs(average_factor - artifact.engagement.overall_score) > 15.0:
                issues.append(
                    CriticIssue(
                        code="engagement_inconsistency",
                        message="Engagement rationale and factor profile are weakly aligned.",
                        component="engagement",
                    )
                )
                score -= 10.0

        if artifact.warnings:
            issues.append(
                CriticIssue(
                    code="guardrail_warnings",
                    message="Guardrails adjusted one or more agent outputs.",
                    component="evaluation",
                )
            )
            score -= min(15.0, float(len(artifact.warnings)) * 5.0)

        bounded_score = max(0.0, min(100.0, score))
        if bounded_score >= 85.0:
            summary = "Strong analytical coverage with grounded signals."
        elif bounded_score >= 65.0:
            summary = "Usable output with a few quality caveats to review."
        else:
            summary = "Output needs revision before it should be trusted broadly."

        return CriticAssessment(
            score=bounded_score,
            summary=summary,
            issues=tuple(issues),
        )
