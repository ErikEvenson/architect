import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.coverage import CoverageItem
from src.models.version import Version

router = APIRouter(prefix="/versions/{version_id}/coverage", tags=["coverage"])


class CoverageItemCreate(BaseModel):
    knowledge_file: str
    item_text: str
    priority: str  # Critical, Recommended, Optional
    status: str = "pending"  # pending, addressed, deferred, na
    question_id: str | None = None
    reason: str | None = None


class CoverageItemUpdate(BaseModel):
    status: str | None = None
    question_id: str | None = None
    reason: str | None = None


class CoverageItemResponse(BaseModel):
    id: uuid.UUID
    version_id: uuid.UUID
    knowledge_file: str
    item_text: str
    priority: str
    status: str
    question_id: uuid.UUID | None
    reason: str | None

    model_config = {"from_attributes": True}


class CoverageSummary(BaseModel):
    total: int
    critical_total: int
    critical_addressed: int
    critical_deferred: int
    critical_pending: int
    recommended_total: int
    recommended_addressed: int
    optional_total: int
    by_file: dict[str, dict[str, int]]


async def _get_version(version_id: uuid.UUID, session: AsyncSession) -> Version:
    version = await session.get(Version, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.get("", response_model=list[CoverageItemResponse])
async def list_coverage(version_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await _get_version(version_id, session)
    result = await session.execute(
        select(CoverageItem)
        .where(CoverageItem.version_id == version_id)
        .order_by(CoverageItem.knowledge_file, CoverageItem.priority)
    )
    return result.scalars().all()


@router.get("/summary", response_model=CoverageSummary)
async def coverage_summary(version_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await _get_version(version_id, session)
    result = await session.execute(
        select(CoverageItem).where(CoverageItem.version_id == version_id)
    )
    items = result.scalars().all()

    summary = CoverageSummary(
        total=len(items),
        critical_total=0, critical_addressed=0, critical_deferred=0, critical_pending=0,
        recommended_total=0, recommended_addressed=0,
        optional_total=0,
        by_file={},
    )

    for item in items:
        # By file
        if item.knowledge_file not in summary.by_file:
            summary.by_file[item.knowledge_file] = {"total": 0, "addressed": 0, "deferred": 0, "pending": 0, "na": 0}
        summary.by_file[item.knowledge_file]["total"] += 1
        summary.by_file[item.knowledge_file][item.status] = summary.by_file[item.knowledge_file].get(item.status, 0) + 1

        # By priority
        if item.priority == "Critical":
            summary.critical_total += 1
            if item.status == "addressed":
                summary.critical_addressed += 1
            elif item.status == "deferred":
                summary.critical_deferred += 1
            elif item.status == "pending":
                summary.critical_pending += 1
        elif item.priority == "Recommended":
            summary.recommended_total += 1
            if item.status == "addressed":
                summary.recommended_addressed += 1
        elif item.priority == "Optional":
            summary.optional_total += 1

    return summary


@router.post("", response_model=CoverageItemResponse, status_code=status.HTTP_201_CREATED)
async def create_coverage_item(
    version_id: uuid.UUID, data: CoverageItemCreate, session: AsyncSession = Depends(get_session)
):
    await _get_version(version_id, session)

    item = CoverageItem(
        version_id=version_id,
        knowledge_file=data.knowledge_file,
        item_text=data.item_text,
        priority=data.priority,
        status=data.status,
        question_id=uuid.UUID(data.question_id) if data.question_id else None,
        reason=data.reason,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.patch("/{item_id}", response_model=CoverageItemResponse)
async def update_coverage_item(
    version_id: uuid.UUID,
    item_id: uuid.UUID,
    data: CoverageItemUpdate,
    session: AsyncSession = Depends(get_session),
):
    await _get_version(version_id, session)
    item = await session.get(CoverageItem, item_id)
    if not item or item.version_id != version_id:
        raise HTTPException(status_code=404, detail="Coverage item not found")

    update_data = data.model_dump(exclude_unset=True)
    if "question_id" in update_data and update_data["question_id"]:
        update_data["question_id"] = uuid.UUID(update_data["question_id"])

    for key, value in update_data.items():
        setattr(item, key, value)

    await session.commit()
    await session.refresh(item)
    return item
