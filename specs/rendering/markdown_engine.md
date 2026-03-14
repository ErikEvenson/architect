# Markdown Rendering Engine Specification

## Overview

The `markdown` engine renders Markdown source into styled HTML. It supports standard Markdown, common extensions (tables, fenced code, admonitions), and diagram embedding references.

## Execution Model

1. Receive Markdown source from artifact `source_code`
2. Process diagram embed references (`![diagram](artifact:{artifact_id})`)
3. Render Markdown to HTML using `python-markdown` + `pymdown-extensions`
4. Wrap in a styled HTML template
5. Write output HTML to artifact output directory

No subprocess needed — rendering happens in-process.

## Source Code Format

Standard Markdown with extensions:

```markdown
# Architecture Overview

## Network Topology

The following diagram shows the VPC layout:

![VPC Diagram](artifact:550e8400-e29b-41d4-a716-446655440000)

## Decision Log

| Decision | Status | Date |
|----------|--------|------|
| Use PostgreSQL | Accepted | 2026-03-01 |

!!! note
    This document is auto-generated from the architecture model.
```

## Diagram Embedding

Reference other artifacts by UUID:

```
![Alt text](artifact:{artifact_id})
```

During rendering, these are resolved to the artifact's SVG output path:
- If the referenced artifact has a successful render with SVG output, embed the SVG inline or as an `<img>` tag
- If the artifact hasn't been rendered, show a placeholder with the artifact name

## Markdown Extensions

Enabled via `pymdown-extensions`:
- **Tables** — pipe tables
- **Fenced code** — with syntax highlighting via `codehilite`
- **Admonitions** — `!!! note`, `!!! warning`, etc.
- **Table of contents** — `[TOC]` placeholder
- **Task lists** — `- [x]` checkboxes

## Output

- **HTML**: Single HTML file with inline CSS styling
- Styled with a clean, readable stylesheet (similar to GitHub markdown rendering)
- Output filename: `document.html`

## Validation

Before rendering, validate that:
1. Source code is not empty

## Templates

Minimal Jinja2 templates provide starting-point heading structures:

### Architecture Document
```markdown
# {{ project_name }} — Architecture Document

## Overview

## Requirements

## Architecture

## Infrastructure

## Security

## Operations
```

### Runbook
```markdown
# {{ project_name }} — Runbook

## Service Overview

## Prerequisites

## Deployment Steps

## Monitoring

## Troubleshooting

## Rollback Procedure
```

Templates are optional starting points — users edit freely after creation.

## Error Handling

| Error | Behavior |
|---|---|
| Empty source | Validation error |
| Invalid diagram reference | Placeholder shown, no error |
| Markdown syntax issues | Best-effort rendering (Markdown is forgiving) |
