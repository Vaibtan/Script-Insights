from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass(frozen=True)
class AnalysisRunRecord:
    run_id: UUID
    script_id: UUID
    revision_id: UUID
    title: str | None
    script_text: str
    status: RunStatus
    failure_message: str | None = None
