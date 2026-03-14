# Deployment Architecture

## Environments

| Environment | Namespace | Image Source | Backend Port | Frontend Port |
|---|---|---|---|---|
| **local-dev** | `architect-dev` | Local Docker build | NodePort 30010 | NodePort 30011 |
| **staging** | `architect-staging` | GHCR (`ghcr.io/erikevenson/architect-*`) | NodePort 30010 | NodePort 30011 |

## Kubernetes Platform

- **Local dev:** Docker Desktop with built-in Kubernetes
- **Staging:** Lima VM with k3s (same as Galaxy)

## Namespace Isolation

Architect runs in its own namespace, separate from Galaxy:
- `architect-dev` — local development
- `architect-staging` — staging environment

Port assignments avoid conflict with Galaxy (30000-30002):
- Backend: 30010
- Frontend: 30011

## Kustomize Structure

```
k8s/
├── base/                    # Shared manifests (no namespace set)
│   ├── kustomization.yaml   # Resources: configmaps, secrets-template excluded
│   ├── namespace.yaml       # Namespace definitions (applied separately)
│   ├── configmaps.yaml      # Backend config, frontend config, nginx config
│   ├── secrets-template.yaml # Reference only, never applied directly
│   └── migration-job.yaml   # Alembic migration Job (applied separately)
├── infrastructure/
│   ├── kustomization.yaml
│   └── postgres.yaml        # StatefulSet + headless service + backup
├── services/
│   ├── kustomization.yaml
│   ├── backend.yaml          # Deployment + NodePort service
│   └── frontend.yaml         # Deployment + NodePort service
└── overlays/
    ├── local-dev/
    │   └── kustomization.yaml  # namespace: architect-dev, bare image tags
    └── staging/
        └── kustomization.yaml  # namespace: architect-staging, GHCR image refs
```

### Overlay Strategy

- **Base** has no namespace — overlays set `namespace:` via kustomize
- **local-dev** uses bare image names (built locally via `build-images.sh`)
- **staging** uses full GHCR paths with version tags

## Deployment Order

1. Create namespace: `kubectl create namespace architect-dev`
2. Set up TLS: `scripts/setup-tls.sh architect-dev`
3. Create secrets: `scripts/create-secrets.sh architect-dev`
4. Deploy infrastructure + services: `scripts/deploy-k8s.sh architect-dev`
5. Run migrations: `kubectl apply -f k8s/base/migration-job.yaml -n architect-dev`

The `deploy-k8s.sh` script handles steps 1 and 4. Steps 2, 3, and 5 are run separately.

## TLS

- Local dev uses `mkcert` for trusted localhost certificates
- TLS secret (`architect-tls`) mounted into nginx container
- nginx serves HTTPS on port 8443, health checks on HTTP port 8080
- Backend does not terminate TLS (nginx handles it)

## Secrets Management

Secrets are created via `scripts/create-secrets.sh` which generates:
- `postgres-password` — PostgreSQL password (auto-generated)

Secrets are mounted as files into containers (not environment variables):
- Backend reads from `SECRETS_DIR` path
- PostgreSQL reads `POSTGRES_PASSWORD` from mounted secret file

## Persistent Storage

| PVC | Size | StorageClass | Purpose |
|---|---|---|---|
| `postgres-data` | 1Gi | hostpath | PostgreSQL data |
| `architect-outputs` | 1Gi | hostpath | Rendered artifacts (diagrams, docs, PDFs) |
| `postgres-backup` | 1Gi | hostpath | Database backups |

## ConfigMaps

- `architect-config` — Backend service configuration (database host, log level)
- `frontend-config` — Runtime JavaScript config (`window.ARCHITECT_CONFIG`)
- `nginx-config` — nginx configuration with reverse proxy to backend

## Resource Limits

Initial development limits (adjust for production):

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---|---|---|---|---|
| backend | 100m | 500m | 128Mi | 512Mi |
| frontend | 50m | 200m | 64Mi | 128Mi |
| postgres | 100m | 500m | 256Mi | 512Mi |
