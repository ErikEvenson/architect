import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_create_version(client, sample_project):
    resp = await client.post(
        f"{API}/projects/{sample_project['id']}/versions",
        json={"version_number": "1.0.0"},
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "draft"


@pytest.mark.asyncio
async def test_create_version_with_label_and_notes(client, sample_project):
    resp = await client.post(
        f"{API}/projects/{sample_project['id']}/versions",
        json={"version_number": "1.0.0", "label": "Initial", "notes": "First draft"},
    )
    assert resp.status_code == 201
    assert resp.json()["label"] == "Initial"
    assert resp.json()["notes"] == "First draft"


@pytest.mark.asyncio
async def test_reject_duplicate_version_number(client, sample_project):
    project_id = sample_project["id"]
    await client.post(f"{API}/projects/{project_id}/versions", json={"version_number": "1.0.0"})
    resp = await client.post(
        f"{API}/projects/{project_id}/versions", json={"version_number": "1.0.0"}
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_versions(client, sample_project):
    project_id = sample_project["id"]
    await client.post(f"{API}/projects/{project_id}/versions", json={"version_number": "1.0.0"})
    await client.post(f"{API}/projects/{project_id}/versions", json={"version_number": "2.0.0"})
    resp = await client.get(f"{API}/projects/{project_id}/versions")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_get_version(client, sample_version, sample_project):
    resp = await client.get(
        f"{API}/projects/{sample_project['id']}/versions/{sample_version['id']}"
    )
    assert resp.status_code == 200
    assert resp.json()["version_number"] == "1.0.0"


@pytest.mark.asyncio
async def test_update_version_status(client, sample_version, sample_project):
    resp = await client.patch(
        f"{API}/projects/{sample_project['id']}/versions/{sample_version['id']}",
        json={"status": "review"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "review"


@pytest.mark.asyncio
async def test_update_version_label(client, sample_version, sample_project):
    resp = await client.patch(
        f"{API}/projects/{sample_project['id']}/versions/{sample_version['id']}",
        json={"label": "Final Draft"},
    )
    assert resp.status_code == 200
    assert resp.json()["label"] == "Final Draft"
