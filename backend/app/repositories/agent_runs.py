from typing import Protocol
from uuid import UUID

from app.domain.agent_runs import AgentRunRecord


class AgentRunRepository(Protocol):
    def save(self, run_id: UUID, agent_runs: tuple[AgentRunRecord, ...]) -> None:
        ...

    def list_by_run(self, run_id: UUID) -> tuple[AgentRunRecord, ...]:
        ...

    def clone(self, source_run_id: UUID, target_run_id: UUID) -> None:
        ...
