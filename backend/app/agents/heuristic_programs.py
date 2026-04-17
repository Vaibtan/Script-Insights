from dataclasses import dataclass

from app.agents.protocols import EmotionProgram
from app.agents.protocols import SummaryProgram
from app.domain.analysis_outputs import EmotionArcPoint
from app.domain.analysis_outputs import EmotionResult
from app.domain.analysis_outputs import EvidenceSpan
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
