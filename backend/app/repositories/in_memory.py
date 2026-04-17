from uuid import UUID

from app.domain.analysis_runs import AnalysisRunRecord
from app.repositories.analysis_runs import AnalysisRunRepository


class InMemoryAnalysisRunRepository(AnalysisRunRepository):
    def __init__(self) -> None:
        self._runs: dict[UUID, AnalysisRunRecord] = {}

    def save(self, run: AnalysisRunRecord) -> None:
        self._runs[run.run_id] = run

    def get(self, run_id: UUID) -> AnalysisRunRecord | None:
        return self._runs.get(run_id)
