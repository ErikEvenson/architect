import uuid

import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_create_client(client):
    resp = await client.post(f"{API}/clients", json={"name": "Acme Corp"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Acme Corp"
    assert data["slug"] == "acme-corp"
    assert data["metadata"] == {}
    assert "id" in data


@pytest.mark.asyncio
async def test_create_client_with_metadata(client):
    resp = await client.post(
        f"{API}/clients", json={"name": "Acme Corp", "metadata": {"industry": "tech"}}
    )
    assert resp.status_code == 201
    assert resp.json()["metadata"]["industry"] == "tech"


@pytest.mark.asyncio
async def test_reject_duplicate_client(client):
    await client.post(f"{API}/clients", json={"name": "Acme Corp"})
    resp = await client.post(f"{API}/clients", json={"name": "Acme Corp"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_list_clients(client):
    await client.post(f"{API}/clients", json={"name": "Acme Corp"})
    await client.post(f"{API}/clients", json={"name": "Globex Inc"})
    resp = await client.get(f"{API}/clients")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_get_client(client, sample_client):
    resp = await client.get(f"{API}/clients/{sample_client['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Acme Corp"


@pytest.mark.asyncio
async def test_get_nonexistent_client(client):
    resp = await client.get(f"{API}/clients/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_client_name(client, sample_client):
    resp = await client.patch(
        f"{API}/clients/{sample_client['id']}", json={"name": "Acme Corporation"}
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Acme Corporation"
    assert resp.json()["slug"] == "acme-corporation"


@pytest.mark.asyncio
async def test_update_client_metadata(client, sample_client):
    resp = await client.patch(
        f"{API}/clients/{sample_client['id']}", json={"metadata": {"industry": "finance"}}
    )
    assert resp.status_code == 200
    assert resp.json()["metadata"]["industry"] == "finance"


@pytest.mark.asyncio
async def test_delete_client(client, sample_client):
    resp = await client.delete(f"{API}/clients/{sample_client['id']}")
    assert resp.status_code == 204
    resp = await client.get(f"{API}/clients/{sample_client['id']}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_client_cascades_to_projects(client, sample_client):
    client_id = sample_client["id"]
    proj_resp = await client.post(
        f"{API}/clients/{client_id}/projects", json={"name": "Cloud Migration"}
    )
    project_id = proj_resp.json()["id"]

    await client.delete(f"{API}/clients/{client_id}")

    resp = await client.get(f"{API}/clients/{client_id}/projects/{project_id}")
    assert resp.status_code == 404
