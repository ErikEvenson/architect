# D2 Rendering Engine Specification

## Overview

The `d2` engine renders diagrams using the [D2](https://d2lang.com/) diagramming language. D2 supports flexible layouts, sequence diagrams, and network topologies with a declarative text syntax.

## Execution Model

1. Receive D2 source code from artifact `source_code`
2. Write source to a temporary `.d2` file
3. Execute via `subprocess`: `d2 --layout=elk --theme=0 input.d2 output.svg`
4. Collect output SVG from the temp directory
5. Copy to the artifact's output directory on PVC
6. Clean up temp directory

## Source Code Format

Standard D2 syntax:

```d2
vpc: VPC {
  subnet-a: Subnet A {
    ec2: EC2 Instance
  }
  subnet-b: Subnet B {
    rds: RDS Database
  }
}

vpc.subnet-a.ec2 -> vpc.subnet-b.rds: SQL
```

### Sequence Diagrams

```d2
shape: sequence_diagram
alice -> bob: Hello
bob -> alice: Hi
```

## Validation

Before rendering, validate that:
1. Source code is not empty
2. Source code is a non-empty string (no further static validation — D2 compiler handles syntax)

## Output

- **SVG**: Vector output (primary format)
- D2 produces high-quality SVG natively
- No PNG output (SVG is sufficient for D2 diagrams; PNG can be added later if needed)

## Layout Engine

- **Default**: ELK (Eclipse Layout Kernel) — produces better layouts for complex diagrams
- Set via `--layout=elk` flag
- ELK is bundled with D2 binary

## Dependencies

- D2 binary installed in backend Docker image
- No additional system dependencies beyond D2 itself

## Timeout

- Default: 60 seconds (shared with diagrams renderer, configurable via `RENDER_TIMEOUT`)
- On timeout: kill subprocess, set render_status to "error"

## Error Handling

| Error | Behavior |
|---|---|
| Empty source | Validation error returned before render attempt |
| D2 syntax error | Render fails, stderr captured as render_error |
| D2 binary not found | Render fails, render_error = "D2 not installed" |
| Timeout | Process killed, render_error = "Render timed out after {timeout}s" |

## Docker Image Changes

Add D2 binary to the backend Dockerfile:

```dockerfile
# Install D2
RUN curl -fsSL https://d2lang.com/install.sh | sh -s --
```

## Security

- Source code executed via D2 binary (no code execution — D2 is a declarative language)
- Temp directory isolated per render job
- Process runs as non-root user (UID 1000)
