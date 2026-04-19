from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from enum import StrEnum
from uuid import UUID

from app.domain.normalization import NormalizationWarning

class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"

class SourceType(StrEnum):
    TEXT = "text"
    PDF = "pdf"

@dataclass(frozen=True)
class AnalysisRunRecord:
    run_id: UUID
    script_id: UUID
    revision_id: UUID
    execution_fingerprint: str
    title: str | None
    script_text: str
    status: RunStatus
    normalized_content_fingerprint: str | None = None
    reused_from_run_id: UUID | None = None
    normalized_candidate_run_id: UUID | None = None
    source_type: SourceType = SourceType.TEXT
    source_document_name: str | None = None
    source_warnings: tuple[NormalizationWarning, ...] = ()
    failure_message: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
