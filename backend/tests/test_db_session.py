from pathlib import Path

from sqlalchemy import text

from app.db.session import create_session_factory


def test_create_session_factory_is_lazy_for_sqlite_files(tmp_path: Path) -> None:
    database_path = tmp_path / "lazy-session.db"

    session_factory = create_session_factory(f"sqlite:///{database_path}")

    assert not database_path.exists()

    with session_factory() as session:
        session.execute(text("SELECT 1"))

    assert database_path.exists()
