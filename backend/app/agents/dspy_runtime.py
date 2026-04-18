from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeVar

import dspy

from app.domain.normalization import NormalizedScript

ResultT = TypeVar("ResultT")


def render_script_text(normalized_script: NormalizedScript) -> str:
    return "\n".join(scene.content for scene in normalized_script.scenes)


def has_live_lm() -> bool:
    return getattr(dspy.settings, "lm", None) is not None


class PredictionParser(Protocol[ResultT]):
    def parse(self, prediction: object, fallback_result: ResultT) -> ResultT:
        ...


@dataclass(slots=True)
class DSPyPredictionRunner(Generic[ResultT]):
    signature: object
    fallback_executor: Callable[[NormalizedScript], ResultT]
    parser: PredictionParser[ResultT]
    predictor_factory: Callable[[object], Any | None] = dspy.Predict
    live_lm_checker: Callable[[], bool] = has_live_lm
    script_renderer: Callable[[NormalizedScript], str] = render_script_text
    _predictor: Any | None = field(init=False, repr=False, default=None)

    def __post_init__(self) -> None:
        try:
            self._predictor = self.predictor_factory(self.signature)
        except Exception:
            self._predictor = None

    def run(self, normalized_script: NormalizedScript) -> ResultT:
        fallback_result = self.fallback_executor(normalized_script)
        if self._predictor is None or not self.live_lm_checker():
            return fallback_result

        try:
            prediction = self._predictor(
                script=self.script_renderer(normalized_script)
            )
            return self.parser.parse(prediction, fallback_result)
        except Exception:
            return fallback_result
