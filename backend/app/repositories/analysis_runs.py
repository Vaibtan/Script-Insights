from typing import Protocol
from uuid import UUID

from app.domain.analysis_runs import AnalysisRunRecord, RunStatus


class AnalysisRunRepository(Protocol):
    def save(self, run: AnalysisRunRecord) -> None:
        ...

    def get(self, run_id: UUID) -> AnalysisRunRecord | None:
        ...

    def update_status(
        self,
        run_id: UUID,
        status: RunStatus,
        failure_message: str | None = None,
    ) -> AnalysisRunRecord | None:
        ...
