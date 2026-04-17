from dataclasses import dataclass
from typing import Protocol

from app.agents.dspy_programs import DSPyEmotionProgram
from app.agents.dspy_programs import DSPySummaryProgram
from app.agents.protocols import EmotionProgram
from app.agents.protocols import SummaryProgram


class ProgramRegistry(Protocol):
    def create_summary_program(self) -> SummaryProgram:
        ...

    def create_emotion_program(self) -> EmotionProgram:
        ...


@dataclass(slots=True)
class DSPyProgramRegistry(ProgramRegistry):
    def create_summary_program(self) -> SummaryProgram:
        return DSPySummaryProgram()

    def create_emotion_program(self) -> EmotionProgram:
        return DSPyEmotionProgram()
