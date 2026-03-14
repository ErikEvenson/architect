import uuid
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.rendering.base import RenderResult
from src.rendering.diagrams_renderer import DiagramsRenderer

API = "/api/v1"

VALID_DIAGRAMS_SOURCE = '''
from diagrams import Diagram
from diagrams.aws.compute import EC2

with Diagram("Test", show=False, outformat=["svg", "png"]):
    EC2("web")
'''

INVALID_SOURCE = "this is not valid python code $$$$"

NO_SHOW_FALSE_SOURCE = '''
from diagrams import Diagram
from diagrams.aws.compute import EC2

with Diagram("Test"):
    EC2("web")
'''


# --- DiagramsRenderer unit tests ---

class TestDiagramsRendererValidation:
    @pytest.mark.asyncio
    async def test_valid_source(self):
        renderer = DiagramsRenderer()
        errors = await renderer.validate_source(VALID_DIAGRAMS_SOURCE)
        assert errors == []

    @pytest.mark.asyncio
    async def test_empty_source(self):
        renderer = DiagramsRenderer()
        errors = await renderer.validate_source("")
        assert "empty" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_none_source(self):
        renderer = DiagramsRenderer()
        errors = await renderer.validate_source(None)
        assert "empty" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_missing_diagrams_import(self):
        renderer = DiagramsRenderer()
        errors = await renderer.validate_source("print('hello')\nshow=False")
        assert any("diagrams" in e.lower() for e in errors)

    @pytest.mark.asyncio
    async def test_missing_show_false(self):
        renderer = DiagramsRenderer()
        errors = await renderer.validate_source(NO_SHOW_FALSE_SOURCE)
        assert any("show=False" in e for e in errors)


class TestDiagramsRendererRender:
    @pytest.mark.asyncio
    async def test_render_with_invalid_source_returns_error(self):
        renderer = DiagramsRenderer()
        output_dir = Path("/tmp/test_render_invalid")
        result = await renderer.render(uuid.uuid4(), "", output_dir)
        assert not result.success
        assert "empty" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_render_with_syntax_error(self):
        renderer = DiagramsRenderer()
        output_dir = Path("/tmp/test_render_syntax")
        source = "from diagrams import Diagram\nshow=False\n(((invalid syntax"
        result = await renderer.render(uuid.uuid4(), source, output_dir)
        assert not result.success
        assert result.error_message is not None

    @pytest.mark.asyncio
    async def test_render_timeout(self):
        renderer = DiagramsRenderer(timeout=1)
        output_dir = Path("/tmp/test_render_timeout")
        source = '''
from diagrams import Diagram
import time
show=False
time.sleep(10)
with Diagram("Test", show=False):
    pass
'''
        result = await renderer.render(uuid.uuid4(), source, output_dir)
        assert not result.success
        assert "timed out" in result.error_message.lower()


# --- RenderResult tests ---

class TestRenderResult:
    def test_success_result(self):
        result = RenderResult(success=True, output_paths=["diagram.svg", "diagram.png"])
        assert result.success
        assert len(result.output_paths) == 2
        assert result.error_message is None

    def test_error_result(self):
        result = RenderResult(success=False, error_message="Something failed")
        assert not result.success
        assert result.output_paths == []
        assert result.error_message == "Something failed"


# --- API endpoint tests ---

class TestRenderAPI:
    @pytest.mark.asyncio
    async def test_trigger_render_no_source(self, client, sample_version):
        # Create artifact without source code
        version_id = sample_version["id"]
        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={"name": "Diagram", "artifact_type": "diagram", "engine": "diagrams_py"},
        )
        artifact_id = art.json()["id"]

        resp = await client.post(
            f"{API}/versions/{version_id}/artifacts/{artifact_id}/render"
        )
        assert resp.status_code == 400
        assert "source" in resp.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_trigger_render_not_found(self, client, sample_version):
        version_id = sample_version["id"]
        resp = await client.post(
            f"{API}/versions/{version_id}/artifacts/{uuid.uuid4()}/render"
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_trigger_render_with_source(self, client, sample_version):
        version_id = sample_version["id"]
        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={
                "name": "Diagram",
                "artifact_type": "diagram",
                "engine": "diagrams_py",
                "source_code": VALID_DIAGRAMS_SOURCE,
            },
        )
        artifact_id = art.json()["id"]

        # Mock the render to avoid needing graphviz installed
        mock_result = RenderResult(
            success=True, output_paths=["test.svg", "test.png"]
        )
        with patch(
            "src.services.render_service.DiagramsRenderer.render",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            # Re-register renderer with the mocked version
            resp = await client.post(
                f"{API}/versions/{version_id}/artifacts/{artifact_id}/render"
            )

        assert resp.status_code == 202
        data = resp.json()
        assert data["render_status"] == "success"
        assert "test.svg" in data["output_paths"]

    @pytest.mark.asyncio
    async def test_get_output_not_found(self, client, sample_version):
        version_id = sample_version["id"]
        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={
                "name": "Diagram",
                "artifact_type": "diagram",
                "engine": "diagrams_py",
                "source_code": VALID_DIAGRAMS_SOURCE,
            },
        )
        artifact_id = art.json()["id"]

        resp = await client.get(
            f"{API}/versions/{version_id}/artifacts/{artifact_id}/outputs/nonexistent.svg"
        )
        assert resp.status_code == 404
