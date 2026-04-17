from typing import Protocol

from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.analysis_runs import RunStatus
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository
from app.services.workflow import AnalysisWorkflowExecutor


class AnalysisDispatcher(Protocol):
    def dispatch(self, run: AnalysisRunRecord) -> None:
        ...


class InlineAnalysisDispatcher(AnalysisDispatcher):
    def __init__(
        self,
        workflow: AnalysisWorkflowExecutor,
        run_repository: AnalysisRunRepository,
        artifact_repository: AnalysisArtifactRepository,
    ) -> None:
        self._workflow = workflow
        self._run_repository = run_repository
        self._artifact_repository = artifact_repository

    def dispatch(self, run: AnalysisRunRecord) -> None:
        self._run_repository.update_status(run.run_id, RunStatus.RUNNING)
        try:
            artifact = self._workflow.execute(run)
        except Exception as exc:
            self._run_repository.update_status(
                run.run_id,
                RunStatus.FAILED,
                failure_message=str(exc),
            )
            return

        self._artifact_repository.save(run.run_id, artifact)
        self._run_repository.update_status(
            run.run_id,
            RunStatus.COMPLETED,
            failure_message=None,
        )
