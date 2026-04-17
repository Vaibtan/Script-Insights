from dataclasses import dataclass
from uuid import UUID

from app.core.settings import Settings
from app.domain.run_views import EngagementDelta
from app.domain.run_views import RevisionLineage
from app.domain.run_views import RunComparison
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository
from app.domain.analysis_artifacts import AnalysisArtifact


@dataclass(slots=True)
class RevisionComparisonService:
    run_repository: AnalysisRunRepository
    artifact_repository: AnalysisArtifactRepository
    settings: Settings

    def compare(
        self,
        *,
        script_id: UUID,
        base_run_id: UUID,
        target_run_id: UUID,
    ) -> RunComparison | None:
        base_run = self.run_repository.get(base_run_id)
        target_run = self.run_repository.get(target_run_id)
        if base_run is None or target_run is None:
            return None
        if base_run.script_id != script_id or target_run.script_id != script_id:
            return None

        base_artifact = self.artifact_repository.get(base_run_id)
        target_artifact = self.artifact_repository.get(target_run_id)

        factor_names = ("hook", "conflict", "tension", "pacing", "stakes", "payoff")
        base_factors = (
            base_artifact.engagement.factors if base_artifact and base_artifact.engagement else {}
        )
        target_factors = (
            target_artifact.engagement.factors if target_artifact and target_artifact.engagement else {}
        )
        factor_deltas: dict[str, float] = {
            name: target_factors.get(name, 0.0) - base_factors.get(name, 0.0)
            for name in factor_names
        }
        overall_delta = (
            (target_artifact.engagement.overall_score if target_artifact and target_artifact.engagement else 0.0)
            - (base_artifact.engagement.overall_score if base_artifact and base_artifact.engagement else 0.0)
        )

        base_recommendations = {
            rec.suggestion
            for rec in (base_artifact.recommendations if base_artifact else ())
        }
        target_recommendations = {
            rec.suggestion
            for rec in (target_artifact.recommendations if target_artifact else ())
        }
        changed_recommendations = tuple(
            sorted((target_recommendations - base_recommendations) | (base_recommendations - target_recommendations))
        )

        base_evidence = self._collect_evidence(base_artifact)
        target_evidence = self._collect_evidence(target_artifact)
        changed_evidence = tuple(sorted((target_evidence - base_evidence) | (base_evidence - target_evidence)))

        return RunComparison(
            result_version=self.settings.result_version,
            script_id=script_id,
            base_run_id=base_run_id,
            target_run_id=target_run_id,
            engagement_delta=EngagementDelta(
                overall_delta=overall_delta,
                factor_deltas=factor_deltas,
            ),
            changed_recommendations=changed_recommendations,
            changed_evidence=changed_evidence,
            revision_lineage=RevisionLineage(
                base_revision_id=base_run.revision_id,
                target_revision_id=target_run.revision_id,
            ),
        )

    @staticmethod
    def _collect_evidence(artifact: AnalysisArtifact | None) -> set[str]:
        if artifact is None:
            return set()

        evidence: set[str] = set()
        if artifact.summary is not None:
            evidence.update(span.text for span in artifact.summary.evidence_spans)
        if artifact.emotion is not None:
            evidence.update(span.text for span in artifact.emotion.evidence_spans)
        if artifact.cliffhanger is not None:
            evidence.update(span.text for span in artifact.cliffhanger.evidence_spans)
        return evidence
