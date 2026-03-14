# Kubernetes Operations

## Checklist

- [ ] Choose package management approach: Helm (templated charts, release management, hooks) vs Kustomize (overlay-based, no templating, built into kubectl) vs hybrid (Helm for third-party, Kustomize for in-house)
- [ ] Implement GitOps with ArgoCD or Flux: define application sources, sync policies (auto vs manual), health checks, and drift detection
- [ ] Plan cluster upgrade strategy: in-place rolling upgrade (control plane then nodes), blue-green (new cluster, traffic shift), or canary (upgrade subset of nodes first)
- [ ] Design etcd backup and restore procedures: automated snapshots (etcdctl snapshot save), off-cluster storage, tested restore runbook
- [ ] Configure certificate rotation: kubeadm auto-rotation (control plane certs), kubelet certificate rotation (--rotate-certificates), manual rotation procedures for custom CAs
- [ ] Set up resource quotas per namespace: CPU/memory requests and limits, PVC count and storage, object count (pods, services, configmaps)
- [ ] Configure LimitRanges per namespace: default resource requests/limits for containers that do not specify them, min/max constraints
- [ ] Plan kubectl debugging workflows: ephemeral containers (kubectl debug), port-forward for service debugging, logs --previous for crashed container logs
- [ ] Design Helm chart repository strategy: OCI registries (preferred, supported since Helm 3.8), ChartMuseum, or Git-based (Flux HelmRepository)
- [ ] Implement Helm hooks for lifecycle management: pre-install/pre-upgrade (schema migration), post-install (seed data), pre-delete (backup)
- [ ] Plan rollback procedures: Helm rollback (revision history), ArgoCD sync to previous commit, kubectl rollout undo for deployments
- [ ] Design multi-environment promotion: dev -> staging -> production with GitOps (branch-per-env, directory-per-env, or ApplicationSet generators)
- [ ] Configure cluster autoscaler or Karpenter for node lifecycle management: scale-up thresholds, scale-down delays, node group design

## Why This Matters

Kubernetes operations encompass the day-2 activities that determine whether a cluster remains reliable, secure, and manageable over time. Without GitOps, configuration drift between what is in Git and what is running in the cluster creates unpredictable behavior and makes incident response harder. Without proper upgrade procedures, cluster upgrades cause extended downtime or workload disruption. Without resource quotas, a single team can consume all cluster resources, causing noisy-neighbor problems. Without backup procedures, etcd corruption or accidental deletion results in complete cluster loss. Helm and Kustomize manage the complexity of deploying applications with environment-specific configuration, but choosing the wrong tool (or using both inconsistently) creates maintenance burden. Operations decisions compound: poor namespace design makes RBAC harder, which makes quota enforcement harder, which makes cost attribution harder.

## Common Decisions (ADR Triggers)

- **Helm vs Kustomize**: Helm provides templating (Go templates), release management (install/upgrade/rollback with revision history), and a chart ecosystem (Artifact Hub). Kustomize provides patch-based overlays without templating, built into kubectl. Helm is better for third-party applications (databases, monitoring stacks) that need parameterization. Kustomize is better for in-house applications where overlays are more readable than templates. Many teams use both: Helm for third-party, Kustomize for in-house.
- **ArgoCD vs Flux**: ArgoCD provides a rich UI, RBAC, SSO, multi-cluster support, and ApplicationSets for fleet management. Flux is controller-based (no UI by default), tightly integrated with Helm and Kustomize, and follows Kubernetes-native patterns (CRDs for everything). Choose ArgoCD when UI and multi-team RBAC are important; Flux for simpler, CRD-driven GitOps. Both are CNCF graduated.
- **In-place upgrade vs blue-green cluster upgrade**: In-place upgrades are simpler and cheaper (no duplicate cluster) but carry risk of upgrade failures affecting production. Blue-green creates a new cluster at the target version, shifts traffic, and decommissions the old cluster. Use in-place for minor version upgrades (1.28 -> 1.29); consider blue-green for major infrastructure changes or when zero-downtime is non-negotiable.
- **Resource quotas: strict vs advisory**: Strict quotas (hard limits) prevent resource exhaustion but cause deployment failures when quotas are exceeded. Advisory quotas (monitor and alert without enforcement) are less disruptive but do not prevent resource contention. Start with advisory monitoring, then enforce quotas once teams have right-sized their workloads. Always enforce in multi-tenant clusters.
- **Karpenter vs Cluster Autoscaler**: Cluster Autoscaler scales node groups based on pending pods and is cloud-agnostic. Karpenter provisions nodes directly (faster, instance-type flexible, consolidation) but is primarily AWS (with Azure in beta). Use Karpenter on AWS for faster scaling and better bin-packing; Cluster Autoscaler for other clouds or multi-cloud.
- **Branch-per-env vs directory-per-env (GitOps)**: Branch-per-env (main=prod, staging=staging) is intuitive but creates merge conflicts and drift between branches. Directory-per-env (environments/dev/, environments/prod/) keeps all environments in one branch with overlays. Directory-per-env is the recommended pattern (used by both ArgoCD and Flux documentation).

## Reference Architectures

### GitOps Deployment Pipeline
```
[Developer] --> [Git Push to feature branch]
        |
  [CI Pipeline (GitHub Actions/GitLab CI)]
  - Build container image
  - Run tests
  - Push image to registry
  - Update image tag in GitOps repo (Kustomize overlay or Helm values)
        |
  [GitOps Repo Structure]
  ├── base/                    # Shared manifests (Kustomize base or Helm chart)
  ├── environments/
  │   ├── dev/                 # Dev overlay (auto-sync)
  │   ├── staging/             # Staging overlay (auto-sync)
  │   └── production/          # Production overlay (manual sync + approval)
        |
  [ArgoCD / Flux]
  - Watches GitOps repo
  - Detects drift from desired state
  - Syncs (auto or manual based on environment)
  - Health checks post-sync
  - Rollback on failed health check
```
CI builds and tests code, then updates the GitOps repo with the new image tag. ArgoCD/Flux detects the change and syncs to the cluster. Dev and staging auto-sync; production requires manual approval or PR merge. Health checks (deployment rollout, custom checks) determine sync success.

### Cluster Upgrade Procedure (In-Place)
```
[Pre-upgrade]
  1. Review release notes and deprecation notices
  2. Run `kubectl deprecations` or Pluto to find removed APIs
  3. Backup etcd: etcdctl snapshot save
  4. Verify PodDisruptionBudgets exist for critical workloads
  5. Test upgrade in staging cluster first

[Control Plane Upgrade]
  6. Upgrade control plane nodes one at a time
     - Managed K8s (EKS/GKE/AKS): API call to upgrade control plane
     - kubeadm: `kubeadm upgrade apply v1.XX.Y` on first CP node,
       `kubeadm upgrade node` on remaining CP nodes
  7. Verify API server, controller-manager, scheduler healthy

[Worker Node Upgrade]
  8. For each node (or node group):
     a. Cordon: kubectl cordon <node>
     b. Drain: kubectl drain <node> --ignore-daemonsets --delete-emptydir-data
     c. Upgrade kubelet and kubectl
     d. Uncordon: kubectl uncordon <node>
  9. Managed K8s: rolling update of node group / managed node pool

[Post-upgrade]
  10. Verify all workloads healthy (kubectl get pods --all-namespaces)
  11. Run smoke tests
  12. Update Helm charts and operators that have version constraints
```
Always upgrade control plane before workers. Never skip minor versions (1.27 -> 1.29 is not supported; must go 1.27 -> 1.28 -> 1.29). PDBs prevent drain from evicting too many pods simultaneously. Staging-first catches breaking changes before production.

### Helm Release Management
```
[Helm Chart Sources]
  ├── Third-party (OCI registry / Artifact Hub)
  │   - prometheus-community/kube-prometheus-stack
  │   - bitnami/postgresql
  │   - ingress-nginx/ingress-nginx
  │
  └── In-house (OCI registry)
      - myorg/api-service (versioned chart)
      - myorg/worker-service (versioned chart)

[Values Management]
  ├── values.yaml           # Chart defaults
  ├── values-dev.yaml       # Dev overrides
  ├── values-staging.yaml   # Staging overrides
  └── values-production.yaml # Production overrides

[ArgoCD Application]
  apiVersion: argoproj.io/v1alpha1
  kind: Application
  spec:
    source:
      repoURL: oci://registry.example.com/charts
      chart: api-service
      targetRevision: 1.2.3
      helm:
        valueFiles:
          - values-production.yaml

[Lifecycle Hooks]
  pre-upgrade:  Job (database migration)
  post-upgrade: Job (cache warm, smoke test)
  pre-delete:   Job (data export/backup)
```
OCI registries for chart storage (replacing ChartMuseum). Per-environment values files with ArgoCD managing the lifecycle. Helm hooks for database migrations and other lifecycle tasks execute as Kubernetes Jobs with configurable weight (ordering) and delete policies.
