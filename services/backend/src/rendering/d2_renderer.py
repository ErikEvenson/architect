import asyncio
import shutil
import tempfile
import uuid
from pathlib import Path

import structlog

from src.rendering.base import BaseRenderer, RenderResult

logger = structlog.get_logger()

DEFAULT_TIMEOUT = 60


class D2Renderer(BaseRenderer):
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, layout: str = "elk"):
        self.timeout = timeout
        self.layout = layout

    async def validate_source(self, source_code: str) -> list[str]:
        errors = []
        if not source_code or not source_code.strip():
            errors.append("Source code is empty")
        return errors

    async def render(
        self, artifact_id: uuid.UUID, source_code: str, output_dir: Path
    ) -> RenderResult:
        errors = await self.validate_source(source_code)
        if errors:
            return RenderResult(success=False, error_message="; ".join(errors))

        tmp_dir = None
        try:
            tmp_dir = Path(tempfile.mkdtemp(prefix="architect_d2_"))
            input_path = tmp_dir / "diagram.d2"
            output_path = tmp_dir / "diagram.svg"
            input_path.write_text(source_code)

            process = await asyncio.create_subprocess_exec(
                "d2",
                f"--layout={self.layout}",
                "--theme=0",
                str(input_path),
                str(output_path),
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
                error_msg = stderr.decode().strip() if stderr else "Unknown D2 render error"
                logger.error(
                    "d2_render_failed",
                    artifact_id=str(artifact_id),
                    returncode=process.returncode,
                    stderr=error_msg,
                )
                return RenderResult(success=False, error_message=error_msg)

            if not output_path.exists():
                return RenderResult(
                    success=False,
                    error_message="D2 completed but no output file was generated",
                )

            # Copy output to final location
            output_dir.mkdir(parents=True, exist_ok=True)
            dest_file = output_dir / "diagram.svg"
            shutil.copy2(str(output_path), str(dest_file))

            logger.info(
                "d2_render_success",
                artifact_id=str(artifact_id),
                output_paths=["diagram.svg"],
            )
            return RenderResult(success=True, output_paths=["diagram.svg"])

        except FileNotFoundError:
            return RenderResult(
                success=False, error_message="D2 not installed"
            )
        except Exception as e:
            logger.exception("d2_render_exception", artifact_id=str(artifact_id))
            return RenderResult(success=False, error_message=str(e))
        finally:
            if tmp_dir and tmp_dir.exists():
                shutil.rmtree(tmp_dir, ignore_errors=True)
