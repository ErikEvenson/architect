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

- **NEVER commit project data to the git repo. This is the #1 rule.** Client data, VM inventories, architecture session content, uploaded files, questions, answers, ADRs, and any data entered through the API or UI must NEVER appear in git. All project data lives exclusively in PostgreSQL (PVC) and the output volume (PVC). The `data/` directory is gitignored. This includes: no client names, no server names, no IP addresses, no infrastructure details, no site names, no VM lists — nothing that came from a client engagement belongs in the repo. When writing code, use generic examples in comments and specs (e.g., "vm_inventory", "server_list"), never real client data.
- **NEVER commit credentials, secrets, or sensitive data to the repo.** This includes: API keys, passwords, tokens, certificates, private keys, .env files, kubeconfig files, service account JSON files, database connection strings with passwords. The repo is public — any committed secret is compromised. If a secret is accidentally committed, rotate it immediately.
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

## Architecture Sessions

For architecture design sessions, read `knowledge/WORKFLOW.md` first.

### Knowledge Library Maintenance

- **Checklists are dynamically generated.** Never rely on a hardcoded list of knowledge categories. At the start of each session, scan `knowledge/` to discover ALL available files. New knowledge files are added regularly.
- **After every session, run a retrospective** (Step 10 in WORKFLOW.md). Identify any topics that came up during the session that no knowledge file covers. Create GitHub issues labeled `knowledge-gap` for each.
- **When adding a new knowledge file**, update the WORKFLOW.md Category Coverage Gate if the new file represents a conditional category (e.g., "include when VDI workloads are in scope").
- **Every knowledge file must follow the standard format**: Scope, Checklist with [Critical]/[Recommended]/[Optional] tags, Why This Matters, Common Decisions (ADR Triggers). See existing files for examples.
- **Cross-reference knowledge files during design.** When a component is added to the architecture, find and load the relevant knowledge file(s). Do not rely solely on general knowledge — the knowledge library contains specific checklist items that prevent common mistakes.

## Default Language

Python for backend. TypeScript for frontend.
