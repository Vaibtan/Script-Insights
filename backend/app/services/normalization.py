import re
from bisect import bisect_left
from bisect import bisect_right

from app.domain.normalization import DialogueBlock
from app.domain.normalization import NormalizationWarning
from app.domain.normalization import NormalizedScript
from app.domain.normalization import SceneBlock

_SCENE_HEADING_RE = re.compile(r"^\s*(scene\b|int\.|ext\.)", flags=re.IGNORECASE)
_DIALOGUE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9 _-]{0,39}):\s*(.+?)\s*$")


class ScriptNormalizer:
    def normalize(self, script_text: str) -> NormalizedScript:
        lines = script_text.splitlines()
        if not lines:
            warning = NormalizationWarning(
                code="empty_script",
                message="Script text is empty after normalization.",
            )
            return NormalizedScript(scenes=(), dialogue_blocks=(), warnings=(warning,))

        line_offsets = self._line_offsets(lines)
        scene_start_indices = [
            index for index, line in enumerate(lines) if _SCENE_HEADING_RE.match(line)
        ]

        warnings: list[NormalizationWarning] = []
        if not scene_start_indices:
            scene_start_indices = [0]
            warnings.append(
                NormalizationWarning(
                    code="missing_scene_heading",
                    message="No explicit scene heading detected; inferred a single scene.",
                )
            )

        scenes = self._build_scenes(lines, line_offsets, scene_start_indices)
        dialogue_blocks = self._build_dialogue_blocks(lines, line_offsets, scenes)
        if not dialogue_blocks:
            warnings.append(
                NormalizationWarning(
                    code="no_dialogue_detected",
                    message="No dialogue blocks were detected in the script.",
                )
            )

        return NormalizedScript(
            scenes=tuple(scenes),
            dialogue_blocks=tuple(dialogue_blocks),
            warnings=tuple(warnings),
        )

    @staticmethod
    def _line_offsets(lines: list[str]) -> list[int]:
        offsets: list[int] = []
        cursor = 0
        for line in lines:
            offsets.append(cursor)
            cursor += len(line) + 1
        return offsets

    @staticmethod
    def _build_scenes(
        lines: list[str], line_offsets: list[int], scene_starts: list[int]
    ) -> list[SceneBlock]:
        scenes: list[SceneBlock] = []
        sorted_starts = sorted(scene_starts)

        for scene_idx, start_line_index in enumerate(sorted_starts):
            end_line_index = (
                sorted_starts[scene_idx + 1]
                if scene_idx + 1 < len(sorted_starts)
                else len(lines)
            )
            scene_lines = lines[start_line_index:end_line_index]
            heading = scene_lines[0].strip() if scene_lines else f"Scene {scene_idx + 1}"
            content = "\n".join(scene_lines).strip()
            start_offset = line_offsets[start_line_index]
            last_line_index = max(start_line_index, end_line_index - 1)
            end_offset = line_offsets[last_line_index] + len(lines[last_line_index])

            scenes.append(
                SceneBlock(
                    scene_index=scene_idx,
                    heading=heading,
                    content=content,
                    start_offset=start_offset,
                    end_offset=end_offset,
                )
            )

        return scenes

    @staticmethod
    def _build_dialogue_blocks(
        lines: list[str], line_offsets: list[int], scenes: list[SceneBlock]
    ) -> list[DialogueBlock]:
        dialogue_blocks: list[DialogueBlock] = []

        for scene in scenes:
            start_index = bisect_left(line_offsets, scene.start_offset)
            end_index = bisect_right(line_offsets, scene.end_offset)
            for line_index in range(start_index, end_index):
                line = lines[line_index]
                line_offset = line_offsets[line_index]
                match = _DIALOGUE_RE.match(line)
                if match is None:
                    continue
                speaker = match.group(1).strip()
                spoken_line = match.group(2).strip()
                dialogue_blocks.append(
                    DialogueBlock(
                        scene_index=scene.scene_index,
                        speaker=speaker,
                        line=spoken_line,
                        start_offset=line_offset,
                        end_offset=line_offset + len(line),
                    )
                )

        return dialogue_blocks
