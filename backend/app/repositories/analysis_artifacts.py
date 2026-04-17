from typing import Protocol
from uuid import UUID

from app.domain.analysis_artifacts import AnalysisArtifact


class AnalysisArtifactRepository(Protocol):
    def save(self, run_id: UUID, artifact: AnalysisArtifact) -> None:
        ...

    def get(self, run_id: UUID) -> AnalysisArtifact | None:
        ...
