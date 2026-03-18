# Infrastructure as Code Planning

## Scope

This file covers how to plan IaC for an architecture design: tool selection, module structure, state management, resource inventory, and effort estimation. For tool-specific details, see the provider files (Terraform, CloudFormation, Heat, Bicep, etc.).

## Checklist

- [ ] **[Critical]** What IaC tool(s) will be used? (Must be asked — not assumed. Options vary by provider.)
- [ ] **[Critical]** What is the module/stack structure? (How are resources grouped — by tier, by service, by environment?)
- [ ] **[Critical]** Where is IaC state stored? (Remote backend: S3, GCS, Azure Storage, Terraform Cloud. Never local for shared work.)
- [ ] **[Recommended]** How are environments managed? (Workspaces, separate state files, var files, directory structure)
- [ ] **[Recommended]** What is the resource inventory? (Every resource to be provisioned, with module assignment and complexity)
- [ ] **[Recommended]** What resources are provisioned manually vs automated? (One-time setup items, bootstrap resources)
- [ ] **[Recommended]** How are IaC changes applied? (CI/CD pipeline: plan on PR, apply on merge. Manual apply for sensitive changes.)
- [ ] **[Recommended]** Is drift detection configured? (Detect manual changes that diverge from IaC state)
- [ ] **[Recommended]** How are secrets handled in IaC? (Never in .tf files. Use variables, Vault, or secrets manager references.)
- [ ] **[Optional]** Is there an IaC testing strategy? (terraform validate, tflint, checkov, terratest, policy-as-code)
- [ ] **[Optional]** Are cost estimates generated from IaC? (Infracost, Terraform Cloud cost estimation)
- [ ] **[Optional]** Is there a module registry? (Terraform Registry, private module registry, git-based modules)

## IaC Tool Selection by Provider

| Provider | Options |
|----------|---------|
| AWS | Terraform, CloudFormation, CDK, Pulumi |
| Azure | Terraform, Bicep, ARM templates, Pulumi |
| GCP | Terraform, Deployment Manager, Pulumi |
| OpenStack | Terraform (OpenStack provider), Heat, Pulumi |
| Nutanix | Terraform (Nutanix provider), Calm blueprints |
| VMware | Terraform (vSphere provider), Ansible, PowerCLI |
| Kubernetes | Helm, Kustomize, Terraform (K8s provider), Pulumi |
| Multi-provider | Terraform (recommended — single tool across providers) |

Multiple tools may be used in one project (e.g., Terraform for infrastructure + Helm for K8s workloads).

## Module Structure Patterns

### By Tier (recommended for three-tier)
```
modules/
├── networking/    # VPC, subnets, security groups, NAT
├── compute/       # EC2/Nova instances, ASG, load balancers
├── database/      # RDS/Trove, caching
├── monitoring/    # CloudWatch, Prometheus
└── dns/           # Route 53, DNS records
```

### By Service (recommended for microservices)
```
modules/
├── shared-infra/  # VPC, cluster, registry
├── service-a/     # Deployment, service, ingress
├── service-b/
└── database/      # Shared database resources
```

### By Environment
```
environments/
├── dev/
│   └── main.tf    # References modules with dev vars
├── staging/
│   └── main.tf
└── production/
    └── main.tf
```

## Resource Inventory Template

| Resource | IaC Module | Provider Resource | Complexity | Notes |
|----------|-----------|-------------------|------------|-------|
| VPC | networking | aws_vpc | Simple | CIDR from variable |
| Public Subnets (3) | networking | aws_subnet | Simple | One per AZ |
| Private Subnets (3) | networking | aws_subnet | Simple | One per AZ |
| NAT Gateway | networking | aws_nat_gateway | Simple | |
| Security Groups | networking | aws_security_group | Moderate | Multiple rules, cross-references |
| EC2 Instance | compute | aws_instance | Simple | From launch template |
| Auto Scaling Group | compute | aws_autoscaling_group | Moderate | Scaling policies |
| ALB | compute | aws_lb | Moderate | Listeners, target groups |
| RDS Instance | database | aws_db_instance | Moderate | Subnet group, parameter group |
| ElastiCache | database | aws_elasticache_cluster | Moderate | Subnet group, replication |

### Complexity Levels

- **Simple** — Standard resource with minimal configuration. Existing modules/examples available.
- **Moderate** — Resource with dependencies, multiple configuration blocks, or conditional logic.
- **Complex** — Custom modules, cross-account, multi-region, or requires custom scripts/provisioners.

## Effort Estimation Guidelines

| Scope | Resources | Modules | Typical Effort |
|-------|-----------|---------|---------------|
| Small | 5-15 | 2-3 | 1-2 weeks |
| Medium | 15-40 | 4-6 | 2-4 weeks |
| Large | 40-100 | 7-12 | 4-8 weeks |
| Enterprise | 100+ | 12+ | 8+ weeks |

*Effort assumes experienced IaC practitioner. Add 50-100% for teams new to the tool.*

## Why This Matters

Architecture without IaC is just a diagram. IaC makes the architecture reproducible, version-controlled, and auditable. Without planning the IaC structure upfront, teams end up with monolithic configs, duplicated code, manual steps, and state management problems that are expensive to fix later.

## Common Decisions (ADR Triggers)

- **IaC tool selection** — which tool(s) for which layer. Must be a user decision, not assumed.
- **State backend** — S3+DynamoDB, Terraform Cloud, GCS, Azure Storage
- **Module granularity** — one module per resource type vs one per logical tier vs one per service
- **Environment strategy** — workspaces vs directory structure vs separate repos
- **CI/CD for IaC** — plan on PR, apply on merge, manual approval gates
- **Drift management** — ignore, detect and alert, auto-remediate

## Reference Links

- [Terraform](https://www.terraform.io/)
- [OpenTofu](https://opentofu.org/)
- [Pulumi](https://www.pulumi.com/)
- [Infracost](https://www.infracost.io/)
- [Checkov](https://www.checkov.io/)
- [tflint](https://github.com/terraform-linters/tflint)

## See Also

- `providers/hashicorp/terraform.md` — Terraform-specific configuration and patterns
- `providers/openstack/heat.md` — OpenStack Heat template patterns
- `general/deployment.md` — Deployment strategy decisions
- `general/governance.md` — Tagging standards, naming conventions, policy-as-code
