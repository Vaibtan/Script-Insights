from dataclasses import dataclass
from typing import Protocol

from app.agents.dspy_programs import DSPyCliffhangerProgram
from app.agents.dspy_programs import DSPyEngagementProgram
from app.agents.dspy_programs import DSPyEmotionProgram
from app.agents.dspy_programs import DSPyRecommendationProgram
from app.agents.dspy_programs import DSPySummaryProgram
from app.agents.protocols import CliffhangerProgram
from app.agents.protocols import EngagementProgram
from app.agents.protocols import EmotionProgram
from app.agents.protocols import RecommendationProgram
from app.agents.protocols import SummaryProgram


class ProgramRegistry(Protocol):
    def create_summary_program(self) -> SummaryProgram:
        ...

    def create_emotion_program(self) -> EmotionProgram:
        ...

    def create_engagement_program(self) -> EngagementProgram:
        ...

    def create_recommendation_program(self) -> RecommendationProgram:
        ...

    def create_cliffhanger_program(self) -> CliffhangerProgram:
        ...


@dataclass(slots=True)
class DSPyProgramRegistry(ProgramRegistry):
    def create_summary_program(self) -> SummaryProgram:
        return DSPySummaryProgram()

    def create_emotion_program(self) -> EmotionProgram:
        return DSPyEmotionProgram()

    def create_engagement_program(self) -> EngagementProgram:
        return DSPyEngagementProgram()

    def create_recommendation_program(self) -> RecommendationProgram:
        return DSPyRecommendationProgram()

    def create_cliffhanger_program(self) -> CliffhangerProgram:
        return DSPyCliffhangerProgram()
