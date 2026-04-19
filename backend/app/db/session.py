from __future__ import annotations

from collections.abc import Callable
from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.db.models import Base


_engine_cache: dict[str, Engine] = {}
_session_factory_cache: dict[str, Callable[[], Session]] = {}


def _apply_runtime_schema_upgrades(engine: Engine) -> None:
    inspector = inspect(engine)
    if "analysis_runs" not in inspector.get_table_names():
        return

    analysis_run_columns = {
        column["name"] for column in inspector.get_columns("analysis_runs")
    }
    if "execution_fingerprint" not in analysis_run_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE analysis_runs "
                    "ADD COLUMN execution_fingerprint VARCHAR(64) NOT NULL DEFAULT ''"
                )
            )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS "
                    "ix_analysis_runs_execution_fingerprint "
                    "ON analysis_runs (execution_fingerprint)"
                )
            )
    if "normalized_content_fingerprint" not in analysis_run_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE analysis_runs "
                    "ADD COLUMN normalized_content_fingerprint VARCHAR(64)"
                )
            )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS "
                    "ix_analysis_runs_normalized_content_fingerprint "
                    "ON analysis_runs (normalized_content_fingerprint)"
                )
            )
    if "reused_from_run_id" not in analysis_run_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE analysis_runs "
                    "ADD COLUMN reused_from_run_id VARCHAR(36)"
                )
            )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS "
                    "ix_analysis_runs_reused_from_run_id "
                    "ON analysis_runs (reused_from_run_id)"
                )
            )
    if "normalized_candidate_run_id" not in analysis_run_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE analysis_runs "
                    "ADD COLUMN normalized_candidate_run_id VARCHAR(36)"
                )
            )
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS "
                    "ix_analysis_runs_normalized_candidate_run_id "
                    "ON analysis_runs (normalized_candidate_run_id)"
                )
            )

    if "analysis_artifacts" in inspector.get_table_names():
        artifact_columns = {
            column["name"] for column in inspector.get_columns("analysis_artifacts")
        }
        if "critic_json" not in artifact_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE analysis_artifacts "
                        "ADD COLUMN critic_json JSON"
                    )
                )


def create_session_factory(database_url: str) -> Callable[[], Session]:
    cached_factory = _session_factory_cache.get(database_url)
    if cached_factory is not None: return cached_factory
    connect_args: dict[str, object] = {}
    if database_url.startswith("sqlite"): connect_args["check_same_thread"] = False
    initialization_lock = Lock()
    initialized_factory: Callable[[], Session] | None = None

    def session_factory() -> Session:
        nonlocal initialized_factory
        if initialized_factory is None:
            with initialization_lock:
                if initialized_factory is None:
                    engine = create_engine(database_url, future = True, connect_args = connect_args)
                    Base.metadata.create_all(engine)
                    _apply_runtime_schema_upgrades(engine)
                    initialized_factory = sessionmaker(bind = engine, expire_on_commit = False, class_ = Session)
                    _engine_cache[database_url] = engine
        return initialized_factory()

    _session_factory_cache[database_url] = session_factory
    return session_factory
