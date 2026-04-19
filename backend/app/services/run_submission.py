from dataclasses import dataclass
from uuid import UUID
from uuid import uuid4

from app.core.settings import Settings
from app.domain.analysis_runs import AnalysisRunRecord, RunStatus
from app.domain.run_views import AnalysisRunHandle
from app.domain.run_views import SubmitAnalysisRunCommand
from app.repositories.agent_runs import AgentRunRepository
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository
from app.services.fingerprints import ExecutionFingerprintService
from app.services.dispatchers import AnalysisDispatcher


@dataclass(slots=True)
class RunSubmissionService:
    repository: AnalysisRunRepository
    artifact_repository: AnalysisArtifactRepository
    agent_run_repository: AgentRunRepository
    dispatcher: AnalysisDispatcher
    fingerprint_service: ExecutionFingerprintService
    settings: Settings

    def submit(self, command: SubmitAnalysisRunCommand) -> AnalysisRunHandle:
        execution_fingerprint = self.fingerprint_service.compute(
            script_text=command.script_text,
            source_warnings=command.source_warnings,
        )
        reusable_run = self.repository.find_reusable_by_fingerprint(execution_fingerprint)
        if reusable_run is not None:
            run = self._build_run(command, execution_fingerprint=execution_fingerprint)
            self.repository.save(run)
            reusable_artifact = self.artifact_repository.get(reusable_run.run_id)
            if reusable_artifact is not None:
                self.artifact_repository.save(run.run_id, reusable_artifact)
                self.agent_run_repository.clone(reusable_run.run_id, run.run_id)
                normalized_content_fingerprint = (
                    reusable_run.normalized_content_fingerprint
                    or self.fingerprint_service.compute_normalized(
                        reusable_artifact.normalized_script
                    )
                )
                self.repository.update_analysis_metadata(
                    run.run_id,
                    normalized_content_fingerprint=normalized_content_fingerprint,
                    reused_from_run_id=reusable_run.run_id,
                    normalized_candidate_run_id=None,
                )
                persisted_run = self.repository.update_status(
                    run.run_id,
                    reusable_run.status,
                    failure_message=None,
                ) or run
                return AnalysisRunHandle(
                    result_version=self.settings.result_version,
                    run_id=persisted_run.run_id,
                    script_id=persisted_run.script_id,
                    revision_id=persisted_run.revision_id,
                    status=persisted_run.status,
                    failure_message=persisted_run.failure_message,
                    reused_from_run_id=reusable_run.run_id,
                )

        in_flight_run = self.repository.find_in_flight_by_fingerprint(execution_fingerprint)
        if in_flight_run is not None:
            run = self._build_run(
                command,
                execution_fingerprint=execution_fingerprint,
                status=in_flight_run.status,
                reused_from_run_id=in_flight_run.run_id,
                normalized_content_fingerprint=in_flight_run.normalized_content_fingerprint,
            )
            self.repository.save(run)
            reconciled_run = self._reconcile_attached_run(run, source_run_id=in_flight_run.run_id)
            return AnalysisRunHandle(
                result_version=self.settings.result_version,
                run_id=reconciled_run.run_id,
                script_id=reconciled_run.script_id,
                revision_id=reconciled_run.revision_id,
                status=reconciled_run.status,
                failure_message=reconciled_run.failure_message,
                reused_from_run_id=in_flight_run.run_id,
            )

        run = self._build_run(command, execution_fingerprint=execution_fingerprint)
        self.repository.save(run)
        self.dispatcher.dispatch(run)
        persisted_run = self.repository.get(run.run_id) or run

        return AnalysisRunHandle(
            result_version=self.settings.result_version,
            run_id=persisted_run.run_id,
            script_id=persisted_run.script_id,
            revision_id=persisted_run.revision_id,
            status=persisted_run.status,
            failure_message=persisted_run.failure_message,
            reused_from_run_id=persisted_run.reused_from_run_id,
        )

    def _reconcile_attached_run(
        self,
        run: AnalysisRunRecord,
        *,
        source_run_id: UUID,
    ) -> AnalysisRunRecord:
        source_run = self.repository.get(source_run_id)
        if source_run is None:
            return run

        if source_run.status in {RunStatus.COMPLETED, RunStatus.PARTIAL}:
            source_artifact = self.artifact_repository.get(source_run_id)
            if source_artifact is None:
                return run
            self.artifact_repository.save(run.run_id, source_artifact)
            self.agent_run_repository.clone(source_run_id, run.run_id)
            normalized_content_fingerprint = (
                source_run.normalized_content_fingerprint
                or self.fingerprint_service.compute_normalized(
                    source_artifact.normalized_script
                )
            )
            self.repository.update_analysis_metadata(
                run.run_id,
                normalized_content_fingerprint=normalized_content_fingerprint,
                reused_from_run_id=source_run_id,
                normalized_candidate_run_id=None,
            )
            return self.repository.update_status(
                run.run_id,
                source_run.status,
                failure_message=source_run.failure_message,
            ) or run

        if source_run.status == RunStatus.FAILED:
            return self.repository.update_status(
                run.run_id,
                RunStatus.FAILED,
                failure_message=source_run.failure_message,
            ) or run

        return self.repository.get(run.run_id) or run

    def _build_run(
        self,
        command: SubmitAnalysisRunCommand,
        *,
        execution_fingerprint: str,
        status: RunStatus = RunStatus.QUEUED,
        reused_from_run_id: UUID | None = None,
        normalized_content_fingerprint: str | None = None,
    ) -> AnalysisRunRecord:
        return AnalysisRunRecord(
            run_id=uuid4(),
            script_id=command.script_id or uuid4(),
            revision_id=uuid4(),
            execution_fingerprint=execution_fingerprint,
            title=command.title,
            script_text=command.script_text,
            status=status,
            normalized_content_fingerprint=normalized_content_fingerprint,
            reused_from_run_id=reused_from_run_id,
            source_type=command.source_type,
            source_document_name=command.source_document_name,
            source_warnings=command.source_warnings,
        )
