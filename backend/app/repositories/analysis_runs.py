from typing import Protocol
from uuid import UUID

from app.domain.analysis_runs import AnalysisRunRecord


class AnalysisRunRepository(Protocol):
    def save(self, run: AnalysisRunRecord) -> None:
        ...

    def get(self, run_id: UUID) -> AnalysisRunRecord | None:
        ...
