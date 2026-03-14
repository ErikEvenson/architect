# Deployment

## Scope

This file covers **what** deployment strategy decisions need to be made (deployment models, IaC approach, rollback procedures). For provider-specific CI/CD implementation, see the provider files.

## Checklist

- [ ] **[Critical]** What is the deployment strategy? (rolling, blue-green, canary, immutable)
- [ ] **[Critical]** How is application code built and packaged? (Docker images, AMIs, packages)
- [ ] **[Critical]** Is there a CI/CD pipeline? What triggers deployments?
- [ ] **[Critical]** How is infrastructure provisioned? (IaC — Terraform, CloudFormation, Pulumi)
- [ ] **[Critical]** Is infrastructure code version controlled?
- [ ] **[Critical]** What is the rollback procedure? How fast is rollback?
- [ ] **[Recommended]** Are database migrations handled as part of deployment?
- [ ] **[Recommended]** Is there a staging/pre-production environment that mirrors production?
- [ ] **[Recommended]** Are deployments zero-downtime?
- [ ] **[Recommended]** Is there a deployment approval process? (manual gates, change management)
- [ ] **[Optional]** How are feature flags managed?
- [ ] **[Optional]** Are deployment metrics tracked? (deploy frequency, lead time, failure rate, MTTR)
- [ ] **[Recommended]** Is there a deployment runbook?

## Why This Matters

Bad deployments are the #1 cause of outages. A reliable deployment pipeline with fast rollback reduces risk. Immutable deployments eliminate configuration drift. IaC ensures environments are reproducible.

## Common Decisions (ADR Triggers)

- **Deployment strategy** — rolling vs blue-green vs immutable
- **IaC tool** — Terraform vs CloudFormation vs Pulumi
- **CI/CD platform** — GitHub Actions, GitLab CI, Jenkins, CodePipeline
- **Artifact format** — Docker images vs AMIs vs packages
- **Environment strategy** — how many environments, how they map to branches

## See Also

- `providers/openshift/ci-cd.md` — OpenShift CI/CD pipelines and deployment
