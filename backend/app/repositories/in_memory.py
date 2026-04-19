from dataclasses import replace
from uuid import UUID

from app.domain.agent_runs import AgentRunRecord
from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.analysis_runs import RunStatus
from app.repositories.agent_runs import AgentRunRepository
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository


class InMemoryAnalysisRunRepository(AnalysisRunRepository):
    def __init__(self) -> None:
        self._runs: dict[UUID, AnalysisRunRecord] = {}

    def save(self, run: AnalysisRunRecord) -> None:
        self._runs[run.run_id] = run

    def get(self, run_id: UUID) -> AnalysisRunRecord | None:
        return self._runs.get(run_id)

    def update_status(
        self,
        run_id: UUID,
        status: RunStatus,
        failure_message: str | None = None,
    ) -> AnalysisRunRecord | None:
        run = self._runs.get(run_id)
        if run is None:
            return None
        updated = replace(run, status=status, failure_message=failure_message)
        self._runs[run_id] = updated
        return updated

    def list_by_script(self, script_id: UUID) -> tuple[AnalysisRunRecord, ...]:
        runs = [run for run in self._runs.values() if run.script_id == script_id]
        return tuple(sorted(runs, key=lambda item: item.created_at, reverse=True))

    def list_queued(self, limit: int | None = None) -> tuple[AnalysisRunRecord, ...]:
        runs = sorted(
            (
                run
                for run in self._runs.values()
                if run.status == RunStatus.QUEUED and run.reused_from_run_id is None
            ),
            key=lambda item: item.created_at,
        )
        if limit is not None:
            runs = runs[:limit]
        return tuple(runs)

    def find_reusable_by_fingerprint(
        self,
        execution_fingerprint: str,
    ) -> AnalysisRunRecord | None:
        matches = [
            run
            for run in self._runs.values()
            if run.execution_fingerprint == execution_fingerprint
            and run.reused_from_run_id is None
            and run.status in {RunStatus.COMPLETED, RunStatus.PARTIAL}
        ]
        if not matches:
            return None
        return max(matches, key=lambda item: item.created_at)

    def find_in_flight_by_fingerprint(
        self,
        execution_fingerprint: str,
    ) -> AnalysisRunRecord | None:
        matches = [
            run
            for run in self._runs.values()
            if run.execution_fingerprint == execution_fingerprint
            and run.reused_from_run_id is None
            and run.status in {RunStatus.QUEUED, RunStatus.RUNNING}
        ]
        if not matches:
            return None
        return max(matches, key=lambda item: item.created_at)

    def find_normalized_candidate(
        self,
        normalized_content_fingerprint: str,
        *,
        exclude_run_id: UUID,
    ) -> AnalysisRunRecord | None:
        matches = [
            run
            for run in self._runs.values()
            if run.run_id != exclude_run_id
            and run.normalized_content_fingerprint == normalized_content_fingerprint
            and run.status in {RunStatus.COMPLETED, RunStatus.PARTIAL}
        ]
        if not matches:
            return None
        return max(matches, key=lambda item: item.created_at)

    def list_reuse_dependents(
        self,
        reused_from_run_id: UUID,
    ) -> tuple[AnalysisRunRecord, ...]:
        runs = [
            run
            for run in self._runs.values()
            if run.reused_from_run_id == reused_from_run_id
            and run.status in {RunStatus.QUEUED, RunStatus.RUNNING}
        ]
        return tuple(sorted(runs, key=lambda item: item.created_at))

    def update_analysis_metadata(
        self,
        run_id: UUID,
        *,
        normalized_content_fingerprint: str | None,
        reused_from_run_id: UUID | None,
        normalized_candidate_run_id: UUID | None,
    ) -> AnalysisRunRecord | None:
        run = self._runs.get(run_id)
        if run is None:
            return None
        updated = replace(
            run,
            normalized_content_fingerprint=normalized_content_fingerprint,
            reused_from_run_id=reused_from_run_id,
            normalized_candidate_run_id=normalized_candidate_run_id,
        )
        self._runs[run_id] = updated
        return updated


class InMemoryAnalysisArtifactRepository(AnalysisArtifactRepository):
    def __init__(self) -> None:
        self._artifacts: dict[UUID, AnalysisArtifact] = {}

    def save(self, run_id: UUID, artifact: AnalysisArtifact) -> None:
        self._artifacts[run_id] = artifact

    def get(self, run_id: UUID) -> AnalysisArtifact | None:
        return self._artifacts.get(run_id)


class InMemoryAgentRunRepository(AgentRunRepository):
    def __init__(self) -> None:
        self._agent_runs: dict[UUID, tuple[AgentRunRecord, ...]] = {}

    def save(self, run_id: UUID, agent_runs: tuple[AgentRunRecord, ...]) -> None:
        self._agent_runs[run_id] = agent_runs

    def list_by_run(self, run_id: UUID) -> tuple[AgentRunRecord, ...]:
        return self._agent_runs.get(run_id, ())

    def clone(self, source_run_id: UUID, target_run_id: UUID) -> None:
        self._agent_runs[target_run_id] = self._agent_runs.get(source_run_id, ())
