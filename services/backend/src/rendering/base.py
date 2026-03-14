import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RenderResult:
    success: bool
    output_paths: list[str] = field(default_factory=list)
    error_message: str | None = None


class BaseRenderer(ABC):
    @abstractmethod
    async def validate_source(self, source_code: str) -> list[str]:
        """Validate source code. Returns list of error messages (empty = valid)."""

    @abstractmethod
    async def render(
        self, artifact_id: uuid.UUID, source_code: str, output_dir: Path
    ) -> RenderResult:
        """Render source code to output files in output_dir. Returns RenderResult."""
