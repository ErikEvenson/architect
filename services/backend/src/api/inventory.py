import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.artifacts import _update_content_timestamp
from src.database import get_session
from src.models.inventory_item import InventoryItem
from src.models.version import Version
from src.schemas.inventory_item import InventoryItemCreate, InventoryItemResponse, InventoryItemUpdate

router = APIRouter(prefix="/versions/{version_id}/inventory", tags=["inventory"])


async def _get_version(version_id: uuid.UUID, session: AsyncSession) -> Version:
    version = await session.get(Version, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.get("", response_model=list[InventoryItemResponse])
async def list_inventory_items(version_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await _get_version(version_id, session)
    result = await session.execute(
        select(InventoryItem)
        .where(InventoryItem.version_id == version_id)
        .order_by(InventoryItem.sort_order, InventoryItem.name)
    )
    return result.scalars().all()


@router.post("", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    version_id: uuid.UUID, data: InventoryItemCreate, session: AsyncSession = Depends(get_session)
):
    await _get_version(version_id, session)

    item = InventoryItem(
        version_id=version_id,
        name=data.name,
        description=data.description,
        data_type=data.data_type,
        data=data.data,
        sort_order=data.sort_order,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    version_id: uuid.UUID, item_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    await _get_version(version_id, session)
    item = await session.get(InventoryItem, item_id)
    if not item or item.version_id != version_id:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.patch("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    version_id: uuid.UUID,
    item_id: uuid.UUID,
    data: InventoryItemUpdate,
    session: AsyncSession = Depends(get_session),
):
    await _get_version(version_id, session)
    item = await session.get(InventoryItem, item_id)
    if not item or item.version_id != version_id:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    update_data = data.model_dump(exclude_unset=True)
    if "data" in update_data and update_data["data"] and update_data["data"] != item.data:
        update_data["data"] = _update_content_timestamp(update_data["data"])
    for key, value in update_data.items():
        setattr(item, key, value)

    await session.commit()
    await session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    version_id: uuid.UUID, item_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    await _get_version(version_id, session)
    item = await session.get(InventoryItem, item_id)
    if not item or item.version_id != version_id:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    await session.delete(item)
    await session.commit()
