import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    diagram = "diagram"
    document = "document"
    pdf_report = "pdf_report"


class DetailLevel(str, Enum):
    conceptual = "conceptual"
    logical = "logical"
    detailed = "detailed"
    deployment = "deployment"


class Engine(str, Enum):
    diagrams_py = "diagrams_py"
    d2 = "d2"
    markdown = "markdown"
    weasyprint = "weasyprint"


class RenderStatus(str, Enum):
    pending = "pending"
    rendering = "rendering"
    success = "success"
    error = "error"


class ArtifactCreate(BaseModel):
    name: str = Field(..., max_length=255)
    artifact_type: ArtifactType
    detail_level: DetailLevel = DetailLevel.conceptual
    engine: Engine
    source_code: str | None = None
    sort_order: int = 0


class ArtifactUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    detail_level: DetailLevel | None = None
    source_code: str | None = None
    sort_order: int | None = None


class ArtifactResponse(BaseModel):
    id: uuid.UUID
    version_id: uuid.UUID
    name: str
    artifact_type: str
    detail_level: str
    engine: str
    source_code: str | None
    output_paths: list[str]
    render_status: str
    render_error: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
