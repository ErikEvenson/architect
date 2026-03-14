# Harbor Container Registry

## Checklist

- [ ] **[Critical]** Configure HTTPS with valid TLS certificates — Docker daemon and Kubernetes refuse to pull from HTTP registries by default; all clients must trust the CA
- [ ] **[Critical]** Set up authentication backend (local DB, LDAP/AD, or OIDC) and disable anonymous access to prevent unauthorized image pushes
- [ ] **[Critical]** Enable vulnerability scanning with scan-on-push policy so every image is scanned by Trivy before deployment
- [ ] **[Critical]** Create robot accounts with scoped permissions for CI/CD pipelines instead of using human user credentials
- [ ] **[Critical]** Configure garbage collection on a recurring schedule to reclaim storage from deleted image layers (without GC, storage grows unbounded)
- [ ] **[Recommended]** Set up image replication between Harbor instances for disaster recovery or multi-site deployments
- [ ] **[Recommended]** Define image retention policies per project (by tag count, age, or label) to automatically clean up old images
- [ ] **[Recommended]** Configure proxy cache projects for Docker Hub and GHCR to avoid rate limits (Docker Hub: 100 pulls/6h anonymous, 200 authenticated)
- [ ] **[Recommended]** Enable image signing with Cosign or Notation and enforce content trust policies to prevent deploying unsigned images
- [ ] **[Recommended]** Deploy external PostgreSQL and Redis for production — the embedded database is not suitable for HA or data durability
- [ ] **[Recommended]** Use S3-compatible object storage (MinIO, AWS S3, Swift) for image blob storage instead of local filesystem
- [ ] **[Optional]** Configure webhook notifications to trigger CI/CD pipelines on image push, scan completion, or replication events
- [ ] **[Optional]** Set up tag immutability rules on production projects to prevent overwriting released image tags
- [ ] **[Optional]** Enable audit logging and forward logs to a centralized logging system for compliance and troubleshooting
- [ ] **[Optional]** Configure quota management per project to prevent any single team from consuming all available storage

## Why This Matters

Harbor is the most widely adopted open-source container registry for enterprises running Kubernetes. Unlike Docker Hub or minimal registries (Docker's `registry:2`), Harbor provides RBAC, vulnerability scanning, image signing, replication, and audit logging in a single platform. Choosing Harbor means you control where your container images live, what security policies are enforced before deployment, and how images flow between environments. A misconfigured registry is a supply chain security risk — images without scanning may contain known CVEs, unsigned images may be tampered with, and unrestricted access lets anyone push or pull sensitive application code.

For air-gapped, regulated, or multi-cloud environments, Harbor is often the only viable option since public registries are either inaccessible or violate data residency requirements. The proxy cache feature also solves a practical problem: Docker Hub rate limits cause production outages when nodes pull images during scaling events.

## Common Decisions (ADR Triggers)

### ADR: Deployment Method — Docker Compose vs Helm vs Operator

**Docker Compose** is the simplest path for a single-node deployment. Harbor's official installer generates a `docker-compose.yml` with all components (core, portal, registry, job service, database, Redis, Trivy). Suitable for dev/test or small teams (<50 users). Limitation: no built-in HA, backup requires stopping services or filesystem snapshots.

**Helm chart** (`goharbor/harbor` chart) is the standard for Kubernetes deployments. Supports external database/Redis, ingress configuration, PVC or S3 storage, and scales horizontally. Use this for any production Kubernetes environment. Requires an existing K8s cluster and ingress controller.

**Harbor Operator** (Kubernetes operator) provides declarative CRDs (`HarborCluster`) for full lifecycle management including automated upgrades, backup/restore, and day-2 operations. More opinionated but reduces operational burden. Still maturing compared to the Helm chart.

**Decision trigger:** If deploying on K8s, choose Helm (stable, well-documented) or Operator (if you want CRD-driven lifecycle). If no K8s cluster exists, Docker Compose for simplicity.

### ADR: Authentication Backend

- **Local database**: Zero dependencies, suitable for small teams. No SSO, users must manage separate credentials.
- **LDAP/Active Directory**: Enterprise standard, centralizes user management. Configure `ldap_url`, `ldap_base_dn`, `ldap_search_filter`. Users authenticate with corporate credentials. Groups map to Harbor project roles.
- **OIDC (Keycloak, Dex, Azure AD, Google)**: Modern SSO, supports MFA. Harbor acts as an OIDC client — configure `oidc_endpoint`, `client_id`, `client_secret`, `scope`. Groups claim maps to Harbor roles. Preferred for organizations already using an identity provider.

**Decision trigger:** Use OIDC if you have an identity provider. Use LDAP if AD is the corporate standard and no OIDC proxy exists. Use local DB only for POC or isolated environments.

### ADR: Storage Backend for Image Blobs

- **Local filesystem**: Simple, fast (NVMe/SSD). Single point of failure, hard to scale, backup requires filesystem tools. Only for single-node or dev.
- **S3-compatible (AWS S3, MinIO, Ceph RGW)**: Durable, scalable, enables HA (multiple Harbor instances share storage). MinIO for on-prem S3 compatibility. Required for any HA deployment.
- **OpenStack Swift**: Native option for OpenStack environments.
- **Azure Blob / GCS**: Use when Harbor runs on the respective cloud.

**Decision trigger:** Always use object storage for production. Local filesystem only for dev/test single-node deployments.

### ADR: Vulnerability Scanning Strategy

Trivy is included by default in Harbor 2.x and requires no additional infrastructure. Scan-on-push ensures every image is evaluated. Key decisions:

- **Scan-on-push**: Enable per project. Adds ~10-30 seconds per push depending on image size and vulnerability DB freshness.
- **Prevent deployment of vulnerable images**: Use Harbor's "Prevent vulnerable images from running" policy at the project level. Set a severity threshold (Critical, High, Medium). Combine with Kubernetes admission controllers (OPA/Gatekeeper, Kyverno) that check Harbor's scan results before allowing pod creation.
- **Scan schedule**: Configure periodic re-scanning (daily/weekly) to catch newly disclosed CVEs in existing images.

### ADR: Image Replication Topology

- **Push-based**: Source Harbor pushes images to remote registries on push/tag events. Lower latency for consumers at the remote site. Source must have network access to the destination.
- **Pull-based**: Destination Harbor pulls images from the source on a schedule or trigger. Useful when the destination is behind a firewall and initiates outbound connections.
- **Hub-and-spoke**: Central Harbor replicates to regional instances. Common for multi-region Kubernetes deployments.
- **Cross-registry**: Harbor can replicate to/from Docker Hub, ECR, GCR, ACR, Quay, and other Harbor instances. Useful for mirroring third-party images into your private registry.

**Decision trigger:** Multi-site or DR requirements trigger this ADR. Choose push for real-time, pull for firewalled destinations.

## Reference Architectures

### Single-Node Development/Test

```
[Docker Compose Host]
  harbor-core (API + UI)
  harbor-portal (web UI)
  registry (image storage - local filesystem /data/registry)
  harbor-db (PostgreSQL 13 - embedded)
  redis (embedded)
  trivy-adapter (vulnerability scanning)
  harbor-jobservice (replication, GC, scan jobs)
  nginx (reverse proxy, TLS termination)

Storage: Local disk, /data mount point
TLS: Self-signed cert or mkcert for local dev
Auth: Local database
Resources: 2 vCPU, 4 GB RAM, 100 GB disk
```

### Production HA on Kubernetes

```
                    [Load Balancer / Ingress]
                           |
          -----------------+-----------------
          |                |                |
   [Harbor Core x3]  [Harbor Portal x2]  [Registry x2]
          |                                    |
   [Harbor JobService x2]              [S3 / MinIO Cluster]
          |                                (image blobs)
   [External PostgreSQL]    [External Redis Sentinel/Cluster]
     (HA, replicated)         (session + job queue)

TLS: cert-manager with Let's Encrypt or internal CA
Auth: OIDC (Keycloak / Azure AD)
Scanning: Trivy (adapter runs as sidecar or separate deployment)
Storage: MinIO cluster (4+ nodes, erasure coding) or AWS S3
Ingress: nginx-ingress or Traefik with TLS passthrough
Resources per Harbor core: 2 vCPU, 4 GB RAM
PostgreSQL: 4 vCPU, 8 GB RAM, 100 GB SSD
Redis: 2 vCPU, 4 GB RAM
MinIO: 4 nodes, 4 vCPU, 8 GB RAM, 1 TB each
```

### Multi-Site with Replication

```
[Site A - Primary]                    [Site B - DR/Regional]
  Harbor (full deployment)    --->      Harbor (full deployment)
  S3 storage (local)        replicate   S3 storage (local)
  PostgreSQL (primary)                  PostgreSQL (independent)

Replication: Push-based, triggered on image push
Scope: Replicate production projects only
Filter: By tag pattern (e.g., v*.*.*, release-*)
Bandwidth: Schedule replication during off-peak if constrained

[CI/CD Pipeline]
  1. Build image
  2. Push to Site A Harbor
  3. Scan completes (Trivy)
  4. If scan passes → auto-replicate to Site B
  5. K8s clusters at both sites pull from local Harbor
```

### Proxy Cache for Rate Limit Mitigation

```
[Kubernetes Cluster]
  |
  +-- imagePullPolicy: IfNotPresent
  |
  +-- /v2/dockerhub-proxy/library/nginx/...
        |
  [Harbor Proxy Cache Project "dockerhub-proxy"]
        |
        +-- Cache hit → serve from local S3/disk
        +-- Cache miss → pull from Docker Hub → cache → serve
        |
  [Docker Hub]  (rate limited: 100 pulls/6h anonymous)

Configuration:
  - Create project type: "Proxy Cache"
  - Endpoint: https://registry-1.docker.io
  - Credential: Docker Hub account (for 200 pulls/6h limit)
  - K8s: Rewrite image references or use containerd mirror config
```
