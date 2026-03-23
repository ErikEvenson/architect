import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class QuestionStatus(str, Enum):
    open = "open"
    answered = "answered"
    deferred = "deferred"


class QuestionCategory(str, Enum):
    requirements = "requirements"
    security = "security"
    scaling = "scaling"
    compliance = "compliance"
    cost = "cost"
    operations = "operations"


class QuestionCreate(BaseModel):
    question_text: str
    category: QuestionCategory = QuestionCategory.requirements


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    answer_text: str | None = None
    status: QuestionStatus | None = None
    category: QuestionCategory | None = None


class KnowledgeSuggestion(BaseModel):
    source_file: str
    checklist_item: str
    priority: Optional[str] = None
    score: float


class QuestionResponse(BaseModel):
    id: uuid.UUID
    version_id: uuid.UUID
    question_text: str
    answer_text: str | None
    status: str
    category: str
    suggestions: list[KnowledgeSuggestion] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
