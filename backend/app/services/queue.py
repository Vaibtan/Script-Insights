from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.domain.analysis_runs import AnalysisRunRecord
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository
from app.services.dispatchers import execute_run_workflow
from app.services.fingerprints import ExecutionFingerprintService
from app.services.workflow import AnalysisWorkflowExecutor


class RunQueue(Protocol):
    def enqueue(self, run_id: UUID) -> None:
        ...

    def pop(self) -> UUID | None:
        ...

    def size(self) -> int:
        ...


@dataclass(slots=True)
class RepositoryBackedRunQueue(RunQueue):
    run_repository: AnalysisRunRepository

    def enqueue(self, run_id: UUID) -> None:
        _ = run_id

    def pop(self) -> UUID | None:
        queued_runs = self.run_repository.list_queued(limit=1)
        if not queued_runs:
            return None
        return queued_runs[0].run_id

    def size(self) -> int:
        return len(self.run_repository.list_queued())


@dataclass(slots=True)
class RunQueueProcessor:
    queue: RunQueue
    workflow: AnalysisWorkflowExecutor
    run_repository: AnalysisRunRepository
    artifact_repository: AnalysisArtifactRepository
    fingerprint_service: ExecutionFingerprintService

    def drain(self) -> int:
        processed = 0
        while True:
            run_id = self.queue.pop()
            if run_id is None:
                return processed
            run = self.run_repository.get(run_id)
            if run is None:
                continue
            execute_run_workflow(
                run=run,
                workflow=self.workflow,
                run_repository=self.run_repository,
                artifact_repository=self.artifact_repository,
                fingerprint_service=self.fingerprint_service,
            )
            processed += 1
