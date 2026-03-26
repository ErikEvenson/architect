# HashiCorp Certifications and Training

## Scope

HashiCorp certification paths and training resources. Covers Terraform Associate (003), Terraform Professional (coming), Vault Associate (002), Vault Professional, Consul Associate (002). Exam format, training platforms (HashiCorp Developer, HashiCorp Learn), relevance to IaC and secrets management engagements.

## Checklist

- [Critical] Is Terraform Associate (003) identified as the baseline certification for all engineers using Terraform — covers HCL, providers, state management, modules, and workflow?
- [Critical] Is the Terraform Associate exam format understood — multiple choice and fill-in-the-blank, 60 minutes, covers Terraform OSS and HCP Terraform concepts?
- [Recommended] Is Vault Associate (002) required for teams managing secrets and encryption — covers authentication methods, secrets engines, policies, tokens, and Vault architecture?
- [Recommended] Is Vault Professional targeted for senior engineers designing production Vault deployments — covers HA, DR replication, performance standbys, namespaces, and advanced configuration?
- [Recommended] Are HashiCorp Developer tutorials (developer.hashicorp.com) leveraged for free hands-on training aligned to each certification?
- [Recommended] Is certification validity tracked — HashiCorp certifications are valid for 2 years and require re-examination at the current version to renew?
- [Recommended] Is Consul Associate evaluated for teams implementing service mesh or service discovery — covers service registration, health checks, KV store, and Consul architecture?
- [Optional] Is Terraform Professional certification evaluated for senior IaC architects when available — covers advanced patterns, collaboration, and enterprise workflows?
- [Optional] Are HashiCorp partner program certification requirements assessed — HashiCorp Partner Network tiers may require minimum certified headcount?
- [Optional] Is Packer certification or training evaluated for teams building machine images as part of IaC pipelines?

## Why This Matters

Terraform is the dominant IaC tool across cloud providers, and Terraform Associate certification validates practical competency with HCL, state management, and module design. Vault certification is increasingly important as secrets management becomes a compliance requirement. The HashiCorp certification program is relatively new compared to cloud provider programs, but certifications carry weight in RFP evaluations and staffing decisions for IaC engagements. The 2-year validity is standard. HashiCorp's free tutorial platform provides extensive hands-on content but structured certification paths help ensure consistent team skill levels.

## Common Decisions (ADR Triggers)

- Terraform Associate priority vs cloud-provider IaC certifications (e.g., AWS CloudFormation not separately certified, Azure has AZ-400 for DevOps)
- Vault Associate vs Vault Professional based on engagement complexity
- Consul certification priority — only relevant if service mesh/discovery is in scope
- HashiCorp certification vs hands-on experience weighting in hiring/staffing
- Free HashiCorp Developer tutorials vs paid instructor-led training

## Training Resources

### Official Training Platform

- **HashiCorp Developer (developer.hashicorp.com)** — free tutorials, documentation, and hands-on exercises for all products, aligned to certification objectives

### Instructor-Led Training

- Delivered by HashiCorp or authorized partners, 2-3 day courses ($1,500-2,500), available for Terraform, Vault, and Consul

### Hands-On Labs

- Instruqt-based interactive labs embedded in tutorials (free)
- HashiCorp Cloud Platform (HCP) free tier for managed Terraform/Vault/Consul

### Learning Paths by Role

- **IaC Engineer:** Terraform Associate → Terraform Professional (when available)
- **Security Engineer:** Vault Associate → Vault Professional
- **Platform Engineer:** Terraform Associate + Consul Associate

### Training Cost and Time Estimates

- ~40-60 hours per Associate cert
- Exam fee $70.50 (Associate)
- Free tutorials via HashiCorp Developer
- Instructor-led training $1,500-2,500 per course

## Reference Links

- [HashiCorp Certifications](https://developer.hashicorp.com/certifications) -- Terraform Associate, Vault Associate/Professional, and Consul Associate exam details
- [HashiCorp Developer Tutorials](https://developer.hashicorp.com/tutorials) -- free hands-on training aligned to certification topics
- [HashiCorp Certification FAQ](https://developer.hashicorp.com/certifications/faq) -- exam format, validity period, renewal process, and retake policies

## See Also

- `general/certification-training.md` -- cross-vendor certification strategy
- `providers/hashicorp/terraform.md` -- Terraform IaC
- `providers/hashicorp/vault.md` -- Vault secrets management
- `providers/hashicorp/consul.md` -- Consul service mesh
- `general/iac-planning.md` -- IaC planning patterns
