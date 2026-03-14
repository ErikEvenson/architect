import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.artifact import Artifact
from src.models.version import Version
from src.schemas.artifact import ArtifactCreate, ArtifactResponse, ArtifactUpdate

router = APIRouter(prefix="/versions/{version_id}/artifacts", tags=["artifacts"])


async def _get_version(version_id: uuid.UUID, session: AsyncSession) -> Version:
    version = await session.get(Version, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


@router.get("", response_model=list[ArtifactResponse])
async def list_artifacts(version_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await _get_version(version_id, session)
    result = await session.execute(
        select(Artifact)
        .where(Artifact.version_id == version_id)
        .order_by(Artifact.sort_order, Artifact.name)
    )
    return result.scalars().all()


@router.post("", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
async def create_artifact(
    version_id: uuid.UUID, data: ArtifactCreate, session: AsyncSession = Depends(get_session)
):
    await _get_version(version_id, session)

    artifact = Artifact(
        version_id=version_id,
        name=data.name,
        artifact_type=data.artifact_type.value,
        detail_level=data.detail_level.value,
        engine=data.engine.value,
        source_code=data.source_code,
        sort_order=data.sort_order,
    )
    session.add(artifact)
    await session.commit()
    await session.refresh(artifact)
    return artifact


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    version_id: uuid.UUID, artifact_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    await _get_version(version_id, session)
    artifact = await session.get(Artifact, artifact_id)
    if not artifact or artifact.version_id != version_id:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@router.patch("/{artifact_id}", response_model=ArtifactResponse)
async def update_artifact(
    version_id: uuid.UUID,
    artifact_id: uuid.UUID,
    data: ArtifactUpdate,
    session: AsyncSession = Depends(get_session),
):
    await _get_version(version_id, session)
    artifact = await session.get(Artifact, artifact_id)
    if not artifact or artifact.version_id != version_id:
        raise HTTPException(status_code=404, detail="Artifact not found")

    update_data = data.model_dump(exclude_unset=True)
    if "detail_level" in update_data:
        update_data["detail_level"] = update_data["detail_level"].value

    for key, value in update_data.items():
        setattr(artifact, key, value)

    await session.commit()
    await session.refresh(artifact)
    return artifact


@router.delete("/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artifact(
    version_id: uuid.UUID, artifact_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    await _get_version(version_id, session)
    artifact = await session.get(Artifact, artifact_id)
    if not artifact or artifact.version_id != version_id:
        raise HTTPException(status_code=404, detail="Artifact not found")
    await session.delete(artifact)
    await session.commit()
