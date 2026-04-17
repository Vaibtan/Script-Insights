from typing import Protocol

from app.domain.analysis_runs import AnalysisRunRecord


class AnalysisDispatcher(Protocol):
    def dispatch(self, run: AnalysisRunRecord) -> None:
        ...


class InlineAnalysisDispatcher(AnalysisDispatcher):
    def dispatch(self, run: AnalysisRunRecord) -> None:
        # Slice 1 intentionally persists and acknowledges the run only.
        # Worker execution will be introduced in later slices.
        _ = run
