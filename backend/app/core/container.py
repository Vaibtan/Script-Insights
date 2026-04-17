from dataclasses import dataclass

from app.agents.registry import DSPyProgramRegistry
from app.agents.registry import ProgramRegistry
from app.core.settings import Settings
from app.core.settings import get_settings
from app.repositories.analysis_artifacts import AnalysisArtifactRepository
from app.repositories.analysis_runs import AnalysisRunRepository
from app.repositories.in_memory import InMemoryAnalysisArtifactRepository
from app.repositories.in_memory import InMemoryAnalysisRunRepository
from app.services.dispatchers import InlineAnalysisDispatcher
from app.services.normalization import ScriptNormalizer
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
    run_submission_service: RunSubmissionService
    run_query_service: RunQueryService


def build_container(
    *,
    settings: Settings | None = None,
    run_repository: AnalysisRunRepository | None = None,
    artifact_repository: AnalysisArtifactRepository | None = None,
    program_registry: ProgramRegistry | None = None,
    workflow: AnalysisWorkflowExecutor | None = None,
) -> AppContainer:
    resolved_settings = settings or get_settings()
    resolved_run_repository = run_repository or InMemoryAnalysisRunRepository()
    resolved_artifact_repository = (
        artifact_repository or InMemoryAnalysisArtifactRepository()
    )

    if workflow is None:
        resolved_program_registry = program_registry or DSPyProgramRegistry()
        workflow = AnalysisWorkflow(
            normalizer=ScriptNormalizer(),
            summary_program=resolved_program_registry.create_summary_program(),
            emotion_program=resolved_program_registry.create_emotion_program(),
        )

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
    run_query_service = RunQueryService(
        run_repository=resolved_run_repository,
        artifact_repository=resolved_artifact_repository,
        settings=resolved_settings,
    )

    return AppContainer(
        settings=resolved_settings,
        run_repository=resolved_run_repository,
        artifact_repository=resolved_artifact_repository,
        workflow=workflow,
        run_submission_service=run_submission_service,
        run_query_service=run_query_service,
    )
