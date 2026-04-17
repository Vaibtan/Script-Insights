from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import dspy

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


def _build_script_text(normalized_script: NormalizedScript) -> str:
    return "\n".join(scene.content for scene in normalized_script.scenes)


def _has_live_lm() -> bool:
    return getattr(dspy.settings, "lm", None) is not None


def _parse_float(raw: object, fallback: float) -> float:
    try:
        return float(str(raw).strip())
    except (TypeError, ValueError):
        return fallback


def _parse_csv(raw: object) -> tuple[str, ...]:
    return tuple(
        item.strip()
        for item in str(raw).split(",")
        if item.strip()
    )


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


@dataclass(slots=True)
class DSPySummaryProgram(SummaryProgram):
    fallback: SummaryProgram

    def __init__(self, fallback: SummaryProgram | None = None) -> None:
        self.fallback = fallback or HeuristicSummaryProgram()
        self._predictor: Any | None = dspy.Predict(_SummarySignature)

    def summarize(self, normalized_script: NormalizedScript) -> SummaryResult:
        fallback_summary = self.fallback.summarize(normalized_script)
        if self._predictor is None or not _has_live_lm():
            return fallback_summary

        try:
            prediction = self._predictor(script=_build_script_text(normalized_script))
            summary_text = str(getattr(prediction, "summary", "")).strip()
            if not summary_text:
                return fallback_summary
            return SummaryResult(
                text=summary_text,
                evidence_spans=fallback_summary.evidence_spans,
            )
        except Exception:
            return fallback_summary


@dataclass(slots=True)
class DSPyEmotionProgram(EmotionProgram):
    fallback: EmotionProgram

    def __init__(self, fallback: EmotionProgram | None = None) -> None:
        self.fallback = fallback or HeuristicEmotionProgram()
        self._predictor: Any | None = dspy.Predict(_EmotionSignature)

    def analyze_emotion(self, normalized_script: NormalizedScript) -> EmotionResult:
        fallback_result = self.fallback.analyze_emotion(normalized_script)
        if self._predictor is None or not _has_live_lm():
            return fallback_result

        try:
            prediction = self._predictor(script=_build_script_text(normalized_script))
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
        except Exception:
            return fallback_result


@dataclass(slots=True)
class DSPyEngagementProgram(EngagementProgram):
    fallback: EngagementProgram

    def __init__(self, fallback: EngagementProgram | None = None) -> None:
        self.fallback = fallback or HeuristicEngagementProgram()
        self._predictor: Any | None = dspy.Predict(_EngagementSignature)

    def score_engagement(self, normalized_script: NormalizedScript) -> EngagementResult:
        fallback_result = self.fallback.score_engagement(normalized_script)
        if self._predictor is None or not _has_live_lm():
            return fallback_result

        try:
            prediction = self._predictor(script=_build_script_text(normalized_script))
            return EngagementResult(
                overall_score=_parse_float(
                    getattr(prediction, "overall_score", fallback_result.overall_score),
                    fallback_result.overall_score,
                ),
                factors={
                    "hook": _parse_float(
                        getattr(prediction, "hook", fallback_result.factors["hook"]),
                        fallback_result.factors["hook"],
                    ),
                    "conflict": _parse_float(
                        getattr(
                            prediction,
                            "conflict",
                            fallback_result.factors["conflict"],
                        ),
                        fallback_result.factors["conflict"],
                    ),
                    "tension": _parse_float(
                        getattr(
                            prediction,
                            "tension",
                            fallback_result.factors["tension"],
                        ),
                        fallback_result.factors["tension"],
                    ),
                    "pacing": _parse_float(
                        getattr(prediction, "pacing", fallback_result.factors["pacing"]),
                        fallback_result.factors["pacing"],
                    ),
                    "stakes": _parse_float(
                        getattr(prediction, "stakes", fallback_result.factors["stakes"]),
                        fallback_result.factors["stakes"],
                    ),
                    "payoff": _parse_float(
                        getattr(prediction, "payoff", fallback_result.factors["payoff"]),
                        fallback_result.factors["payoff"],
                    ),
                },
                rationale=str(
                    getattr(prediction, "rationale", fallback_result.rationale)
                ).strip()
                or fallback_result.rationale,
            )
        except Exception:
            return fallback_result


@dataclass(slots=True)
class DSPyRecommendationProgram(RecommendationProgram):
    fallback: RecommendationProgram

    def __init__(self, fallback: RecommendationProgram | None = None) -> None:
        self.fallback = fallback or HeuristicRecommendationProgram()
        self._predictor: Any | None = dspy.Predict(_RecommendationSignature)

    def suggest_improvements(
        self, normalized_script: NormalizedScript
    ) -> Sequence[Recommendation]:
        fallback_result = self.fallback.suggest_improvements(normalized_script)
        if self._predictor is None or not _has_live_lm():
            return fallback_result

        try:
            prediction = self._predictor(script=_build_script_text(normalized_script))
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
        except Exception:
            return fallback_result


@dataclass(slots=True)
class DSPyCliffhangerProgram(CliffhangerProgram):
    fallback: CliffhangerProgram

    def __init__(self, fallback: CliffhangerProgram | None = None) -> None:
        self.fallback = fallback or HeuristicCliffhangerProgram()
        self._predictor: Any | None = dspy.Predict(_CliffhangerSignature)

    def detect_cliffhanger(
        self, normalized_script: NormalizedScript
    ) -> CliffhangerResult:
        fallback_result = self.fallback.detect_cliffhanger(normalized_script)
        if self._predictor is None or not _has_live_lm():
            return fallback_result

        try:
            prediction = self._predictor(script=_build_script_text(normalized_script))
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
        except Exception:
            return fallback_result
