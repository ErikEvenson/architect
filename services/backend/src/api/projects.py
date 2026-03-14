import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.client import Client
from src.models.project import Project
from src.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from src.services.slug import generate_slug

router = APIRouter(prefix="/clients/{client_id}/projects", tags=["projects"])


async def _get_client(client_id: uuid.UUID, session: AsyncSession) -> Client:
    client = await session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("", response_model=list[ProjectResponse])
async def list_projects(client_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await _get_client(client_id, session)
    result = await session.execute(
        select(Project).where(Project.client_id == client_id).order_by(Project.name)
    )
    return result.scalars().all()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    client_id: uuid.UUID, data: ProjectCreate, session: AsyncSession = Depends(get_session)
):
    await _get_client(client_id, session)
    slug = generate_slug(data.name)

    existing = await session.execute(
        select(Project).where(Project.client_id == client_id, Project.slug == slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="Project with this name already exists for client"
        )

    project = Project(
        client_id=client_id,
        name=data.name,
        slug=slug,
        description=data.description,
        cloud_providers=data.cloud_providers,
        status=data.status.value,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    client_id: uuid.UUID, project_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    await _get_client(client_id, session)
    project = await session.get(Project, project_id)
    if not project or project.client_id != client_id:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    client_id: uuid.UUID,
    project_id: uuid.UUID,
    data: ProjectUpdate,
    session: AsyncSession = Depends(get_session),
):
    await _get_client(client_id, session)
    project = await session.get(Project, project_id)
    if not project or project.client_id != client_id:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data:
        update_data["slug"] = generate_slug(update_data["name"])
    if "status" in update_data:
        update_data["status"] = update_data["status"].value

    for key, value in update_data.items():
        setattr(project, key, value)

    await session.commit()
    await session.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    client_id: uuid.UUID, project_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    await _get_client(client_id, session)
    project = await session.get(Project, project_id)
    if not project or project.client_id != client_id:
        raise HTTPException(status_code=404, detail="Project not found")
    await session.delete(project)
    await session.commit()
