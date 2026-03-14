# Services Architecture

## Overview

Architect consists of three services deployed as separate containers in Kubernetes:

1. **architect-backend** — FastAPI application serving the REST API
2. **architect-frontend** — React SPA served by nginx-unprivileged
3. **postgres** — PostgreSQL 16 database (StatefulSet)

A fourth component, **db-migrations**, runs as a Kubernetes Job to apply Alembic migrations before services start.

## Service Details

### architect-backend

| Property | Value |
|---|---|
| **Runtime** | Python 3.12, FastAPI + Uvicorn |
| **Port** | 8000 (internal) |
| **NodePort** | 30010 (local-dev) |
| **Image** | `architect-backend:<version>` (local), `ghcr.io/erikevenson/architect-backend:<version>` (GHCR) |
| **Health** | `/health/live` (liveness), `/health/ready` (readiness — checks DB connection) |

**Responsibilities:**
- REST API for all CRUD operations (clients, projects, versions, artifacts, ADRs, questions)
- Diagram rendering via Python `diagrams` library and D2
- Document rendering via Markdown + Jinja2
- PDF generation via WeasyPrint
- Artifact output management (filesystem-backed by PVC)

**Key dependencies (system):**
- Graphviz (for `diagrams` library)
- D2 binary (for D2 rendering)
- WeasyPrint system dependencies (fonts, cairo, pango)

**Security:**
- Runs as non-root user (UID 1000)
- Read-only root filesystem
- All capabilities dropped
- Secrets mounted as files (not environment variables)

### architect-frontend

| Property | Value |
|---|---|
| **Runtime** | nginx-unprivileged (Alpine) |
| **Ports** | 8080 (HTTP, health only), 8443 (HTTPS) |
| **NodePort** | 30011 (local-dev, maps to 8443) |
| **Image** | `architect-frontend:<version>` (local), `ghcr.io/erikevenson/architect-frontend:<version>` (GHCR) |
| **Health** | HTTP GET on port 8080 |

**Responsibilities:**
- Serve the React SPA (Vite-built static assets)
- TLS termination via mkcert certificates (local-dev)
- Reverse proxy `/api/` requests to architect-backend
- SPA fallback routing (`try_files $uri $uri/ /index.html`)

**Build:**
- Multi-stage Docker build: Node 20 (build) → nginx-unprivileged (production)
- Vite builds optimized production bundle

### postgres

| Property | Value |
|---|---|
| **Runtime** | PostgreSQL 16 (official image) |
| **Port** | 5432 (ClusterIP, headless service) |
| **Storage** | 1Gi PVC (`hostpath` StorageClass for local-dev) |
| **Image** | `postgres:16-alpine` |

**Responsibilities:**
- Persistent storage for all application data
- Headless service for stable DNS within namespace

**Backup:**
- Daily CronJob running `pg_dump` to backup PVC
- 7-day retention

### db-migrations

| Property | Value |
|---|---|
| **Runtime** | Python 3.12-slim |
| **Image** | `architect-db-migrations:<version>` (local), `ghcr.io/erikevenson/architect-db-migrations:<version>` (GHCR) |
| **Execution** | Kubernetes Job (run before service deployments) |

**Responsibilities:**
- Run `alembic upgrade head` against the database
- Applied separately from main kustomization (manual step)
- `restartPolicy: OnFailure`, `backoffLimit: 3`

## Inter-Service Communication

```
Browser → (HTTPS :8443) → nginx → (HTTP :8000) → FastAPI → (TCP :5432) → PostgreSQL
                                                          → (filesystem) → PVC (outputs)
```

- Frontend proxies API calls to backend via nginx reverse proxy
- Backend connects to PostgreSQL via async connection pool (asyncpg)
- Rendered artifacts are written to PVC-backed filesystem
- No inter-service gRPC or message queues needed (single backend service)

## Shared Patterns

- All containers run as non-root
- All containers use read-only root filesystem where possible
- Health checks on all services (liveness + readiness)
- Init containers wait for dependency readiness before starting
- Secrets mounted as files from Kubernetes secrets
