from dataclasses import dataclass
from uuid import uuid4

from app.core.settings import Settings
from app.domain.analysis_runs import AnalysisRunRecord, RunStatus
from app.domain.run_views import AnalysisRunHandle
from app.domain.run_views import SubmitAnalysisRunCommand
from app.repositories.analysis_runs import AnalysisRunRepository
from app.services.dispatchers import AnalysisDispatcher


@dataclass(slots=True)
class RunSubmissionService:
    repository: AnalysisRunRepository
    dispatcher: AnalysisDispatcher
    settings: Settings

    def submit(self, command: SubmitAnalysisRunCommand) -> AnalysisRunHandle:
        run = AnalysisRunRecord(
            run_id=uuid4(),
            script_id=uuid4(),
            revision_id=uuid4(),
            title=command.title,
            script_text=command.script_text,
            status=RunStatus.QUEUED,
        )
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
        )
