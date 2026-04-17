from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Settings:
    app_name: str = "Script Insights API"
    api_v1_prefix: str = "/api/v1"
    result_version: str = "v1"
    execution_mode: Literal["inline", "queued"] = "inline"


def get_settings() -> Settings:
    return Settings()
