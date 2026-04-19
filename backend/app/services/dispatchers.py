import logging
from typing import Protocol
from uuid import UUID

from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.analysis_runs import RunStatus
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository
from app.services.fingerprints import ExecutionFingerprintService
from app.services.workflow import AnalysisWorkflowExecutor


class AnalysisDispatcher(Protocol):
    def dispatch(self, run: AnalysisRunRecord) -> None:
        ...


class QueueEnqueuer(Protocol):
    def enqueue(self, run_id: UUID) -> None:
        ...


def _fan_out_reused_result(
    *,
    source_run_id: UUID,
    final_status: RunStatus,
    failure_message: str | None,
    normalized_content_fingerprint: str | None,
    artifact_repository: AnalysisArtifactRepository,
    run_repository: AnalysisRunRepository,
) -> None:
    source_artifact = (
        artifact_repository.get(source_run_id) if failure_message is None else None
    )
    for dependent_run in run_repository.list_reuse_dependents(source_run_id):
        if source_artifact is not None:
            artifact_repository.save(dependent_run.run_id, source_artifact)
        run_repository.update_status(
            dependent_run.run_id,
            final_status,
            failure_message=failure_message,
        )
        run_repository.update_analysis_metadata(
            dependent_run.run_id,
            normalized_content_fingerprint=normalized_content_fingerprint,
            reused_from_run_id=source_run_id,
            normalized_candidate_run_id=None,
        )


def execute_run_workflow(
    *,
    run: AnalysisRunRecord,
    workflow: AnalysisWorkflowExecutor,
    run_repository: AnalysisRunRepository,
    artifact_repository: AnalysisArtifactRepository,
    fingerprint_service: ExecutionFingerprintService,
) -> None:
    logger = logging.getLogger("app.services.reuse")
    run_repository.update_status(run.run_id, RunStatus.RUNNING)
    try:
        artifact = workflow.execute(run)
    except Exception as exc:
        run_repository.update_status(
            run.run_id,
            RunStatus.FAILED,
            failure_message=str(exc),
        )
        _fan_out_reused_result(
            source_run_id=run.run_id,
            final_status=RunStatus.FAILED,
            failure_message=str(exc),
            normalized_content_fingerprint=run.normalized_content_fingerprint,
            artifact_repository=artifact_repository,
            run_repository=run_repository,
        )
        return

    normalized_content_fingerprint = fingerprint_service.compute_normalized(
        artifact.normalized_script
    )
    normalized_candidate = run_repository.find_normalized_candidate(
        normalized_content_fingerprint,
        exclude_run_id=run.run_id,
    )
    artifact_repository.save(run.run_id, artifact)
    final_status = RunStatus.PARTIAL if artifact.warnings else RunStatus.COMPLETED
    run_repository.update_status(
        run.run_id,
        final_status,
        failure_message=None,
    )
    run_repository.update_analysis_metadata(
        run.run_id,
        normalized_content_fingerprint=normalized_content_fingerprint,
        reused_from_run_id=run.reused_from_run_id,
        normalized_candidate_run_id=(
            normalized_candidate.run_id if normalized_candidate is not None else None
        ),
    )
    _fan_out_reused_result(
        source_run_id=run.run_id,
        final_status=final_status,
        failure_message=None,
        normalized_content_fingerprint=normalized_content_fingerprint,
        artifact_repository=artifact_repository,
        run_repository=run_repository,
    )
    if normalized_candidate is not None:
        logger.info(
            "normalized_reuse_candidate_detected",
            extra={
                "run_id": str(run.run_id),
                "candidate_run_id": str(normalized_candidate.run_id),
                "normalized_content_fingerprint": normalized_content_fingerprint,
            },
        )


class InlineAnalysisDispatcher(AnalysisDispatcher):
    def __init__(
        self,
        workflow: AnalysisWorkflowExecutor,
        run_repository: AnalysisRunRepository,
        artifact_repository: AnalysisArtifactRepository,
        fingerprint_service: ExecutionFingerprintService,
    ) -> None:
        self._workflow = workflow
        self._run_repository = run_repository
        self._artifact_repository = artifact_repository
        self._fingerprint_service = fingerprint_service

    def dispatch(self, run: AnalysisRunRecord) -> None:
        execute_run_workflow(
            run=run,
            workflow=self._workflow,
            run_repository=self._run_repository,
            artifact_repository=self._artifact_repository,
            fingerprint_service=self._fingerprint_service,
        )


class QueuedAnalysisDispatcher(AnalysisDispatcher):
    def __init__(self, queue: QueueEnqueuer) -> None:
        self._queue = queue

    def dispatch(self, run: AnalysisRunRecord) -> None:
        self._queue.enqueue(run.run_id)
