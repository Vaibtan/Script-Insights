from dataclasses import dataclass
from typing import Protocol

from app.agents.protocols import EmotionProgram
from app.agents.protocols import SummaryProgram
from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.analysis_runs import AnalysisRunRecord
from app.services.normalization import ScriptNormalizer


class AnalysisWorkflowExecutor(Protocol):
    def execute(self, run: AnalysisRunRecord) -> AnalysisArtifact:
        ...


@dataclass(slots=True)
class AnalysisWorkflow:
    normalizer: ScriptNormalizer
    summary_program: SummaryProgram | None = None
    emotion_program: EmotionProgram | None = None

    def execute(self, run: AnalysisRunRecord) -> AnalysisArtifact:
        normalized_script = self.normalizer.normalize(run.script_text)
        summary = (
            self.summary_program.summarize(normalized_script)
            if self.summary_program is not None
            else None
        )
        emotion = (
            self.emotion_program.analyze_emotion(normalized_script)
            if self.emotion_program is not None
            else None
        )
        return AnalysisArtifact(
            normalized_script=normalized_script,
            summary=summary,
            emotion=emotion,
        )
