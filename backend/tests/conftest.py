from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.settings import reset_settings_cache


@pytest.fixture()
def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    from app.main import create_app

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("EXECUTION_MODE", "inline")
    monkeypatch.setenv("GROQ_API_KEY", "")
    reset_settings_cache()
    return create_app()


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "")
    if "dspy" in sys.modules:
        sys.modules["dspy"].settings.configure(lm=None)
    reset_settings_cache()
    yield
    if "dspy" in sys.modules:
        sys.modules["dspy"].settings.configure(lm=None)
    reset_settings_cache()
