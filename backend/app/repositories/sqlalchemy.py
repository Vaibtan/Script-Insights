from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.analysis_runs import RunStatus
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository
from app.repositories.sqlalchemy_gateway import SqlAlchemyPersistenceGateway


@dataclass(slots=True)
class SqlAlchemyAnalysisRunRepository(AnalysisRunRepository):
    _gateway: SqlAlchemyPersistenceGateway

    def __init__(
        self,
        session_factory: Callable[[], Session] | None = None,
        *,
        gateway: SqlAlchemyPersistenceGateway | None = None,
    ) -> None:
        if gateway is None and session_factory is None:
            raise ValueError("session_factory or gateway is required")
        self._gateway = gateway or SqlAlchemyPersistenceGateway(session_factory)

    def save(self, run: AnalysisRunRecord) -> None:
        self._gateway.save_run(run)

    def get(self, run_id: UUID) -> AnalysisRunRecord | None:
        return self._gateway.get_run(run_id)

    def update_status(
        self,
        run_id: UUID,
        status: RunStatus,
        failure_message: str | None = None,
    ) -> AnalysisRunRecord | None:
        return self._gateway.update_run_status(run_id, status, failure_message)

    def list_by_script(self, script_id: UUID) -> tuple[AnalysisRunRecord, ...]:
        return self._gateway.list_runs_by_script(script_id)

    def list_queued(self, limit: int | None = None) -> tuple[AnalysisRunRecord, ...]:
        return self._gateway.list_queued_runs(limit)


@dataclass(slots=True)
class SqlAlchemyAnalysisArtifactRepository(AnalysisArtifactRepository):
    _gateway: SqlAlchemyPersistenceGateway

    def __init__(
        self,
        session_factory: Callable[[], Session] | None = None,
        *,
        gateway: SqlAlchemyPersistenceGateway | None = None,
    ) -> None:
        if gateway is None and session_factory is None:
            raise ValueError("session_factory or gateway is required")
        self._gateway = gateway or SqlAlchemyPersistenceGateway(session_factory)

    def save(self, run_id: UUID, artifact: AnalysisArtifact) -> None:
        self._gateway.save_artifact(run_id, artifact)

    def get(self, run_id: UUID) -> AnalysisArtifact | None:
        return self._gateway.get_artifact(run_id)
