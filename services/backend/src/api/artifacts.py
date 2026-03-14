import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.adr import ADR
from src.models.artifact import Artifact
from src.models.question import Question
from src.models.version import Version
from src.schemas.artifact import ArtifactCreate, ArtifactResponse, ArtifactUpdate


class CloneRequest(BaseModel):
    target_version_id: str

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


@router.post("/clone", response_model=list[ArtifactResponse], status_code=status.HTTP_201_CREATED)
async def clone_artifacts(
    version_id: uuid.UUID,
    data: CloneRequest,
    session: AsyncSession = Depends(get_session),
):
    """Clone all artifacts, ADRs, and questions from this version to a target version."""
    await _get_version(version_id, session)

    target_version_id = uuid.UUID(data.target_version_id)
    target_version = await session.get(Version, target_version_id)
    if not target_version:
        raise HTTPException(status_code=404, detail="Target version not found")

    # Clone artifacts (source code only, no rendered outputs)
    result = await session.execute(
        select(Artifact)
        .where(Artifact.version_id == version_id)
        .order_by(Artifact.sort_order, Artifact.name)
    )
    source_artifacts = result.scalars().all()

    cloned = []
    for src in source_artifacts:
        clone = Artifact(
            version_id=target_version_id,
            name=src.name,
            artifact_type=src.artifact_type,
            detail_level=src.detail_level,
            engine=src.engine,
            source_code=src.source_code,
            sort_order=src.sort_order,
        )
        session.add(clone)
        cloned.append(clone)

    # Clone ADRs (reset numbering per version)
    adr_result = await session.execute(
        select(ADR).where(ADR.version_id == version_id).order_by(ADR.adr_number)
    )
    for src_adr in adr_result.scalars().all():
        clone_adr = ADR(
            version_id=target_version_id,
            adr_number=src_adr.adr_number,
            title=src_adr.title,
            status=src_adr.status,
            context=src_adr.context,
            decision=src_adr.decision,
            consequences=src_adr.consequences,
        )
        session.add(clone_adr)

    # Clone questions
    q_result = await session.execute(
        select(Question).where(Question.version_id == version_id).order_by(Question.created_at)
    )
    for src_q in q_result.scalars().all():
        clone_q = Question(
            version_id=target_version_id,
            question_text=src_q.question_text,
            answer_text=src_q.answer_text,
            status=src_q.status,
            category=src_q.category,
        )
        session.add(clone_q)

    await session.commit()
    for c in cloned:
        await session.refresh(c)

    return cloned
