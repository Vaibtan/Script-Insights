from __future__ import annotations

from collections.abc import Sequence

import dspy

from app.agents.dspy_runtime import DSPyPredictionRunner
from app.agents.dspy_runtime import PredictionParser
from app.agents.heuristic_programs import HeuristicCliffhangerProgram
from app.agents.heuristic_programs import HeuristicEngagementProgram
from app.agents.heuristic_programs import HeuristicEmotionProgram
from app.agents.heuristic_programs import HeuristicRecommendationProgram
from app.agents.heuristic_programs import HeuristicSummaryProgram
from app.agents.protocols import CliffhangerProgram
from app.agents.protocols import EngagementProgram
from app.agents.protocols import EmotionProgram
from app.agents.protocols import RecommendationProgram
from app.agents.protocols import SummaryProgram
from app.domain.analysis_outputs import CliffhangerResult
from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import EngagementResult
from app.domain.analysis_outputs import Recommendation
from app.domain.analysis_outputs import SummaryResult
from app.domain.normalization import NormalizedScript


def _parse_float(raw: object, fallback: float) -> float:
    try:
        return float(str(raw).strip())
    except (TypeError, ValueError):
        return fallback


def _parse_csv(raw: object) -> tuple[str, ...]:
    return tuple(item.strip() for item in str(raw).split(",") if item.strip())


class _SummarySignature(dspy.Signature):
    script = dspy.InputField()
    summary = dspy.OutputField(desc="Three to four lines summarizing the script.")


class _EmotionSignature(dspy.Signature):
    script = dspy.InputField()
    dominant_emotions = dspy.OutputField(desc="Comma-separated emotions.")
    valence = dspy.OutputField(desc="A value between -1 and 1.")
    arousal = dspy.OutputField(desc="A value between 0 and 1.")


class _EngagementSignature(dspy.Signature):
    script = dspy.InputField()
    overall_score = dspy.OutputField(desc="A score between 0 and 100.")
    hook = dspy.OutputField(desc="A score between 0 and 100.")
    conflict = dspy.OutputField(desc="A score between 0 and 100.")
    tension = dspy.OutputField(desc="A score between 0 and 100.")
    pacing = dspy.OutputField(desc="A score between 0 and 100.")
    stakes = dspy.OutputField(desc="A score between 0 and 100.")
    payoff = dspy.OutputField(desc="A score between 0 and 100.")
    rationale = dspy.OutputField()


class _RecommendationSignature(dspy.Signature):
    script = dspy.InputField()
    recommendations = dspy.OutputField(
        desc="One recommendation per line formatted as category|suggestion|rationale."
    )


class _CliffhangerSignature(dspy.Signature):
    script = dspy.InputField()
    moment_text = dspy.OutputField()
    why_it_works = dspy.OutputField()


class _SummaryParser(PredictionParser[SummaryResult]):
    def parse(
        self,
        prediction: object,
        fallback_result: SummaryResult,
    ) -> SummaryResult:
        summary_text = str(getattr(prediction, "summary", "")).strip()
        if not summary_text:
            return fallback_result
        return SummaryResult(
            text=summary_text,
            evidence_spans=fallback_result.evidence_spans,
        )


class _EmotionParser(PredictionParser[EmotionResult]):
    def parse(
        self,
        prediction: object,
        fallback_result: EmotionResult,
    ) -> EmotionResult:
        dominant_emotions = _parse_csv(
            getattr(prediction, "dominant_emotions", "")
        ) or fallback_result.dominant_emotions
        return EmotionResult(
            dominant_emotions=dominant_emotions,
            valence=_parse_float(
                getattr(prediction, "valence", fallback_result.valence),
                fallback_result.valence,
            ),
            arousal=_parse_float(
                getattr(prediction, "arousal", fallback_result.arousal),
                fallback_result.arousal,
            ),
            emotional_arc=fallback_result.emotional_arc,
            evidence_spans=fallback_result.evidence_spans,
        )


class _EngagementParser(PredictionParser[EngagementResult]):
    _factor_names = ("hook", "conflict", "tension", "pacing", "stakes", "payoff")

    def parse(
        self,
        prediction: object,
        fallback_result: EngagementResult,
    ) -> EngagementResult:
        factors = {
            factor_name: _parse_float(
                getattr(prediction, factor_name, fallback_result.factors[factor_name]),
                fallback_result.factors[factor_name],
            )
            for factor_name in self._factor_names
        }
        rationale = str(
            getattr(prediction, "rationale", fallback_result.rationale)
        ).strip()
        return EngagementResult(
            overall_score=_parse_float(
                getattr(prediction, "overall_score", fallback_result.overall_score),
                fallback_result.overall_score,
            ),
            factors=factors,
            rationale=rationale or fallback_result.rationale,
        )


class _RecommendationParser(PredictionParser[Sequence[Recommendation]]):
    def parse(
        self,
        prediction: object,
        fallback_result: Sequence[Recommendation],
    ) -> Sequence[Recommendation]:
        parsed: list[Recommendation] = []
        for line in str(getattr(prediction, "recommendations", "")).splitlines():
            parts = [part.strip() for part in line.split("|")]
            if len(parts) != 3 or not all(parts):
                continue
            parsed.append(
                Recommendation(
                    category=parts[0],
                    suggestion=parts[1],
                    rationale=parts[2],
                )
            )
        return tuple(parsed) if parsed else fallback_result


class _CliffhangerParser(PredictionParser[CliffhangerResult]):
    def parse(
        self,
        prediction: object,
        fallback_result: CliffhangerResult,
    ) -> CliffhangerResult:
        moment_text = str(
            getattr(prediction, "moment_text", fallback_result.moment_text)
        ).strip()
        why_it_works = str(
            getattr(prediction, "why_it_works", fallback_result.why_it_works)
        ).strip()
        if not moment_text or not why_it_works:
            return fallback_result
        return CliffhangerResult(
            moment_text=moment_text,
            why_it_works=why_it_works,
            evidence_spans=fallback_result.evidence_spans,
        )


class DSPySummaryProgram(SummaryProgram):
    def __init__(self, fallback: SummaryProgram | None = None) -> None:
        self.fallback = fallback or HeuristicSummaryProgram()
        self._runner = DSPyPredictionRunner(
            signature=_SummarySignature,
            fallback_executor=self.fallback.summarize,
            parser=_SummaryParser(),
        )

    def summarize(self, normalized_script: NormalizedScript) -> SummaryResult:
        return self._runner.run(normalized_script)


class DSPyEmotionProgram(EmotionProgram):
    def __init__(self, fallback: EmotionProgram | None = None) -> None:
        self.fallback = fallback or HeuristicEmotionProgram()
        self._runner = DSPyPredictionRunner(
            signature=_EmotionSignature,
            fallback_executor=self.fallback.analyze_emotion,
            parser=_EmotionParser(),
        )

    def analyze_emotion(self, normalized_script: NormalizedScript) -> EmotionResult:
        return self._runner.run(normalized_script)


class DSPyEngagementProgram(EngagementProgram):
    def __init__(self, fallback: EngagementProgram | None = None) -> None:
        self.fallback = fallback or HeuristicEngagementProgram()
        self._runner = DSPyPredictionRunner(
            signature=_EngagementSignature,
            fallback_executor=self.fallback.score_engagement,
            parser=_EngagementParser(),
        )

    def score_engagement(self, normalized_script: NormalizedScript) -> EngagementResult:
        return self._runner.run(normalized_script)


class DSPyRecommendationProgram(RecommendationProgram):
    def __init__(self, fallback: RecommendationProgram | None = None) -> None:
        self.fallback = fallback or HeuristicRecommendationProgram()
        self._runner = DSPyPredictionRunner(
            signature=_RecommendationSignature,
            fallback_executor=self.fallback.suggest_improvements,
            parser=_RecommendationParser(),
        )

    def suggest_improvements(
        self, normalized_script: NormalizedScript
    ) -> Sequence[Recommendation]:
        return self._runner.run(normalized_script)


class DSPyCliffhangerProgram(CliffhangerProgram):
    def __init__(self, fallback: CliffhangerProgram | None = None) -> None:
        self.fallback = fallback or HeuristicCliffhangerProgram()
        self._runner = DSPyPredictionRunner(
            signature=_CliffhangerSignature,
            fallback_executor=self.fallback.detect_cliffhanger,
            parser=_CliffhangerParser(),
        )

    def detect_cliffhanger(
        self, normalized_script: NormalizedScript
    ) -> CliffhangerResult:
        return self._runner.run(normalized_script)
