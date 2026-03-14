import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.question import Question
from src.models.version import Version
from src.schemas.question import QuestionCreate, QuestionResponse, QuestionUpdate

router = APIRouter(prefix="/versions/{version_id}/questions", tags=["questions"])


async def _get_version(version_id: uuid.UUID, session: AsyncSession) -> Version:
    version = await session.get(Version, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.get("", response_model=list[QuestionResponse])
async def list_questions(
    version_id: uuid.UUID,
    status_filter: str | None = Query(None, alias="status"),
    category: str | None = None,
    session: AsyncSession = Depends(get_session),
):
    await _get_version(version_id, session)
    query = select(Question).where(Question.version_id == version_id)

    if status_filter:
        query = query.where(Question.status == status_filter)
    if category:
        query = query.where(Question.category == category)

    query = query.order_by(Question.created_at)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    version_id: uuid.UUID, data: QuestionCreate, session: AsyncSession = Depends(get_session)
):
    await _get_version(version_id, session)

    question = Question(
        version_id=version_id,
        question_text=data.question_text,
        category=data.category.value,
    )
    session.add(question)
    await session.commit()
    await session.refresh(question)
    return question


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    version_id: uuid.UUID, question_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    await _get_version(version_id, session)
    question = await session.get(Question, question_id)
    if not question or question.version_id != version_id:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.patch("/{question_id}", response_model=QuestionResponse)
async def update_question(
    version_id: uuid.UUID,
    question_id: uuid.UUID,
    data: QuestionUpdate,
    session: AsyncSession = Depends(get_session),
):
    await _get_version(version_id, session)
    question = await session.get(Question, question_id)
    if not question or question.version_id != version_id:
        raise HTTPException(status_code=404, detail="Question not found")

    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    if "category" in update_data:
        update_data["category"] = update_data["category"].value

    for key, value in update_data.items():
        setattr(question, key, value)

    await session.commit()
    await session.refresh(question)
    return question
