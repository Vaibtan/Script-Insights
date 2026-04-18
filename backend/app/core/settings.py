from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import NoDecode
from pydantic_settings import SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = BACKEND_ROOT / ".env"


class Settings(BaseSettings):
    app_name: str = "Script Insights API"
    api_v1_prefix: str = "/api/v1"
    result_version: str = "v1"
    execution_mode: Literal["inline", "queued"] = "inline"
    database_url: str = "sqlite:///./script_insights.db"
    groq_api_key: str | None = None
    groq_model: str = "groq/llama-3.3-70b-versatile"
    cors_origins: Annotated[tuple[str, ...], NoDecode] = ("http://localhost:3000",)

    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(
        cls,
        value: object,
    ) -> tuple[str, ...] | object:
        if value is None:
            return ("http://localhost:3000",)
        if isinstance(value, str):
            parsed = tuple(origin.strip() for origin in value.split(",") if origin.strip())
            return parsed or ("http://localhost:3000",)
        if isinstance(value, (list, tuple)):
            parsed = tuple(str(origin).strip() for origin in value if str(origin).strip())
            return parsed or ("http://localhost:3000",)
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
