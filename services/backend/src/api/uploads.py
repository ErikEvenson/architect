import re
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_session
from src.models.client import Client
from src.models.project import Project
from src.models.upload import Upload
from src.models.version import Version
from src.schemas.upload import UploadResponse

router = APIRouter(prefix="/versions/{version_id}/uploads", tags=["uploads"])

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


def _sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal and filesystem issues."""
    # Take only the basename
    name = Path(filename).name
    # Replace anything that isn't alphanumeric, dash, underscore, or dot
    name = re.sub(r"[^\w\-.]", "_", name)
    # Collapse multiple underscores/dots
    name = re.sub(r"__+", "_", name)
    name = re.sub(r"\.\.+", ".", name)
    return name or "unnamed"


async def _get_version(version_id: uuid.UUID, session: AsyncSession) -> Version:
    version = await session.get(Version, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


async def _resolve_upload_dir(version: Version, upload_id: uuid.UUID, session: AsyncSession) -> Path:
    """Build the upload directory path."""
    project = await session.get(Project, version.project_id)
    client = await session.get(Client, project.client_id)
    return (
        Path(settings.output_dir)
        / client.slug
        / project.slug
        / version.version_number
        / "uploads"
        / str(upload_id)
    )


@router.get("", response_model=list[UploadResponse])
async def list_uploads(version_id: uuid.UUID, session: AsyncSession = Depends(get_session)):
    await _get_version(version_id, session)
    result = await session.execute(
        select(Upload)
        .where(Upload.version_id == version_id)
        .order_by(Upload.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def create_upload(
    version_id: uuid.UUID,
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
):
    version = await _get_version(version_id, session)

    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Read file content
    content = await file.read()
    file_size = len(content)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 100 MB)")

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    stored_filename = _sanitize_filename(file.filename)
    content_type = file.content_type or "application/octet-stream"

    # Create database record first to get the ID
    upload = Upload(
        version_id=version_id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        content_type=content_type,
        file_size=file_size,
    )
    session.add(upload)
    await session.flush()  # Get the ID

    # Write file to disk
    upload_dir = await _resolve_upload_dir(version, upload.id, session)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / stored_filename
    file_path.write_bytes(content)

    await session.commit()
    await session.refresh(upload)
    return upload


@router.get("/{upload_id}/download")
async def download_upload(
    version_id: uuid.UUID, upload_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    version = await _get_version(version_id, session)
    upload = await session.get(Upload, upload_id)
    if not upload or upload.version_id != version_id:
        raise HTTPException(status_code=404, detail="Upload not found")

    upload_dir = await _resolve_upload_dir(version, upload.id, session)
    file_path = upload_dir / upload.stored_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    # Prevent path traversal
    if not file_path.resolve().is_relative_to(upload_dir.resolve()):
        raise HTTPException(status_code=400, detail="Invalid filename")

    return FileResponse(
        str(file_path),
        media_type=upload.content_type,
        filename=upload.original_filename,
    )


@router.delete("/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(
    version_id: uuid.UUID, upload_id: uuid.UUID, session: AsyncSession = Depends(get_session)
):
    version = await _get_version(version_id, session)
    upload = await session.get(Upload, upload_id)
    if not upload or upload.version_id != version_id:
        raise HTTPException(status_code=404, detail="Upload not found")

    # Delete file from disk
    upload_dir = await _resolve_upload_dir(version, upload.id, session)
    if upload_dir.exists():
        shutil.rmtree(upload_dir)

    await session.delete(upload)
    await session.commit()
