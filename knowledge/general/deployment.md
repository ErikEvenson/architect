# Deployment

## Scope

This file covers deployment strategy decisions: how application code moves from source control to production, including deployment models, rollback procedures, infrastructure as code, database migration coordination, environment promotion, and deployment observability. For provider-specific CI/CD pipeline implementation, see the provider files. For container orchestration details, see `general/container-orchestration.md`.

## Checklist

- [ ] **[Critical]** Select a deployment strategy based on downtime tolerance, blast radius, and operational complexity — rolling update (gradual instance replacement, no extra capacity needed, partial rollback is messy), blue-green (instant cutover between two full environments, doubles infrastructure cost, clean rollback), canary (routes a small percentage of traffic to the new version, requires traffic splitting capability, best for validating changes at scale), or recreate (all instances replaced simultaneously, simplest but causes downtime, acceptable only for non-production or scheduled maintenance windows)
- [ ] **[Critical]** Define the rollback procedure and target rollback time — automated rollback on health check failure vs. manual operator decision, whether rollback requires a forward-fix deployment or a revert to previous artifact, and the maximum acceptable rollback duration (typically under 5 minutes for customer-facing services)
- [ ] **[Critical]** Determine how infrastructure is provisioned and managed — Terraform (multi-cloud, large ecosystem, state file management overhead), Pulumi (general-purpose languages instead of HCL, same state concerns), CloudFormation (AWS-native, no state file to manage, AWS-only), Ansible (configuration management with provisioning bolted on, agentless, procedural), or Crossplane (Kubernetes-native IaC, good for platform teams, steep learning curve)
- [ ] **[Critical]** Ensure infrastructure code is version controlled, peer-reviewed, and applied only through CI/CD — never through manual `terraform apply` or console clicks in production; enforce this with OIDC-based CI/CD credentials and no long-lived human credentials for infrastructure changes
- [ ] **[Critical]** Define how database schema migrations are coordinated with application deployments — run migrations before deployment (expand-then-contract pattern for backward compatibility), use a separate migration job or init container, ensure migrations are idempotent and backward-compatible so the previous application version continues to work during rollout, and plan for migration rollback (not all migrations are reversible)
- [ ] **[Critical]** Define the artifact versioning and promotion strategy — immutable artifacts built once and promoted across environments (never rebuilt per environment), semantic versioning or commit-SHA tagging, container image signing and provenance attestation (Cosign, Notary), and a single artifact repository as the source of truth (container registry, package repo)
- [ ] **[Recommended]** Design the environment promotion pipeline — number of environments (dev, staging, production at minimum), what gates exist between stages (automated tests, manual approval, soak time), whether staging mirrors production in configuration and scale, and how environment-specific configuration is injected (config maps, parameter store, sealed secrets) without baking it into the artifact
- [ ] **[Recommended]** Define zero-downtime deployment requirements — whether the application supports graceful shutdown (connection draining, in-flight request completion), readiness and liveness probe configuration, pre-stop hooks for cleanup, PodDisruptionBudgets or equivalent to prevent over-aggressive rollouts, and minimum available instance count during deployment
- [ ] **[Recommended]** Implement deployment observability — deploy event markers in monitoring dashboards (Grafana annotations, Datadog deploy tracking), automated error rate comparison before/after deployment, deployment duration tracking, and correlation of deployment events with incident timelines for post-mortems
- [ ] **[Recommended]** Establish deployment frequency targets aligned with DORA metrics — measure deployment frequency (daily/weekly/monthly), lead time for changes (commit to production), change failure rate (percentage of deployments causing incidents), and mean time to recovery (MTTR); set improvement targets and review quarterly
- [ ] **[Recommended]** Define the deployment approval and change management process — who can approve production deployments, whether deployments require a change request (CAB, lightweight review, or fully automated), deployment blackout windows (end of quarter, holidays), and how emergency hotfixes bypass the normal process while maintaining auditability
- [ ] **[Recommended]** Implement configuration management strategy — externalize all environment-specific configuration from application code, use a hierarchical configuration system (defaults < environment < overrides), encrypt secrets at rest (Vault, AWS Secrets Manager, SOPS), rotate secrets without redeployment, and validate configuration at startup before accepting traffic
- [ ] **[Optional]** Implement feature flags to decouple deployment from release — select a feature flag platform (LaunchDarkly, Unleash, Flagsmith, application-config-based), define flag lifecycle management (creation, progressive rollout, cleanup of stale flags), use flags for trunk-based development to merge incomplete features safely, and establish a maximum flag age policy to prevent permanent technical debt
- [ ] **[Optional]** Evaluate GitOps for declarative deployment management — store desired state in Git and use a reconciliation controller (Argo CD, Flux) to converge actual state; benefits include audit trail, drift detection, and self-healing; trade-offs include added complexity, secret management challenges, and the need for a Git-centric workflow

## Why This Matters

Deployment is the highest-risk routine activity in operations. Industry data consistently shows that deployments and configuration changes cause the majority of production incidents. A poorly designed deployment process creates a compounding problem: teams that fear deployments deploy less frequently, which means each deployment carries more changes, which increases the blast radius when something goes wrong, which reinforces the fear. Breaking this cycle requires investment in deployment automation, fast rollback, and deployment observability.

The deployment strategy directly affects availability, developer velocity, and operational cost. A blue-green deployment gives instant rollback but doubles infrastructure spend. A canary deployment minimizes blast radius but requires sophisticated traffic management and automated analysis. Rolling updates are the simplest to implement but offer the worst rollback story. There is no universally correct answer — the choice depends on the application's downtime tolerance, the team's operational maturity, and the infrastructure budget.

Infrastructure as code has shifted from a best practice to a baseline expectation. Manual infrastructure changes create drift, make environments unreproducible, and eliminate the ability to audit what changed and when. However, adopting IaC introduces its own challenges — state management, secret handling, module versioning, and blast radius control — that must be addressed in the architecture rather than discovered during an incident.

## Common Decisions (ADR Triggers)

### ADR: Deployment Strategy Selection

**Context:** The application requires a deployment model that balances availability, rollback speed, and infrastructure cost.

**Options:**

| Criterion | Rolling Update | Blue-Green | Canary | Recreate |
|---|---|---|---|---|
| Downtime | None (if health checks configured) | None (instant cutover) | None (gradual shift) | Yes (full restart) |
| Rollback Speed | Slow (must roll forward or re-deploy) | Instant (switch back to old environment) | Fast (shift traffic back) | Slow (full redeploy) |
| Infrastructure Cost | No extra capacity needed | 2x capacity during deployment | Minimal extra (canary instances) | No extra capacity |
| Complexity | Low | Moderate (routing, environment sync) | High (traffic splitting, metrics analysis) | Lowest |
| Database Compatibility | Must handle mixed versions during rollout | Can run migrations between cutover | Must handle mixed versions | Single version at a time |
| Best Fit | Stateless microservices, Kubernetes default | Mission-critical with zero-downtime requirement | High-traffic services needing gradual validation | Dev/test environments, batch processing |

**Decision drivers:** Downtime tolerance (SLA commitments), rollback time requirement, infrastructure budget, database migration complexity, and team operational maturity.

### ADR: Infrastructure as Code Tool Selection

**Context:** The organization needs to manage infrastructure declaratively with version control, drift detection, and repeatable provisioning.

**Options:**
- **Terraform:** Multi-cloud, largest ecosystem of providers, HCL language (purpose-built, easy to learn, limited expressiveness). Requires state file management (remote backend, state locking). Mature, battle-tested. Open-source core with BSL license (post-August 2023) or use OpenTofu fork (MPL).
- **Pulumi:** Uses general-purpose languages (Python, TypeScript, Go, C#) instead of a DSL. Same state management concerns as Terraform. Better for teams that prefer real programming constructs (loops, conditionals, type checking). Smaller provider ecosystem.
- **CloudFormation / CDK:** AWS-native, no state file to manage (AWS manages it). CDK generates CloudFormation from TypeScript/Python. AWS-only; not viable for multi-cloud. Deep integration with AWS services.
- **Crossplane:** Kubernetes-native IaC using CRDs. Infrastructure managed like any other Kubernetes resource. Best for platform engineering teams building internal developer platforms. Steep learning curve, requires Kubernetes expertise.

**Decision drivers:** Cloud strategy (single vs. multi-cloud), team language preferences, state management tolerance, existing Kubernetes investment, and licensing considerations.

### ADR: Database Migration Strategy During Deployment

**Context:** Application deployments frequently require database schema changes that must be coordinated with code deployment.

**Options:**
- **Expand-contract (recommended):** Phase 1 deploys a backward-compatible schema change (add column, create table). Phase 2 deploys application code that uses the new schema. Phase 3 removes old columns/tables. Requires two deployments for breaking changes but guarantees zero-downtime and safe rollback.
- **Pre-deployment migration job:** A migration runs before the new application version starts. Simpler workflow but the old application version must tolerate the new schema during rollout. Rollback requires a reverse migration.
- **Application-managed migration at startup:** Each instance checks and applies migrations on boot (e.g., Flyway, Alembic auto-migrate). Risk of race conditions with multiple instances starting simultaneously. Requires distributed locking.

**Decision drivers:** Downtime tolerance, rollback requirements, team discipline for backward-compatible migrations, and database size (large tables make some ALTER operations impractical without online DDL tools like pt-online-schema-change or gh-ost).

### ADR: Environment Promotion Strategy

**Context:** The organization needs a defined path for promoting changes from development to production with appropriate validation at each stage.

**Options:**
- **Three-environment (dev/staging/prod):** Minimum viable pipeline. Staging mirrors production configuration. Automated tests gate promotion. Simple to manage, but staging may diverge from production over time.
- **Four-environment (dev/staging/pre-prod/prod):** Pre-prod is a production-scale environment for performance testing and final validation. Higher infrastructure cost, better confidence.
- **Per-PR ephemeral environments:** Spin up a full environment for each pull request using Kubernetes namespaces or serverless. Excellent developer experience, high infrastructure cost, complex to manage stateful dependencies.

**Decision drivers:** Infrastructure budget, deployment frequency target, need for performance testing, regulatory requirements for production-like validation, and team size.

## See Also

- `providers/openshift/ci-cd.md` — OpenShift CI/CD pipelines and deployment
- `general/container-orchestration.md` — Container orchestration and runtime configuration
- `general/disaster-recovery.md` — Failover and recovery procedures
- `general/change-management.md` — Change management practices, approval workflows, and maintenance windows
- `general/iac-planning.md` — Infrastructure as code planning, tool selection, module structure, and state management
