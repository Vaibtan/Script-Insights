from __future__ import annotations

from collections.abc import Callable
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.db.models import Base


_engine_cache: dict[str, Engine] = {}
_session_factory_cache: dict[str, Callable[[], Session]] = {}


def create_session_factory(database_url: str) -> Callable[[], Session]:
    cached_factory = _session_factory_cache.get(database_url)
    if cached_factory is not None:
        return cached_factory

    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    initialization_lock = Lock()
    initialized_factory: Callable[[], Session] | None = None

    def session_factory() -> Session:
        nonlocal initialized_factory
        if initialized_factory is None:
            with initialization_lock:
                if initialized_factory is None:
                    engine = create_engine(
                        database_url,
                        future=True,
                        connect_args=connect_args,
                    )
                    Base.metadata.create_all(engine)
                    initialized_factory = sessionmaker(
                        bind=engine,
                        expire_on_commit=False,
                        class_=Session,
                    )
                    _engine_cache[database_url] = engine
        return initialized_factory()

    _session_factory_cache[database_url] = session_factory
    return session_factory
