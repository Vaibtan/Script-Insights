from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.agent_runs import AgentRunRecord
from app.repositories.agent_runs import AgentRunRepository
from app.repositories.sqlalchemy_gateway import SqlAlchemyPersistenceGateway


@dataclass(slots=True)
class SqlAlchemyAgentRunRepository(AgentRunRepository):
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

    def save(self, run_id: UUID, agent_runs: tuple[AgentRunRecord, ...]) -> None:
        self._gateway.save_agent_runs(run_id, agent_runs)

    def list_by_run(self, run_id: UUID) -> tuple[AgentRunRecord, ...]:
        return self._gateway.list_agent_runs(run_id)

    def clone(self, source_run_id: UUID, target_run_id: UUID) -> None:
        self._gateway.clone_agent_runs(source_run_id, target_run_id)
