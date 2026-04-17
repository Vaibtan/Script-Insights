from typing import Annotated

from fastapi import Depends, FastAPI, status

from app.api.dependencies import get_run_submission_service
from app.api.schemas import SubmitAnalysisRunRequest, SubmitAnalysisRunResponse
from app.core.settings import get_settings
from app.repositories.in_memory import InMemoryAnalysisRunRepository
from app.services.dispatchers import InlineAnalysisDispatcher
from app.services.run_submission import RunSubmissionService

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    run_repository = InMemoryAnalysisRunRepository()
    dispatcher = InlineAnalysisDispatcher()
    app.state.run_submission_service = RunSubmissionService(
        repository=run_repository,
        dispatcher=dispatcher,
        settings=settings,
    )

    @app.get(f"{settings.api_v1_prefix}/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        f"{settings.api_v1_prefix}/analysis/runs",
        response_model=SubmitAnalysisRunResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    def submit_analysis_run(
        payload: SubmitAnalysisRunRequest,
        run_submission_service: Annotated[
            RunSubmissionService, Depends(get_run_submission_service)
        ],
    ) -> SubmitAnalysisRunResponse:
        return run_submission_service.submit(payload)

    return app


app = create_app()
