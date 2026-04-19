from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class AgentRunStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class AgentRunRecord:
    agent_name: str
    status: AgentRunStatus
    backend: str
    model_name: str | None
    started_at: datetime
    completed_at: datetime
    latency_ms: int
    warnings: tuple[str, ...] = ()
    failure_message: str | None = None
