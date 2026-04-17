import fitz
from fastapi.testclient import TestClient

from app.core.container import build_container
from app.main import create_app
from app.services.pdf_extraction import ExtractedPdfText


def _build_pdf_bytes(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def test_pdf_upload_is_normalized_and_surfaces_warnings(client: TestClient) -> None:
    pdf_content = _build_pdf_bytes("Riya: Why now?\nArjun: The truth is out.")

    response = client.post(
        "/api/v1/analysis/runs/upload",
        files={"file": ("script.pdf", pdf_content, "application/pdf")},
        data={"title": "PDF Script"},
    )

    assert response.status_code == 202
    handle = response.json()
    run_id = handle["run_id"]

    detail_response = client.get(f"/api/v1/analysis/runs/{run_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["status"] in {"completed", "partial"}
    normalized = detail["normalized_script"]
    assert normalized is not None
    assert len(normalized["scenes"]) == 1
    assert len(normalized["dialogue_blocks"]) >= 1
    assert len(normalized["warnings"]) >= 1


def test_pdf_upload_can_continue_existing_script_lineage_and_keep_extraction_warnings() -> None:
    class StubPdfExtractor:
        def extract_text(self, pdf_bytes: bytes) -> ExtractedPdfText:
            _ = pdf_bytes
            return ExtractedPdfText(
                text="Scene: Upload path\nRiya: Why now?\nArjun: Because the truth changed.",
                warnings=("pdf_layout_noise",),
            )

    container = build_container()
    container.pdf_text_extractor = StubPdfExtractor()  # type: ignore[assignment]
    client = TestClient(create_app(container=container))

    seed = client.post(
        "/api/v1/analysis/runs",
        json={
            "title": "Seed Script",
            "script_text": "Scene: Seed\nRiya: Why now?\nArjun: Because everything changed.",
        },
    )
    assert seed.status_code == 202
    seed_body = seed.json()

    pdf_content = _build_pdf_bytes("placeholder")
    response = client.post(
        "/api/v1/analysis/runs/upload",
        files={"file": ("revision.pdf", pdf_content, "application/pdf")},
        data={"title": "Revision PDF", "script_id": seed_body["script_id"]},
    )

    assert response.status_code == 202
    handle = response.json()
    assert handle["script_id"] == seed_body["script_id"]

    detail_response = client.get(f"/api/v1/analysis/runs/{handle['run_id']}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["script_id"] == seed_body["script_id"]
    assert any(
        warning["code"] == "pdf_layout_noise"
        for warning in detail["normalized_script"]["warnings"]
    )
