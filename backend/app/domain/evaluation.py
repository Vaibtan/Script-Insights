from dataclasses import dataclass


@dataclass(frozen=True)
class AnalysisWarning:
    code: str
    message: str
    component: str


@dataclass(frozen=True)
class CriticIssue:
    code: str
    message: str
    component: str


@dataclass(frozen=True)
class CriticAssessment:
    score: float
    summary: str
    issues: tuple[CriticIssue, ...] = ()
