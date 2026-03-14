import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class VersionStatus(str, Enum):
    draft = "draft"
    review = "review"
    approved = "approved"
    superseded = "superseded"


class VersionCreate(BaseModel):
    version_number: str = Field(..., max_length=20)
    label: str | None = Field(None, max_length=255)
    status: VersionStatus = VersionStatus.draft
    notes: str | None = None


class VersionUpdate(BaseModel):
    label: str | None = Field(None, max_length=255)
    status: VersionStatus | None = None
    notes: str | None = None


class VersionResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    version_number: str
    label: str | None
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
