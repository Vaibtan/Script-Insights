from dataclasses import dataclass


@dataclass(frozen=True)
class NormalizationWarning:
    code: str
    message: str


@dataclass(frozen=True)
class SceneBlock:
    scene_index: int
    heading: str
    content: str
    start_offset: int
    end_offset: int


@dataclass(frozen=True)
class DialogueBlock:
    scene_index: int
    speaker: str
    line: str
    start_offset: int
    end_offset: int


@dataclass(frozen=True)
class NormalizedScript:
    scenes: tuple[SceneBlock, ...]
    dialogue_blocks: tuple[DialogueBlock, ...]
    warnings: tuple[NormalizationWarning, ...]
