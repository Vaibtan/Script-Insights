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

    def list_by_script(self, script_id: UUID) -> tuple[AnalysisRunRecord, ...]:
        ...

    def list_queued(self, limit: int | None = None) -> tuple[AnalysisRunRecord, ...]:
        ...

    def find_reusable_by_fingerprint(
        self,
        execution_fingerprint: str,
    ) -> AnalysisRunRecord | None:
        ...

    def find_in_flight_by_fingerprint(
        self,
        execution_fingerprint: str,
    ) -> AnalysisRunRecord | None:
        ...

    def find_normalized_candidate(
        self,
        normalized_content_fingerprint: str,
        *,
        exclude_run_id: UUID,
    ) -> AnalysisRunRecord | None:
        ...

    def list_reuse_dependents(
        self,
        reused_from_run_id: UUID,
    ) -> tuple[AnalysisRunRecord, ...]:
        ...

    def update_analysis_metadata(
        self,
        run_id: UUID,
        *,
        normalized_content_fingerprint: str | None,
        reused_from_run_id: UUID | None,
        normalized_candidate_run_id: UUID | None,
    ) -> AnalysisRunRecord | None:
        ...
