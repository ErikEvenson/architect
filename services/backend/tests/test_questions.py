import pytest

API = "/api/v1"


@pytest.mark.asyncio
async def test_create_question(client, sample_version):
    resp = await client.post(
        f"{API}/versions/{sample_version['id']}/questions",
        json={"question_text": "What is the RPO requirement?"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "open"
    assert data["category"] == "requirements"


@pytest.mark.asyncio
async def test_create_question_with_category(client, sample_version):
    resp = await client.post(
        f"{API}/versions/{sample_version['id']}/questions",
        json={"question_text": "What compliance standards apply?", "category": "compliance"},
    )
    assert resp.status_code == 201
    assert resp.json()["category"] == "compliance"


@pytest.mark.asyncio
async def test_list_questions(client, sample_version):
    version_id = sample_version["id"]
    await client.post(
        f"{API}/versions/{version_id}/questions",
        json={"question_text": "What is the RPO?"},
    )
    await client.post(
        f"{API}/versions/{version_id}/questions",
        json={"question_text": "What is the RTO?"},
    )
    resp = await client.get(f"{API}/versions/{version_id}/questions")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_filter_questions_by_status(client, sample_version):
    version_id = sample_version["id"]

    # Create open question
    await client.post(
        f"{API}/versions/{version_id}/questions",
        json={"question_text": "What is the RPO?"},
    )

    # Create answered question
    q2 = await client.post(
        f"{API}/versions/{version_id}/questions",
        json={"question_text": "What is the budget?"},
    )
    await client.patch(
        f"{API}/versions/{version_id}/questions/{q2.json()['id']}",
        json={"status": "answered", "answer_text": "$1M"},
    )

    resp = await client.get(f"{API}/versions/{version_id}/questions?status=open")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["question_text"] == "What is the RPO?"


@pytest.mark.asyncio
async def test_filter_questions_by_category(client, sample_version):
    version_id = sample_version["id"]
    await client.post(
        f"{API}/versions/{version_id}/questions",
        json={"question_text": "What is the RPO?", "category": "requirements"},
    )
    await client.post(
        f"{API}/versions/{version_id}/questions",
        json={"question_text": "What about PCI?", "category": "compliance"},
    )

    resp = await client.get(f"{API}/versions/{version_id}/questions?category=compliance")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_answer_question(client, sample_version):
    version_id = sample_version["id"]
    create_resp = await client.post(
        f"{API}/versions/{version_id}/questions",
        json={"question_text": "What is the RPO?"},
    )
    q_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{API}/versions/{version_id}/questions/{q_id}",
        json={"answer_text": "4 hours", "status": "answered"},
    )
    assert resp.status_code == 200
    assert resp.json()["answer_text"] == "4 hours"
    assert resp.json()["status"] == "answered"


@pytest.mark.asyncio
async def test_defer_question(client, sample_version):
    version_id = sample_version["id"]
    create_resp = await client.post(
        f"{API}/versions/{version_id}/questions",
        json={"question_text": "What is the RPO?"},
    )
    q_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{API}/versions/{version_id}/questions/{q_id}",
        json={"status": "deferred"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "deferred"


@pytest.mark.asyncio
async def test_get_question(client, sample_version):
    version_id = sample_version["id"]
    create_resp = await client.post(
        f"{API}/versions/{version_id}/questions",
        json={"question_text": "What is the RPO?"},
    )
    q_id = create_resp.json()["id"]

    resp = await client.get(f"{API}/versions/{version_id}/questions/{q_id}")
    assert resp.status_code == 200
    assert resp.json()["question_text"] == "What is the RPO?"


@pytest.mark.asyncio
async def test_change_question_category(client, sample_version):
    version_id = sample_version["id"]
    create_resp = await client.post(
        f"{API}/versions/{version_id}/questions",
        json={"question_text": "What is the RPO?", "category": "requirements"},
    )
    q_id = create_resp.json()["id"]

    resp = await client.patch(
        f"{API}/versions/{version_id}/questions/{q_id}",
        json={"category": "operations"},
    )
    assert resp.status_code == 200
    assert resp.json()["category"] == "operations"
