from dataclasses import dataclass
from typing import Any
from app.agents.heuristic_programs import HeuristicEmotionProgram
from app.agents.heuristic_programs import HeuristicSummaryProgram
from app.agents.protocols import EmotionProgram
from app.agents.protocols import SummaryProgram
from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import SummaryResult
from app.domain.normalization import NormalizedScript
import dspy

class _SummarySignature(dspy.Signature):
    script = dspy.InputField()
    summary = dspy.OutputField()


@dataclass(slots=True)
class DSPySummaryProgram(SummaryProgram):
    fallback: SummaryProgram

    def __init__(self, fallback: SummaryProgram | None = None) -> None:
        self.fallback = fallback or HeuristicSummaryProgram()
        self._predictor: Any | None = None
        if dspy is not None:
            self._predictor = dspy.Predict(_SummarySignature)

    def summarize(self, normalized_script: NormalizedScript) -> SummaryResult:
        if self._predictor is None or dspy is None:
            return self.fallback.summarize(normalized_script)

        lm = getattr(dspy.settings, "lm", None)
        if lm is None:
            return self.fallback.summarize(normalized_script)

        try:
            script_text = "\n".join(scene.content for scene in normalized_script.scenes)
            prediction = self._predictor(script=script_text)
            summary_text = str(getattr(prediction, "summary", "")).strip()
            if not summary_text:
                return self.fallback.summarize(normalized_script)
            fallback_summary = self.fallback.summarize(normalized_script)
            return SummaryResult(
                text=summary_text,
                evidence_spans=fallback_summary.evidence_spans,
            )
        except Exception: return self.fallback.summarize(normalized_script)


@dataclass(slots = True)
class DSPyEmotionProgram(EmotionProgram):
    fallback: EmotionProgram

    def __init__(self, fallback: EmotionProgram | None = None) -> None:
        self.fallback = fallback or HeuristicEmotionProgram()

    def analyze_emotion(self, normalized_script: NormalizedScript) -> EmotionResult:
        # Slice 4 starts with a deterministic implementation for contract stability.
        # This wrapper keeps the DSPy integration point explicit for later upgrades.
        return self.fallback.analyze_emotion(normalized_script)
