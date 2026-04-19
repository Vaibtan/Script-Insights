from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic
from typing import Protocol
from typing import TypeVar

from app.agents.llm_gateway import LLMGateway
from app.domain.normalization import NormalizedScript

ResultT = TypeVar("ResultT")


def render_script_text(normalized_script: NormalizedScript) -> str:
    return "\n".join(scene.content for scene in normalized_script.scenes)


class PredictionParser(Protocol[ResultT]):
    def parse(self, prediction: object, fallback_result: ResultT) -> ResultT:
        ...


@dataclass(slots=True)
class DSPyPredictionRunner(Generic[ResultT]):
    signature: object
    fallback_executor: Callable[[NormalizedScript], ResultT]
    parser: PredictionParser[ResultT]
    gateway: LLMGateway
    script_renderer: Callable[[NormalizedScript], str] = render_script_text

    def run(self, normalized_script: NormalizedScript) -> ResultT:
        fallback_result = self.fallback_executor(normalized_script)
        try:
            prediction = self.gateway.predict(
                signature=self.signature,
                inputs={"script": self.script_renderer(normalized_script)},
            )
        except Exception:
            return fallback_result
        if prediction is None:
            return fallback_result

        try:
            return self.parser.parse(prediction, fallback_result)
        except Exception:
            return fallback_result
