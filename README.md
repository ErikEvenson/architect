# Architect

Cloud architecture design tool for generating production-grade deliverables — diagrams, documents, and PDF reports.

Architect combines a structured knowledge library with an interactive design workflow to produce comprehensive architecture documentation for cloud infrastructure projects.

## What It Does

- **Conversational architecture design** — LLM-powered chat interface with tool-call loop for creating artifacts, recording decisions, and managing questions, backed by RAG over the knowledge library
- **Architectural Decision Records (ADRs)** — every design decision is documented with context, decision, and consequences
- **Question tracking** — clarifying questions are tracked per project with status and category
- **Diagram generation** — Python `diagrams` library (AWS, Azure, GCP, Nutanix, VMware, OpenStack icons) and D2 for flexible layouts
- **Document rendering** — Markdown to styled HTML with diagram embedding
- **PDF export** — professional reports with cover page, table of contents, and embedded diagrams
- **Knowledge library** — 330+ markdown files covering 45+ providers, architecture patterns, compliance frameworks, certifications, and training resources
- **Coverage tracking** — track which knowledge library checklist items have been addressed in the design
- **Inventory management** — attach VM inventories, network data, and analysis to versions
- **File uploads** — attach reference documents and data files to versions
- **Vector search (RAG)** — semantic search over the knowledge library, vendor docs, and uploaded files using pgvector embeddings, with a web UI for index management (start, stop, pause, resume, clear, timeout, progress tracking)
- **MCP server** — public [`@eevenson/architect-knowledge-mcp`](https://www.npmjs.com/package/@eevenson/architect-knowledge-mcp) npm package exposes the knowledge library to Claude Desktop, Claude Code, Cursor, and any MCP-compatible client

## MCP Server

The knowledge library is available as a standalone MCP server for use with any MCP-compatible client. No deployment needed — it runs locally via npx:

```json
{
  "mcpServers": {
    "architect-knowledge": {
      "command": "npx",
      "args": ["@eevenson/architect-knowledge-mcp"]
    }
  }
}
```

Three tools are exposed: `search_knowledge`, `list_categories`, and `read_file`. The server fetches knowledge files from this public repo and caches them locally. No client data is ever included.

See the [architect-knowledge-mcp](https://github.com/ErikEvenson/architect-knowledge-mcp) repo for full documentation.

## Architecture

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Uvicorn (Python 3.12) |
| Chat/LLM | SSE streaming, OpenAI-compatible API (local or Anthropic) |
| Frontend | React + Vite + TypeScript + Tailwind CSS |
| Database | PostgreSQL 16 + pgvector (K8s StatefulSet) |
| Vector Search | pgvector + ONNX Runtime (all-MiniLM-L6-v2) |
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
├── knowledge/            # Architecture knowledge library (330+ files)
│   ├── general/          # Universal concerns
│   ├── providers/        # Provider-specific (30+ vendors: AWS, Azure, GCP, Nutanix, VMware, etc.)
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
                                              (1) → (*) InventoryItem
                                              (1) → (*) Upload
                                              (1) → (*) CoverageItem
```

- **Client** — organization the architecture is for
- **Project** — specific architecture engagement
- **Version** — architecture iteration (semver), each version is an independent design
- **Artifact** — diagram, document, or PDF report
- **ADR** — architectural decision record (sequential per version)
- **Question** — clarifying question with status and category
- **InventoryItem** — VM inventory, network data, or analysis attached to a version
- **Upload** — reference documents and files (PVC-backed, 100MB limit)
- **CoverageItem** — tracks which knowledge library checklist items are addressed
- **KnowledgeEmbedding** — vector embedding of a knowledge library chunk

## RAG Architecture

Architect uses Retrieval-Augmented Generation (RAG) to enhance the knowledge library with semantic search. This runs alongside the existing rule-based file loading — not as a replacement.

### How It Works

```
Knowledge Files (330+ .md)    Vendor Docs (550+ URLs)    Uploaded Files
        │                           │                        │
        ▼                           ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Markdown Parser │    │ Concurrent Fetch  │    │  Text Extraction │
│ Extract items   │    │ (20 parallel)     │    │  .md .txt .csv   │
│ per checklist   │    │ Paragraph Chunk   │    │  .json .yaml etc │
└─────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                        │
        └───────────────────────┼────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────┐
│         all-MiniLM-L6-v2 (ONNX Runtime)             │
│         384-dimensional normalized embeddings         │
│         Parallel threads, pipelined DB writes         │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│              PostgreSQL 16 + pgvector                 │
│  knowledge_embeddings table with HNSW cosine index   │
│  Content-hash deduplication for incremental reindex  │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│              Retrieval (dual strategy)                │
│                                                      │
│  1. Rule-based: load all files for active provider,  │
│     pattern, and compliance scope (guarantees no     │
│     Critical items are missed)                       │
│                                                      │
│  2. Vector search: cosine similarity against query   │
│     text, surfaces related items from NON-loaded     │
│     files (cross-cutting discovery)                  │
└──────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────┐
│              Integration Points                       │
│                                                      │
│  • After Q&A pairs — inline suggestions in response  │
│  • After rule-based loading — additional file recs   │
│  • During artifact generation — cross-references     │
└──────────────────────────────────────────────────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Vector store | pgvector (PostgreSQL extension) | Store and query 384-dim embeddings via HNSW index |
| Embedding model | `all-MiniLM-L6-v2` (ONNX Runtime) | Generate embeddings locally with parallel threads, no external API |
| Chunking | Custom markdown parser | Extract individual checklist items with `[Critical]`/`[Recommended]`/`[Optional]` tags |
| Indexing | Background task with web UI controls | Start, stop, pause, resume, clear, configurable timeout, real-time progress |
| Data sources | Knowledge files + vendor docs + uploads | Indexes all three sources; vendor docs fetched concurrently (20 parallel) |
| Search | Cosine similarity with min-score filter | Configurable top-k, file exclusion, priority filtering |
| Suggestions | Inline in API responses | `suggestions` array on question responses when answers are provided |

### Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Vector store | pgvector in existing PostgreSQL | No new infrastructure; single database for all data |
| Embedding runtime | ONNX Runtime (not PyTorch) | ~300 MB RAM vs ~3 GB; parallel thread support; no CUDA dependency |
| Chunk granularity | Individual checklist items | Matches the workflow's unit of work (one question per item) |
| Indexing model | Background task with server-side state | Progress survives page navigation; supports pause/resume/cancel |
| Vendor doc fetching | 20-way concurrent with semaphore | Reduces fetch phase from minutes to seconds |
| Embedding pipeline | Pre-fetch next batch during DB commit | Overlaps CPU-bound inference with I/O-bound writes |
| Deduplication | SHA-256 content hash | Only re-embeds changed chunks on reindex |
| Fallback | Graceful degradation | If embeddings aren't indexed, suggestions are empty — never errors |
| Dual retrieval | Rule-based primary + vector secondary | Rules guarantee completeness; vectors add discovery |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/knowledge/search` | POST | Semantic search with query, top-k, min-score, file exclusion, priority filter |
| `/knowledge/search` | GET | Search via query params (fetch-only clients) |
| `/knowledge/reindex` | POST | Start background reindex (knowledge files, vendor docs, uploads) |
| `/knowledge/reindex/status` | GET | Index status, background task state, and progress |
| `/knowledge/reindex/stop` | POST | Cancel a running reindex |
| `/knowledge/reindex/pause` | POST | Pause a running reindex between batches |
| `/knowledge/reindex/resume` | POST | Resume a paused reindex |
| `/knowledge/reindex/clear` | POST | Delete all embeddings from the index |
| `/knowledge/reindex/timeout` | POST | Set or clear the reindex timeout |

## API

All endpoints under `/api/v1/`. See full OpenAPI spec at `/docs` when running.

| Resource | Endpoints |
|----------|-----------|
| Clients | CRUD at `/clients` |
| Projects | CRUD at `/clients/{id}/projects` |
| Versions | CRUD at `/projects/{id}/versions` |
| Artifacts | CRUD + clone at `/versions/{id}/artifacts` |
| ADRs | CRUD at `/versions/{id}/adrs` |
| Questions | CRUD + filter at `/versions/{id}/questions` |
| Inventory | CRUD at `/versions/{id}/inventory` |
| Uploads | Upload/download/delete at `/versions/{id}/uploads` |
| Coverage | CRUD + summary at `/versions/{id}/coverage` |
| Rendering | Trigger + outputs + PDF export at `/versions/{id}/artifacts/{id}/render` |
| Chat | SSE streaming at `/chat` |
| Templates | List + render at `/templates` |
| Knowledge | Browse + vector search + reindex at `/knowledge` |

## Rendering Engines

| Engine | Use Case | Output |
|--------|----------|--------|
| `diagrams_py` | Cloud architecture with provider icons | SVG + PNG (300 DPI) |
| `d2` | Sequence diagrams, flowcharts | SVG |
| `markdown` | Architecture documents | HTML |
| `weasyprint` | PDF reports | PDF |

## Knowledge Library

The knowledge library drives the architecture design workflow. Files are organized by:

- **General** (65+ files) — compute, networking, data, security, observability, DR, cost, storage, identity, AI/ML services, ITSM, messaging patterns, supply chain security, performance testing, email migration, certification/training, and more
- **Providers** (230+ files) — 45+ vendors: AWS, Azure, GCP, Nutanix, VMware, OpenStack, OpenShift, Kubernetes, HashiCorp, Cisco, Dell, HPE, NetApp, Pure Storage, Snowflake, Databricks, Confluent/Kafka, MongoDB, Redis, Elasticsearch, Cassandra, CrowdStrike, Okta, CyberArk, Dynatrace, New Relic, GitLab, GitHub, Jenkins, ArgoCD, FluxCD, Cloudflare, RabbitMQ, Juniper, Arista, and more
- **Patterns** (30+ files) — three-tier web, microservices, hybrid cloud, zero trust, application modernization, security operations, hypervisor migration, datacenter relocation, managed cloud services, and more
- **Compliance** (12 files) — PCI DSS, HIPAA, SOC2, FedRAMP, GDPR, CCPA/CPRA, ISO 27001, NIST 800-171/CMMC, SOX, CSA CCM, CJIS, ITAR
- **Frameworks** (3 files) — AWS/Azure/GCP Well-Architected Framework review checklists
- **Failures** (5 files) — real-world anti-patterns for networking, data, scaling, security, and deployment

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

1. Write/update specs in `specs/` **before** implementation
2. Commit specs separately from implementation
3. Write tests derived from specs (TDD)
4. Implement to make tests pass
5. Commit implementation with tests

### Specs

| Directory | Contents |
|-----------|----------|
| `specs/api/` | OpenAPI 3.1 spec for all REST endpoints |
| `specs/architecture/` | System design: services, chat/LLM, knowledge/embeddings, rendering, CI/CD, deployment |
| `specs/data/` | Database schema: 11 tables with columns, indexes, constraints, cascade behavior |
| `specs/behavior/` | Gherkin acceptance criteria: 13 feature files covering all user-facing features |
| `specs/rendering/` | Rendering engine specs: D2, diagrams-py, markdown, PDF, icons |

## License

MIT License. See [LICENSE](LICENSE).
