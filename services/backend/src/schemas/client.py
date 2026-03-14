import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class ClientCreate(BaseModel):
    name: str = Field(..., max_length=255)
    logo_path: str | None = None
    metadata: dict = Field(default_factory=dict)


class ClientUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    logo_path: str | None = None
    metadata: dict | None = None


class ClientResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    logo_path: str | None
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_metadata(cls, data):
        """Map ORM 'metadata_' attribute to schema 'metadata' field."""
        if hasattr(data, "metadata_"):
            # ORM object — read metadata_ attribute
            obj_dict = {
                "id": data.id,
                "name": data.name,
                "slug": data.slug,
                "logo_path": data.logo_path,
                "metadata": data.metadata_,
                "created_at": data.created_at,
                "updated_at": data.updated_at,
            }
            return obj_dict
        return data
