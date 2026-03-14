import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ADRStatus(str, Enum):
    proposed = "proposed"
    accepted = "accepted"
    deprecated = "deprecated"
    superseded = "superseded"


class ADRCreate(BaseModel):
    title: str = Field(..., max_length=255)
    status: ADRStatus = ADRStatus.proposed
    context: str
    decision: str
    consequences: str


class ADRUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    status: ADRStatus | None = None
    context: str | None = None
    decision: str | None = None
    consequences: str | None = None


class ADRResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    adr_number: int
    title: str
    status: str
    context: str
    decision: str
    consequences: str
    superseded_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
