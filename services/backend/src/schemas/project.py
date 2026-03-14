import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    cloud_providers: list[str] = Field(default_factory=list)
    status: ProjectStatus = ProjectStatus.draft


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    cloud_providers: list[str] | None = None
    status: ProjectStatus | None = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    slug: str
    description: str | None
    cloud_providers: list[str]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
