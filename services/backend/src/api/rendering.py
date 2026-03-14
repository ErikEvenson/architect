import tempfile
import uuid
from pathlib import Path

import markdown
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models.artifact import Artifact
from src.models.client import Client
from src.models.project import Project
from src.models.version import Version
from src.schemas.artifact import ArtifactResponse
from src.services.render_service import resolve_output_dir, trigger_render

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

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


ARTIFACT_PDF_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@page { size: A4; margin: 2cm; @bottom-center { content: counter(page); font-size: 10pt; color: #6b7280; } }
body { font-family: DejaVu Sans, sans-serif; font-size: 11pt; line-height: 1.6; color: #1a1a1a; }
h1 { font-size: 20pt; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem; }
h2 { font-size: 16pt; margin-top: 1.2em; border-bottom: 1px solid #d1d5db; padding-bottom: 0.2em; }
.meta { font-size: 9pt; color: #9ca3af; margin-bottom: 2em; }
.diagram { text-align: center; margin: 1em 0; }
.diagram svg { max-width: 100%; height: auto; width: 100%; }
table { border-collapse: collapse; width: 100%; margin: 0.5em 0; }
th, td { border: 1px solid #d1d5db; padding: 0.4em 0.6em; text-align: left; font-size: 10pt; }
th { background: #f3f4f6; font-weight: 600; }
code { background: #f3f4f6; padding: 0.15rem 0.3rem; border-radius: 3px; font-size: 0.9em; }
pre { background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 6px; overflow-x: auto; }
pre code { background: none; padding: 0; color: inherit; }
</style>
</head>
<body>
<h1>{{ name }}</h1>
<div class="meta">{{ client_name }} / {{ project_name }} / v{{ version_number }} &mdash; {{ detail_level }}</div>
{{ content | safe }}
</body>
</html>"""


@router.post("/export-pdf")
async def export_artifact_pdf(
    version_id: uuid.UUID,
    artifact_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    """Export a single artifact as a PDF."""
    import re

    artifact = await _get_artifact(version_id, artifact_id, session)

    # Get project context
    version = await session.get(Version, artifact.version_id)
    project = await session.get(Project, version.project_id)
    client = await session.get(Client, project.client_id)

    # Build HTML content based on artifact type
    if artifact.artifact_type == "diagram" and artifact.render_status == "success":
        output_dir = await resolve_output_dir(artifact, session)
        svg_files = [p for p in artifact.output_paths if p.endswith(".svg")]
        if svg_files:
            svg_path = output_dir / svg_files[0]
            if svg_path.exists():
                svg = svg_path.read_text()
                # Strip hardcoded dimensions for PDF scaling
                svg = re.sub(r'(<svg[^>]*?)\s+width="[^"]*"', r'\1', svg)
                svg = re.sub(r'(<svg[^>]*?)\s+height="[^"]*"', r'\1', svg)
                svg = re.sub(r'<\?xml[^?]*\?>\s*', '', svg)
                svg = re.sub(r'<!DOCTYPE[^>]*>\s*', '', svg)
                svg = re.sub(r'<!--.*?-->\s*', '', svg, flags=re.DOTALL)
                content = f'<div class="diagram">{svg}</div>'
            else:
                raise HTTPException(status_code=404, detail="Rendered output not found")
        else:
            raise HTTPException(status_code=400, detail="No SVG output available")

    elif artifact.artifact_type == "document" and artifact.source_code:
        md = markdown.Markdown(extensions=["tables", "fenced_code", "codehilite", "toc"])
        content = md.convert(artifact.source_code)

    elif artifact.source_code:
        md = markdown.Markdown(extensions=["tables", "fenced_code"])
        content = md.convert(artifact.source_code)

    else:
        raise HTTPException(status_code=400, detail="No content to export")

    # Render HTML
    from jinja2 import Template

    template = Template(ARTIFACT_PDF_TEMPLATE)
    html = template.render(
        name=artifact.name,
        client_name=client.name,
        project_name=project.name,
        version_number=version.version_number,
        detail_level=artifact.detail_level,
        content=content,
    )

    # Convert to PDF
    from weasyprint import HTML

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        HTML(string=html).write_pdf(tmp.name)
        return FileResponse(
            tmp.name,
            media_type="application/pdf",
            filename=f"{artifact.name}.pdf",
        )
