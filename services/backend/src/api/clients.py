import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.client import Client
from src.schemas.client import ClientCreate, ClientResponse, ClientUpdate
from src.services.slug import generate_slug

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=list[ClientResponse])
async def list_clients(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Client).order_by(Client.name))
    return result.scalars().all()


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(data: ClientCreate, session: AsyncSession = Depends(get_session)):
    slug = generate_slug(data.name)
    existing = await session.execute(select(Client).where(Client.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Client with this name already exists")

    client = Client(
        name=data.name,
        slug=slug,
        logo_path=data.logo_path,
        metadata_=data.metadata,
    )
    session.add(client)
    await session.commit()
    await session.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: uuid.UUID, data: ClientUpdate, session: AsyncSession = Depends(get_session)
):
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        update_data["slug"] = generate_slug(update_data["name"])
    if "metadata" in update_data:
        update_data["metadata_"] = update_data.pop("metadata")

    for key, value in update_data.items():
        setattr(client, key, value)

    await session.commit()
    await session.refresh(client)
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    await session.delete(client)
    await session.commit()
