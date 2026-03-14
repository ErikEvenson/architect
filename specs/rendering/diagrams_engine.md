# Python Diagrams Engine Specification

## Overview

The `diagrams_py` engine renders cloud architecture diagrams using the Python [diagrams](https://diagrams.mingrammer.com/) library. Source code is Python that uses the diagrams API to define nodes and edges.

## Execution Model

1. Receive Python source code from artifact `source_code`
2. Write source to a temporary `.py` file
3. Execute via `subprocess.run(["python3", script_path], ...)` with timeout
4. Collect output files (SVG and PNG) from the temp directory
5. Copy outputs to the artifact's output directory on PVC
6. Clean up temp directory

## Source Code Format

Source code is standard Python using the `diagrams` library:

```python
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB

with Diagram("Web Service", show=False, direction="LR", outformat=["svg", "png"]):
    ELB("lb") >> EC2("web1")
```

**Required conventions:**
- Must use `show=False` (no GUI display)
- Must include `outformat=["svg", "png"]` for both output formats
- The `filename` parameter controls output file naming (defaults to diagram title)
- Source is executed in a temp directory, so output paths are relative

## Validation

Before rendering, validate that:
1. Source code is not empty
2. Source code contains `from diagrams` import (basic sanity check)
3. Source code contains `show=False` (prevent GUI attempts)

## Output

- **SVG**: Vector output, embedded in frontend viewer
- **PNG**: Raster output at 300 DPI (set via `graph_attr={"dpi": "300"}`)
- Output files named based on the Diagram title (spaces replaced with underscores)

## Dependencies

- Python 3.12 (same as backend)
- `diagrams` Python package (installed in backend image)
- Graphviz system package (installed in backend Dockerfile)

## Timeout

- Default: 60 seconds
- Configurable via `RENDER_TIMEOUT` environment variable
- On timeout: kill subprocess, set render_status to "error", store timeout message

## Error Handling

| Error | Behavior |
|---|---|
| Empty source | Validation error returned before render attempt |
| Missing `show=False` | Validation error |
| Python syntax error | Render fails, stderr captured as render_error |
| Import error | Render fails, stderr captured as render_error |
| Timeout | Process killed, render_error = "Render timed out after {timeout}s" |
| Graphviz not found | Render fails, stderr captured |

## Security

- Source code is executed in a subprocess (not `eval`/`exec` in the main process)
- Temp directory is isolated per render job
- No network access needed during rendering
- Process runs as non-root user (UID 1000)
