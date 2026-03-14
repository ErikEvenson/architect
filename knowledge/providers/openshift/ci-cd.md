# OpenShift CI/CD

## Checklist

- [ ] Deploy OpenShift Pipelines operator (Tekton) for cloud-native CI/CD pipelines
- [ ] Deploy OpenShift GitOps operator (ArgoCD) for declarative continuous delivery
- [ ] Define pipeline architecture: Tekton Pipelines with Tasks, TaskRuns, PipelineRuns, and Workspaces
- [ ] Configure Tekton Triggers for webhook-based pipeline execution (GitHub, GitLab, Bitbucket webhooks)
- [ ] Evaluate Source-to-Image (S2I) builds for simple language-specific containerization vs Dockerfile/Buildah builds
- [ ] Set up BuildConfig resources for OpenShift-native builds (S2I, Docker, Custom, Pipeline strategies)
- [ ] Configure ImageStreams for image lifecycle management, tag policies, and automatic deployment triggers
- [ ] Deploy Quay registry (or mirror registry for disconnected) as the enterprise container image repository
- [ ] Design GitOps repository structure: app-of-apps, monorepo, or repo-per-team pattern
- [ ] Define promotion strategy: namespace-based (dev/staging/prod) vs cluster-based (dev cluster/prod cluster)
- [ ] Configure Operator Lifecycle Manager (OLM) for installing and upgrading operators with approval policies
- [ ] Implement Helm chart deployment strategy: Helm operator, ArgoCD Helm support, or Tekton Helm tasks
- [ ] Set up artifact signing: Tekton Chains for pipeline attestation and image signing with Sigstore/cosign
- [ ] Configure pipeline security: dedicated service accounts, SCC restrictions, workspace cleanup, secret injection via Vault

## Why This Matters

CI/CD on OpenShift is built around two complementary operators: OpenShift Pipelines (Tekton) handles the build-test-publish cycle, and OpenShift GitOps (ArgoCD) handles the deploy-sync-reconcile cycle. Together they implement a full GitOps workflow where Git is the single source of truth for both application code and deployment configuration.

Tekton is a Kubernetes-native CI/CD framework where every pipeline step runs as a container in a pod. This provides isolation, reproducibility, and scalability -- but it also means pipelines consume cluster resources. `PipelineRun` objects create pods, which need storage (Workspaces backed by PVCs or emptyDir), service accounts (with appropriate SCCs for building images), and network access (to pull dependencies and push images). Without resource planning, build pipelines can starve application workloads.

Source-to-Image (S2I) is an OpenShift-specific build strategy that combines a builder image (e.g., `nodejs:18-ubi8`) with application source code to produce a runnable container image without requiring a Dockerfile. S2I is fast and secure (no privileged build) but less flexible than Dockerfile/Buildah builds. BuildConfig objects manage the build lifecycle, and ImageStreams track the resulting images with automatic rollout triggers.

OpenShift GitOps (ArgoCD) reconciles the desired state in Git with the actual state in the cluster. ArgoCD Application CRDs define the source (Git repo, path, revision) and destination (cluster, namespace). The ArgoCD ApplicationSet controller enables fleet-wide deployment patterns (generate Applications per cluster, per namespace, or per pull request).

OLM manages the operator lifecycle -- installation, upgrades, and dependency resolution. Operators are distributed via CatalogSources (OperatorHub), and InstallPlans control whether upgrades require manual approval. In production, set `installPlanApproval: Manual` for critical operators to prevent unplanned upgrades.

## Common Decisions (ADR Triggers)

- **Tekton vs external CI (Jenkins, GitHub Actions, GitLab CI)**: Tekton runs natively on the cluster with Kubernetes RBAC and SCC integration. External CI is appropriate when teams already have mature pipelines elsewhere. Jenkins on OpenShift is deprecated in favor of Tekton.
- **S2I vs Dockerfile/Buildah builds**: S2I is simpler and runs unprivileged but limits customization. Buildah (via Tekton `buildah` ClusterTask) supports standard Dockerfiles and also runs unprivileged on OpenShift. Avoid Docker-in-Docker builds which require privileged SCCs.
- **GitOps repository structure**: Monorepo (all manifests in one repo) is simpler for small teams. App-of-apps (ArgoCD pattern with a root Application pointing to child Applications) scales to larger organizations. Repo-per-team gives autonomy but complicates cross-cutting changes.
- **Promotion strategy**: Namespace-based promotion (dev/staging/prod in same cluster) is simpler but shares failure domain. Cluster-based promotion (separate clusters per environment) provides stronger isolation. Kustomize overlays or Helm values files differentiate environments.
- **Image lifecycle**: ImageStreams (OpenShift-native, supports import policies and triggers) vs direct registry references. ImageStreams add complexity but enable periodic re-import for base image CVE patching and automatic deployment triggers on new tags.
- **OLM upgrade policy**: Automatic approval (operators upgrade immediately) vs manual approval (operators wait for explicit approval). Manual approval is recommended for production to prevent unexpected operator upgrades from breaking workloads.

## Version Notes

| Feature | OCP 4.12 | OCP 4.14 | OCP 4.16 |
|---|---|---|---|
| OpenShift Pipelines (Tekton) | 1.9 (Tekton 0.41) | 1.13 (Tekton 0.53) | 1.15 (Tekton 0.59) |
| OpenShift GitOps (ArgoCD) | 1.7 (ArgoCD 2.5) | 1.11 (ArgoCD 2.9) | 1.13 (ArgoCD 2.11) |
| Tekton Chains | Tech Preview | GA | GA |
| Tekton Hub (ClusterTasks) | Supported | Supported (deprecation notice) | Deprecated (use Resolvers) |
| Tekton Resolvers | Tech Preview | GA | GA |
| S2I builds (BuildConfig) | Supported | Supported | Supported (maintenance mode) |
| Shipwright (builds) | Tech Preview | Tech Preview | GA |
| Jenkins on OpenShift | Deprecated | Deprecated | Removed from samples |
| ApplicationSet controller | GA (bundled with GitOps) | GA | GA (progressive rollout) |
| Tekton Results | Not available | Tech Preview | GA |

**Key changes across versions:**
- **Tekton/Pipelines operator:** Each OCP release ships a corresponding Pipelines operator version. ClusterTasks are being replaced by Tekton Resolvers (hub, git, bundle, cluster resolvers) which provide more flexible task sourcing. Plan to migrate ClusterTask references to Resolver-based references.
- **GitOps operator:** Tracks upstream ArgoCD closely. OCP 4.14+ includes improved multi-tenancy support with ArgoCD AppProjects and RBAC integration with OpenShift Groups. OCP 4.16 adds progressive rollout support in ApplicationSets (canary/blue-green at the GitOps level).
- **S2I changes:** S2I remains supported but is in maintenance mode. Red Hat recommends Shipwright (which reached GA in OCP 4.16) as the strategic build framework. Shipwright supports S2I, Buildpacks, Kaniko, and Buildah strategies through a unified Build/BuildRun API.
- **Jenkins removal:** Jenkins was deprecated in OCP 4.12 and the Jenkins sample templates were removed in OCP 4.16. Teams should migrate to Tekton Pipelines. The `jenkins-client-plugin` for triggering Tekton PipelineRuns from legacy Jenkins is available as a migration bridge.
- **Tekton Chains:** Reached GA in OCP 4.14, providing supply chain security through automatic pipeline attestation and image signing with Sigstore/cosign. Integrates with Tekton Results for long-term storage of pipeline run metadata.

## Reference Architectures

- **Enterprise GitOps pipeline**: Tekton pipelines (clone -> build -> test -> scan -> push) triggered by GitHub webhooks, Tekton Chains for attestation, Quay for image storage with Clair scanning, ArgoCD for deployment, Kustomize overlays for environment differentiation, promotion via Git merge (dev branch -> staging branch -> prod branch).
- **Multi-cluster GitOps**: ArgoCD hub on management cluster, ApplicationSets generating deployments across spoke clusters managed by RHACM, cluster-scoped secrets synced via ESO, promotion by updating image tags in Git.
- **Disconnected / air-gapped CI/CD**: Mirror registry (oc-mirror) for operator catalogs and base images, Tekton pipelines with pre-cached dependencies, Quay mirror for image distribution, ArgoCD syncing from internal Git server (Gitea, GitLab self-hosted).
- **Developer self-service**: OpenShift Dev Spaces (Eclipse Che) for cloud-based IDEs, Tekton pipeline templates via TektonHub, ArgoCD AppProjects per team with RBAC, namespace provisioning via ProjectRequest or Namespace Configuration Operator.
- **Compliance-gated pipeline**: Tekton pipeline with mandatory security gates (image scan, compliance check, SBOM generation), Tekton Chains for non-repudiation, OPA/Gatekeeper policies blocking non-compliant deployments, ArgoCD sync waves for ordered rollout (namespace -> RBAC -> secrets -> app).
