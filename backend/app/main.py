from uuid import UUID

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from app.api.mappers import to_analysis_run_detail_response
from app.api.mappers import to_submit_analysis_run_response
from app.api.dependencies import get_run_query_service
from app.api.dependencies import get_run_submission_service
from app.api.schemas import AnalysisRunDetailResponse
from app.api.schemas import SubmitAnalysisRunRequest
from app.api.schemas import SubmitAnalysisRunResponse
from app.core.container import AppContainer
from app.core.container import build_container
from app.domain.run_views import SubmitAnalysisRunCommand
from app.services.run_query import RunQueryService
from app.services.run_submission import RunSubmissionService

def create_app(container: AppContainer | None = None) -> FastAPI:
    resolved_container = container or build_container()
    settings = resolved_container.settings
    app = FastAPI(title=settings.app_name)
    app.state.container = resolved_container

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
        result = run_submission_service.submit(
            command=SubmitAnalysisRunCommand(
                script_text=payload.script_text,
                title=payload.title,
            ),
        )
        return to_submit_analysis_run_response(result)

    @app.get(
        f"{settings.api_v1_prefix}/analysis/runs/{{run_id}}",
        response_model=AnalysisRunDetailResponse,
    )
    def get_analysis_run(
        run_id: UUID,
        run_query_service: Annotated[RunQueryService, Depends(get_run_query_service)],
    ) -> AnalysisRunDetailResponse:
        run_detail = run_query_service.get_run_detail(run_id=run_id)
        if run_detail is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Run not found."
            )
        return to_analysis_run_detail_response(run_detail)

    return app


app = create_app()
