import re
import uuid
from pathlib import Path

import markdown
import structlog

from src.rendering.base import BaseRenderer, RenderResult

logger = structlog.get_logger()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1a1a1a; max-width: 900px; margin: 0 auto; padding: 2rem; }}
h1 {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem; }}
h2 {{ border-bottom: 1px solid #e5e7eb; padding-bottom: 0.3rem; margin-top: 2rem; }}
h3 {{ margin-top: 1.5rem; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th, td {{ border: 1px solid #d1d5db; padding: 0.5rem 0.75rem; text-align: left; }}
th {{ background: #f3f4f6; font-weight: 600; }}
tr:nth-child(even) {{ background: #f9fafb; }}
code {{ background: #f3f4f6; padding: 0.15rem 0.3rem; border-radius: 3px; font-size: 0.9em; }}
pre {{ background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 6px; overflow-x: auto; }}
pre code {{ background: none; padding: 0; color: inherit; }}
blockquote {{ border-left: 4px solid #3b82f6; margin: 1rem 0; padding: 0.5rem 1rem; background: #eff6ff; }}
img {{ max-width: 100%; height: auto; }}
.admonition {{ border-left: 4px solid #3b82f6; background: #eff6ff; padding: 0.75rem 1rem; margin: 1rem 0; border-radius: 0 4px 4px 0; }}
.admonition-title {{ font-weight: 600; margin-bottom: 0.25rem; }}
.admonition.warning {{ border-color: #f59e0b; background: #fffbeb; }}
.admonition.danger {{ border-color: #ef4444; background: #fef2f2; }}
.task-list-item {{ list-style: none; }}
.task-list-item input {{ margin-right: 0.5rem; }}
</style>
</head>
<body>
{content}
</body>
</html>"""

# Pattern to match artifact references: ![alt](artifact:uuid)
ARTIFACT_REF_PATTERN = re.compile(
    r"!\[([^\]]*)\]\(artifact:([0-9a-f-]+)\)"
)


class MarkdownRenderer(BaseRenderer):
    def __init__(self, artifact_output_base: Path | None = None):
        self.artifact_output_base = artifact_output_base

    async def validate_source(self, source_code: str) -> list[str]:
        errors = []
        if not source_code or not source_code.strip():
            errors.append("Source code is empty")
        return errors

    def _resolve_artifact_refs(self, source: str) -> str:
        """Replace artifact:uuid references with placeholder or actual paths."""

        def replacer(match: re.Match) -> str:
            alt = match.group(1)
            artifact_id = match.group(2)
            # Return a placeholder — actual resolution would need DB access
            # In practice, the render service will pre-resolve these before calling render
            return f'<div style="border:1px dashed #9ca3af; padding:1rem; text-align:center; color:#6b7280;">' \
                   f'[Diagram: {alt or artifact_id}]</div>'

        return ARTIFACT_REF_PATTERN.sub(replacer, source)

    async def render(
        self, artifact_id: uuid.UUID, source_code: str, output_dir: Path
    ) -> RenderResult:
        errors = await self.validate_source(source_code)
        if errors:
            return RenderResult(success=False, error_message="; ".join(errors))

        try:
            # Resolve diagram references
            processed_source = self._resolve_artifact_refs(source_code)

            # Render markdown to HTML
            md = markdown.Markdown(
                extensions=[
                    "tables",
                    "fenced_code",
                    "codehilite",
                    "admonition",
                    "toc",
                    "pymdownx.tasklist",
                    "pymdownx.tilde",
                ],
                extension_configs={
                    "codehilite": {"css_class": "highlight", "guess_lang": False},
                    "toc": {"permalink": True},
                    "pymdownx.tasklist": {"custom_checkbox": True},
                },
            )
            html_content = md.convert(processed_source)

            # Wrap in styled template
            full_html = HTML_TEMPLATE.format(content=html_content)

            # Write output
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / "document.html"
            output_path.write_text(full_html, encoding="utf-8")

            logger.info("markdown_render_success", artifact_id=str(artifact_id))
            return RenderResult(success=True, output_paths=["document.html"])

        except Exception as e:
            logger.exception("markdown_render_exception", artifact_id=str(artifact_id))
            return RenderResult(success=False, error_message=str(e))
