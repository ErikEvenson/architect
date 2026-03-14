import uuid

import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_clone_artifacts(client, sample_project, sample_version):
    project_id = sample_project["id"]
    version_id = sample_version["id"]

    # Create artifacts in source version
    await client.post(
        f"{API}/versions/{version_id}/artifacts",
        json={
            "name": "VPC Diagram",
            "artifact_type": "diagram",
            "engine": "diagrams_py",
            "source_code": "from diagrams import Diagram\nshow=False",
            "sort_order": 0,
        },
    )
    await client.post(
        f"{API}/versions/{version_id}/artifacts",
        json={
            "name": "Architecture Doc",
            "artifact_type": "document",
            "engine": "markdown",
            "source_code": "# Overview",
            "sort_order": 1,
        },
    )

    # Create target version
    target = await client.post(
        f"{API}/projects/{project_id}/versions",
        json={"version_number": "2.0.0"},
    )
    target_version_id = target.json()["id"]

    # Clone
    resp = await client.post(
        f"{API}/versions/{version_id}/artifacts/clone",
        json={"target_version_id": target_version_id},
    )
    assert resp.status_code == 201
    cloned = resp.json()
    assert len(cloned) == 2


@pytest.mark.asyncio
async def test_cloned_artifacts_have_source_code(client, sample_project, sample_version):
    project_id = sample_project["id"]
    version_id = sample_version["id"]

    await client.post(
        f"{API}/versions/{version_id}/artifacts",
        json={
            "name": "Diagram",
            "artifact_type": "diagram",
            "engine": "diagrams_py",
            "source_code": "test source code\nshow=False",
        },
    )

    target = await client.post(
        f"{API}/projects/{project_id}/versions",
        json={"version_number": "2.0.0"},
    )
    target_version_id = target.json()["id"]

    resp = await client.post(
        f"{API}/versions/{version_id}/artifacts/clone",
        json={"target_version_id": target_version_id},
    )
    cloned = resp.json()
    assert cloned[0]["source_code"] == "test source code\nshow=False"


@pytest.mark.asyncio
async def test_cloned_artifacts_are_pending(client, sample_project, sample_version):
    project_id = sample_project["id"]
    version_id = sample_version["id"]

    await client.post(
        f"{API}/versions/{version_id}/artifacts",
        json={
            "name": "Diagram",
            "artifact_type": "diagram",
            "engine": "diagrams_py",
            "source_code": "source\nshow=False",
        },
    )

    target = await client.post(
        f"{API}/projects/{project_id}/versions",
        json={"version_number": "2.0.0"},
    )
    target_version_id = target.json()["id"]

    resp = await client.post(
        f"{API}/versions/{version_id}/artifacts/clone",
        json={"target_version_id": target_version_id},
    )
    cloned = resp.json()
    assert cloned[0]["render_status"] == "pending"
    assert cloned[0]["output_paths"] == []


@pytest.mark.asyncio
async def test_clone_to_nonexistent_version(client, sample_version):
    version_id = sample_version["id"]
    resp = await client.post(
        f"{API}/versions/{version_id}/artifacts/clone",
        json={"target_version_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_clone_empty_version(client, sample_project, sample_version):
    project_id = sample_project["id"]
    version_id = sample_version["id"]

    target = await client.post(
        f"{API}/projects/{project_id}/versions",
        json={"version_number": "2.0.0"},
    )
    target_version_id = target.json()["id"]

    resp = await client.post(
        f"{API}/versions/{version_id}/artifacts/clone",
        json={"target_version_id": target_version_id},
    )
    assert resp.status_code == 201
    assert resp.json() == []
