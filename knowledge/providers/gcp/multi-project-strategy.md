# GCP Multi-Project Strategy

## Scope

GCP's resource organization is centered on the **project** as the primary blast-radius boundary, in contrast to AWS where the account plays that role and Azure where the subscription does. Covers when to use folders vs projects, the cost of project sprawl, Shared VPC for centralizing networking across projects, project lifecycle (creation, deletion, recovery), the relationship to billing accounts, the standard reference architecture for multi-project organizations, and the diagnostic patterns for accounts that have accumulated dozens of projects without an organizing structure. Mirrors `providers/aws/multi-account.md` for the GCP-specific concerns.

## Why projects matter

A GCP project is the unit that owns:

- **Resources** (VMs, buckets, databases, BigQuery datasets — every resource belongs to exactly one project)
- **IAM bindings** at the project level (which inherit to all resources in the project)
- **Billing** (a project is associated with a billing account; cost is attributed to the project)
- **Quotas and limits** (per-project API quotas)
- **APIs enabled** (each API must be enabled per project)
- **Service accounts** (service accounts are owned by a specific project)
- **Audit logs** (Admin Activity logs are per-project)

The project is the strongest blast-radius boundary in GCP. A compromise contained to a single project does not directly affect other projects in the same organization (though shared VPCs and shared service accounts can blur the boundary if they are not designed carefully).

The project boundary is roughly equivalent to:

- **AWS account** — for IAM scope, billing, and resource ownership
- **Azure subscription** — for resource ownership, quotas, and the strongest blast radius
- **Azure resource group** — for the lighter-weight grouping that does not include billing or quota implications (closest analog: GCP's labels and folder structure)

## When to create a new project

The standard rule of thumb: **one project per (workload × environment)**. A web application has separate `web-prod`, `web-staging`, `web-dev` projects. A data pipeline has separate `data-prod`, `data-staging`, `data-dev` projects.

Project creation should also happen when:

- A new workload is starting and needs its own resources, IAM, and billing attribution
- A workload's risk profile requires isolation from other workloads (e.g., regulated data should not share a project with non-regulated data)
- A workload's quota needs are different from other workloads in the same project (project quotas are shared across all resources)
- A workload needs different organizational policies than other workloads
- A team boundary changes and the team needs ownership of its own resources

Project creation should **not** happen for:

- Per-developer sandboxes (use a single shared sandbox project with strict cost controls instead, or use Cloud Workstations / Cloud Shell)
- Per-feature-branch test environments (use namespaces in a shared GKE cluster, or short-lived projects with auto-cleanup)
- Per-component within a workload (the workload should be a single project unless components have meaningfully different ownership)

## Folders for grouping

Folders are the GCP grouping container, equivalent to AWS Organizations OUs. A folder can contain projects and other folders, up to 10 levels of nesting. Folders are used to:

- Group projects by environment (Production, Non-Production, Sandbox)
- Group projects by business unit (Payments, Analytics, Platform)
- Apply IAM bindings at the folder level (a binding at the folder level inherits to all projects in that folder)
- Apply Organization Policies at the folder level (the GCP analog of AWS SCPs)

The standard reference structure for a mid-sized organization:

```
Organization (acme.com)
├── Production folder
│   ├── Payments folder
│   │   ├── prod-payments-api
│   │   ├── prod-payments-db
│   │   └── prod-payments-analytics
│   ├── Analytics folder
│   │   ├── prod-analytics-warehouse
│   │   └── prod-analytics-pipeline
│   └── Platform folder
│       ├── prod-platform-infra
│       └── prod-platform-tooling
├── Non-Production folder
│   └── (similar structure with dev/staging projects)
├── Shared folder
│   ├── shared-network (Shared VPC host project)
│   ├── shared-security (Cloud KMS, Secret Manager, security tooling)
│   └── shared-logging (log sink destinations)
├── Sandbox folder
│   └── per-team or per-project sandbox projects
└── Suspended folder
    └── projects pending deletion
```

## Shared VPC

**Shared VPC** is the GCP pattern for centralizing networking across multiple projects. A "host project" owns the VPC, and "service projects" attach their resources to subnets in the host project's VPC.

Shared VPC is the right answer when:

- Multiple workloads need to communicate on the same private network without going through public endpoints
- The networking team wants to own and audit the network design centrally, separately from the workload teams
- The organization wants a single Cloud DNS, Cloud Router, Cloud VPN, or Cloud Interconnect setup that all workloads use

Shared VPC is **not** the right answer when:

- Workloads have genuinely independent network requirements (separate IP ranges, separate firewall policies, separate routing)
- The blast radius of a network compromise needs to be the size of one project, not the size of all projects sharing the VPC
- The workload is in a regulated perimeter that requires network-level isolation

The Shared VPC host project is typically the `shared-network` project under the Shared folder. Service projects are workload projects that consume the shared network.

## Project lifecycle

### Creation

Projects should be created via **Terraform / IaC** or via the **Project Factory** module that automatically applies the standard configuration:

- Move to the right folder
- Apply the standard IAM bindings (workload owner, security team read access)
- Configure billing
- Enable the standard APIs the workload needs
- Apply default labels (`environment`, `owner`, `cost-center`, `business-unit`)
- Configure log sinks to the shared logging project

Manual project creation via the console is the source of "snowflake" projects that diverge from the standard. Disable manual creation at the org level via Organization Policy (`compute.skipDefaultNetworkCreation` and similar) to enforce the IaC path.

### Deletion

Projects should be **shut down** before deletion, with a 30-day cooldown:

1. Move the project to the `Suspended` folder
2. Apply a deny-everything Organization Policy at the Suspended folder level
3. Wait 30 days, monitoring for any errors that indicate the project is still being used
4. Schedule project deletion

The 30-day cooldown is critical. Project deletion is not immediately reversible — once the deletion grace period (30 days for projects) elapses, the project and all its resources are gone forever.

### Recovery

Within the 30-day grace period, a deleted project can be restored via `gcloud projects undelete <project-id>`. After the grace period, the project is unrecoverable.

## Common Implementation Patterns

### Standard project structure for a mid-sized organization

- **One organization** tied to the corporate Cloud Identity / Workspace domain
- **Folders** for environment (Production, Non-Production), business unit (Payments, Analytics, Platform), and shared infrastructure (Shared)
- **Projects** per (workload × environment), grouped under the appropriate folder
- **Shared VPC** in the `shared-network` project, with service projects attached as needed
- **Shared security** project for Cloud KMS keys and Secret Manager that span multiple workloads
- **Shared logging** project for centralized log sinks

### Project Factory for automated provisioning

A Project Factory is a Terraform module (or equivalent) that creates projects with the standard configuration. The factory takes inputs like project name, owner email, environment, and business unit, and produces:

- A project in the right folder
- Standard labels applied
- Standard IAM bindings (workload owner, security read, billing admin)
- APIs enabled
- VPC attachment to the shared VPC host
- Log sink to the shared logging project
- Default Cloud KMS key ring and key
- Default Cloud Storage bucket for build artifacts

The factory is invoked via a pull request workflow, which provides audit trail and review of every new project.

### Shared services project

The `shared-services` project (or `shared-security` in some structures) holds resources used by multiple workloads:

- **Cloud KMS key rings and keys** that are shared across workloads with the same data classification
- **Secret Manager secrets** that are shared (e.g., third-party API keys used by multiple workloads)
- **Artifact Registry repositories** for shared container images and language packages
- **Service accounts** that workloads can impersonate for cross-workload integration

The shared services project requires careful IAM design — every grant is shared across multiple workloads, so the blast radius of a misgrant is wider than for a workload-specific project.

## Common Decisions (ADR Triggers)

- **Project per workload vs project per environment vs project per (workload × environment)** — project per (workload × environment) is the standard. Project per environment (one prod project for everything) is too coarse. Project per workload (one project for all environments) blurs the production/non-production boundary.
- **Folder structure: by environment first vs by business unit first** — environment-first is more common because IAM and Organization Policy patterns typically vary by environment more than by business unit. Business-unit-first is appropriate when business units operate semi-independently with different security postures.
- **Shared VPC vs per-project VPCs** — Shared VPC for organizations where networking is centrally managed. Per-project VPCs for organizations where workloads are operationally independent and the network is not a shared concern.
- **Project Factory via Terraform vs Project Factory via gcloud scripts** — Terraform is more declarative and easier to audit. gcloud scripts are simpler for one-off use. Pick one and stick with it.
- **Suspended folder + deletion vs immediate deletion** — Suspended folder + 30-day cooldown for any project that has had real workloads. Immediate deletion only for sandbox projects that are known to have no dependencies.

## Reference Links

- [Resource hierarchy](https://cloud.google.com/resource-manager/docs/cloud-platform-resource-hierarchy)
- [Organization, folders, and projects](https://cloud.google.com/resource-manager/docs/creating-managing-organization)
- [Shared VPC](https://cloud.google.com/vpc/docs/shared-vpc)
- [Project Factory (Terraform module)](https://github.com/terraform-google-modules/terraform-google-project-factory)
- [Cloud Foundation Toolkit](https://cloud.google.com/foundation-toolkit)

## See Also

- `providers/gcp/iam-organizations.md` — IAM model and resource hierarchy in detail
- `providers/gcp/networking.md` — Shared VPC details and broader networking
- `providers/gcp/security.md` — broader security service set
- `providers/aws/multi-account.md` — equivalent multi-account architecture in AWS
- `providers/azure/landing-zones.md` — equivalent landing zone architecture in Azure
- `frameworks/aws-security-reference-architecture.md` — AWS SRA, similar in shape
