# Project Instructions

## Development Workflow

### Spec-First Mandatory

Always update specs in `specs/` BEFORE any implementation. Commit spec changes separately from implementation.

### Spec Formats

- `specs/architecture/` — Markdown: system design, services, deployment, rendering pipeline
- `specs/api/` — OpenAPI YAML: REST API contracts for all endpoints
- `specs/data/` — Markdown: database schema, entity relationships, constraints
- `specs/behavior/` — Gherkin `.feature` files: acceptance criteria for all user-facing features
- `specs/rendering/` — Markdown: diagram engine specs, output formats, icon strategy

### TDD

Write tests derived from specs BEFORE implementation. Write code to make tests pass.

### Commit Conventions

1. Spec changes committed separately from implementation
2. Tests committed with implementation (since tests are written first, they fail until implementation is done)

## Architecture

- **Backend:** FastAPI + Uvicorn (Python 3.12) — `services/backend/`
- **Frontend:** React + Vite + TypeScript, served via nginx-unprivileged — `services/frontend/`
- **Database:** PostgreSQL 16 (K8s StatefulSet)
- **Migrations:** Alembic — `db/`

## Environments

| Environment | Namespace | Backend Port | Frontend Port |
|---|---|---|---|
| local-dev | `architect-dev` | NodePort 30010 | NodePort 30011 |
| staging | `architect-staging` | NodePort 30010 | NodePort 30011 |

## Key Rules

- **NEVER commit credentials, secrets, or sensitive data to the repo.** This includes: API keys, passwords, tokens, certificates, private keys, .env files, kubeconfig files, service account JSON files, database connection strings with passwords. The repo is public — any committed secret is compromised. If a secret is accidentally committed, rotate it immediately.
- **No project data in the git repo.** All runtime data is externalized (PostgreSQL PVC, output PVC). `data/` is gitignored.
- **Secrets as mounted files**, not environment variables.
- **Non-root containers** with read-only root filesystem and dropped capabilities.
- **TLS everywhere** via mkcert for local dev.
- **Independent versioning** per service (semantic versioning, starting at 0.1.0).

## Scripts

- `scripts/build-images.sh` — Build all Docker images
- `scripts/deploy-k8s.sh <namespace>` — Deploy to Kubernetes
- `scripts/setup-tls.sh <namespace>` — Generate and install TLS certificates
- `scripts/create-secrets.sh <namespace>` — Generate and install secrets
- `scripts/run-tests.sh` — Run all test suites
- `scripts/bump-version.sh <service> <version>` — Bump service version

## Default Language

Python for backend. TypeScript for frontend.
