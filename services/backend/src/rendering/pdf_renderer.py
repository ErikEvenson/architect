import uuid
from datetime import datetime, timezone
from pathlib import Path

import markdown
import structlog
from jinja2 import Environment, FileSystemLoader

from src.rendering.base import BaseRenderer, RenderResult

logger = structlog.get_logger()

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


class PDFRenderer(BaseRenderer):
    async def validate_source(self, source_code: str) -> list[str]:
        # PDF reports don't use source_code — they compile from sibling artifacts
        return []

    async def render(
        self, artifact_id: uuid.UUID, source_code: str, output_dir: Path
    ) -> RenderResult:
        """Render a PDF report. source_code is ignored; context must be set via render_pdf()."""
        # This method exists to satisfy the interface but PDF rendering
        # needs extra context (sibling artifacts, project info).
        # Use render_pdf() directly from the render service.
        return RenderResult(
            success=False,
            error_message="Use render_pdf() with full context instead of render()",
        )

    async def render_pdf(
        self,
        artifact_id: uuid.UUID,
        output_dir: Path,
        project_name: str,
        client_name: str,
        version_number: str,
        client_logo: str | None,
        artifacts: list[dict],
    ) -> RenderResult:
        """Render a PDF report with full project context.

        artifacts: list of dicts with keys:
            name, artifact_type, detail_level, svg_content (optional), html_content (optional)
        """
        try:
            # Render HTML from template
            template = env.get_template("pdf/report.html.j2")
            html = template.render(
                project_name=project_name,
                client_name=client_name,
                version_number=version_number,
                client_logo=client_logo,
                generated_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                artifacts=artifacts,
            )

            # Convert HTML to PDF via WeasyPrint
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "report.pdf"

            # Save debug HTML
            debug_path = output_dir / "report_debug.html"
            debug_path.write_text(html, encoding="utf-8")

            from weasyprint import HTML

            HTML(string=html).write_pdf(str(output_path))

            logger.info("pdf_render_success", artifact_id=str(artifact_id))
            return RenderResult(success=True, output_paths=["report.pdf"])

        except Exception as e:
            logger.exception("pdf_render_exception", artifact_id=str(artifact_id))
            return RenderResult(success=False, error_message=str(e))
