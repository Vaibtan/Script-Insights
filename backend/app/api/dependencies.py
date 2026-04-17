from typing import cast

from fastapi import Request

from app.core.container import AppContainer
from app.services.run_query import RunQueryService
from app.services.run_submission import RunSubmissionService


def get_container(request: Request) -> AppContainer:
    return cast(AppContainer, request.app.state.container)


def get_run_submission_service(request: Request) -> RunSubmissionService:
    return get_container(request).run_submission_service


def get_run_query_service(request: Request) -> RunQueryService:
    return get_container(request).run_query_service
