import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_session
from src.models.artifact import Artifact
from src.models.version import Version
from src.schemas.artifact import ArtifactResponse
from src.services.render_service import resolve_output_dir, trigger_render

router = APIRouter(prefix="/versions/{version_id}/artifacts/{artifact_id}", tags=["rendering"])


async def _get_artifact(
    version_id: uuid.UUID, artifact_id: uuid.UUID, session: AsyncSession
) -> Artifact:
    version = await session.get(Version, version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    artifact = await session.get(Artifact, artifact_id)
    if not artifact or artifact.version_id != version_id:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@router.post("/render", response_model=ArtifactResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_artifact_render(
    version_id: uuid.UUID,
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    artifact = await _get_artifact(version_id, artifact_id, session)

    if not artifact.source_code and artifact.engine != "weasyprint":
        raise HTTPException(status_code=400, detail="No source code to render")

    try:
        updated_artifact = await trigger_render(artifact_id, session)
        return updated_artifact
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


CONTENT_TYPES = {
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".pdf": "application/pdf",
    ".html": "text/html",
}


@router.get("/outputs/{filename}")
async def get_rendered_output(
    version_id: uuid.UUID,
    artifact_id: uuid.UUID,
    filename: str,
    session: AsyncSession = Depends(get_session),
):
    artifact = await _get_artifact(version_id, artifact_id, session)
    output_dir = await resolve_output_dir(artifact, session)
    file_path = output_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    # Prevent path traversal
    if not file_path.resolve().is_relative_to(output_dir.resolve()):
        raise HTTPException(status_code=400, detail="Invalid filename")

    suffix = Path(filename).suffix.lower()
    content_type = CONTENT_TYPES.get(suffix, "application/octet-stream")

    return FileResponse(str(file_path), media_type=content_type)
