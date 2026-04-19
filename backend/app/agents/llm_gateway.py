from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field
import logging
from typing import Any

import dspy

from app.core.settings import Settings

_configured_identity: tuple[str, str | None] | None = None


def reset_llm_gateway_state() -> None:
    global _configured_identity
    _configured_identity = None


@dataclass(frozen=True, slots=True)
class LLMGatewayIdentity:
    backend: str
    model: str | None


class LLMGateway:
    @property
    def backend_name(self) -> str:
        raise NotImplementedError

    @property
    def model_name(self) -> str | None:
        raise NotImplementedError

    def has_live_inference(self) -> bool:
        raise NotImplementedError

    def predict(
        self,
        *,
        signature: object,
        inputs: Mapping[str, object],
    ) -> object | None:
        raise NotImplementedError

    def identity(self) -> LLMGatewayIdentity:
        return LLMGatewayIdentity(
            backend=self.backend_name,
            model=self.model_name,
        )


@dataclass(slots=True)
class DSPyLLMGateway(LLMGateway):
    settings: Settings
    predictor_factory: Any = dspy.Predict
    lm_factory: Any = dspy.LM
    configure_callback: Any = dspy.configure
    _predictors: dict[object, Any] = field(default_factory=dict, init=False, repr=False)

    @property
    def backend_name(self) -> str:
        return "groq" if self.settings.groq_api_key else "heuristic"

    @property
    def model_name(self) -> str | None:
        return self.settings.groq_model if self.settings.groq_api_key else None

    def has_live_inference(self) -> bool:
        global _configured_identity

        if not self.settings.groq_api_key:
            return False

        desired_identity = (self.backend_name, self.model_name)
        current_lm = getattr(dspy.settings, "lm", None)
        if current_lm is not None and _configured_identity == desired_identity:
            return True

        logger = logging.getLogger("app.agents.llm_gateway")
        try:
            lm = self.lm_factory(self.settings.groq_model, api_key=self.settings.groq_api_key)
            self.configure_callback(lm=lm)
            self._predictors.clear()
            _configured_identity = desired_identity
            logger.info("llm_gateway_configured", extra={"model": self.settings.groq_model})
            return True
        except Exception:
            logger.exception(
                "llm_gateway_configuration_failed",
                extra={"model": self.settings.groq_model},
            )
            return False

    def predict(
        self,
        *,
        signature: object,
        inputs: Mapping[str, object],
    ) -> object | None:
        if not self.has_live_inference():
            return None

        predictor = self._predictors.get(signature)
        if predictor is None:
            try:
                predictor = self.predictor_factory(signature)
            except Exception:
                return None
            self._predictors[signature] = predictor

        try:
            return predictor(**dict(inputs))
        except Exception:
            return None
