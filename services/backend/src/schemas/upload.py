import uuid
from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    id: uuid.UUID
    version_id: uuid.UUID
    original_filename: str
    content_type: str
    file_size: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
