from __future__ import annotations

import logging

import dspy

from app.core.settings import Settings


def configure_dspy_for_settings(settings: Settings) -> None:
    if not settings.groq_api_key:
        return

    current_lm = getattr(dspy.settings, "lm", None)
    if current_lm is not None:
        return

    logger = logging.getLogger("app.agents.dspy")
    try:
        lm = dspy.LM(settings.groq_model, api_key=settings.groq_api_key)
        dspy.configure(lm=lm)
        logger.info("dspy_lm_configured", extra={"model": settings.groq_model})
    except Exception:
        logger.exception(
            "dspy_lm_configuration_failed",
            extra={"model": settings.groq_model},
        )
