# Deployment

## Checklist

- [ ] What is the deployment strategy? (rolling, blue-green, canary, immutable)
- [ ] How is application code built and packaged? (Docker images, AMIs, packages)
- [ ] Is there a CI/CD pipeline? What triggers deployments?
- [ ] How is infrastructure provisioned? (IaC — Terraform, CloudFormation, Pulumi)
- [ ] Is infrastructure code version controlled?
- [ ] What is the rollback procedure? How fast is rollback?
- [ ] Are database migrations handled as part of deployment?
- [ ] Is there a staging/pre-production environment that mirrors production?
- [ ] Are deployments zero-downtime?
- [ ] Is there a deployment approval process? (manual gates, change management)
- [ ] How are feature flags managed?
- [ ] Are deployment metrics tracked? (deploy frequency, lead time, failure rate, MTTR)
- [ ] Is there a deployment runbook?

## Why This Matters

Bad deployments are the #1 cause of outages. A reliable deployment pipeline with fast rollback reduces risk. Immutable deployments eliminate configuration drift. IaC ensures environments are reproducible.

## Common Decisions (ADR Triggers)

- **Deployment strategy** — rolling vs blue-green vs immutable
- **IaC tool** — Terraform vs CloudFormation vs Pulumi
- **CI/CD platform** — GitHub Actions, GitLab CI, Jenkins, CodePipeline
- **Artifact format** — Docker images vs AMIs vs packages
- **Environment strategy** — how many environments, how they map to branches
