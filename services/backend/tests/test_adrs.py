import pytest

API = "/api/v1"

ADR_DATA = {
    "title": "Use PostgreSQL",
    "context": "Need relational DB",
    "decision": "PostgreSQL 16",
    "consequences": "Team needs PG experience",
}


@pytest.mark.asyncio
async def test_create_adr(client, sample_version):
    resp = await client.post(
        f"{API}/versions/{sample_version['id']}/adrs", json=ADR_DATA
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["adr_number"] == 1
    assert data["status"] == "proposed"
    assert data["title"] == "Use PostgreSQL"


@pytest.mark.asyncio
async def test_adr_numbers_sequential_per_version(client, sample_version):
    version_id = sample_version["id"]
    await client.post(f"{API}/versions/{version_id}/adrs", json=ADR_DATA)
    resp = await client.post(
        f"{API}/versions/{version_id}/adrs",
        json={**ADR_DATA, "title": "Use Kubernetes"},
    )
    assert resp.status_code == 201
    assert resp.json()["adr_number"] == 2


@pytest.mark.asyncio
async def test_adr_numbers_independent_per_version(client, sample_project):
    project_id = sample_project["id"]

    # Create two versions on the same project
    v1 = (
        await client.post(
            f"{API}/projects/{project_id}/versions", json={"version_number": "1.0.0"}
        )
    ).json()
    v2 = (
        await client.post(
            f"{API}/projects/{project_id}/versions", json={"version_number": "2.0.0"}
        )
    ).json()

    # Add an ADR to each version
    await client.post(f"{API}/versions/{v1['id']}/adrs", json=ADR_DATA)
    resp = await client.post(
        f"{API}/versions/{v2['id']}/adrs",
        json={**ADR_DATA, "title": "Use S3"},
    )
    assert resp.status_code == 201
    # Each version starts its own ADR numbering at 1
    assert resp.json()["adr_number"] == 1


@pytest.mark.asyncio
async def test_list_adrs(client, sample_version):
    version_id = sample_version["id"]
    await client.post(f"{API}/versions/{version_id}/adrs", json=ADR_DATA)
    await client.post(
        f"{API}/versions/{version_id}/adrs", json={**ADR_DATA, "title": "Use Kubernetes"}
    )
    resp = await client.get(f"{API}/versions/{version_id}/adrs")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_get_adr(client, sample_version):
    version_id = sample_version["id"]
    create_resp = await client.post(f"{API}/versions/{version_id}/adrs", json=ADR_DATA)
    adr_id = create_resp.json()["id"]

    resp = await client.get(f"{API}/versions/{version_id}/adrs/{adr_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Use PostgreSQL"


@pytest.mark.asyncio
async def test_update_adr_status(client, sample_version):
    version_id = sample_version["id"]
    create_resp = await client.post(f"{API}/versions/{version_id}/adrs", json=ADR_DATA)
    adr_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{API}/versions/{version_id}/adrs/{adr_id}", json={"status": "accepted"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_update_adr_context(client, sample_version):
    version_id = sample_version["id"]
    create_resp = await client.post(f"{API}/versions/{version_id}/adrs", json=ADR_DATA)
    adr_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{API}/versions/{version_id}/adrs/{adr_id}", json={"context": "Need JSONB support"}
    )
    assert resp.status_code == 200
    assert resp.json()["context"] == "Need JSONB support"


@pytest.mark.asyncio
async def test_supersede_adr(client, sample_version):
    version_id = sample_version["id"]

    # Create original ADR
    old_resp = await client.post(
        f"{API}/versions/{version_id}/adrs",
        json={**ADR_DATA, "title": "Use MySQL", "status": "accepted"},
    )
    old_adr = old_resp.json()

    # Supersede it
    new_resp = await client.post(
        f"{API}/versions/{version_id}/adrs/{old_adr['id']}/supersede",
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
    old_check = await client.get(f"{API}/versions/{version_id}/adrs/{old_adr['id']}")
    old_data = old_check.json()
    assert old_data["status"] == "superseded"
    assert old_data["superseded_by"] == new_adr["id"]
