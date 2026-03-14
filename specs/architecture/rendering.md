# Rendering Pipeline Architecture

## Overview

Architect uses a pluggable renderer architecture. Each rendering engine implements a common interface and executes diagram/document source code in a subprocess with timeout protection.

## Base Renderer Interface

```python
class BaseRenderer(ABC):
    @abstractmethod
    async def validate_source(self, source_code: str) -> list[str]:
        """Validate source code. Returns list of error messages (empty = valid)."""

    @abstractmethod
    async def render(self, artifact_id: UUID, source_code: str, output_dir: Path) -> RenderResult:
        """Render source code to output files. Returns RenderResult with paths and status."""
```

## RenderResult

```python
@dataclass
class RenderResult:
    success: bool
    output_paths: list[str]      # Relative paths to generated files
    error_message: str | None     # Error details if success=False
```

## Render Status Lifecycle

```
pending → rendering → success
                    → error
```

- **pending**: Artifact created with source code, not yet rendered
- **rendering**: Render job in progress
- **success**: Render completed, output files available
- **error**: Render failed, error message stored on artifact

## Output Storage

Rendered files are stored on a PVC-backed filesystem:

```
{output_dir}/{client_slug}/{project_slug}/{version_number}/{artifact_id}/
├── diagram.svg
├── diagram.png
└── ...
```

- `output_dir` defaults to `/app/data/outputs` (configurable via `OUTPUT_DIR`)
- Path components use slugs for human-navigable structure
- Each artifact gets its own subdirectory (by UUID) to avoid name collisions

## Renderer Registry

Renderers are registered by engine name:

| Engine | Renderer Class | Output Formats |
|---|---|---|
| `diagrams_py` | `DiagramsRenderer` | SVG, PNG (300 DPI) |
| `d2` | `D2Renderer` | SVG |
| `markdown` | `MarkdownRenderer` | HTML |
| `weasyprint` | `PDFRenderer` | PDF |

## Subprocess Execution

All renderers that execute external tools (diagrams, D2) use subprocess execution with:
- **Timeout**: 60 seconds (configurable via `RENDER_TIMEOUT`)
- **Isolation**: Temporary directory for each render job
- **Cleanup**: Temp files removed after output is copied to final location
- **Error capture**: stderr captured and stored as `render_error` on artifact

## API Endpoints

### Trigger Render
`POST /api/v1/versions/{version_id}/artifacts/{artifact_id}/render`

- Sets artifact `render_status` to "rendering"
- Executes renderer in background
- Returns immediately with updated artifact (status=rendering)

### Get Artifact (existing)
`GET /api/v1/versions/{version_id}/artifacts/{artifact_id}`

- Returns artifact with current `render_status` and `output_paths`
- Clients poll this endpoint to check render completion

### Get Rendered Output
`GET /api/v1/versions/{version_id}/artifacts/{artifact_id}/outputs/{filename}`

- Serves rendered file (SVG, PNG, etc.) from PVC
- Content-Type based on file extension
