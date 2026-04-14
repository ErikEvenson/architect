# Knowledge Library and Embedding System Architecture

## Overview

The knowledge library is a collection of 285+ markdown files containing cloud architecture best practices, vendor-specific checklists, compliance frameworks, and design patterns. The embedding system enables semantic search over this library using pgvector.

## Components

### Knowledge Library Structure

```
knowledge/
├── general/          — universal concerns (compute, networking, security, etc.)
├── providers/        — vendor-specific files organized by provider
│   ├── aws/
│   ├── azure/
│   ├── gcp/
│   ├── nutanix/
│   ├── vmware/
│   └── ... (30+ providers)
├── patterns/         — architecture patterns (microservices, hybrid-cloud, etc.)
├── compliance/       — compliance frameworks (PCI, HIPAA, SOC2, etc.)
├── frameworks/       — well-architected frameworks
├── failures/         — anti-patterns and failure modes
├── WORKFLOW.md       — architecture session workflow
└── CONTRIBUTING.md   — knowledge file format guide
```

### Embedding Service (`src/services/embedding_service.py`)

- **Model:** all-MiniLM-L6-v2 (384-dimensional vectors, ONNX Runtime inference)
- **Tokenizer:** Truncation at 128 tokens per chunk
- **Storage:** pgvector extension in PostgreSQL (`knowledge_embeddings` table)
- **Index:** HNSW with cosine distance for approximate nearest neighbor search

### Indexing Process (`POST /api/v1/knowledge/reindex`)

1. Scan all `.md` files in the knowledge directory
2. Parse each file into sections (scope, checklist items, why-this-matters, common decisions)
3. Extract checklist items with priority tags ([Critical], [Recommended], [Optional])
4. Fetch vendor documentation from reference URLs in knowledge files
5. Index uploaded files from the current project
6. Generate embeddings for each chunk using all-MiniLM-L6-v2
7. Upsert into `knowledge_embeddings` table (skip unchanged content via SHA-256 hash)

Background task controls: cancel, pause, resume, timeout (default 5 minutes).

### Vendor Doc Fetcher

The vendor doc fetcher retrieves pages referenced in `## Reference Links` sections and indexes their extracted text alongside the knowledge files themselves.

- **User-Agent:** Requests are sent with a browser-style `User-Agent` string. The default httpx UA is blocked by common anti-bot protections (Akamai, Cloudflare bot-fight, and aggressively on `hpe.com`). The UA is configurable via `VENDOR_FETCH_USER_AGENT` for debugging.
- **Retry policy:** Transient failures (connection reset, read timeout, empty body on a 200 response, HTTP 429/5xx) are retried with exponential backoff up to `VENDOR_FETCH_MAX_RETRIES` attempts (default 2 retries, so 3 total attempts). Permanent failures (404, DNS failure) are not retried.
- **Failure visibility:** The reindex status response exposes both total failure counts and per-host failure counts in `progress.vendor_docs_failed` and `progress.vendor_docs_failed_by_host`. This lets operators detect vendor-side blocking patterns without having to grep the errors array.

### Search (`POST /api/v1/knowledge/search`)

1. Generate embedding for the query text
2. Cosine similarity search against pgvector HNSW index
3. Return top-k results (default 10) with source file, section, content, and score
4. Minimum score threshold: 0.35

### Knowledge API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/knowledge` | GET | Tree view of all knowledge files |
| `/knowledge/search` | POST/GET | Semantic search |
| `/knowledge/reindex` | POST | Trigger background reindexing |
| `/knowledge/reindex/status` | GET | Reindex progress and status |
| `/knowledge/reindex/stop` | POST | Cancel running reindex |
| `/knowledge/reindex/pause` | POST | Pause running reindex |
| `/knowledge/reindex/resume` | POST | Resume paused reindex |
| `/knowledge/{path}` | GET | Read specific knowledge file |

## Knowledge File Format

Each knowledge file follows a standard structure:
- `# Title`
- `## Scope` — what the file covers and doesn't cover
- `## Checklist` — actionable items tagged `[Critical]`, `[Recommended]`, `[Optional]`
- `## Why This Matters` — business and technical impact
- `## Common Decisions (ADR Triggers)` — architectural decisions this topic drives
- `## Reference Links` — official vendor documentation URLs
- `## See Also` — cross-references to related knowledge files

## Deployment Notes

- Knowledge files are baked into the backend Docker image at build time
- Reindexing must be triggered after deploying a new image with updated knowledge files
- The pgvector extension must be enabled in PostgreSQL (`CREATE EXTENSION vector;`)
- ONNX Runtime runs inference on CPU (no GPU required)
