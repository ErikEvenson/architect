# CI/CD Pipeline Design

## Overview

Two GitHub Actions workflows handle continuous integration and delivery:

1. **CI** (`ci.yml`) — Runs on PRs to `main`: build, lint, test
2. **Build+Push** (`build-push.yml`) — Runs on push to `main`: build multi-platform images, push to GHCR

## CI Workflow (`ci.yml`)

**Trigger:** Pull requests to `main`

### Backend Job
1. Build backend Docker image
2. Build test image on top (install dev dependencies)
3. Run `ruff check src/` (lint)
4. Run `pytest` with coverage

### Frontend Job
1. Set up Node 20
2. `npm ci`
3. `npm run build` (TypeScript + Vite)
4. `npm test` (Vitest)

### Kustomize Validation Job
1. Validate all overlays: `kubectl kustomize k8s/overlays/local-dev > /dev/null`
2. Validate staging: `kubectl kustomize k8s/overlays/staging > /dev/null`

## Build+Push Workflow (`build-push.yml`)

**Trigger:** Push to `main`

### Services Matrix
- `architect-backend`
- `architect-frontend`
- `architect-db-migrations`

### Steps per Service
1. Set up QEMU + Docker Buildx
2. Log in to GHCR (`ghcr.io`)
3. Read version from service config (`pyproject.toml` or `package.json`)
4. Build multi-platform image (`linux/amd64,linux/arm64`)
5. Push with tags: `VERSION`, short SHA, `latest`

### Cleanup Job
- Delete old untagged GHCR versions (keep 10)

## Version Management

- `scripts/bump-version.sh <service> <version>` updates:
  - Service config (`pyproject.toml` or `package.json`)
  - Kustomize overlay image tags
  - Migration job image tag (if backend)

## Docker Ignore

`.dockerignore` prevents unnecessary files from entering build context:
- `.git/`, `node_modules/`, `__pycache__/`, `data/`, tests, specs, docs
