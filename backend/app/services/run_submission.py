from dataclasses import dataclass
from uuid import uuid4

from app.api.schemas import SubmitAnalysisRunRequest, SubmitAnalysisRunResponse
from app.core.settings import Settings
from app.domain.analysis_runs import AnalysisRunRecord, RunStatus
from app.repositories.analysis_runs import AnalysisRunRepository
from app.services.dispatchers import AnalysisDispatcher


@dataclass(slots=True)
class RunSubmissionService:
    repository: AnalysisRunRepository
    dispatcher: AnalysisDispatcher
    settings: Settings

    def submit(self, request: SubmitAnalysisRunRequest) -> SubmitAnalysisRunResponse:
        run = AnalysisRunRecord(
            run_id=uuid4(),
            script_id=uuid4(),
            revision_id=uuid4(),
            title=request.title,
            script_text=request.script_text,
            status=RunStatus.QUEUED,
        )
        self.repository.save(run)
        self.dispatcher.dispatch(run)

        return SubmitAnalysisRunResponse(
            result_version=self.settings.result_version,
            run_id=run.run_id,
            script_id=run.script_id,
            revision_id=run.revision_id,
            status=run.status,
        )
