# Architect

Cloud architecture design tool for generating production-grade deliverables — diagrams, documents, and PDF reports.

Architect combines a structured knowledge library with an interactive design workflow to produce comprehensive architecture documentation for cloud infrastructure projects.

## What It Does

- **Conversational architecture design** — Claude Code acts as the architect, using a knowledge library to systematically ask questions, identify gaps, and make decisions
- **Architectural Decision Records (ADRs)** — every design decision is documented with context, decision, and consequences
- **Question tracking** — clarifying questions are tracked per project with status and category
- **Diagram generation** — Python `diagrams` library (AWS, Azure, GCP, Nutanix, VMware, OpenStack icons) and D2 for flexible layouts
- **Document rendering** — Markdown to styled HTML with diagram embedding
- **PDF export** — professional reports with cover page, table of contents, and embedded diagrams
- **Knowledge library** — extensible markdown-based best practices, organized by provider, pattern, and compliance framework

## Architecture

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn (Python 3.12) |
| Frontend | React + Vite + TypeScript + Tailwind CSS |
| Database | PostgreSQL 16 (K8s StatefulSet) |
| Diagrams | Python `diagrams` + D2 |
| PDFs | WeasyPrint + Jinja2 |
| Migrations | Alembic |
| Deployment | Kubernetes + Kustomize |

## Quick Start

### Prerequisites

- Docker Desktop with Kubernetes enabled
- `mkcert` installed
- `kubectl` configured

### Deploy

```bash
# Build images
scripts/build-images.sh

# Set up namespace, TLS, and secrets
kubectl create namespace architect-dev
scripts/setup-tls.sh architect-dev
scripts/create-secrets.sh architect-dev

# Deploy
scripts/deploy-k8s.sh architect-dev

# Run database migrations
kubectl apply -f k8s/base/migration-job.yaml -n architect-dev
```

### Access

- **Frontend**: https://localhost:30011
- **API docs**: http://localhost:30010/docs

## Project Structure

```
architect/
├── services/
│   ├── backend/          # FastAPI application
│   │   ├── src/
│   │   │   ├── api/      # REST API routers
│   │   │   ├── models/   # SQLAlchemy ORM models
│   │   │   ├── schemas/  # Pydantic request/response schemas
│   │   │   ├── services/ # Business logic
│   │   │   ├── rendering/# Diagram, D2, Markdown, PDF renderers
│   │   │   └── templates/# Jinja2 templates (PDF, documents)
│   │   └── tests/        # pytest test suite
│   └── frontend/         # React SPA
│       └── src/
│           ├── api/      # API client and types
│           ├── components/# UI components
│           ├── pages/    # Route pages
│           └── stores/   # Zustand state
├── knowledge/            # Architecture knowledge library
│   ├── general/          # Universal concerns (8 files)
│   ├── providers/        # Provider-specific (AWS, Azure, GCP, etc.)
│   ├── patterns/         # Architecture patterns (three-tier, microservices, etc.)
│   ├── compliance/       # Compliance frameworks (PCI, HIPAA, SOC2, FedRAMP)
│   ├── frameworks/       # Well-Architected Frameworks
│   └── failures/         # Anti-patterns and failure modes
├── specs/                # Specifications (architecture, API, behavior)
├── db/                   # Alembic migrations
├── k8s/                  # Kubernetes manifests (Kustomize)
│   ├── base/
│   ├── infrastructure/
│   ├── services/
│   └── overlays/         # local-dev, staging
└── scripts/              # Build, deploy, and utility scripts
```

## Data Model

```
Client (1) → (*) Project (1) → (*) Version (1) → (*) Artifact
                            (1) → (*) ADR
                            (1) → (*) Question
```

- **Client** — organization the architecture is for
- **Project** — specific architecture engagement
- **Version** — architecture iteration (semver)
- **Artifact** — diagram, document, or PDF report
- **ADR** — architectural decision record (sequential per project)
- **Question** — clarifying question with status and category

## API

All endpoints under `/api/v1/`. See full OpenAPI spec at `/docs` when running.

| Resource | Endpoints |
|----------|-----------|
| Clients | CRUD at `/clients` |
| Projects | CRUD at `/clients/{id}/projects` |
| Versions | CRUD at `/projects/{id}/versions` |
| Artifacts | CRUD at `/versions/{id}/artifacts` |
| ADRs | CRUD + supersede at `/projects/{id}/adrs` |
| Questions | CRUD + filter at `/projects/{id}/questions` |
| Rendering | Trigger + outputs at `/versions/{id}/artifacts/{id}/render` |
| Templates | List + render at `/templates` |
| Knowledge | Browse at `/knowledge` |

## Rendering Engines

| Engine | Use Case | Output |
|--------|----------|--------|
| `diagrams_py` | Cloud architecture with provider icons | SVG + PNG (300 DPI) |
| `d2` | Sequence diagrams, flowcharts | SVG |
| `markdown` | Architecture documents | HTML |
| `weasyprint` | PDF reports | PDF |

## Knowledge Library

The knowledge library drives the architecture design workflow. Files are organized by:

- **General** — universal concerns: compute, networking, data, security, observability, DR, cost, deployment
- **Providers** — AWS, Azure, GCP, Nutanix, VMware, OpenStack specific guidance
- **Patterns** — three-tier web, microservices, data pipeline, static site, hybrid cloud
- **Compliance** — PCI DSS, HIPAA, SOC2, FedRAMP control mappings
- **Frameworks** — AWS/Azure/GCP Well-Architected Framework review checklists
- **Failures** — real-world anti-patterns and failure modes

Browse the library in the UI via the **Knowledge** link in the header.

## Scripts

| Script | Purpose |
|--------|---------|
| `build-images.sh` | Build all Docker images |
| `deploy-k8s.sh` | Deploy to Kubernetes |
| `setup-tls.sh` | Generate mkcert TLS certificates |
| `create-secrets.sh` | Generate and install K8s secrets |
| `run-tests.sh` | Run all test suites |
| `bump-version.sh` | Bump service version |

## Development

### Backend tests

```bash
cd services/backend
pip install -e ".[dev]" aiosqlite
pytest tests/ -v
```

### Spec-first workflow

1. Write/update specs in `specs/` before implementation
2. Commit specs separately
3. Write tests derived from specs
4. Implement to make tests pass
5. Commit implementation

## License

Private repository.
