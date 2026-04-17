from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class ScriptModel(Base):
    __tablename__ = "scripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ScriptRevisionModel(Base):
    __tablename__ = "script_revisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    script_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scripts.id"), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(16), nullable=False)
    script_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_warnings_json: Mapped[list[dict[str, str]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SourceDocumentModel(Base):
    __tablename__ = "source_documents"

    revision_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("script_revisions.id"), primary_key=True
    )
    filename: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    extraction_warnings_json: Mapped[list[dict[str, str]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AnalysisRunModel(Base):
    __tablename__ = "analysis_runs"

    run_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    script_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("scripts.id"), nullable=False, index=True
    )
    revision_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("script_revisions.id"), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    script_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    failure_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class NormalizedScriptModel(Base):
    __tablename__ = "normalized_scripts"

    revision_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("script_revisions.id"), primary_key=True
    )
    scenes_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    dialogue_blocks_json: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    warnings_json: Mapped[list[dict[str, str]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AnalysisArtifactModel(Base):
    __tablename__ = "analysis_artifacts"

    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analysis_runs.run_id"), primary_key=True
    )
    summary_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    emotion_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    engagement_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    recommendations_json: Mapped[list[dict[str, str]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    cliffhanger_json: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    warnings_json: Mapped[list[dict[str, str]]] = mapped_column(
        JSON, nullable=False, default=list
    )
