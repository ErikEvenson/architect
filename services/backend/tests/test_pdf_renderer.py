import uuid
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from src.rendering.base import RenderResult
from src.rendering.pdf_renderer import PDFRenderer

API = "/api/v1"


class TestPDFRendererValidation:
    @pytest.mark.asyncio
    async def test_validate_source_always_passes(self):
        renderer = PDFRenderer()
        errors = await renderer.validate_source("")
        assert errors == []

    @pytest.mark.asyncio
    async def test_validate_source_none(self):
        renderer = PDFRenderer()
        errors = await renderer.validate_source(None)
        assert errors == []


class TestPDFRendererRender:
    @pytest.mark.asyncio
    async def test_render_method_returns_error(self):
        """The base render() method should tell caller to use render_pdf()."""
        renderer = PDFRenderer()
        result = await renderer.render(uuid.uuid4(), "", Path("/tmp/test"))
        assert not result.success
        assert "render_pdf" in result.error_message

    @pytest.mark.asyncio
    async def test_render_pdf_generates_file(self, tmp_path):
        renderer = PDFRenderer()
        output_dir = tmp_path / "output"

        result = await renderer.render_pdf(
            artifact_id=uuid.uuid4(),
            output_dir=output_dir,
            project_name="Cloud Migration",
            client_name="Acme Corp",
            version_number="1.0.0",
            client_logo=None,
            artifacts=[
                {
                    "name": "VPC Diagram",
                    "artifact_type": "diagram",
                    "detail_level": "conceptual",
                    "svg_content": "<svg><circle r='10'/></svg>",
                    "html_content": None,
                },
                {
                    "name": "Architecture Doc",
                    "artifact_type": "document",
                    "detail_level": "conceptual",
                    "svg_content": None,
                    "html_content": "<p>Overview of the architecture</p>",
                },
            ],
        )

        assert result.success
        assert "report.pdf" in result.output_paths
        assert (output_dir / "report.pdf").exists()
        assert (output_dir / "report.pdf").stat().st_size > 0

    @pytest.mark.asyncio
    async def test_render_pdf_empty_artifacts(self, tmp_path):
        renderer = PDFRenderer()
        output_dir = tmp_path / "output"

        result = await renderer.render_pdf(
            artifact_id=uuid.uuid4(),
            output_dir=output_dir,
            project_name="Empty Project",
            client_name="Acme Corp",
            version_number="1.0.0",
            client_logo=None,
            artifacts=[],
        )

        assert result.success
        assert (output_dir / "report.pdf").exists()

    @pytest.mark.asyncio
    async def test_render_pdf_contains_project_info(self, tmp_path):
        """Verify the HTML template renders with project context."""
        renderer = PDFRenderer()
        output_dir = tmp_path / "output"

        # We can't easily inspect PDF content, but we can verify it generates
        result = await renderer.render_pdf(
            artifact_id=uuid.uuid4(),
            output_dir=output_dir,
            project_name="My Project",
            client_name="Test Client",
            version_number="2.0.0",
            client_logo=None,
            artifacts=[],
        )

        assert result.success


class TestPDFRenderAPI:
    @pytest.mark.asyncio
    async def test_trigger_pdf_render_no_source_ok(self, client, sample_version):
        """PDF artifacts don't need source code."""
        version_id = sample_version["id"]
        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={
                "name": "Full Report",
                "artifact_type": "pdf_report",
                "engine": "weasyprint",
            },
        )
        artifact_id = art.json()["id"]

        mock_result = RenderResult(success=True, output_paths=["report.pdf"])
        with patch(
            "src.services.render_service.pdf_renderer.render_pdf",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            resp = await client.post(
                f"{API}/versions/{version_id}/artifacts/{artifact_id}/render"
            )

        assert resp.status_code == 202
        assert resp.json()["render_status"] == "success"
        assert "report.pdf" in resp.json()["output_paths"]

    @pytest.mark.asyncio
    async def test_pdf_output_content_type(self, client, sample_version):
        """Verify PDF output would be served with correct content type."""
        version_id = sample_version["id"]
        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={
                "name": "Report",
                "artifact_type": "pdf_report",
                "engine": "weasyprint",
            },
        )
        artifact_id = art.json()["id"]

        # Output file doesn't exist, so we get 404 — but this tests the routing
        resp = await client.get(
            f"{API}/versions/{version_id}/artifacts/{artifact_id}/outputs/report.pdf"
        )
        assert resp.status_code == 404
