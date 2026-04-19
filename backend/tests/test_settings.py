from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.settings import Settings


_SETTINGS_ENV_KEYS = (
    "APP_NAME",
    "API_V1_PREFIX",
    "RESULT_VERSION",
    "ANALYSIS_FINGERPRINT_VERSION",
    "EXECUTION_MODE",
    "DATABASE_URL",
    "CORS_ORIGINS",
    "GROQ_API_KEY",
    "GROQ_MODEL",
)


def _clear_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _SETTINGS_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_settings_load_from_env_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_settings_env(monkeypatch)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "APP_NAME=Script Insights Test API",
                "API_V1_PREFIX=/api/test",
                "RESULT_VERSION=v2",
                "ANALYSIS_FINGERPRINT_VERSION=v7",
                "NORMALIZED_FINGERPRINT_VERSION=v9",
                "EXECUTION_MODE=queued",
                "DATABASE_URL=sqlite:///./custom.db",
                "CORS_ORIGINS=http://localhost:3000,http://localhost:3001",
                "GROQ_API_KEY=test-key",
                "GROQ_MODEL=groq/test-model",
            ]
        ),
        encoding="utf-8",
    )

    settings = Settings(_env_file=env_file)

    assert settings.app_name == "Script Insights Test API"
    assert settings.api_v1_prefix == "/api/test"
    assert settings.result_version == "v2"
    assert settings.analysis_fingerprint_version == "v7"
    assert settings.normalized_fingerprint_version == "v9"
    assert settings.execution_mode == "queued"
    assert settings.database_url == "sqlite:///./custom.db"
    assert settings.cors_origins == (
        "http://localhost:3000",
        "http://localhost:3001",
    )
    assert settings.groq_api_key == "test-key"
    assert settings.groq_model == "groq/test-model"


def test_settings_reject_invalid_execution_mode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_settings_env(monkeypatch)
    env_file = tmp_path / ".env"
    env_file.write_text("EXECUTION_MODE=invalid\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        Settings(_env_file=env_file)
