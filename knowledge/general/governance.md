# Cloud Governance

## Scope

This file covers **organizational governance practices** for cloud environments: tagging, naming, account structure, FinOps, policy-as-code, and guardrails. For cost optimization specifics, see `general/cost.md`. For security controls, see `general/security.md`.

## Checklist

- [ ] **[Critical]** Are mandatory tags defined and enforced? (owner, environment, cost-center, project at minimum)
- [ ] **[Critical]** Is there a resource naming convention? (documented, consistent across providers, enforced via policy)
- [ ] **[Critical]** Is the account/subscription/project structure defined? (landing zones, organizational units, separation of concerns)
- [ ] **[Recommended]** Is policy-as-code implemented? (OPA/Gatekeeper, HashiCorp Sentinel, Azure Policy, AWS SCPs)
- [ ] **[Critical]** Are Service Control Policies or Organization Policies restricting dangerous actions? (prevent disabling logging, public S3 buckets, unapproved regions)
- [ ] **[Critical]** Are budget alerts and spending controls in place? (per account, per team, per project)
- [ ] **[Recommended]** Is there a FinOps practice? (cost visibility, allocation, optimization cadence)
- [ ] **[Optional]** Is there a Cloud Center of Excellence or platform team? (standards, enablement, shared services)
- [ ] **[Recommended]** Are guardrails automated rather than gate-based? (prevent vs approve — guardrails scale, gates do not)
- [ ] **[Optional]** Is there a service catalog of approved architectures? (pre-approved patterns, self-service provisioning)
- [ ] **[Recommended]** Is there a process for requesting exceptions to governance policies?
- [ ] **[Recommended]** Are resource lifecycle policies defined? (TTL for dev environments, cleanup automation)

## Why This Matters

Without governance, cloud environments become ungovernable within months. Untagged resources make cost allocation impossible — finance cannot attribute spend to teams or projects. Missing naming conventions lead to confusion and accidental deletions. Flat account structures create blast radius problems where one team's misconfiguration affects everyone.

The most damaging governance failure is **shadow IT at scale**: teams provisioning resources without standards, creating security gaps, cost surprises, and compliance violations that compound over time. Governance is not bureaucracy — it is the operating system for cloud at scale.

## Tagging Standards

### Mandatory Tags (Enforce via Policy)

| Tag Key | Purpose | Example Values |
|---------|---------|----------------|
| `owner` | Team or individual responsible | `platform-team`, `jane.doe@company.com` |
| `environment` | Deployment stage | `production`, `staging`, `development`, `sandbox` |
| `cost-center` | Financial allocation | `engineering-1234`, `marketing-5678` |
| `project` | Business project or product | `checkout-service`, `data-pipeline-v2` |

### Recommended Tags (Encourage Adoption)

| Tag Key | Purpose | Example Values |
|---------|---------|----------------|
| `managed-by` | IaC tool that manages the resource | `terraform`, `cloudformation`, `pulumi` |
| `data-classification` | Sensitivity level | `public`, `internal`, `confidential`, `restricted` |
| `compliance` | Applicable compliance framework | `hipaa`, `pci`, `sox` |
| `ttl` | Expected resource lifetime | `2025-12-31`, `ephemeral`, `permanent` |
| `backup` | Backup policy | `daily`, `weekly`, `none` |

### Tag Enforcement

| Provider | Enforcement Mechanism | Capability |
|----------|-----------------------|------------|
| **AWS** | SCP + AWS Config Rules + Tag Policies | Prevent untagged resource creation, auto-remediate |
| **Azure** | Azure Policy (deny/append/audit) | Deny resource creation without required tags, inherit tags |
| **GCP** | Organization Policy + Labels | Audit label presence, restrict resource creation |

## Resource Naming Conventions

### Recommended Pattern

```
{provider}-{environment}-{region}-{project}-{resource-type}-{identifier}
```

### Examples

| Resource | Name |
|----------|------|
| AWS VPC | `aws-prod-use1-checkout-vpc-main` |
| Azure Resource Group | `az-prod-eus-checkout-rg` |
| GCP GKE Cluster | `gcp-prod-usc1-platform-gke-primary` |
| S3 Bucket | `aws-prod-use1-checkout-data-lake` |

### Naming Rules

- Lowercase only (avoid case-sensitivity issues across providers)
- Hyphens as separators (underscores cause issues in DNS names)
- No personal names or temporary designations (`test-123`, `johns-bucket`)
- Include environment to prevent accidental cross-environment operations
- Keep under 63 characters (DNS label limit)

## Account / Subscription / Project Structure

### Landing Zone Pattern

```
Organization Root
├── Security OU
│   ├── Log Archive Account (centralized logging)
│   ├── Security Tooling Account (GuardDuty, Security Hub)
│   └── Audit Account (read-only cross-account access)
├── Infrastructure OU
│   ├── Network Hub Account (Transit Gateway, DNS)
│   ├── Shared Services Account (CI/CD, artifact repos)
│   └── Identity Account (SSO, directory services)
├── Workloads OU
│   ├── Production OU
│   │   ├── Team-A Production Account
│   │   └── Team-B Production Account
│   ├── Staging OU
│   │   ├── Team-A Staging Account
│   │   └── Team-B Staging Account
│   └── Development OU
│       ├── Team-A Development Account
│       └── Team-B Development Account
└── Sandbox OU
    ├── Developer Sandbox Accounts (auto-cleanup, spending cap)
    └── Experimentation Accounts
```

### Provider Landing Zone Tools

| Provider | Tool | What It Provides |
|----------|------|-----------------|
| **AWS** | Control Tower + Account Factory | Automated account provisioning, guardrails, SSO |
| **Azure** | Cloud Adoption Framework Landing Zones | Management groups, policy, deployment stacks (Blueprints deprecated July 2026), Hub-spoke networking |
| **GCP** | Cloud Foundation Toolkit | Organization, folders, projects, shared VPC |

### Account Separation Principles

- **Production is always separate** from non-production (blast radius isolation)
- **Security and logging accounts** are separate and restricted (tamper-proof audit trail)
- **Sandbox accounts** have spending caps and auto-cleanup (safe experimentation)
- **One workload per account** is ideal; group only tightly coupled services
- **Networking hub** centralizes connectivity (Transit Gateway, Hub VNet, Shared VPC)

## Policy-as-Code

| Tool | Scope | Language | Best For |
|------|-------|----------|----------|
| **OPA / Gatekeeper** | Kubernetes, Terraform, CI/CD | Rego | K8s admission control, Terraform plan validation |
| **HashiCorp Sentinel** | Terraform Enterprise/Cloud | Sentinel | Terraform-native policy enforcement |
| **AWS SCPs** | AWS Organizations | JSON | Account-level permission boundaries |
| **Azure Policy** | Azure subscriptions | JSON | Resource compliance, auto-remediation |
| **GCP Organization Policy** | GCP organization/folders | Constraints | Resource restriction, location enforcement |

### Essential Policies to Implement

1. **Deny public storage** — No public S3 buckets, Azure blob containers, or GCS buckets
2. **Require encryption** — All storage and databases must use encryption at rest
3. **Restrict regions** — Resources only in approved regions (data sovereignty)
4. **Require logging** — CloudTrail, Activity Log, or Audit Log cannot be disabled
5. **Enforce tagging** — Resources without mandatory tags are denied
6. **Restrict instance types** — Prevent expensive instance types in dev/sandbox
7. **Deny public IPs** — Compute instances cannot have direct public IPs (use load balancers)
8. **Require MFA** — Privileged actions require multi-factor authentication

## Guardrails vs Gates

| Aspect | Guardrails | Gates |
|--------|-----------|-------|
| **Mechanism** | Automated prevention/detection | Manual approval/review |
| **Speed** | Instant (no human bottleneck) | Hours to days |
| **Scalability** | Scales to thousands of teams | Does not scale |
| **Developer experience** | Self-service within boundaries | Ticket-and-wait |
| **When to use** | Default for all standard controls | High-risk exceptions only |

**Prefer guardrails.** Gates create bottlenecks and frustration. Guardrails let teams move fast within safe boundaries. Reserve gates for genuinely exceptional requests (new region, new compliance scope, production database schema changes).

## FinOps Practices

### FinOps Maturity Phases

1. **Inform** — Visibility into who is spending what (tagging, cost dashboards, allocation)
2. **Optimize** — Act on cost data (rightsizing, reserved instances, spot, waste elimination)
3. **Operate** — Continuous governance (budget alerts, anomaly detection, optimization cadence)

### Key FinOps Activities

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Cost allocation review | Monthly | FinOps team + Finance |
| Rightsizing recommendations | Monthly | Engineering teams |
| Reserved instance / savings plan planning | Quarterly | FinOps team |
| Anomaly investigation | As alerted | Resource owner |
| Unused resource cleanup | Weekly (automated) | Platform team |
| Unit cost tracking (cost per transaction, per user) | Monthly | Product + Engineering |

### Budget Controls

| Provider | Budget Tool | Alert Capabilities |
|----------|------------|-------------------|
| **AWS** | AWS Budgets | Forecasted and actual spend, SNS/email alerts, auto-actions |
| **Azure** | Cost Management Budgets | Action groups, auto-shutdown, email alerts |
| **GCP** | Cloud Billing Budgets | Pub/Sub alerts, programmatic responses |

## Cloud Center of Excellence (CCoE)

A CCoE is a cross-functional team that establishes cloud standards and enables adoption. It is **not** a gate — it is a platform team.

### CCoE Responsibilities

- Define and maintain **reference architectures** (pre-approved, well-tested patterns)
- Provide **self-service infrastructure modules** (Terraform modules, CloudFormation templates)
- Run **enablement programs** (training, office hours, architecture reviews)
- Manage **shared services** (CI/CD, observability, networking, security tooling)
- Track **cloud maturity** across teams and drive improvement

### CCoE Anti-Patterns

- Becoming a bottleneck (approval-based instead of enablement-based)
- Building ivory tower standards nobody follows
- Not including practitioners from delivery teams
- Focusing on control instead of capability

## Common Decisions (ADR Triggers)

- **Tagging strategy** — which tags are mandatory, enforcement mechanism, tag inheritance
- **Account structure** — single vs multi-account, OU hierarchy, account provisioning process
- **Naming convention** — pattern, abbreviations, uniqueness requirements
- **Policy-as-code tool** — OPA vs Sentinel vs native provider policies
- **Guardrails vs gates** — what requires automated prevention vs manual approval
- **FinOps model** — centralized FinOps team vs embedded in engineering vs hybrid
- **Budget alert thresholds** — percentage-based vs absolute, who gets notified
- **CCoE charter** — scope, staffing model, relationship to security and platform teams

## See Also

- `general/cost.md` — Cost optimization techniques and pricing models
- `general/security.md` — Security controls and compliance mapping
- `general/identity.md` — IAM, SSO, and access management
- `compliance/soc2.md` — SOC 2 governance controls (CC1)
