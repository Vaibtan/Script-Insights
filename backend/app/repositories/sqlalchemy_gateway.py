from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AnalysisArtifactModel
from app.db.models import AnalysisRunModel
from app.db.models import NormalizedScriptModel
from app.db.models import ScriptModel
from app.db.models import ScriptRevisionModel
from app.db.models import SourceDocumentModel
from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.analysis_runs import RunStatus
from app.repositories.sqlalchemy_codecs import AnalysisArtifactCodec
from app.repositories.sqlalchemy_codecs import AnalysisRunGraphCodec
from app.repositories.sqlalchemy_codecs import SerializedAnalysisArtifact
from app.repositories.sqlalchemy_codecs import SerializedNormalizedScript


@dataclass(slots=True)
class SqlAlchemyPersistenceGateway:
    session_factory: Callable[[], Session]
    run_codec: AnalysisRunGraphCodec = field(default_factory=AnalysisRunGraphCodec)
    artifact_codec: AnalysisArtifactCodec = field(default_factory=AnalysisArtifactCodec)

    def save_run(self, run: AnalysisRunRecord) -> None:
        graph = self.run_codec.serialize(run)
        with self.session_factory() as session:
            if session.get(ScriptModel, graph.script.id) is None:
                session.add(graph.script)
            session.add(graph.revision)
            if graph.source_document is not None:
                session.add(graph.source_document)
            session.add(graph.run)
            session.commit()

    def get_run(self, run_id: UUID) -> AnalysisRunRecord | None:
        with self.session_factory() as session:
            run_model = session.get(AnalysisRunModel, str(run_id))
            if run_model is None:
                return None
            return self._hydrate_run(session, run_model)

    def update_run_status(
        self,
        run_id: UUID,
        status: RunStatus,
        failure_message: str | None = None,
    ) -> AnalysisRunRecord | None:
        with self.session_factory() as session:
            run_model = session.get(AnalysisRunModel, str(run_id))
            if run_model is None:
                return None
            run_model.status = status.value
            run_model.failure_message = failure_message
            session.commit()
            session.refresh(run_model)
            return self._hydrate_run(session, run_model)

    def list_runs_by_script(self, script_id: UUID) -> tuple[AnalysisRunRecord, ...]:
        with self.session_factory() as session:
            rows = session.scalars(
                select(AnalysisRunModel)
                .where(AnalysisRunModel.script_id == str(script_id))
                .order_by(AnalysisRunModel.created_at.desc())
            ).all()
            return tuple(self._hydrate_run(session, row) for row in rows)

    def list_queued_runs(
        self, limit: int | None = None
    ) -> tuple[AnalysisRunRecord, ...]:
        with self.session_factory() as session:
            query = (
                select(AnalysisRunModel)
                .where(AnalysisRunModel.status == RunStatus.QUEUED.value)
                .order_by(AnalysisRunModel.created_at.asc())
            )
            if limit is not None:
                query = query.limit(limit)
            rows = session.scalars(query).all()
            return tuple(self._hydrate_run(session, row) for row in rows)

    def save_artifact(self, run_id: UUID, artifact: AnalysisArtifact) -> None:
        payload = self.artifact_codec.serialize(artifact)
        with self.session_factory() as session:
            run_model = session.get(AnalysisRunModel, str(run_id))
            if run_model is None:
                raise ValueError(f"Unknown run_id {run_id}")
            self._upsert_normalized_script(
                session=session,
                revision_id=run_model.revision_id,
                payload=payload.normalized_script,
            )
            self._upsert_analysis_artifact(
                session=session,
                run_id=run_id,
                payload=payload,
            )
            session.commit()

    def get_artifact(self, run_id: UUID) -> AnalysisArtifact | None:
        with self.session_factory() as session:
            artifact_model = session.get(AnalysisArtifactModel, str(run_id))
            if artifact_model is None:
                return None

            run_model = session.get(AnalysisRunModel, str(run_id))
            if run_model is None:
                return None

            normalized_model = session.get(NormalizedScriptModel, run_model.revision_id)
            if normalized_model is None:
                return None

            return self.artifact_codec.deserialize(
                SerializedAnalysisArtifact(
                    normalized_script=SerializedNormalizedScript(
                        scenes_json=normalized_model.scenes_json,
                        dialogue_blocks_json=normalized_model.dialogue_blocks_json,
                        warnings_json=normalized_model.warnings_json,
                    ),
                    summary_json=artifact_model.summary_json,
                    emotion_json=artifact_model.emotion_json,
                    engagement_json=artifact_model.engagement_json,
                    recommendations_json=artifact_model.recommendations_json,
                    cliffhanger_json=artifact_model.cliffhanger_json,
                    warnings_json=artifact_model.warnings_json,
                )
            )

    def _hydrate_run(
        self,
        session: Session,
        run_model: AnalysisRunModel,
    ) -> AnalysisRunRecord:
        revision_model = session.get(ScriptRevisionModel, run_model.revision_id)
        if revision_model is None:
            raise ValueError(f"Missing script revision for run {run_model.run_id}")
        source_document_model = session.get(SourceDocumentModel, run_model.revision_id)
        return self.run_codec.deserialize(
            run_model,
            revision_model,
            source_document_model,
        )

    def _upsert_normalized_script(
        self,
        *,
        session: Session,
        revision_id: str,
        payload: SerializedNormalizedScript,
    ) -> None:
        normalized_model = session.get(NormalizedScriptModel, revision_id)
        if normalized_model is None:
            session.add(
                NormalizedScriptModel(
                    revision_id=revision_id,
                    scenes_json=payload.scenes_json,
                    dialogue_blocks_json=payload.dialogue_blocks_json,
                    warnings_json=payload.warnings_json,
                    created_at=datetime.now(timezone.utc),
                )
            )
            return

        normalized_model.scenes_json = payload.scenes_json
        normalized_model.dialogue_blocks_json = payload.dialogue_blocks_json
        normalized_model.warnings_json = payload.warnings_json

    def _upsert_analysis_artifact(
        self,
        *,
        session: Session,
        run_id: UUID,
        payload: SerializedAnalysisArtifact,
    ) -> None:
        artifact_model = session.get(AnalysisArtifactModel, str(run_id))
        if artifact_model is None:
            session.add(
                AnalysisArtifactModel(
                    run_id=str(run_id),
                    summary_json=payload.summary_json,
                    emotion_json=payload.emotion_json,
                    engagement_json=payload.engagement_json,
                    recommendations_json=payload.recommendations_json,
                    cliffhanger_json=payload.cliffhanger_json,
                    warnings_json=payload.warnings_json,
                )
            )
            return

        artifact_model.summary_json = payload.summary_json
        artifact_model.emotion_json = payload.emotion_json
        artifact_model.engagement_json = payload.engagement_json
        artifact_model.recommendations_json = payload.recommendations_json
        artifact_model.cliffhanger_json = payload.cliffhanger_json
        artifact_model.warnings_json = payload.warnings_json
