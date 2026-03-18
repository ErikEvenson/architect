# Deployment Failure Patterns

## Scope

Covers common deployment failure patterns including missing rollback plans, configuration drift, inadequate health checks, simultaneous deployments, missing canary rollouts, and CI/CD pipeline failures. Does not cover general deployment strategy design (see `general/deployment.md`) or CI/CD tooling configuration (see `general/ci-cd.md`).

## Checklist

- [ ] **[Critical]** **No rollback plan or rollback never tested** — Goes wrong: a bad deployment reaches production and the team cannot revert because the rollback procedure is undocumented, untested, or blocked by database schema changes that are not backward-compatible. The outage extends for hours. Happens because: rollback is assumed to be "just redeploy the old version" without considering state changes, schema migrations, or configuration dependencies. Prevent by: documenting and testing rollback procedures for every release, maintaining backward-compatible schema migrations, keeping previous deployment artifacts readily available, and practicing rollback during non-emergency windows.

- [ ] **[Critical]** **Database migration breaks running application** — Goes wrong: a migration runs during deployment that drops a column, renames a table, or adds a constraint that conflicts with the currently running application version, causing immediate 500 errors for all users. Happens because: migrations are tightly coupled to application deployments and assume the old version stops before the new schema takes effect. Prevent by: using expand-and-contract migration patterns (add new column, migrate data, update code, remove old column in a later release), running migrations separately from application deploys, and testing migrations against the current production code version.

- [ ] **[Critical]** **Configuration drift between environments** — Goes wrong: the application works in staging but fails in production because environment configurations have diverged over time (different instance types, different environment variables, different security group rules, different feature flags). Happens because: manual changes are made directly in production without updating IaC, or staging and production use fundamentally different infrastructure. Prevent by: managing all configuration through IaC, using parameterized templates with environment-specific values, drifting detection tools (terraform plan, AWS Config), and prohibiting manual console changes.

- [ ] **[Critical]** **Missing or inadequate health checks** — Goes wrong: the load balancer or orchestrator marks a crashed or hung instance as healthy and continues routing traffic to it, or marks a slow-starting instance as unhealthy and kills it before it finishes initializing, creating a restart loop. Happens because: health checks use a shallow endpoint (TCP port check or static 200 response) that does not verify actual application readiness, or startup grace periods are too short. Prevent by: implementing deep health checks that verify database connectivity and critical dependency availability, configuring appropriate startup grace periods, and using separate liveness vs readiness probes.

- [ ] **[Critical]** **Deploying all instances simultaneously** — Goes wrong: a bug in the new version takes down 100% of capacity at once, causing a complete outage with no healthy instances to serve traffic while the issue is diagnosed. Happens because: "deploy all at once" is the simplest strategy and is fastest to complete. Prevent by: using rolling deployments (one batch at a time), blue-green deployments (switch traffic after validation), or canary deployments (route small percentage first), and configuring minimum healthy percentage thresholds.

- [ ] **[Recommended]** **No canary or staged rollout for critical changes** — Goes wrong: a subtle performance regression or edge-case bug that passed testing reaches all users immediately, and the problem is only discovered through a flood of support tickets or dashboards turning red. Happens because: canary deployments are seen as complex to implement, or the team lacks traffic-shifting infrastructure. Prevent by: implementing canary deployments that route 1-5% of traffic to the new version first, monitoring error rates and latency during the canary phase, and automating rollback when canary metrics breach thresholds.

- [ ] **[Critical]** **Deployment pipeline has no automated tests** — Goes wrong: regressions, broken imports, and configuration errors reach production because nothing verifies correctness between code merge and deployment. Happens because: testing is manual, or tests exist but are not integrated into the CI/CD pipeline. Prevent by: requiring automated test suites (unit, integration, contract) as pipeline gates, failing the pipeline on test failures, and tracking test coverage to prevent erosion.

- [ ] **[Critical]** **Secrets or configuration injected at wrong environment** — Goes wrong: production deployment uses staging database credentials, or staging deployment uses production API keys, causing data corruption or unintended operations against production systems. Happens because: environment-specific secrets are managed manually, or deployment scripts have environment parameters that default to the wrong value. Prevent by: namespacing secrets by environment in the secrets manager, validating the target environment in deployment scripts, using deployment approvals for production, and never sharing secret names across environments.

- [ ] **[Recommended]** **IaC and application deployment not coordinated** — Goes wrong: application code is deployed that depends on new infrastructure (a new queue, a new database table, a new IAM permission) that has not been provisioned yet, causing runtime failures. Happens because: infrastructure and application deployments are managed by different teams or pipelines with no dependency ordering. Prevent by: deploying infrastructure changes before application changes, using feature flags to decouple code deployment from feature activation, and defining explicit dependencies between infrastructure and application pipelines.

- [ ] **[Recommended]** **No deployment observability or deployment markers** — Goes wrong: performance degradation is detected but the team cannot correlate it with a deployment because there are no deployment markers in monitoring dashboards, and deployment history is only in the CI/CD tool that nobody checks during incidents. Happens because: deployment events are not integrated with monitoring systems. Prevent by: annotating monitoring dashboards with deployment events (Datadog, Grafana annotations), logging deployment metadata (version, commit SHA, deployer), and setting up automated alerts that compare metrics before and after deployment.

- [ ] **[Recommended]** **Long-lived feature branches merged without integration testing** — Goes wrong: a branch that has diverged from main for weeks is merged and deployed, introducing a large blast radius of changes that interact in unexpected ways, causing multiple simultaneous failures that are hard to isolate. Happens because: feature branches are kept open to avoid deploying incomplete features, and merge conflicts are resolved hastily. Prevent by: using trunk-based development with feature flags, merging to main daily, running integration tests on every merge, and keeping the blast radius of each deployment small.

- [ ] **[Critical]** **Container image tags reused or using :latest in production** — Goes wrong: a "latest" or mutable tag is redeployed and the underlying image has changed, causing unexpected behavior, or a rollback to a previous tag pulls a different image than expected because the tag was overwritten. Happens because: using :latest is convenient during development and the habit carries to production. Prevent by: using immutable image tags (git SHA or semantic version), enforcing tag immutability in the container registry, and referencing specific digests for critical deployments.

- [ ] **[Recommended]** **Missing deployment approval gates for production** — Goes wrong: an engineer accidentally deploys an untested branch to production, or an automated pipeline pushes a broken build to production without human review. Happens because: the pipeline has no manual approval step, or the approval step is a formality that is rubber-stamped. Prevent by: requiring manual approval for production deployments, implementing branch protection rules, separating CI (build and test) from CD (deploy), and logging who approved each production deployment.

- [ ] **[Critical]** **Ignoring deployment pipeline failures and forcing deploys** — Goes wrong: a failing test, lint error, or security scan is bypassed with a force flag or pipeline skip, and the underlying issue causes a production incident. Happens because: there is pressure to deploy quickly, and the failing check is assumed to be a false positive. Prevent by: treating pipeline failures as blockers without override ability (or requiring senior approval for overrides), investigating flaky tests rather than skipping them, and tracking override frequency as a team health metric.

## Why This Matters

Deployments are the single most common cause of production outages. Every deployment is a controlled introduction of change into a running system, and without proper safeguards, any deployment can cause an uncontrolled outage. Rollback capability is the most critical safety net: if you cannot roll back in minutes, every deployment is a high-stakes gamble. Staged rollouts, health checks, and deployment observability transform deployments from risky events into routine, reversible operations.

## Common Decisions (ADR Triggers)

- **Deployment strategy** — rolling vs blue-green vs canary, minimum healthy percentage
- **Rollback mechanism** — redeploy previous version vs infrastructure-level switch, rollback SLA
- **Database migration approach** — expand-and-contract vs synchronized migration, tooling selection
- **Pipeline gate policy** — which checks are blocking, override policy, approval requirements
- **Image tagging strategy** — semantic versioning vs git SHA, tag immutability enforcement
- **Feature flag management** — build-time vs runtime flags, flag lifecycle and cleanup policy

## See Also

- `general/deployment.md` — Deployment strategy design and rollout patterns
- `general/ci-cd.md` — CI/CD pipeline architecture and tooling
- `failures/data.md` — Data failure patterns related to schema migrations during deployment
- `general/container-orchestration.md` — Container orchestration and health check configuration
