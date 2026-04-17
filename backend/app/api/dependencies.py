from typing import cast

from fastapi import Request

from app.services.run_submission import RunSubmissionService


def get_run_submission_service(request: Request) -> RunSubmissionService:
    return cast(RunSubmissionService, request.app.state.run_submission_service)
