from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from app.core.settings import Settings
from app.domain.normalization import NormalizationWarning
from app.domain.normalization import NormalizedScript


def _canonicalize_script_text(script_text: str) -> str:
    return script_text.replace("\r\n", "\n").replace("\r", "\n")


def _canonicalize_normalized_content(text: str) -> str:
    return "\n".join(
        line.strip() for line in _canonicalize_script_text(text).splitlines()
    ).strip()


def _serialize_warnings(
    warnings: tuple[NormalizationWarning, ...],
) -> list[dict[str, str]]:
    return sorted(
        [{"code": warning.code, "message": warning.message} for warning in warnings],
        key=lambda item: (item["code"], item["message"]),
    )


@dataclass(slots=True)
class ExecutionFingerprintService:
    settings: Settings

    def compute(
        self,
        *,
        script_text: str,
        source_warnings: tuple[NormalizationWarning, ...],
    ) -> str:
        payload = {
            "fingerprint_version": self.settings.analysis_fingerprint_version,
            "result_version": self.settings.result_version,
            "llm_backend": "groq" if self.settings.groq_api_key else "heuristic",
            "groq_model": self.settings.groq_model,
            "script_text": _canonicalize_script_text(script_text),
            "source_warnings": _serialize_warnings(source_warnings),
        }
        return sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

    def compute_normalized(self, normalized_script: NormalizedScript) -> str:
        payload = {
            "normalized_fingerprint_version": self.settings.normalized_fingerprint_version,
            "scenes": [
                {
                    "scene_index": scene.scene_index,
                    "heading": scene.heading.strip(),
                    "content": _canonicalize_normalized_content(scene.content),
                }
                for scene in normalized_script.scenes
            ],
            "dialogue_blocks": [
                {
                    "scene_index": dialogue.scene_index,
                    "speaker": dialogue.speaker,
                    "line": dialogue.line,
                }
                for dialogue in normalized_script.dialogue_blocks
            ],
            "warnings": _serialize_warnings(normalized_script.warnings),
        }
        return sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
