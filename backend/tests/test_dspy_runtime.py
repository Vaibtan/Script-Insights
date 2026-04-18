from dataclasses import dataclass
from types import SimpleNamespace

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


def test_prediction_runner_returns_fallback_without_live_lm() -> None:
    predictor_calls = 0

    def predictor_factory(signature: object) -> object:
        _ = signature

        def predictor(*, script: str) -> object:
            nonlocal predictor_calls
            predictor_calls += 1
            _ = script
            return SimpleNamespace(text="predicted")

        return predictor

    runner = DSPyPredictionRunner(
        signature=object(),
        fallback_executor=lambda normalized_script: _FallbackResult(text="fallback"),
        parser=_Parser(),
        predictor_factory=predictor_factory,
        live_lm_checker=lambda: False,
        script_renderer=lambda normalized_script: "rendered",
    )

    result = runner.run(_normalized_script())

    assert result == _FallbackResult(text="fallback")
    assert predictor_calls == 0


def test_prediction_runner_uses_parser_on_success() -> None:
    runner = DSPyPredictionRunner(
        signature=object(),
        fallback_executor=lambda normalized_script: _FallbackResult(text="fallback"),
        parser=_Parser(),
        predictor_factory=lambda signature: (
            lambda *, script: SimpleNamespace(text=f"predicted:{script}")
        ),
        live_lm_checker=lambda: True,
        script_renderer=lambda normalized_script: "scene text",
    )

    result = runner.run(_normalized_script())

    assert result == _FallbackResult(text="fallback:predicted:scene text")


def test_prediction_runner_returns_fallback_on_predictor_error() -> None:
    runner = DSPyPredictionRunner(
        signature=object(),
        fallback_executor=lambda normalized_script: _FallbackResult(text="fallback"),
        parser=_Parser(),
        predictor_factory=lambda signature: (
            lambda *, script: (_ for _ in ()).throw(RuntimeError("boom"))
        ),
        live_lm_checker=lambda: True,
        script_renderer=lambda normalized_script: "scene text",
    )

    result = runner.run(_normalized_script())

    assert result == _FallbackResult(text="fallback")
