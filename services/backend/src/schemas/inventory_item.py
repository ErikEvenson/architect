import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class InventoryItemCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    data_type: str = Field("custom", max_length=50)
    data: str
    sort_order: int = 0


class InventoryItemUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    data_type: str | None = Field(None, max_length=50)
    data: str | None = None
    sort_order: int | None = None


class InventoryItemResponse(BaseModel):
    id: uuid.UUID
    version_id: uuid.UUID
    name: str
    description: str | None
    data_type: str
    data: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
