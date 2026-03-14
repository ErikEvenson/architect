import uuid
from pathlib import Path

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.artifact import Artifact
from src.models.project import Project
from src.models.version import Version
from src.rendering.base import BaseRenderer
from src.rendering.d2_renderer import D2Renderer
from src.rendering.diagrams_renderer import DiagramsRenderer
from src.rendering.markdown_renderer import MarkdownRenderer

logger = structlog.get_logger()

RENDERERS: dict[str, BaseRenderer] = {
    "diagrams_py": DiagramsRenderer(),
    "d2": D2Renderer(),
    "markdown": MarkdownRenderer(),
}


def get_renderer(engine: str) -> BaseRenderer | None:
    return RENDERERS.get(engine)


async def resolve_output_dir(artifact: Artifact, session: AsyncSession) -> Path:
    """Build the output directory path: {output_dir}/{client_slug}/{project_slug}/{version_number}/{artifact_id}/"""
    version = await session.get(Version, artifact.version_id)
    project = await session.get(Project, version.project_id)

    # Get client slug
    from src.models.client import Client

    client = await session.get(Client, project.client_id)

    return (
        Path(settings.output_dir)
        / client.slug
        / project.slug
        / version.version_number
        / str(artifact.id)
    )


async def trigger_render(artifact_id: uuid.UUID, session: AsyncSession) -> Artifact:
    """Trigger a render for an artifact. Updates status and executes renderer."""
    artifact = await session.get(Artifact, artifact_id)
    if not artifact:
        raise ValueError("Artifact not found")

    if not artifact.source_code:
        raise ValueError("No source code to render")

    renderer = get_renderer(artifact.engine)
    if not renderer:
        raise ValueError(f"No renderer available for engine: {artifact.engine}")

    # Set status to rendering
    artifact.render_status = "rendering"
    artifact.render_error = None
    await session.commit()
    await session.refresh(artifact)

    # Execute render
    output_dir = await resolve_output_dir(artifact, session)
    result = await renderer.render(artifact.id, artifact.source_code, output_dir)

    # Update artifact with result
    if result.success:
        artifact.render_status = "success"
        artifact.output_paths = result.output_paths
        artifact.render_error = None
    else:
        artifact.render_status = "error"
        artifact.render_error = result.error_message

    await session.commit()
    await session.refresh(artifact)
    return artifact
