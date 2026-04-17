from typing import cast

from fastapi import Request

from app.core.container import AppContainer
from app.services.pdf_extraction import PdfTextExtractor
from app.services.revision_compare import RevisionComparisonService
from app.services.queue import RunQueueProcessor
from app.services.run_history import RunHistoryService
from app.services.run_query import RunQueryService
from app.services.run_submission import RunSubmissionService


def get_container(request: Request) -> AppContainer:
    return cast(AppContainer, request.app.state.container)


def get_run_submission_service(request: Request) -> RunSubmissionService:
    return get_container(request).run_submission_service


def get_run_query_service(request: Request) -> RunQueryService:
    return get_container(request).run_query_service


def get_pdf_text_extractor(request: Request) -> PdfTextExtractor:
    return get_container(request).pdf_text_extractor


def get_run_history_service(request: Request) -> RunHistoryService:
    return get_container(request).run_history_service


def get_revision_comparison_service(request: Request) -> RevisionComparisonService:
    return get_container(request).revision_comparison_service


def get_run_queue_processor(request: Request) -> RunQueueProcessor:
    return get_container(request).run_queue_processor
