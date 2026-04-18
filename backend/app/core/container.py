from dataclasses import dataclass

from app.db.session import create_session_factory
from app.agents.dspy_config import configure_dspy_for_settings
from app.agents.registry import DSPyProgramRegistry
from app.agents.registry import ProgramRegistry
from app.core.settings import Settings
from app.core.settings import get_settings
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository
from app.repositories.sqlalchemy import SqlAlchemyAnalysisArtifactRepository
from app.repositories.sqlalchemy import SqlAlchemyAnalysisRunRepository
from app.repositories.sqlalchemy_gateway import SqlAlchemyPersistenceGateway
from app.evaluation.evaluator import AnalysisEvaluator
from app.services.dispatchers import InlineAnalysisDispatcher
from app.services.dispatchers import QueuedAnalysisDispatcher
from app.services.normalization import ScriptNormalizer
from app.services.pdf_extraction import PdfTextExtractor
from app.services.queue import RepositoryBackedRunQueue
from app.services.queue import RunQueue
from app.services.queue import RunQueueProcessor
from app.services.revision_compare import RevisionComparisonService
from app.services.run_history import RunHistoryService
from app.services.run_query import RunQueryService
from app.services.run_submission import RunSubmissionService
from app.services.workflow import AnalysisWorkflow
from app.services.workflow import AnalysisWorkflowExecutor


@dataclass(slots=True)
class AppContainer:
    settings: Settings
    run_repository: AnalysisRunRepository
    artifact_repository: AnalysisArtifactRepository
    workflow: AnalysisWorkflowExecutor
    run_queue: RunQueue
    run_queue_processor: RunQueueProcessor
    pdf_text_extractor: PdfTextExtractor
    run_submission_service: RunSubmissionService
    run_query_service: RunQueryService
    run_history_service: RunHistoryService
    revision_comparison_service: RevisionComparisonService


def build_container(
    *,
    settings: Settings | None = None,
    run_repository: AnalysisRunRepository | None = None,
    artifact_repository: AnalysisArtifactRepository | None = None,
    program_registry: ProgramRegistry | None = None,
    workflow: AnalysisWorkflowExecutor | None = None,
) -> AppContainer:
    resolved_settings = settings or get_settings()
    configure_dspy_for_settings(resolved_settings)
    sqlalchemy_gateway = (
        SqlAlchemyPersistenceGateway(
            create_session_factory(resolved_settings.database_url)
        )
        if run_repository is None or artifact_repository is None
        else None
    )

    if run_repository is None:
        if sqlalchemy_gateway is None:
            raise ValueError("sqlalchemy_gateway is required for default run repository")
        resolved_run_repository = SqlAlchemyAnalysisRunRepository(
            gateway=sqlalchemy_gateway
        )
    else:
        resolved_run_repository = run_repository

    if artifact_repository is None:
        if sqlalchemy_gateway is None:
            raise ValueError(
                "sqlalchemy_gateway is required for default artifact repository"
            )
        resolved_artifact_repository = SqlAlchemyAnalysisArtifactRepository(
            gateway=sqlalchemy_gateway
        )
    else:
        resolved_artifact_repository = artifact_repository

    if workflow is None:
        resolved_program_registry = program_registry or DSPyProgramRegistry()
        workflow = AnalysisWorkflow(
            normalizer=ScriptNormalizer(),
            summary_program=resolved_program_registry.create_summary_program(),
            emotion_program=resolved_program_registry.create_emotion_program(),
            engagement_program=resolved_program_registry.create_engagement_program(),
            recommendation_program=resolved_program_registry.create_recommendation_program(),
            cliffhanger_program=resolved_program_registry.create_cliffhanger_program(),
            evaluator=AnalysisEvaluator(),
        )

    run_queue = RepositoryBackedRunQueue(run_repository=resolved_run_repository)
    run_queue_processor = RunQueueProcessor(
        queue=run_queue,
        workflow=workflow,
        run_repository=resolved_run_repository,
        artifact_repository=resolved_artifact_repository,
    )
    if resolved_settings.execution_mode == "queued":
        dispatcher = QueuedAnalysisDispatcher(queue=run_queue)
    else:
        dispatcher = InlineAnalysisDispatcher(
            workflow=workflow,
            run_repository=resolved_run_repository,
            artifact_repository=resolved_artifact_repository,
        )
    run_submission_service = RunSubmissionService(
        repository=resolved_run_repository,
        dispatcher=dispatcher,
        settings=resolved_settings,
    )
    pdf_text_extractor = PdfTextExtractor()
    run_query_service = RunQueryService(
        run_repository=resolved_run_repository,
        artifact_repository=resolved_artifact_repository,
        settings=resolved_settings,
    )
    run_history_service = RunHistoryService(
        run_repository=resolved_run_repository,
        settings=resolved_settings,
    )
    revision_comparison_service = RevisionComparisonService(
        run_repository=resolved_run_repository,
        artifact_repository=resolved_artifact_repository,
        settings=resolved_settings,
    )

    return AppContainer(
        settings=resolved_settings,
        run_repository=resolved_run_repository,
        artifact_repository=resolved_artifact_repository,
        workflow=workflow,
        run_queue=run_queue,
        run_queue_processor=run_queue_processor,
        pdf_text_extractor=pdf_text_extractor,
        run_submission_service=run_submission_service,
        run_query_service=run_query_service,
        run_history_service=run_history_service,
        revision_comparison_service=revision_comparison_service,
    )
