import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.project import Project
from src.models.version import Version
from src.schemas.version import VersionCreate, VersionResponse, VersionUpdate

router = APIRouter(prefix="/projects/{project_id}/versions", tags=["versions"])


async def _get_project(project_id: uuid.UUID, session: AsyncSession) -> Project:
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("", response_model=list[VersionResponse])
async def list_versions(project_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await _get_project(project_id, session)
    result = await session.execute(
        select(Version).where(Version.project_id == project_id).order_by(Version.version_number)
    )
    return result.scalars().all()


@router.post("", response_model=VersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    project_id: uuid.UUID, data: VersionCreate, session: AsyncSession = Depends(get_session)
):
    await _get_project(project_id, session)

    existing = await session.execute(
        select(Version).where(
            Version.project_id == project_id, Version.version_number == data.version_number
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="Version number already exists for project"
        )

    version = Version(
        project_id=project_id,
        version_number=data.version_number,
        label=data.label,
        status=data.status.value,
        notes=data.notes,
    )
    session.add(version)
    await session.commit()
    await session.refresh(version)
    return version


@router.get("/{version_id}", response_model=VersionResponse)
async def get_version(
    project_id: uuid.UUID, version_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    await _get_project(project_id, session)
    version = await session.get(Version, version_id)
    if not version or version.project_id != project_id:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.patch("/{version_id}", response_model=VersionResponse)
async def update_version(
    project_id: uuid.UUID,
    version_id: uuid.UUID,
    data: VersionUpdate,
    session: AsyncSession = Depends(get_session),
):
    await _get_project(project_id, session)
    version = await session.get(Version, version_id)
    if not version or version.project_id != project_id:
        raise HTTPException(status_code=404, detail="Version not found")

    update_data = data.model_dump(exclude_unset=True)
    if "status" in update_data:
        update_data["status"] = update_data["status"].value

    for key, value in update_data.items():
        setattr(version, key, value)

    await session.commit()
    await session.refresh(version)
    return version
