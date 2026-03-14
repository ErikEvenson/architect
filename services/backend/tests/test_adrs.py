import uuid

import pytest

API = "/api/v1"

ADR_DATA = {
    "title": "Use PostgreSQL",
    "context": "Need relational DB",
    "decision": "PostgreSQL 16",
    "consequences": "Team needs PG experience",
}


@pytest.mark.asyncio
async def test_create_adr(client, sample_project):
    resp = await client.post(
        f"{API}/projects/{sample_project['id']}/adrs", json=ADR_DATA
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["adr_number"] == 1
    assert data["status"] == "proposed"
    assert data["title"] == "Use PostgreSQL"


@pytest.mark.asyncio
async def test_adr_numbers_sequential_per_project(client, sample_project):
    project_id = sample_project["id"]
    await client.post(f"{API}/projects/{project_id}/adrs", json=ADR_DATA)
    resp = await client.post(
        f"{API}/projects/{project_id}/adrs",
        json={**ADR_DATA, "title": "Use Kubernetes"},
    )
    assert resp.status_code == 201
    assert resp.json()["adr_number"] == 2


@pytest.mark.asyncio
async def test_adr_numbers_independent_per_project(client, sample_client):
    client_id = sample_client["id"]

    # Create first project with an ADR
    p1 = (
        await client.post(f"{API}/clients/{client_id}/projects", json={"name": "Project A"})
    ).json()
    await client.post(f"{API}/projects/{p1['id']}/adrs", json=ADR_DATA)

    # Create second project with an ADR
    p2 = (
        await client.post(f"{API}/clients/{client_id}/projects", json={"name": "Project B"})
    ).json()
    resp = await client.post(
        f"{API}/projects/{p2['id']}/adrs",
        json={**ADR_DATA, "title": "Use S3"},
    )
    assert resp.status_code == 201
    assert resp.json()["adr_number"] == 1


@pytest.mark.asyncio
async def test_list_adrs(client, sample_project):
    project_id = sample_project["id"]
    await client.post(f"{API}/projects/{project_id}/adrs", json=ADR_DATA)
    await client.post(
        f"{API}/projects/{project_id}/adrs", json={**ADR_DATA, "title": "Use Kubernetes"}
    )
    resp = await client.get(f"{API}/projects/{project_id}/adrs")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_get_adr(client, sample_project):
    project_id = sample_project["id"]
    create_resp = await client.post(f"{API}/projects/{project_id}/adrs", json=ADR_DATA)
    adr_id = create_resp.json()["id"]

    resp = await client.get(f"{API}/projects/{project_id}/adrs/{adr_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Use PostgreSQL"


@pytest.mark.asyncio
async def test_update_adr_status(client, sample_project):
    project_id = sample_project["id"]
    create_resp = await client.post(f"{API}/projects/{project_id}/adrs", json=ADR_DATA)
    adr_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{API}/projects/{project_id}/adrs/{adr_id}", json={"status": "accepted"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_update_adr_context(client, sample_project):
    project_id = sample_project["id"]
    create_resp = await client.post(f"{API}/projects/{project_id}/adrs", json=ADR_DATA)
    adr_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{API}/projects/{project_id}/adrs/{adr_id}", json={"context": "Need JSONB support"}
    )
    assert resp.status_code == 200
    assert resp.json()["context"] == "Need JSONB support"


@pytest.mark.asyncio
async def test_supersede_adr(client, sample_project):
    project_id = sample_project["id"]

    # Create original ADR
    old_resp = await client.post(
        f"{API}/projects/{project_id}/adrs",
        json={**ADR_DATA, "title": "Use MySQL", "status": "accepted"},
    )
    old_adr = old_resp.json()

    # Supersede it
    new_resp = await client.post(
        f"{API}/projects/{project_id}/adrs/{old_adr['id']}/supersede",
        json={
            "title": "Use PostgreSQL",
            "context": "MySQL lacks features",
            "decision": "Switch to PostgreSQL",
            "consequences": "Migration needed",
        },
    )
    assert new_resp.status_code == 201
    new_adr = new_resp.json()
    assert new_adr["adr_number"] == 2
    assert new_adr["status"] == "proposed"

    # Verify old ADR is superseded
    old_check = await client.get(f"{API}/projects/{project_id}/adrs/{old_adr['id']}")
    old_data = old_check.json()
    assert old_data["status"] == "superseded"
    assert old_data["superseded_by"] == new_adr["id"]
