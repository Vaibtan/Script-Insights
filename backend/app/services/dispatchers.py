from typing import Protocol
from uuid import UUID

from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.analysis_runs import RunStatus
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository
from app.services.workflow import AnalysisWorkflowExecutor


class AnalysisDispatcher(Protocol):
    def dispatch(self, run: AnalysisRunRecord) -> None:
        ...


class QueueEnqueuer(Protocol):
    def enqueue(self, run_id: UUID) -> None:
        ...


def execute_run_workflow(
    *,
    run: AnalysisRunRecord,
    workflow: AnalysisWorkflowExecutor,
    run_repository: AnalysisRunRepository,
    artifact_repository: AnalysisArtifactRepository,
) -> None:
    run_repository.update_status(run.run_id, RunStatus.RUNNING)
    try:
        artifact = workflow.execute(run)
    except Exception as exc:
        run_repository.update_status(
            run.run_id,
            RunStatus.FAILED,
            failure_message=str(exc),
        )
        return

    artifact_repository.save(run.run_id, artifact)
    final_status = RunStatus.PARTIAL if artifact.warnings else RunStatus.COMPLETED
    run_repository.update_status(
        run.run_id,
        final_status,
        failure_message=None,
    )


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
        execute_run_workflow(
            run=run,
            workflow=self._workflow,
            run_repository=self._run_repository,
            artifact_repository=self._artifact_repository,
        )


class QueuedAnalysisDispatcher(AnalysisDispatcher):
    def __init__(self, queue: QueueEnqueuer) -> None:
        self._queue = queue

    def dispatch(self, run: AnalysisRunRecord) -> None:
        self._queue.enqueue(run.run_id)
