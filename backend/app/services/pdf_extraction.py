from dataclasses import dataclass
from pathlib import Path
import tempfile

import pymupdf4llm


@dataclass(frozen=True)
class ExtractedPdfText:
    text: str
    warnings: tuple[str, ...]


@dataclass(slots=True)
class PdfTextExtractor:
    def extract_text(self, pdf_bytes: bytes) -> ExtractedPdfText:
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(pdf_bytes)
                temp_path = Path(temp_file.name)

            raw = pymupdf4llm.to_markdown(str(temp_path))
            text = str(raw).strip()
            warnings: list[str] = []
            if not text:
                warnings.append("pdf_extraction_empty")
            return ExtractedPdfText(text=text, warnings=tuple(warnings))
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink(missing_ok=True)
