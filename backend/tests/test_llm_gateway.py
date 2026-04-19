from types import SimpleNamespace

from app.agents.llm_gateway import DSPyLLMGateway
from app.agents.llm_gateway import reset_llm_gateway_state
from app.core.settings import get_settings


def test_llm_gateway_reports_heuristic_mode_without_api_key() -> None:
    reset_llm_gateway_state()
    gateway = DSPyLLMGateway(
        get_settings().model_copy(update={"groq_api_key": None})
    )

    assert gateway.backend_name == "heuristic"
    assert gateway.model_name is None
    assert gateway.has_live_inference() is False
    assert gateway.predict(signature=object(), inputs={"script": "scene"}) is None


def test_llm_gateway_uses_predictor_when_live_inference_is_available() -> None:
    reset_llm_gateway_state()
    configured: dict[str, object] = {}

    gateway = DSPyLLMGateway(
        get_settings().model_copy(
            update={
                "groq_api_key": "test-key",
                "groq_model": "groq/test-model",
            }
        ),
        predictor_factory=lambda signature: (
            lambda **inputs: SimpleNamespace(signature=signature, inputs=inputs)
        ),
        lm_factory=lambda model, api_key: {"model": model, "api_key": api_key},
        configure_callback=lambda **kwargs: configured.update(kwargs),
    )

    prediction = gateway.predict(
        signature="sig",
        inputs={"script": "scene text"},
    )

    assert gateway.backend_name == "groq"
    assert gateway.model_name == "groq/test-model"
    assert configured["lm"] == {
        "model": "groq/test-model",
        "api_key": "test-key",
    }
    assert prediction == SimpleNamespace(
        signature="sig",
        inputs={"script": "scene text"},
    )


def test_llm_gateway_reconfigures_when_model_identity_changes() -> None:
    reset_llm_gateway_state()
    configured: list[dict[str, object]] = []

    def configure_callback(**kwargs: object) -> None:
        configured.append(dict(kwargs))

    first_gateway = DSPyLLMGateway(
        get_settings().model_copy(
            update={
                "groq_api_key": "test-key",
                "groq_model": "groq/model-a",
            }
        ),
        predictor_factory=lambda signature: (lambda **inputs: (signature, inputs)),
        lm_factory=lambda model, api_key: {"model": model, "api_key": api_key},
        configure_callback=configure_callback,
    )
    second_gateway = DSPyLLMGateway(
        get_settings().model_copy(
            update={
                "groq_api_key": "test-key",
                "groq_model": "groq/model-b",
            }
        ),
        predictor_factory=lambda signature: (lambda **inputs: (signature, inputs)),
        lm_factory=lambda model, api_key: {"model": model, "api_key": api_key},
        configure_callback=configure_callback,
    )

    first_gateway.predict(signature="sig-a", inputs={"script": "scene a"})
    second_gateway.predict(signature="sig-b", inputs={"script": "scene b"})

    assert configured == [
        {"lm": {"model": "groq/model-a", "api_key": "test-key"}},
        {"lm": {"model": "groq/model-b", "api_key": "test-key"}},
    ]
