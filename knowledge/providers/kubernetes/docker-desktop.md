# Docker Desktop Kubernetes

## Checklist

- [ ] **[Critical]** Allocate sufficient CPU and memory in Docker Desktop preferences (Settings > Resources); Kubernetes shares resources with Docker containers, default 2GB is often insufficient for multi-service workloads
- [ ] **[Critical]** Verify kubectl context is set to docker-desktop (`kubectl config use-context docker-desktop`) before running commands to avoid accidentally targeting a production cluster
- [ ] **[Critical]** Understand data persistence behavior: persistent volumes survive pod restarts but are lost when "Reset Kubernetes Cluster" is used in Docker Desktop settings
- [ ] **[Recommended]** Use Kustomize overlays pattern (base + local-dev overlay) to configure hostpath storage, NodePorts, and reduced resource requests for local development while keeping production manifests separate
- [ ] **[Recommended]** Build container images locally with `docker build` — images are immediately available to Kubernetes without pushing to a registry because Docker Desktop shares the container runtime
- [ ] **[Recommended]** Test services via NodePort (localhost:nodePort) or LoadBalancer (services receive localhost IP) to validate connectivity before deploying to cloud environments
- [ ] **[Recommended]** On Apple Silicon Macs, verify all container images have ARM64 variants or explicitly enable Rosetta 2 emulation for amd64 images (Settings > General > Use Rosetta); expect performance degradation with emulated images
- [ ] **[Recommended]** Use `host.docker.internal` hostname from within containers to reach services running on the host machine (databases, APIs running outside Kubernetes)
- [ ] **[Recommended]** Set resource requests and limits in manifests even for local development to validate that workloads fit within the allocated resources and catch sizing issues early
- [ ] **[Optional]** Configure WSL2 backend on Windows (recommended over Hyper-V) for better file system performance, lower memory overhead, and Linux-native container execution
- [ ] **[Optional]** Review Docker Desktop licensing: free for personal use, education, and small businesses (<250 employees and <$10M revenue); paid subscription required for larger organizations
- [ ] **[Optional]** Use `kubectl config get-contexts` to verify available contexts when switching between Docker Desktop, cloud clusters, and other local environments
- [ ] **[Optional]** Reset the Kubernetes cluster (Settings > Kubernetes > Reset Kubernetes Cluster) periodically to clean up accumulated resources and test fresh deployment procedures

## Why This Matters

Docker Desktop provides the lowest-friction path to running Kubernetes locally on macOS and Windows. Enabling Kubernetes in settings provisions a single-node cluster that shares the Docker daemon, meaning locally built images are immediately available to Kubernetes without registry configuration. This eliminates the build-push-pull cycle that slows development iteration.

However, Docker Desktop Kubernetes is a single-node cluster with significant limitations: no high availability testing, no node affinity validation, no multi-zone scheduling, and shared resources with Docker containers. Understanding these constraints is essential to avoid building architectures that work locally but fail in production multi-node environments. The Kustomize overlays pattern (base manifests + environment-specific overlays for local-dev, staging, production) bridges this gap by allowing local development to use simplified configurations (hostpath storage, NodePorts) while production uses cloud-native equivalents (EBS/PV, LoadBalancer with cloud provider).

## Common Decisions (ADR Triggers)

- **Docker Desktop vs minikube vs kind vs K3s for local development** -- Docker Desktop is simplest if Docker Desktop is already installed (one checkbox to enable), shares Docker image cache, and provides LoadBalancer support out of the box. Minikube offers multi-node simulation, add-on ecosystem (dashboard, ingress, metrics-server), and multiple drivers (Docker, VirtualBox, HyperKit). Kind (Kubernetes in Docker) excels at CI/CD testing with fast cluster creation/destruction and multi-node simulation via Docker containers. K3s provides a production-viable lightweight distribution that can run locally and in production with the same configuration. Choose Docker Desktop for simplicity when Docker is already required; K3s when parity with production edge/on-prem deployment is needed.
- **NodePort vs LoadBalancer for local access** -- Docker Desktop uniquely assigns localhost to LoadBalancer services, making them accessible like any local service. NodePort works the same as any Kubernetes (localhost:30000-32767). For local development, LoadBalancer type is convenient but masks the fact that cloud LoadBalancers behave differently (external IPs, health checks, annotations). Use NodePort in local-dev overlays for consistency, or LoadBalancer for convenience with awareness of the behavioral difference.
- **hostpath storage vs no persistence** -- Docker Desktop provides a hostpath-provisioner StorageClass. Persistent volumes use paths on the Docker Desktop VM's filesystem. Data survives pod restarts but is lost on Kubernetes cluster reset. For local development, hostpath is sufficient for databases and stateful services. Do not rely on it for data durability -- treat it as ephemeral storage that happens to persist across restarts.
- **Shared Docker daemon vs separate registry** -- Docker Desktop's shared daemon means `docker build -t myapp:latest .` makes the image immediately available to Kubernetes pods referencing `myapp:latest`. This eliminates the need for a local registry but creates a workflow difference from production where images come from ECR/GCR/Docker Hub. Set `imagePullPolicy: IfNotPresent` (not `Always`) in local-dev overlays to leverage local images.
- **WSL2 vs Hyper-V backend (Windows)** -- WSL2 is recommended: it runs a real Linux kernel, provides better file system performance for bind mounts from the Linux filesystem, uses dynamic memory allocation (Hyper-V reserves a fixed amount), and supports Linux-native containers directly. Hyper-V is only needed for Windows containers or specific enterprise configurations.

## Reference Architectures

### Local Development with Kustomize Overlays
```
manifests/
  base/
    deployment.yaml       # Standard Deployment
    service.yaml          # ClusterIP service
    kustomization.yaml
  overlays/
    local-dev/
      resource-patch.yaml    # Reduced CPU/memory requests
      service-patch.yaml     # NodePort or LoadBalancer for localhost
      storage-patch.yaml     # hostpath StorageClass
      kustomization.yaml     # References base + patches
    production/
      service-patch.yaml     # Cloud LoadBalancer with annotations
      storage-patch.yaml     # EBS/cloud StorageClass
      hpa.yaml               # Autoscaling (not needed locally)
      kustomization.yaml

Apply locally: kubectl apply -k manifests/overlays/local-dev/
Apply production: kubectl apply -k manifests/overlays/production/
```
Base manifests define the workload structure. Local-dev overlay substitutes cloud-specific resources with Docker Desktop equivalents. Production overlay adds cloud provider annotations, storage classes, and scaling policies. Same application manifests, different infrastructure configuration.

### Shared Image Workflow
```
[Developer Machine]
  │
  ├── docker build -t myapp:v1 .
  │     (image stored in Docker daemon)
  │
  ├── kubectl apply -f deployment.yaml
  │     (image: myapp:v1, imagePullPolicy: IfNotPresent)
  │     (Kubernetes uses same Docker daemon — no push needed)
  │
  └── docker compose up  (non-K8s services: databases, queues)
        (containers share network via host.docker.internal)

[Docker Desktop VM]
  ├── Docker daemon (shared)
  ├── Kubernetes (single node)
  │     ├── CoreDNS
  │     ├── kube-proxy
  │     └── hostpath-provisioner
  └── Resources: allocated CPU/memory shared between Docker and K8s
```
Docker containers and Kubernetes pods coexist on the same Docker Desktop VM. Supporting services (databases, message queues) can run as Docker Compose services while the application runs in Kubernetes pods, connected via host.docker.internal DNS.

### Resource Allocation Guidelines
```
Docker Desktop Resource Settings:
  Minimal (small apps):    2 CPU,  4GB RAM,  20GB disk
  Standard (3-5 services): 4 CPU,  8GB RAM,  40GB disk
  Heavy (monitoring + apps): 6 CPU, 12GB RAM, 60GB disk

Budget breakdown (8GB allocation example):
  Kubernetes system pods:  ~500MB
  Docker daemon overhead:  ~300MB
  Available for workloads: ~7.2GB
  Per-service estimate:    ~500MB-1GB each → 5-7 services
```
Resource allocation is shared between Docker containers and Kubernetes. Monitor actual usage with `docker stats` and `kubectl top nodes` to tune allocation. Over-allocating starves the host OS; under-allocating causes OOMKill in pods.
