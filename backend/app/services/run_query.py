from dataclasses import dataclass
from uuid import UUID

from app.core.settings import Settings
from app.repositories.agent_runs import AgentRunRepository
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository
from app.domain.run_views import AnalysisRunDetail


@dataclass(slots=True)
class RunQueryService:
    run_repository: AnalysisRunRepository
    artifact_repository: AnalysisArtifactRepository
    agent_run_repository: AgentRunRepository
    settings: Settings

    def get_run_detail(self, run_id: UUID) -> AnalysisRunDetail | None:
        run = self.run_repository.get(run_id)
        if run is None:
            return None

        artifact = self.artifact_repository.get(run_id)
        return AnalysisRunDetail(
            result_version=self.settings.result_version,
            run=run,
            normalized_script=artifact.normalized_script if artifact is not None else None,
            summary=artifact.summary if artifact is not None else None,
            emotion=artifact.emotion if artifact is not None else None,
            engagement=artifact.engagement if artifact is not None else None,
            recommendations=artifact.recommendations if artifact is not None else (),
            cliffhanger=artifact.cliffhanger if artifact is not None else None,
            critic_assessment=artifact.critic_assessment if artifact is not None else None,
            agent_runs=self.agent_run_repository.list_by_run(run_id),
            warnings=artifact.warnings if artifact is not None else (),
        )
