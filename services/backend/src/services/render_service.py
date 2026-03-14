import uuid
from pathlib import Path

import markdown
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models.artifact import Artifact
from src.models.client import Client
from src.models.project import Project
from src.models.version import Version
from src.rendering.base import BaseRenderer
from src.rendering.d2_renderer import D2Renderer
from src.rendering.diagrams_renderer import DiagramsRenderer
from src.rendering.markdown_renderer import MarkdownRenderer
from src.rendering.pdf_renderer import PDFRenderer

logger = structlog.get_logger()

RENDERERS: dict[str, BaseRenderer] = {
    "diagrams_py": DiagramsRenderer(),
    "d2": D2Renderer(),
    "markdown": MarkdownRenderer(),
    "weasyprint": PDFRenderer(),
}

pdf_renderer = PDFRenderer()


def get_renderer(engine: str) -> BaseRenderer | None:
    return RENDERERS.get(engine)


async def resolve_output_dir(artifact: Artifact, session: AsyncSession) -> Path:
    """Build the output directory path."""
    version = await session.get(Version, artifact.version_id)
    project = await session.get(Project, version.project_id)
    client = await session.get(Client, project.client_id)

    return (
        Path(settings.output_dir)
        / client.slug
        / project.slug
        / version.version_number
        / str(artifact.id)
    )


async def _collect_sibling_artifacts(
    artifact: Artifact, session: AsyncSession
) -> tuple[list[dict], str, str, str, str | None]:
    """Collect sibling artifacts and project context for PDF compilation."""
    version = await session.get(Version, artifact.version_id)
    project = await session.get(Project, version.project_id)
    client = await session.get(Client, project.client_id)

    # Get all non-PDF artifacts in the same version, ordered by sort_order
    result = await session.execute(
        select(Artifact)
        .where(Artifact.version_id == artifact.version_id)
        .where(Artifact.id != artifact.id)
        .order_by(Artifact.sort_order, Artifact.name)
    )
    siblings = result.scalars().all()

    compiled = []
    for sib in siblings:
        entry = {
            "name": sib.name,
            "artifact_type": sib.artifact_type,
            "detail_level": sib.detail_level,
            "svg_content": None,
            "html_content": None,
        }

        if sib.artifact_type == "diagram" and sib.render_status == "success":
            # Try to read the SVG file
            sib_output_dir = await resolve_output_dir(sib, session)
            svg_files = [p for p in sib.output_paths if p.endswith(".svg")]
            if svg_files:
                svg_path = sib_output_dir / svg_files[0]
                if svg_path.exists():
                    entry["svg_content"] = svg_path.read_text()

        elif sib.artifact_type == "document" and sib.source_code:
            # Render markdown to HTML inline
            md = markdown.Markdown(extensions=["tables", "fenced_code"])
            entry["html_content"] = md.convert(sib.source_code)

        compiled.append(entry)

    return compiled, project.name, client.name, version.version_number, client.logo_path


async def trigger_render(artifact_id: uuid.UUID, session: AsyncSession) -> Artifact:
    """Trigger a render for an artifact. Updates status and executes renderer."""
    artifact = await session.get(Artifact, artifact_id)
    if not artifact:
        raise ValueError("Artifact not found")

    is_pdf = artifact.engine == "weasyprint"

    if not is_pdf and not artifact.source_code:
        raise ValueError("No source code to render")

    if not is_pdf:
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

    if is_pdf:
        siblings, project_name, client_name, version_number, client_logo = (
            await _collect_sibling_artifacts(artifact, session)
        )
        result = await pdf_renderer.render_pdf(
            artifact.id,
            output_dir,
            project_name=project_name,
            client_name=client_name,
            version_number=version_number,
            client_logo=client_logo,
            artifacts=siblings,
        )
    else:
        renderer = get_renderer(artifact.engine)
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
