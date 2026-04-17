from uuid import UUID
from uuid import uuid4
import logging
from time import perf_counter

from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from app.api.mappers import to_run_comparison_response
from app.api.mappers import to_run_history_response
from app.api.mappers import to_analysis_run_detail_response
from app.api.mappers import to_submit_analysis_run_response
from app.api.dependencies import get_pdf_text_extractor
from app.api.dependencies import get_revision_comparison_service
from app.api.dependencies import get_run_queue_processor
from app.api.dependencies import get_run_history_service
from app.api.dependencies import get_run_query_service
from app.api.dependencies import get_run_submission_service
from app.api.schemas import AnalysisRunDetailResponse
from app.api.schemas import QueueDrainResponse
from app.api.schemas import RunComparisonResponse
from app.api.schemas import RunHistoryResponse
from app.api.schemas import SubmitAnalysisRunRequest
from app.api.schemas import SubmitAnalysisRunResponse
from app.core.container import AppContainer
from app.core.container import build_container
from app.core.logging import configure_logging
from app.core.logging import reset_request_id
from app.core.logging import set_request_id
from app.domain.run_views import SubmitAnalysisRunCommand
from app.domain.analysis_runs import RunStatus
from app.domain.analysis_runs import SourceType
from app.domain.normalization import NormalizationWarning
from app.services.pdf_extraction import PdfTextExtractor
from app.services.queue import RunQueueProcessor
from app.services.revision_compare import RevisionComparisonService
from app.services.run_history import RunHistoryService
from app.services.run_query import RunQueryService
from app.services.run_submission import RunSubmissionService

def create_app(container: AppContainer | None = None) -> FastAPI:
    configure_logging()
    logger = logging.getLogger("app.api.requests")
    resolved_container = container or build_container()
    settings = resolved_container.settings
    app = FastAPI(title=settings.app_name)
    app.state.container = resolved_container
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_logging_middleware(request, call_next):  # type: ignore[no-untyped-def]
        request_id = request.headers.get("x-request-id", "").strip() or str(uuid4())
        token = set_request_id(request_id)
        start = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((perf_counter() - start) * 1000, 2)
            logger.exception(
                "request_failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                },
            )
            reset_request_id(token)
            raise

        duration_ms = round((perf_counter() - start) * 1000, 2)
        response.headers["x-request-id"] = request_id
        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        reset_request_id(token)
        return response

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
                script_id=payload.script_id,
                source_type=SourceType.TEXT,
            ),
        )
        return to_submit_analysis_run_response(result)

    @app.post(
        f"{settings.api_v1_prefix}/analysis/runs/upload",
        response_model=SubmitAnalysisRunResponse,
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def submit_analysis_run_upload(
        file: UploadFile = File(...),
        title: str | None = Form(default=None),
        script_id: UUID | None = Form(default=None),
        *,
        run_submission_service: Annotated[
            RunSubmissionService, Depends(get_run_submission_service)
        ],
        pdf_text_extractor: Annotated[
            PdfTextExtractor, Depends(get_pdf_text_extractor)
        ],
    ) -> SubmitAnalysisRunResponse:
        filename = file.filename or ""
        if file.content_type != "application/pdf" and not filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF uploads are supported.",
            )
        pdf_bytes = await file.read()
        extracted = pdf_text_extractor.extract_text(pdf_bytes)
        if not extracted.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to extract text from the PDF file.",
            )
        result = run_submission_service.submit(
            command=SubmitAnalysisRunCommand(
                script_text=extracted.text,
                title=title,
                script_id=script_id,
                source_type=SourceType.PDF,
                source_document_name=filename or None,
                source_warnings=tuple(
                    NormalizationWarning(
                        code=warning_code,
                        message=warning_code.replace("_", " "),
                    )
                    for warning_code in extracted.warnings
                ),
            )
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

    @app.get(
        f"{settings.api_v1_prefix}/scripts/{{script_id}}/runs",
        response_model=RunHistoryResponse,
    )
    def get_script_run_history(
        script_id: UUID,
        run_history_service: Annotated[
            RunHistoryService, Depends(get_run_history_service)
        ],
        revision_id: UUID | None = None,
        run_status: RunStatus | None = Query(default=None, alias="status"),
    ) -> RunHistoryResponse:
        history = run_history_service.get_history(
            script_id,
            revision_id=revision_id,
            status=run_status,
        )
        return to_run_history_response(history)

    @app.get(
        f"{settings.api_v1_prefix}/scripts/{{script_id}}/compare",
        response_model=RunComparisonResponse,
    )
    def compare_script_runs(
        script_id: UUID,
        base_run_id: UUID,
        target_run_id: UUID,
        revision_comparison_service: Annotated[
            RevisionComparisonService, Depends(get_revision_comparison_service)
        ],
    ) -> RunComparisonResponse:
        comparison = revision_comparison_service.compare(
            script_id=script_id,
            base_run_id=base_run_id,
            target_run_id=target_run_id,
        )
        if comparison is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unable to compare the requested runs.",
            )
        return to_run_comparison_response(comparison)

    @app.post(
        f"{settings.api_v1_prefix}/analysis/workers/drain",
        response_model=QueueDrainResponse,
    )
    def drain_worker_queue(
        run_queue_processor: Annotated[
            RunQueueProcessor, Depends(get_run_queue_processor)
        ],
    ) -> QueueDrainResponse:
        return QueueDrainResponse(processed=run_queue_processor.drain())

    return app


app = create_app()
