from dataclasses import replace
from uuid import UUID

from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.analysis_runs import RunStatus
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository


class InMemoryAnalysisRunRepository(AnalysisRunRepository):
    def __init__(self) -> None:
        self._runs: dict[UUID, AnalysisRunRecord] = {}

    def save(self, run: AnalysisRunRecord) -> None:
        self._runs[run.run_id] = run

    def get(self, run_id: UUID) -> AnalysisRunRecord | None:
        return self._runs.get(run_id)

    def update_status(
        self,
        run_id: UUID,
        status: RunStatus,
        failure_message: str | None = None,
    ) -> AnalysisRunRecord | None:
        run = self._runs.get(run_id)
        if run is None:
            return None
        updated = replace(run, status=status, failure_message=failure_message)
        self._runs[run_id] = updated
        return updated


class InMemoryAnalysisArtifactRepository(AnalysisArtifactRepository):
    def __init__(self) -> None:
        self._artifacts: dict[UUID, AnalysisArtifact] = {}

    def save(self, run_id: UUID, artifact: AnalysisArtifact) -> None:
        self._artifacts[run_id] = artifact

    def get(self, run_id: UUID) -> AnalysisArtifact | None:
        return self._artifacts.get(run_id)
