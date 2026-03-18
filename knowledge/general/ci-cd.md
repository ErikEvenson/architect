# CI/CD Pipeline Design

## Scope

This file covers cloud-agnostic CI/CD pipeline architecture: platform selection, pipeline design patterns, artifact management, testing stages, deployment integration, and operational concerns like build performance and secret handling. For deployment strategy decisions (rolling, blue-green, canary), see [Deployment](deployment.md). For provider-specific CI/CD tooling, see [Azure DevOps](../providers/azure/devops.md), [GCP DevOps](../providers/gcp/devops.md), and [OpenShift CI/CD](../providers/openshift/ci-cd.md). For infrastructure-as-code decisions, see [IaC Planning](iac-planning.md).

## Checklist

- [ ] **[Critical]** Select a CI/CD platform aligned with source control, team size, and security requirements (GitHub Actions, GitLab CI, Jenkins, Azure DevOps, Tekton, CircleCI)
- [ ] **[Critical]** Define a branching and promotion strategy — trunk-based development with short-lived feature branches vs. GitFlow with long-lived release branches — and enforce it with branch protection rules
- [ ] **[Critical]** Eliminate long-lived credentials in pipelines — use OIDC federation (GitHub Actions OIDC to AWS/Azure/GCP), workload identity, or Vault dynamic secrets for all cloud and registry authentication
- [ ] **[Critical]** Implement mandatory testing stages with quality gates: unit tests, static analysis (SAST), dependency/container scanning, and at least one integration test suite that blocks promotion
- [ ] **[Critical]** Sign and verify build artifacts — container images (cosign/Notary), packages (GPG), SBOMs (SPDX/CycloneDX) — to establish a verifiable supply chain
- [ ] **[Critical]** Store artifacts in a dedicated registry or repository (Harbor, Artifactory, ECR, GHCR) with retention policies, vulnerability scanning, and promotion between registries for environment separation
- [ ] **[Recommended]** Decide between GitOps pull-based deployment (ArgoCD, Flux) and traditional push-based CI-triggered deployment — GitOps provides drift detection and declarative state, push-based offers simpler initial setup
- [ ] **[Recommended]** Implement build caching (Docker layer caching, dependency caches, incremental compilation) and parallelize independent pipeline stages to keep build times under 10 minutes
- [ ] **[Recommended]** Evaluate self-hosted vs. SaaS runners — self-hosted runners provide network access to private infrastructure and avoid egress costs, but require patching, scaling, and ephemeral cleanup
- [ ] **[Recommended]** Design pipeline structure for monorepo or polyrepo — monorepos need path-based triggering and affected-service detection; polyrepos need cross-repo dependency coordination
- [ ] **[Recommended]** Integrate deployment strategies (rolling, blue-green, canary) into the pipeline with automated smoke tests and rollback triggers at each stage
- [ ] **[Recommended]** Add DAST (dynamic application security testing) and end-to-end tests in a staging or pre-production environment before production promotion
- [ ] **[Optional]** Implement pipeline-as-code templates or shared libraries (reusable workflows, Jenkins shared libraries, GitLab CI includes) to standardize pipelines across teams
- [ ] **[Optional]** Track DORA metrics (deployment frequency, lead time for changes, change failure rate, mean time to recovery) from CI/CD telemetry to measure delivery performance
- [ ] **[Optional]** Configure ChatOps integration (Slack/Teams notifications, deployment approvals via chat) and manual approval gates for production deployments in regulated environments

## Why This Matters

CI/CD pipelines are the central nervous system of software delivery. A poorly designed pipeline either slows teams down — 30-minute builds, flaky tests, manual deployment steps — or creates risk by shipping untested or unsigned artifacts to production. Organizations that treat CI/CD as an afterthought end up with fragile, snowflake pipelines that only one person understands, and deployments that require a war room.

Supply chain attacks (SolarWinds, Codecov, xz-utils) have elevated CI/CD security from a nice-to-have to a board-level concern. Pipelines that use long-lived credentials, pull unverified dependencies, or skip artifact signing are attack surfaces. A compromised build pipeline can inject malicious code into every deployment across the organization. OIDC federation, signed artifacts, pinned dependencies, and ephemeral runners are now baseline requirements for any serious production pipeline.

The difference between high-performing and low-performing teams often comes down to CI/CD maturity. Teams that deploy multiple times per day with automated rollback recover from failures in minutes. Teams that deploy monthly with manual steps accumulate risk and spend weekends on failed releases. The pipeline design decisions made early — platform, branching strategy, testing stages, deployment integration — determine which category an organization falls into.

## Common Decisions (ADR Triggers)

### ADR: CI/CD Platform Selection

**Context:** The organization needs a CI/CD platform to build, test, and deploy applications across multiple environments.

**Options:**

| Criterion | GitHub Actions | GitLab CI | Jenkins | Azure DevOps | Tekton | CircleCI |
|---|---|---|---|---|---|---|
| Source Control Integration | Native (GitHub) | Native (GitLab) | Plugin-based (any SCM) | Native (Azure Repos), GitHub | Any (event-driven) | GitHub, Bitbucket |
| Pipeline Definition | YAML workflows | `.gitlab-ci.yml` | Jenkinsfile (Groovy) | YAML pipelines | Kubernetes CRDs | YAML config |
| Runner Model | GitHub-hosted or self-hosted | SaaS or self-managed runners | Always self-hosted (controller + agents) | Microsoft-hosted or self-hosted | Kubernetes-native pods | SaaS or self-hosted (runner) |
| Ecosystem | Marketplace actions (reuse risk) | Built-in registry, security scanning | Plugin ecosystem (1800+ plugins) | Boards, artifacts, test plans integrated | Cloud-native, composable | Orbs marketplace |
| Security Features | OIDC federation, Dependabot, code scanning | SAST/DAST/container scanning built-in | Plugin-dependent, high maintenance | Service connections, managed identity | Chains (SLSA provenance) | Contexts, OIDC |
| Scaling | Auto-scales (SaaS), ARC for self-hosted | Auto-scale runners, Kubernetes executor | Manual scaling, Kubernetes plugin | Auto-scale agents (VMSS) | Kubernetes-native auto-scale | Auto-scales (SaaS) |
| Cost Model | Free tier + per-minute (SaaS), free self-hosted | Free tier + per-minute (SaaS), free self-managed | Free (OSS), infrastructure cost only | Free tier + per-minute, free self-hosted | Free (OSS), infrastructure cost only | Free tier + per-minute |
| Best Fit | GitHub-native teams, OSS projects | GitLab-native teams, integrated DevSecOps | Complex enterprise with existing investment | Microsoft/Azure shops | Kubernetes-native, supply chain security | SaaS-first small-to-mid teams |

**Decision drivers:** Existing source control platform, security scanning requirements, self-hosted vs. SaaS preference, Kubernetes-native requirement, team familiarity, and budget model.

### ADR: GitOps vs. Push-Based Deployment

**Context:** The team needs to decide how deployments are triggered and how desired state is reconciled with actual state.

**Options:**
- **GitOps pull-based (ArgoCD, Flux):** A controller in the cluster watches a Git repository and reconciles desired state continuously. Provides drift detection, audit trail via Git history, and declarative rollback (revert a commit). Requires separating application code repos from deployment manifest repos. Adds operational complexity (controller HA, multi-cluster sync).
- **Push-based CI-triggered:** The CI pipeline runs `kubectl apply`, `helm upgrade`, or a cloud CLI command after tests pass. Simpler to set up, single pipeline definition. No drift detection — manual changes go unnoticed. Credentials must be available to the CI system.
- **Hybrid:** CI pipeline builds and tests artifacts, then updates a manifest repo (image tag bump), which ArgoCD/Flux picks up. Combines CI strengths (build/test) with GitOps strengths (deployment reconciliation).

**Recommendation:** Use the hybrid approach for production workloads — CI handles build/test/sign, GitOps handles deployment and drift detection. Use pure push-based for non-production environments where simplicity matters more than drift control.

### ADR: Branching and Promotion Strategy

**Context:** The team must standardize how code flows from development to production.

**Options:**
- **Trunk-based development:** All developers commit to `main` (or short-lived feature branches merged within 1-2 days). Releases cut from main. Requires feature flags for incomplete work. Fastest flow, lowest merge complexity, best for continuous deployment.
- **GitFlow:** Long-lived `develop` and `main` branches, plus `release/*` and `hotfix/*` branches. Clear release process with explicit versioning. Higher merge complexity, slower flow. Suitable for packaged software with scheduled releases.
- **Environment branching:** Branches map to environments (`dev`, `staging`, `prod`). Code promoted by merging between branches. Simple mental model but creates merge debt and cherry-pick nightmares. Generally discouraged.

**Decision drivers:** Release cadence (continuous vs. scheduled), team size, regulatory requirements for release traceability, and whether feature flags are in place.

### ADR: Self-Hosted vs. SaaS Runners

**Context:** The team must decide where CI/CD jobs execute.

**Options:**
- **SaaS-hosted runners:** Zero maintenance, auto-scaled, pay-per-minute. Cannot access private networks without tunneling. Compute constrained by vendor tiers. Data leaves your network boundary.
- **Self-hosted runners (persistent):** Full network access, custom tooling pre-installed. Require patching, monitoring, and scaling. Risk of contamination between jobs if not properly isolated.
- **Self-hosted ephemeral runners (Kubernetes-based):** Each job gets a fresh pod. Network access plus clean environment. Requires Kubernetes cluster and runner operator (Actions Runner Controller, GitLab Kubernetes executor). Higher infrastructure complexity, best isolation.

**Recommendation:** Use SaaS runners for open-source and public-facing projects. Use self-hosted ephemeral runners (Kubernetes-based) for enterprise workloads requiring private network access or strict isolation. Never use persistent self-hosted runners without job isolation for security-sensitive workloads.

### ADR: Monorepo vs. Polyrepo Pipeline Design

**Context:** The organization has multiple services and must decide how CI/CD pipelines are structured relative to repository layout.

**Options:**
- **Monorepo with path-based triggers:** All services in one repository, pipelines triggered by changed paths. Atomic cross-service changes, shared tooling. Requires build system intelligence (Bazel, Nx, Turborepo) to avoid rebuilding everything on every commit. Pipeline complexity grows with service count.
- **Polyrepo with per-service pipelines:** Each service has its own repository and pipeline. Clear ownership boundaries, independent release cycles. Cross-service changes require coordinated PRs. Shared pipeline logic via templates or reusable workflows.

**Decision drivers:** Number of services, frequency of cross-service changes, team structure (Conway's Law), and build system maturity.

## See Also

- [Deployment](deployment.md) — deployment strategies (rolling, blue-green, canary) and rollback procedures
- [Testing Strategy](testing-strategy.md) — test pyramid design, coverage targets, and test environment management
- [Security](security.md) — supply chain security, secrets management principles
- [IaC Planning](iac-planning.md) — infrastructure-as-code tool selection and state management
- [Governance](governance.md) — change management, approval workflows, compliance gates
- [Observability](observability.md) — monitoring deployments, tracking DORA metrics
