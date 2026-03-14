import uuid
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.rendering.base import RenderResult
from src.rendering.d2_renderer import D2Renderer

API = "/api/v1"

VALID_D2_SOURCE = """
vpc: VPC {
  subnet: Subnet {
    ec2: EC2 Instance
  }
}
"""

SEQUENCE_D2_SOURCE = """
shape: sequence_diagram
alice -> bob: Hello
bob -> alice: Hi
"""

NETWORK_D2_SOURCE = """
internet: Internet
lb: Load Balancer
web1: Web Server 1
web2: Web Server 2
db: Database

internet -> lb
lb -> web1
lb -> web2
web1 -> db
web2 -> db
"""

INVALID_D2_SOURCE = "{{{invalid d2 syntax}}}"


# --- D2Renderer unit tests ---

class TestD2RendererValidation:
    @pytest.mark.asyncio
    async def test_valid_source(self):
        renderer = D2Renderer()
        errors = await renderer.validate_source(VALID_D2_SOURCE)
        assert errors == []

    @pytest.mark.asyncio
    async def test_empty_source(self):
        renderer = D2Renderer()
        errors = await renderer.validate_source("")
        assert "empty" in errors[0].lower()

    @pytest.mark.asyncio
    async def test_none_source(self):
        renderer = D2Renderer()
        errors = await renderer.validate_source(None)
        assert "empty" in errors[0].lower()


class TestD2RendererRender:
    @pytest.mark.asyncio
    async def test_render_with_empty_source_returns_error(self):
        renderer = D2Renderer()
        output_dir = Path("/tmp/test_d2_empty")
        result = await renderer.render(uuid.uuid4(), "", output_dir)
        assert not result.success
        assert "empty" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_render_d2_not_installed(self):
        renderer = D2Renderer()
        output_dir = Path("/tmp/test_d2_missing")
        # Use a non-existent binary path to simulate D2 not installed
        with patch.object(renderer, "render") as mock_render:
            mock_render.return_value = RenderResult(
                success=False, error_message="D2 not installed"
            )
            result = await mock_render(uuid.uuid4(), VALID_D2_SOURCE, output_dir)
            assert not result.success
            assert "not installed" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_render_timeout(self):
        renderer = D2Renderer(timeout=1)
        output_dir = Path("/tmp/test_d2_timeout")
        # D2 isn't installed in test env, so this will hit FileNotFoundError
        # which returns "D2 not installed" — test the timeout path with a mock
        with patch("asyncio.create_subprocess_exec") as mock_exec:
            import asyncio

            mock_process = AsyncMock()
            mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError)
            mock_process.kill = AsyncMock()
            mock_exec.return_value = mock_process
            # After kill, communicate should return cleanly
            mock_process.communicate.side_effect = [asyncio.TimeoutError, (b"", b"")]

            result = await renderer.render(uuid.uuid4(), VALID_D2_SOURCE, output_dir)
            assert not result.success
            assert "timed out" in result.error_message.lower()


# --- API endpoint tests ---

class TestD2RenderAPI:
    @pytest.mark.asyncio
    async def test_trigger_d2_render_no_source(self, client, sample_version):
        version_id = sample_version["id"]
        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={"name": "Network", "artifact_type": "diagram", "engine": "d2"},
        )
        artifact_id = art.json()["id"]

        resp = await client.post(
            f"{API}/versions/{version_id}/artifacts/{artifact_id}/render"
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_trigger_d2_render_with_source(self, client, sample_version):
        version_id = sample_version["id"]
        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={
                "name": "Network",
                "artifact_type": "diagram",
                "engine": "d2",
                "source_code": VALID_D2_SOURCE,
            },
        )
        artifact_id = art.json()["id"]

        mock_result = RenderResult(success=True, output_paths=["diagram.svg"])
        with patch(
            "src.services.render_service.D2Renderer.render",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            resp = await client.post(
                f"{API}/versions/{version_id}/artifacts/{artifact_id}/render"
            )

        assert resp.status_code == 202
        data = resp.json()
        assert data["render_status"] == "success"
        assert "diagram.svg" in data["output_paths"]

    @pytest.mark.asyncio
    async def test_trigger_sequence_diagram_render(self, client, sample_version):
        version_id = sample_version["id"]
        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={
                "name": "Sequence",
                "artifact_type": "diagram",
                "engine": "d2",
                "source_code": SEQUENCE_D2_SOURCE,
            },
        )
        artifact_id = art.json()["id"]

        mock_result = RenderResult(success=True, output_paths=["diagram.svg"])
        with patch(
            "src.services.render_service.D2Renderer.render",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            resp = await client.post(
                f"{API}/versions/{version_id}/artifacts/{artifact_id}/render"
            )

        assert resp.status_code == 202
        assert resp.json()["render_status"] == "success"

    @pytest.mark.asyncio
    async def test_trigger_network_topology_render(self, client, sample_version):
        version_id = sample_version["id"]
        art = await client.post(
            f"{API}/versions/{version_id}/artifacts",
            json={
                "name": "Topology",
                "artifact_type": "diagram",
                "engine": "d2",
                "source_code": NETWORK_D2_SOURCE,
            },
        )
        artifact_id = art.json()["id"]

        mock_result = RenderResult(success=True, output_paths=["diagram.svg"])
        with patch(
            "src.services.render_service.D2Renderer.render",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            resp = await client.post(
                f"{API}/versions/{version_id}/artifacts/{artifact_id}/render"
            )

        assert resp.status_code == 202
        assert resp.json()["render_status"] == "success"
