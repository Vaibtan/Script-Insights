from dataclasses import dataclass

from app.agents.llm_gateway import LLMGateway
from app.core.settings import get_settings
from app.services.fingerprints import ExecutionFingerprintService


@dataclass(frozen=True)
class _Gateway(LLMGateway):
    backend_name_value: str
    model_name_value: str | None

    @property
    def backend_name(self) -> str:
        return self.backend_name_value

    @property
    def model_name(self) -> str | None:
        return self.model_name_value

    def has_live_inference(self) -> bool:
        return self.backend_name_value != "heuristic"

    def predict(self, *, signature: object, inputs: dict[str, object]) -> object | None:
        _ = signature
        _ = inputs
        return None


def test_heuristic_fingerprint_does_not_change_when_only_groq_model_changes() -> None:
    base_settings = get_settings().model_copy(
        update={
            "groq_api_key": None,
            "groq_model": "groq/model-a",
        }
    )
    variant_settings = base_settings.model_copy(
        update={"groq_model": "groq/model-b"}
    )

    base_service = ExecutionFingerprintService(
        llm_gateway=_Gateway(backend_name_value="heuristic", model_name_value=None),
        settings=base_settings,
    )
    variant_service = ExecutionFingerprintService(
        llm_gateway=_Gateway(backend_name_value="heuristic", model_name_value=None),
        settings=variant_settings,
    )

    base_fingerprint = base_service.compute(
        script_text="Scene: Stable\nA: Same execution.\nB: Same result.",
        source_warnings=(),
    )
    variant_fingerprint = variant_service.compute(
        script_text="Scene: Stable\nA: Same execution.\nB: Same result.",
        source_warnings=(),
    )

    assert base_fingerprint == variant_fingerprint
