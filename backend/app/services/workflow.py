from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from time import perf_counter
from collections.abc import Callable
from typing import Protocol
from typing import TypeVar

from app.agents.llm_gateway import LLMGateway
from app.agents.protocols import CliffhangerProgram
from app.agents.protocols import EngagementProgram
from app.agents.protocols import EmotionProgram
from app.agents.protocols import RecommendationProgram
from app.agents.protocols import SummaryProgram
from app.domain.agent_runs import AgentRunRecord
from app.domain.agent_runs import AgentRunStatus
from app.domain.analysis_artifacts import AnalysisArtifact
from app.domain.analysis_runs import AnalysisRunRecord
from app.domain.evaluation import AnalysisWarning
from app.domain.normalization import NormalizedScript
from app.evaluation.evaluator import AnalysisEvaluator
from app.services.normalization import ScriptNormalizer

AgentResultT = TypeVar("AgentResultT")


class AnalysisWorkflowExecutor(Protocol):
    def execute(self, run: AnalysisRunRecord) -> AnalysisArtifact:
        ...


@dataclass(slots=True)
class AnalysisWorkflow:
    normalizer: ScriptNormalizer
    llm_gateway: LLMGateway
    summary_program: SummaryProgram | None = None
    emotion_program: EmotionProgram | None = None
    engagement_program: EngagementProgram | None = None
    recommendation_program: RecommendationProgram | None = None
    cliffhanger_program: CliffhangerProgram | None = None
    evaluator: AnalysisEvaluator | None = None

    def execute(self, run: AnalysisRunRecord) -> AnalysisArtifact:
        agent_runs: list[AgentRunRecord] = []
        workflow_warnings: list[AnalysisWarning] = []
        normalized_script = self.normalizer.normalize(run.script_text)
        if run.source_warnings:
            normalized_script = NormalizedScript(
                scenes=normalized_script.scenes,
                dialogue_blocks=normalized_script.dialogue_blocks,
                warnings=normalized_script.warnings + run.source_warnings,
            )
        summary = (
            self._execute_agent(
                agent_name="summary",
                normalized_script=normalized_script,
                agent_runs=agent_runs,
                workflow_warnings=workflow_warnings,
                executor=self.summary_program.summarize,
                failure_result=None,
            )
            if self.summary_program is not None
            else None
        )
        emotion = (
            self._execute_agent(
                agent_name="emotion",
                normalized_script=normalized_script,
                agent_runs=agent_runs,
                workflow_warnings=workflow_warnings,
                executor=self.emotion_program.analyze_emotion,
                failure_result=None,
            )
            if self.emotion_program is not None
            else None
        )
        engagement = (
            self._execute_agent(
                agent_name="engagement",
                normalized_script=normalized_script,
                agent_runs=agent_runs,
                workflow_warnings=workflow_warnings,
                executor=self.engagement_program.score_engagement,
                failure_result=None,
            )
            if self.engagement_program is not None
            else None
        )
        recommendations = (
            tuple(
                self._execute_agent(
                    agent_name="recommendations",
                    normalized_script=normalized_script,
                    agent_runs=agent_runs,
                    workflow_warnings=workflow_warnings,
                    executor=self.recommendation_program.suggest_improvements,
                    failure_result=(),
                )
            )
            if self.recommendation_program is not None
            else ()
        )
        cliffhanger = (
            self._execute_agent(
                agent_name="cliffhanger",
                normalized_script=normalized_script,
                agent_runs=agent_runs,
                workflow_warnings=workflow_warnings,
                executor=self.cliffhanger_program.detect_cliffhanger,
                failure_result=None,
            )
            if self.cliffhanger_program is not None
            else None
        )
        artifact = AnalysisArtifact(
            normalized_script=normalized_script,
            summary=summary,
            emotion=emotion,
            engagement=engagement,
            recommendations=recommendations,
            cliffhanger=cliffhanger,
            agent_runs=tuple(agent_runs),
            warnings=tuple(workflow_warnings),
        )
        if self.evaluator is not None:
            return self.evaluator.evaluate(artifact)
        return artifact

    def _execute_agent(
        self,
        *,
        agent_name: str,
        normalized_script: NormalizedScript,
        agent_runs: list[AgentRunRecord],
        workflow_warnings: list[AnalysisWarning],
        executor: Callable[[NormalizedScript], AgentResultT],
        failure_result: AgentResultT,
    ) -> AgentResultT:
        started_at = datetime.now(timezone.utc)
        started_clock = perf_counter()
        agent_warnings = (
            ("heuristic_execution",)
            if self.llm_gateway.backend_name == "heuristic"
            else ()
        )
        try:
            result = executor(normalized_script)
        except Exception as exc:
            completed_at = datetime.now(timezone.utc)
            agent_runs.append(
                AgentRunRecord(
                    agent_name=agent_name,
                    status=AgentRunStatus.FAILED,
                    backend=self.llm_gateway.backend_name,
                    model_name=self.llm_gateway.model_name,
                    started_at=started_at,
                    completed_at=completed_at,
                    latency_ms=int((perf_counter() - started_clock) * 1000),
                    warnings=agent_warnings,
                    failure_message=str(exc),
                )
            )
            workflow_warnings.append(
                AnalysisWarning(
                    code="agent_execution_failed",
                    message=f"{agent_name} agent failed: {exc}",
                    component=agent_name,
                )
            )
            return failure_result

        completed_at = datetime.now(timezone.utc)
        agent_runs.append(
            AgentRunRecord(
                agent_name=agent_name,
                status=AgentRunStatus.COMPLETED,
                backend=self.llm_gateway.backend_name,
                model_name=self.llm_gateway.model_name,
                started_at=started_at,
                completed_at=completed_at,
                latency_ms=int((perf_counter() - started_clock) * 1000),
                warnings=agent_warnings,
            )
        )
        return result
