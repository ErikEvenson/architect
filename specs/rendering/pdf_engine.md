# PDF Rendering Engine Specification

## Overview

The `weasyprint` engine generates professional PDF reports from architecture projects. It compiles all artifacts for a version into a single PDF with cover page, table of contents, and embedded diagrams.

## Execution Model

1. Receive render request for a PDF artifact
2. Collect all sibling artifacts in the same version (diagrams, documents)
3. Build HTML from Jinja2 templates: cover → TOC → content sections
4. Embed SVG diagrams inline, render markdown documents as HTML sections
5. Convert HTML to PDF via WeasyPrint
6. Write output PDF to artifact output directory

## Template Structure

```
templates/
├── pdf/
│   ├── report.html.j2    # Main report template
│   ├── cover.html.j2     # Cover page partial
│   ├── toc.html.j2       # Table of contents partial
│   └── section.html.j2   # Content section partial
```

### Cover Page
- Project name
- Client name
- Version number
- Client logo (if available)
- Generation date

### Table of Contents
- Auto-generated from artifact names and types
- Grouped by detail level (conceptual → logical → detailed → deployment)

### Content Sections
- Each artifact rendered as a section
- Diagrams: SVG embedded inline
- Documents: markdown rendered to HTML

## CSS Paged Media

```css
@page {
  size: A4;
  margin: 2cm;
  @bottom-center { content: counter(page); }
}
@page :first { margin-top: 0; }
h1, h2 { page-break-after: avoid; }
.diagram { page-break-inside: avoid; }
.cover { page-break-after: always; }
.toc { page-break-after: always; }
```

## Source Code

The PDF artifact's `source_code` field is unused — the report is compiled from sibling artifacts in the same version. The engine collects them automatically.

## Output

- **PDF**: Single file `report.pdf`
- A4 page size
- Page numbers in footer
- Fonts: system sans-serif (DejaVu Sans for broad Unicode support)

## Dependencies

- WeasyPrint (Python package, already in requirements)
- System fonts: `fonts-dejavu-core` in Docker image
- cairo, pango, gdk-pixbuf system libraries (WeasyPrint deps)

## Validation

- No source code validation needed (report is compiled from other artifacts)
- At least one sibling artifact should exist (warn if version has no other artifacts)

## Error Handling

| Error | Behavior |
|---|---|
| No sibling artifacts | Warning in PDF, empty content section |
| Missing SVG for diagram | Placeholder text in section |
| WeasyPrint error | render_status = "error", stderr captured |

## Docker Image Changes

Add WeasyPrint system dependencies to backend Dockerfile:

```dockerfile
RUN apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0
```
