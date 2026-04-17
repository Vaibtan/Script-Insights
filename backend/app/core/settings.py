from dataclasses import dataclass
import os
from typing import Literal


@dataclass(frozen=True)
class Settings:
    app_name: str = "Script Insights API"
    api_v1_prefix: str = "/api/v1"
    result_version: str = "v1"
    execution_mode: Literal["inline", "queued"] = "inline"
    database_url: str = "sqlite:///./script_insights.db"
    groq_api_key: str | None = None
    groq_model: str = "groq/llama-3.3-70b-versatile"
    cors_origins: tuple[str, ...] = ("http://localhost:3000",)


def get_settings() -> Settings:
    raw_execution_mode = os.getenv("EXECUTION_MODE", "inline").strip().lower()
    execution_mode: Literal["inline", "queued"] = (
        "queued" if raw_execution_mode == "queued" else "inline"
    )
    return Settings(
        app_name=os.getenv("APP_NAME", "Script Insights API"),
        api_v1_prefix=os.getenv("API_V1_PREFIX", "/api/v1"),
        result_version=os.getenv("RESULT_VERSION", "v1"),
        execution_mode=execution_mode,
        database_url=os.getenv("DATABASE_URL", "sqlite:///./script_insights.db"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        groq_model=os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile"),
        cors_origins=tuple(
            origin.strip()
            for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
            if origin.strip()
        ),
    )
