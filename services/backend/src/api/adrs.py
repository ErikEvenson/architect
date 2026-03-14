import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.adr import ADR
from src.models.project import Project
from src.schemas.adr import ADRCreate, ADRResponse, ADRUpdate

router = APIRouter(prefix="/projects/{project_id}/adrs", tags=["adrs"])


async def _get_project(project_id: uuid.UUID, session: AsyncSession) -> Project:
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def _next_adr_number(project_id: uuid.UUID, session: AsyncSession) -> int:
    result = await session.execute(
        select(func.coalesce(func.max(ADR.adr_number), 0)).where(ADR.project_id == project_id)
    )
    return result.scalar() + 1


@router.get("", response_model=list[ADRResponse])
async def list_adrs(project_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await _get_project(project_id, session)
    result = await session.execute(
        select(ADR).where(ADR.project_id == project_id).order_by(ADR.adr_number)
    )
    return result.scalars().all()


@router.post("", response_model=ADRResponse, status_code=status.HTTP_201_CREATED)
async def create_adr(
    project_id: uuid.UUID, data: ADRCreate, session: AsyncSession = Depends(get_session)
):
    await _get_project(project_id, session)
    adr_number = await _next_adr_number(project_id, session)

    adr = ADR(
        project_id=project_id,
        adr_number=adr_number,
        title=data.title,
        status=data.status.value,
        context=data.context,
        decision=data.decision,
        consequences=data.consequences,
    )
    session.add(adr)
    await session.commit()
    await session.refresh(adr)
    return adr


@router.get("/{adr_id}", response_model=ADRResponse)
async def get_adr(
    project_id: uuid.UUID, adr_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    await _get_project(project_id, session)
    adr = await session.get(ADR, adr_id)
    if not adr or adr.project_id != project_id:
        raise HTTPException(status_code=404, detail="ADR not found")
    return adr


@router.patch("/{adr_id}", response_model=ADRResponse)
async def update_adr(
    project_id: uuid.UUID,
    adr_id: uuid.UUID,
    data: ADRUpdate,
    session: AsyncSession = Depends(get_session),
):
    await _get_project(project_id, session)
    adr = await session.get(ADR, adr_id)
    if not adr or adr.project_id != project_id:
        raise HTTPException(status_code=404, detail="ADR not found")

    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data:
        update_data["status"] = update_data["status"].value

    for key, value in update_data.items():
        setattr(adr, key, value)

    await session.commit()
    await session.refresh(adr)
    return adr


@router.post("/{adr_id}/supersede", response_model=ADRResponse, status_code=status.HTTP_201_CREATED)
async def supersede_adr(
    project_id: uuid.UUID,
    adr_id: uuid.UUID,
    data: ADRCreate,
    session: AsyncSession = Depends(get_session),
):
    await _get_project(project_id, session)
    old_adr = await session.get(ADR, adr_id)
    if not old_adr or old_adr.project_id != project_id:
        raise HTTPException(status_code=404, detail="ADR not found")

    adr_number = await _next_adr_number(project_id, session)

    new_adr = ADR(
        project_id=project_id,
        adr_number=adr_number,
        title=data.title,
        status=data.status.value,
        context=data.context,
        decision=data.decision,
        consequences=data.consequences,
    )
    session.add(new_adr)
    await session.flush()

    old_adr.status = "superseded"
    old_adr.superseded_by = new_adr.id

    await session.commit()
    await session.refresh(new_adr)
    return new_adr
