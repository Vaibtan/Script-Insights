from dataclasses import dataclass

from app.agents.protocols import CliffhangerProgram
from app.agents.protocols import EngagementProgram
from app.agents.protocols import EmotionProgram
from app.agents.protocols import RecommendationProgram
from app.agents.protocols import SummaryProgram
from app.domain.analysis_outputs import CliffhangerResult
from app.domain.analysis_outputs import EngagementResult
from app.domain.analysis_outputs import EmotionArcPoint
from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import EvidenceSpan
from app.domain.analysis_outputs import Recommendation
from app.domain.analysis_outputs import SummaryResult
from app.domain.normalization import NormalizedScript


@dataclass(slots=True)
class HeuristicSummaryProgram(SummaryProgram):
    max_lines: int = 3

    def summarize(self, normalized_script: NormalizedScript) -> SummaryResult:
        scene_lines: list[str] = []
        for scene in normalized_script.scenes:
            content = scene.content.strip()
            if not content:
                continue
            scene_lines.append(content)
            if len(scene_lines) >= self.max_lines:
                break

        if not scene_lines:
            scene_lines = ["No story content could be extracted from the script."]

        summary_text = "\n".join(scene_lines[: self.max_lines])
        first_scene = normalized_script.scenes[0]
        evidence = EvidenceSpan(
            start_offset=first_scene.start_offset,
            end_offset=first_scene.end_offset,
            text=first_scene.content,
        )
        return SummaryResult(text=summary_text, evidence_spans=(evidence,))


@dataclass(slots=True)
class HeuristicEmotionProgram(EmotionProgram):
    def analyze_emotion(self, normalized_script: NormalizedScript) -> EmotionResult:
        dialogue_text = " ".join(
            dialogue.line.lower() for dialogue in normalized_script.dialogue_blocks
        )

        emotion = "neutral"
        valence = 0.0
        arousal = 0.25
        if any(token in dialogue_text for token in ("truth", "fault", "sorry", "why")):
            emotion = "tense"
            valence = -0.2
            arousal = 0.7
        if any(token in dialogue_text for token in ("love", "hope", "forgive")):
            emotion = "hopeful"
            valence = 0.35
            arousal = 0.55

        first_scene = normalized_script.scenes[0]
        evidence = EvidenceSpan(
            start_offset=first_scene.start_offset,
            end_offset=first_scene.end_offset,
            text=first_scene.content,
        )
        arc = EmotionArcPoint(
            beat_index=0, emotion=emotion, valence=valence, arousal=arousal
        )
        return EmotionResult(
            dominant_emotions=(emotion,),
            valence=valence,
            arousal=arousal,
            emotional_arc=(arc,),
            evidence_spans=(evidence,),
        )


@dataclass(slots=True)
class HeuristicEngagementProgram(EngagementProgram):
    def score_engagement(self, normalized_script: NormalizedScript) -> EngagementResult:
        dialogue_count = len(normalized_script.dialogue_blocks)
        scene_count = len(normalized_script.scenes)
        has_question = any(
            "?" in dialogue.line for dialogue in normalized_script.dialogue_blocks
        )

        hook = 70.0 if has_question else 55.0
        conflict = min(95.0, 45.0 + dialogue_count * 8.0)
        tension = min(95.0, 50.0 + dialogue_count * 7.0)
        pacing = 75.0 if 1 <= scene_count <= 3 else 60.0
        stakes = 72.0 if any(
            token in " ".join(d.line.lower() for d in normalized_script.dialogue_blocks)
            for token in ("truth", "fault", "accident", "secret")
        ) else 58.0
        payoff = 65.0 if dialogue_count >= 2 else 45.0

        factors = {
            "hook": hook,
            "conflict": conflict,
            "tension": tension,
            "pacing": pacing,
            "stakes": stakes,
            "payoff": payoff,
        }
        overall = sum(factors.values()) / len(factors)
        return EngagementResult(
            overall_score=overall,
            factors=factors,
            rationale="Heuristic engagement estimate from hook, conflict, tension, pacing, stakes, and payoff.",
        )


@dataclass(slots=True)
class HeuristicRecommendationProgram(RecommendationProgram):
    def suggest_improvements(
        self, normalized_script: NormalizedScript
    ) -> tuple[Recommendation, ...]:
        recommendations: list[Recommendation] = [
            Recommendation(
                category="conflict",
                suggestion="Raise immediate friction in the opening exchange.",
                rationale="Early conflict increases viewer retention in short-form scenes.",
            ),
            Recommendation(
                category="dialogue",
                suggestion="Tighten dialogue lines to remove explanatory phrasing.",
                rationale="Shorter, high-subtext lines improve rhythm and character voice.",
            ),
        ]
        if len(normalized_script.dialogue_blocks) < 3:
            recommendations.append(
                Recommendation(
                    category="pacing",
                    suggestion="Add one escalation beat before the reveal.",
                    rationale="An extra beat can improve tension build-up before payoff.",
                )
            )
        else:
            recommendations.append(
                Recommendation(
                    category="emotional_impact",
                    suggestion="Strengthen the protagonist's emotional reaction after the reveal.",
                    rationale="Post-reveal emotional payoff helps scenes feel earned.",
                )
            )
        return tuple(recommendations)


@dataclass(slots=True)
class HeuristicCliffhangerProgram(CliffhangerProgram):
    def detect_cliffhanger(self, normalized_script: NormalizedScript) -> CliffhangerResult:
        if normalized_script.dialogue_blocks:
            last_dialogue = normalized_script.dialogue_blocks[-1]
            moment_text = f"{last_dialogue.speaker}: {last_dialogue.line}"
            span = EvidenceSpan(
                start_offset=last_dialogue.start_offset,
                end_offset=last_dialogue.end_offset,
                text=moment_text,
            )
        else:
            last_scene = normalized_script.scenes[-1]
            moment_text = last_scene.content
            span = EvidenceSpan(
                start_offset=last_scene.start_offset,
                end_offset=last_scene.end_offset,
                text=last_scene.content,
            )

        return CliffhangerResult(
            moment_text=moment_text,
            why_it_works="The final beat introduces unresolved information that sustains curiosity.",
            evidence_spans=(span,),
        )
