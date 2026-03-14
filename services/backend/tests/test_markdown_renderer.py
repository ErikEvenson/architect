import uuid
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.rendering.base import RenderResult
from src.rendering.markdown_renderer import MarkdownRenderer

API = "/api/v1"

VALID_MARKDOWN = """# Architecture Overview

## Network

| Component | Type |
|-----------|------|
| VPC | Network |
| EC2 | Compute |

!!! note
    This is a test document.
"""

MARKDOWN_WITH_DIAGRAM_REF = """# Overview

![VPC Diagram](artifact:550e8400-e29b-41d4-a716-446655440000)
"""


class TestMarkdownRendererValidation:
    @pytest.mark.asyncio
    async def test_valid_source(self):
        renderer = MarkdownRenderer()
        errors = await renderer.validate_source(VALID_MARKDOWN)
        assert errors == []

    @pytest.mark.asyncio
    async def test_empty_source(self):
        renderer = MarkdownRenderer()
        errors = await renderer.validate_source("")
        assert "empty" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_none_source(self):
        renderer = MarkdownRenderer()
        errors = await renderer.validate_source(None)
        assert "empty" in errors[0].lower()


class TestMarkdownRendererRender:
    @pytest.mark.asyncio
    async def test_render_valid_markdown(self, tmp_path):
        renderer = MarkdownRenderer()
        output_dir = tmp_path / "output"
        result = await renderer.render(uuid.uuid4(), VALID_MARKDOWN, output_dir)
        assert result.success
        assert "document.html" in result.output_paths
        html = (output_dir / "document.html").read_text()
        assert "<h1" in html
        assert "<table" in html
        assert "Architecture Overview" in html

    @pytest.mark.asyncio
    async def test_render_with_inline_css(self, tmp_path):
        renderer = MarkdownRenderer()
        output_dir = tmp_path / "output"
        await renderer.render(uuid.uuid4(), "# Test", output_dir)
        html = (output_dir / "document.html").read_text()
        assert "<style>" in html
        assert "font-family" in html

    @pytest.mark.asyncio
    async def test_render_with_diagram_reference(self, tmp_path):
        renderer = MarkdownRenderer()
        output_dir = tmp_path / "output"
        result = await renderer.render(uuid.uuid4(), MARKDOWN_WITH_DIAGRAM_REF, output_dir)
        assert result.success
        html = (output_dir / "document.html").read_text()
        assert "VPC Diagram" in html

    @pytest.mark.asyncio
    async def test_render_empty_source_fails(self, tmp_path):
        renderer = MarkdownRenderer()
        result = await renderer.render(uuid.uuid4(), "", tmp_path / "output")
        assert not result.success
        assert "empty" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_render_with_table(self, tmp_path):
        renderer = MarkdownRenderer()
        output_dir = tmp_path / "output"
        result = await renderer.render(uuid.uuid4(), VALID_MARKDOWN, output_dir)
        assert result.success
        html = (output_dir / "document.html").read_text()
        assert "<th" in html
        assert "Component" in html


class TestMarkdownRenderAPI:
    @pytest.mark.asyncio
    async def test_trigger_markdown_render(self, client, sample_version):
        version_id = sample_version["id"]
        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={
                "name": "Architecture Doc",
                "artifact_type": "document",
                "engine": "markdown",
                "source_code": VALID_MARKDOWN,
            },
        )
        artifact_id = art.json()["id"]

        mock_result = RenderResult(success=True, output_paths=["document.html"])
        with patch(
            "src.services.render_service.MarkdownRenderer.render",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            resp = await client.post(
                f"{API}/versions/{version_id}/artifacts/{artifact_id}/render"
            )

        assert resp.status_code == 202
        assert resp.json()["render_status"] == "success"
        assert "document.html" in resp.json()["output_paths"]


class TestTemplatesAPI:
    @pytest.mark.asyncio
    async def test_list_templates(self, client):
        resp = await client.get(f"{API}/templates")
        assert resp.status_code == 200
        templates = resp.json()
        assert "architecture" in templates
        assert "runbook" in templates

    @pytest.mark.asyncio
    async def test_render_architecture_template(self, client):
        resp = await client.post(
            f"{API}/templates/render",
            json={"template_name": "architecture", "project_name": "Cloud Migration"},
        )
        assert resp.status_code == 200
        source = resp.json()["source_code"]
        assert "Cloud Migration" in source
        assert "Architecture Document" in source
        assert "## Security" in source

    @pytest.mark.asyncio
    async def test_render_runbook_template(self, client):
        resp = await client.post(
            f"{API}/templates/render",
            json={"template_name": "runbook", "project_name": "My Service"},
        )
        assert resp.status_code == 200
        source = resp.json()["source_code"]
        assert "My Service" in source
        assert "Runbook" in source

    @pytest.mark.asyncio
    async def test_render_unknown_template(self, client):
        resp = await client.post(
            f"{API}/templates/render",
            json={"template_name": "nonexistent"},
        )
        assert resp.status_code == 404
