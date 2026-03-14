import uuid

import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_create_project(client, sample_client):
    resp = await client.post(
        f"{API}/clients/{sample_client['id']}/projects",
        json={"name": "Cloud Migration"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"] == "cloud-migration"
    assert data["status"] == "draft"
    assert data["cloud_providers"] == []


@pytest.mark.asyncio
async def test_create_project_with_cloud_providers(client, sample_client):
    resp = await client.post(
        f"{API}/clients/{sample_client['id']}/projects",
        json={"name": "Hybrid Cloud", "cloud_providers": ["aws", "nutanix"]},
    )
    assert resp.status_code == 201
    assert "aws" in resp.json()["cloud_providers"]
    assert "nutanix" in resp.json()["cloud_providers"]


@pytest.mark.asyncio
async def test_reject_duplicate_project_per_client(client, sample_client):
    client_id = sample_client["id"]
    await client.post(f"{API}/clients/{client_id}/projects", json={"name": "Cloud Migration"})
    resp = await client.post(
        f"{API}/clients/{client_id}/projects", json={"name": "Cloud Migration"}
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_allow_same_project_name_different_clients(client):
    c1 = (await client.post(f"{API}/clients", json={"name": "Acme Corp"})).json()
    c2 = (await client.post(f"{API}/clients", json={"name": "Globex Inc"})).json()

    r1 = await client.post(
        f"{API}/clients/{c1['id']}/projects", json={"name": "Cloud Migration"}
    )
    r2 = await client.post(
        f"{API}/clients/{c2['id']}/projects", json={"name": "Cloud Migration"}
    )
    assert r1.status_code == 201
    assert r2.status_code == 201


@pytest.mark.asyncio
async def test_list_projects(client, sample_client):
    client_id = sample_client["id"]
    await client.post(f"{API}/clients/{client_id}/projects", json={"name": "Cloud Migration"})
    await client.post(f"{API}/clients/{client_id}/projects", json={"name": "DR Setup"})
    resp = await client.get(f"{API}/clients/{client_id}/projects")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_get_project(client, sample_project, sample_client):
    resp = await client.get(
        f"{API}/clients/{sample_client['id']}/projects/{sample_project['id']}"
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Cloud Migration"


@pytest.mark.asyncio
async def test_update_project_status(client, sample_project, sample_client):
    resp = await client.patch(
        f"{API}/clients/{sample_client['id']}/projects/{sample_project['id']}",
        json={"status": "active"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


@pytest.mark.asyncio
async def test_update_project_description(client, sample_project, sample_client):
    resp = await client.patch(
        f"{API}/clients/{sample_client['id']}/projects/{sample_project['id']}",
        json={"description": "Migrate on-prem to AWS"},
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "Migrate on-prem to AWS"


@pytest.mark.asyncio
async def test_delete_project(client, sample_project, sample_client):
    resp = await client.delete(
        f"{API}/clients/{sample_client['id']}/projects/{sample_project['id']}"
    )
    assert resp.status_code == 204
    resp = await client.get(
        f"{API}/clients/{sample_client['id']}/projects/{sample_project['id']}"
    )
    assert resp.status_code == 404
