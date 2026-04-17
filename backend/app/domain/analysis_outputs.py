from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceSpan:
    start_offset: int
    end_offset: int
    text: str


@dataclass(frozen=True)
class SummaryResult:
    text: str
    evidence_spans: tuple[EvidenceSpan, ...]


@dataclass(frozen=True)
class EmotionArcPoint:
    beat_index: int
    emotion: str
    valence: float
    arousal: float


@dataclass(frozen=True)
class EmotionResult:
    dominant_emotions: tuple[str, ...]
    valence: float
    arousal: float
    emotional_arc: tuple[EmotionArcPoint, ...]
    evidence_spans: tuple[EvidenceSpan, ...]


@dataclass(frozen=True)
class EngagementResult:
    overall_score: float
    factors: dict[str, float]
    rationale: str


@dataclass(frozen=True)
class Recommendation:
    category: str
    suggestion: str
    rationale: str


@dataclass(frozen=True)
class CliffhangerResult:
    moment_text: str
    why_it_works: str
    evidence_spans: tuple[EvidenceSpan, ...]
