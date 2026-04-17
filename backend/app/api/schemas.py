from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.analysis_runs import RunStatus


class SubmitAnalysisRunRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    script_text: str = Field(min_length=1)
    title: str | None = Field(default=None, min_length=1)


class SubmitAnalysisRunResponse(BaseModel):
    result_version: str
    run_id: UUID
    script_id: UUID
    revision_id: UUID
    status: RunStatus
