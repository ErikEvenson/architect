import asyncio
import shutil
import tempfile
import uuid
from pathlib import Path

import structlog

from src.rendering.base import BaseRenderer, RenderResult

logger = structlog.get_logger()

DEFAULT_TIMEOUT = 60


class DiagramsRenderer(BaseRenderer):
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout

    async def validate_source(self, source_code: str) -> list[str]:
        errors = []
        if not source_code or not source_code.strip():
            errors.append("Source code is empty")
            return errors
        if "from diagrams" not in source_code and "import diagrams" not in source_code:
            errors.append("Source code must import from the diagrams library")
        if "show=False" not in source_code:
            errors.append("Source code must include show=False to prevent GUI display")
        return errors

    async def render(
        self, artifact_id: uuid.UUID, source_code: str, output_dir: Path
    ) -> RenderResult:
        errors = await self.validate_source(source_code)
        if errors:
            return RenderResult(success=False, error_message="; ".join(errors))

        tmp_dir = None
        try:
            tmp_dir = Path(tempfile.mkdtemp(prefix="architect_render_"))
            script_path = tmp_dir / "diagram.py"
            script_path.write_text(source_code)

            process = await asyncio.create_subprocess_exec(
                "python3",
                str(script_path),
                cwd=str(tmp_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.communicate()
                return RenderResult(
                    success=False,
                    error_message=f"Render timed out after {self.timeout}s",
                )

            if process.returncode != 0:
                error_msg = stderr.decode().strip() if stderr else "Unknown render error"
                logger.error(
                    "render_failed",
                    artifact_id=str(artifact_id),
                    returncode=process.returncode,
                    stderr=error_msg,
                )
                return RenderResult(success=False, error_message=error_msg)

            # Collect output files
            output_dir.mkdir(parents=True, exist_ok=True)
            output_paths = []

            for ext in ("*.svg", "*.png"):
                for src_file in tmp_dir.glob(ext):
                    dest_file = output_dir / src_file.name
                    shutil.copy2(str(src_file), str(dest_file))
                    output_paths.append(src_file.name)

            if not output_paths:
                return RenderResult(
                    success=False,
                    error_message="Render completed but no output files were generated",
                )

            logger.info(
                "render_success",
                artifact_id=str(artifact_id),
                output_paths=output_paths,
            )
            return RenderResult(success=True, output_paths=output_paths)

        except Exception as e:
            logger.exception("render_exception", artifact_id=str(artifact_id))
            return RenderResult(success=False, error_message=str(e))
        finally:
            if tmp_dir and tmp_dir.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)
