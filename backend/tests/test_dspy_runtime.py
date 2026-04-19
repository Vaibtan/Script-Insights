from dataclasses import dataclass
from types import SimpleNamespace

from app.agents.llm_gateway import LLMGateway
from app.agents.dspy_runtime import DSPyPredictionRunner
from app.agents.dspy_runtime import PredictionParser
from app.domain.normalization import NormalizedScript


@dataclass(frozen=True)
class _FallbackResult:
    text: str


class _Parser(PredictionParser[_FallbackResult]):
    def parse(
        self,
        prediction: object,
        fallback_result: _FallbackResult,
    ) -> _FallbackResult:
        return _FallbackResult(text=f"{fallback_result.text}:{getattr(prediction, 'text')}")


def _normalized_script() -> NormalizedScript:
    return NormalizedScript(scenes=(), dialogue_blocks=(), warnings=())


@dataclass
class _Gateway(LLMGateway):
    prediction: object | None = None
    calls: int = 0

    @property
    def backend_name(self) -> str:
        return "heuristic"

    @property
    def model_name(self) -> str | None:
        return None

    def has_live_inference(self) -> bool:
        return self.prediction is not None

    def predict(self, *, signature: object, inputs: dict[str, object]) -> object | None:
        _ = signature
        _ = inputs
        self.calls += 1
        return self.prediction


def test_prediction_runner_returns_fallback_without_live_lm() -> None:
    gateway = _Gateway(prediction=None)

    runner = DSPyPredictionRunner(
        signature=object(),
        fallback_executor=lambda normalized_script: _FallbackResult(text="fallback"),
        parser=_Parser(),
        gateway=gateway,
        script_renderer=lambda normalized_script: "rendered",
    )

    result = runner.run(_normalized_script())

    assert result == _FallbackResult(text="fallback")
    assert gateway.calls == 1


def test_prediction_runner_uses_parser_on_success() -> None:
    gateway = _Gateway(prediction=SimpleNamespace(text="predicted:scene text"))
    runner = DSPyPredictionRunner(
        signature=object(),
        fallback_executor=lambda normalized_script: _FallbackResult(text="fallback"),
        parser=_Parser(),
        gateway=gateway,
        script_renderer=lambda normalized_script: "scene text",
    )

    result = runner.run(_normalized_script())

    assert result == _FallbackResult(text="fallback:predicted:scene text")


def test_prediction_runner_returns_fallback_on_predictor_error() -> None:
    gateway = _Gateway(prediction=None)

    def predict(*, signature: object, inputs: dict[str, object]) -> object | None:
        _ = signature
        _ = inputs
        raise RuntimeError("boom")

    gateway.predict = predict  # type: ignore[method-assign]
    runner = DSPyPredictionRunner(
        signature=object(),
        fallback_executor=lambda normalized_script: _FallbackResult(text="fallback"),
        parser=_Parser(),
        gateway=gateway,
        script_renderer=lambda normalized_script: "scene text",
    )

    result = runner.run(_normalized_script())

    assert result == _FallbackResult(text="fallback")
