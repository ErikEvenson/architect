import asyncio
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.base import Base

# Use SQLite for tests (no PostgreSQL required)
TEST_DATABASE_URL = "sqlite+aiosqlite:///test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    """Create tables before each test, drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_session():
    async with test_session() as session:
        yield session


@pytest.fixture
async def client():
    from src.database import get_session
    from src.main import app

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


API = "/api/v1"


@pytest.fixture
async def sample_client(client):
    """Create and return a sample client."""
    resp = await client.post(f"{API}/clients", json={"name": "Acme Corp"})
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
async def sample_project(client, sample_client):
    """Create and return a sample project."""
    client_id = sample_client["id"]
    resp = await client.post(
        f"{API}/clients/{client_id}/projects",
        json={"name": "Cloud Migration"},
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
async def sample_version(client, sample_project):
    """Create and return a sample version."""
    project_id = sample_project["id"]
    resp = await client.post(
        f"{API}/projects/{project_id}/versions",
        json={"version_number": "1.0.0"},
    )
    assert resp.status_code == 201
    return resp.json()
