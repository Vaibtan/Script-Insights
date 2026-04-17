from pathlib import Path
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.main import create_app


@pytest.fixture()
def app() -> FastAPI:
    return create_app()


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)
