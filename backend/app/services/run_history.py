from dataclasses import dataclass
from uuid import UUID

from app.core.settings import Settings
from app.domain.analysis_runs import RunStatus
from app.domain.run_views import RunHistory
from app.domain.run_views import RunHistoryEntry
from app.repositories.analysis_runs import AnalysisRunRepository


@dataclass(slots=True)
class RunHistoryService:
    run_repository: AnalysisRunRepository
    settings: Settings

    def get_history(
        self,
        script_id: UUID,
        *,
        revision_id: UUID | None = None,
        status: RunStatus | None = None,
    ) -> RunHistory:
        runs = self.run_repository.list_by_script(script_id)
        if revision_id is not None:
            runs = tuple(run for run in runs if run.revision_id == revision_id)
        if status is not None:
            runs = tuple(run for run in runs if run.status == status)

        return RunHistory(
            result_version=self.settings.result_version,
            script_id=script_id,
            runs=tuple(
                RunHistoryEntry(
                    run_id=run.run_id,
                    revision_id=run.revision_id,
                    status=run.status,
                    created_at=run.created_at,
                )
                for run in runs
            ),
        )
