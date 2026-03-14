import uuid

import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_create_artifact(client, sample_version):
    resp = await client.post(
        f"{API}/versions/{sample_version['id']}/artifacts",
        json={"name": "Network Diagram", "artifact_type": "diagram", "engine": "diagrams_py"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Network Diagram"
    assert data["artifact_type"] == "diagram"
    assert data["detail_level"] == "conceptual"
    assert data["engine"] == "diagrams_py"
    assert data["render_status"] == "pending"
    assert data["output_paths"] == []
    assert data["sort_order"] == 0


@pytest.mark.asyncio
async def test_create_artifact_with_source(client, sample_version):
    resp = await client.post(
        f"{API}/versions/{sample_version['id']}/artifacts",
        json={
            "name": "VPC Diagram",
            "artifact_type": "diagram",
            "engine": "d2",
            "detail_level": "detailed",
            "source_code": "vpc: VPC",
            "sort_order": 1,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["source_code"] == "vpc: VPC"
    assert data["detail_level"] == "detailed"
    assert data["sort_order"] == 1


@pytest.mark.asyncio
async def test_list_artifacts(client, sample_version):
    version_id = sample_version["id"]
    await client.post(
        f"{API}/versions/{version_id}/artifacts",
        json={"name": "Diagram 1", "artifact_type": "diagram", "engine": "diagrams_py"},
    )
    await client.post(
        f"{API}/versions/{version_id}/artifacts",
        json={"name": "Diagram 2", "artifact_type": "diagram", "engine": "d2"},
    )
    resp = await client.get(f"{API}/versions/{version_id}/artifacts")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_get_artifact(client, sample_version):
    version_id = sample_version["id"]
    create_resp = await client.post(
        f"{API}/versions/{version_id}/artifacts",
        json={"name": "Diagram", "artifact_type": "diagram", "engine": "diagrams_py"},
    )
    artifact_id = create_resp.json()["id"]

    resp = await client.get(f"{API}/versions/{version_id}/artifacts/{artifact_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Diagram"


@pytest.mark.asyncio
async def test_update_artifact(client, sample_version):
    version_id = sample_version["id"]
    create_resp = await client.post(
        f"{API}/versions/{version_id}/artifacts",
        json={"name": "Diagram", "artifact_type": "diagram", "engine": "diagrams_py"},
    )
    artifact_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{API}/versions/{version_id}/artifacts/{artifact_id}",
        json={"name": "Updated Diagram", "source_code": "from diagrams import Diagram"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Diagram"
    assert resp.json()["source_code"] == "from diagrams import Diagram"


@pytest.mark.asyncio
async def test_delete_artifact(client, sample_version):
    version_id = sample_version["id"]
    create_resp = await client.post(
        f"{API}/versions/{version_id}/artifacts",
        json={"name": "Diagram", "artifact_type": "diagram", "engine": "diagrams_py"},
    )
    artifact_id = create_resp.json()["id"]

    resp = await client.delete(f"{API}/versions/{version_id}/artifacts/{artifact_id}")
    assert resp.status_code == 204

    resp = await client.get(f"{API}/versions/{version_id}/artifacts/{artifact_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_artifact(client, sample_version):
    resp = await client.get(f"{API}/versions/{sample_version['id']}/artifacts/{uuid.uuid4()}")
    assert resp.status_code == 404
