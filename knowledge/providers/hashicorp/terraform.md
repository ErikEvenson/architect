# HashiCorp Terraform

## Checklist

- [ ] State is stored in a remote backend (S3 + DynamoDB for locking, GCS, Azure Blob, or Terraform Cloud); local state is never used beyond initial prototyping
- [ ] State locking is enabled and tested; DynamoDB table exists for S3 backend, or backend natively supports locking (GCS, Terraform Cloud, Azure with lease)
- [ ] State file access is restricted via IAM policies; state contains sensitive values (passwords, keys, certificates) in plaintext and must be treated as a secret
- [ ] Workspaces or directory-based separation isolates environments (dev/staging/production); workspace-based separation uses `terraform.workspace` conditionals, directory-based uses separate backend configs
- [ ] Modules are versioned and sourced from a registry (Terraform Registry, private registry, or Git tags); `source` references pin to a specific version, never `main` branch
- [ ] Provider versions are constrained in `required_providers` block with pessimistic version constraints (`~> 5.0`); unconstrained providers risk breaking changes on `terraform init`
- [ ] Lifecycle rules are used deliberately: `prevent_destroy` on databases and stateful resources, `ignore_changes` on fields managed outside Terraform (e.g., ASG desired count, tags managed by external systems)
- [ ] `terraform plan` output is reviewed and approved before `terraform apply` in CI/CD; no auto-apply without plan review except in controlled Terraform Cloud workspaces
- [ ] Sensitive variables are marked with `sensitive = true` and injected via environment variables (`TF_VAR_*`), Vault, or Terraform Cloud variable sets; never hardcoded in `.tf` files
- [ ] Import blocks (`import {}`) and `moved {}` blocks are used for adopting existing resources and refactoring without destroy/recreate cycles
- [ ] `.terraform.lock.hcl` is committed to version control to ensure consistent provider versions across team members and CI/CD
- [ ] Data sources are used to reference resources managed outside the current Terraform configuration; cross-state references use `terraform_remote_state` or data sources against the actual API
- [ ] CI/CD pipeline runs `terraform fmt -check`, `terraform validate`, and `tflint` or `checkov` before `terraform plan`

## Why This Matters

Terraform manages the actual infrastructure. A state file out of sync with reality causes resource duplication, accidental destruction, or drift that is expensive to reconcile. State locking prevents two engineers or CI pipelines from applying conflicting changes simultaneously, which can corrupt state or create partial deployments. Unpinned provider versions mean that `terraform init` on Tuesday may pull a different provider version than Monday, changing plan behavior silently. Module versioning without pinning means that a module author's breaking change propagates to all consumers on their next `init`. Lifecycle rules prevent Terraform from destroying a production database during a refactor. These are not edge cases; they are the primary failure modes teams encounter when scaling Terraform usage beyond a single operator.

## Common Decisions (ADR Triggers)

- **State backend selection**: S3 + DynamoDB is the most common for AWS shops (cheap, reliable, well-documented). Terraform Cloud provides state management, locking, run history, and policy enforcement in one service but adds cost and vendor dependency. GCS and Azure Blob are natural choices for their respective clouds. Document the backend, who has access, and the backup/recovery strategy.
- **Workspace-based vs directory-based environment separation**: Workspaces share the same code with different state files, requiring conditionals (`terraform.workspace == "prod"`) for environment-specific values. Directory-based separation (envs/dev/, envs/prod/) duplicates backend config but makes each environment's configuration explicit. Workspaces are simpler for small differences; directories are clearer for large divergence. Terragrunt offers a third approach with DRY configuration and automatic backend config generation.
- **Module granularity**: One module per logical component (VPC, EKS cluster, RDS instance) vs large modules that bundle related resources (entire application stack). Fine-grained modules are more reusable but require more wiring. Coarse modules are faster to deploy but harder to customize. Decide based on team size and reuse requirements.
- **Terraform Cloud/Enterprise vs self-managed CI/CD**: Terraform Cloud provides remote execution, state management, Sentinel policies, cost estimation, and a UI. Self-managed (GitHub Actions, GitLab CI, Jenkins) provides more control and avoids per-resource pricing. The decision affects workflow, auditability, and policy enforcement capabilities.
- **Terragrunt adoption**: Terragrunt adds DRY configuration, automatic remote state setup, dependency management between modules, and `run-all` for multi-module operations. It adds a tool to the chain (Terragrunt wraps Terraform) but significantly reduces boilerplate in large, multi-environment, multi-account setups. Adopt early or not at all; retrofitting is painful.
- **Import strategy for existing resources**: `terraform import` (CLI) vs `import` blocks (declarative, plannable). Import blocks are preferred in Terraform 1.5+ because they appear in plan output and can be code-reviewed. Document the process for adopting brownfield infrastructure.
- **Sensitive data handling**: Terraform state stores all attribute values in plaintext. Options include encrypting the state backend (S3 SSE-KMS), using Vault for dynamic secrets that rotate automatically, or restructuring to keep secrets outside Terraform entirely. The choice affects the security model and operational complexity.

## Reference Architectures

## Version Notes

| Feature | 1.5 | 1.6 | 1.7 | 1.8 | 1.9 |
|---|---|---|---|---|---|
| `import` block (declarative) | GA | GA | GA | GA | GA |
| `removed` block | Not available | GA | GA | GA | GA |
| `check` block (assertions) | GA | GA | GA | GA | GA |
| `terraform test` framework | Experimental | GA | GA (improved mocking) | GA | GA |
| Provider-defined functions | Not available | Not available | GA | GA | GA |
| `ephemeral` resources | Not available | Not available | Not available | Not available | GA |
| `moved` block (refactoring) | GA | GA | GA | GA | GA |
| S3 state backend native locking | Not available | Not available | Not available | GA (no DynamoDB needed) | GA |
| `.tf.json` generation improvements | GA | GA | GA | GA | GA |
| Provider installation caching | GA | GA | GA (improved) | GA | GA |
| `terraform plan -generate-config-out` | GA (import config gen) | GA | GA | GA | GA |
| HCP Terraform (cloud block) | GA | GA | GA | GA | GA |
| License | MPL 2.0 | BSL 1.1 | BSL 1.1 | BSL 1.1 | BSL 1.1 |

**Key changes across versions:**
- **1.5 -- Import blocks:** Introduced declarative `import` blocks that appear in `terraform plan` output and can be code-reviewed, replacing the imperative `terraform import` CLI command. Combined with `terraform plan -generate-config-out`, this enables generating HCL configuration for existing resources during import.
- **1.6 -- Removed blocks and testing GA:** The `removed` block allows declaring that a resource should be removed from state without destroying the actual infrastructure (the inverse of import). The `terraform test` framework reached GA, enabling integration tests with `.tftest.hcl` files that create real infrastructure, run assertions, and clean up.
- **1.7 -- Provider functions and mock testing:** Provider-defined functions allow providers to expose custom functions callable in HCL expressions (e.g., `provider::aws::arn_parse()`). The testing framework added mock providers and override capabilities for faster, isolated testing without provisioning real infrastructure.
- **1.8 -- S3 native locking and refactoring:** The S3 backend gained native state locking using S3 conditional writes, eliminating the need for a DynamoDB table for lock management. This simplifies the most common backend configuration.
- **1.9 -- Ephemeral resources:** Ephemeral resources are created, used during the plan/apply cycle, and then discarded -- they are never stored in state. This is designed for sensitive data like temporary credentials, reducing the security risk of secrets persisting in state files.
- **License change (1.6):** Terraform changed from Mozilla Public License 2.0 (open source) to Business Source License 1.1 starting with version 1.6. This prompted the creation of OpenTofu, a community fork maintaining the MPL 2.0 license. Evaluate licensing implications for your organization when choosing between Terraform 1.6+ and OpenTofu.

### Multi-Account AWS with Terragrunt

```
repo-structure/
  |-- terragrunt.hcl              (root config: remote_state, generate provider)
  |-- _envcommon/                  (shared module configurations)
  |     |-- vpc.hcl
  |     |-- eks.hcl
  |     |-- rds.hcl
  |
  |-- accounts/
       |-- dev/
       |    |-- account.hcl        (account_id, region defaults)
       |    |-- us-east-1/
       |         |-- vpc/
       |         |    |-- terragrunt.hcl  (include root + envcommon/vpc)
       |         |-- eks/
       |         |    |-- terragrunt.hcl  (dependency on vpc)
       |         |-- rds/
       |              |-- terragrunt.hcl  (dependency on vpc)
       |
       |-- staging/
       |    |-- (same structure, different values)
       |
       |-- prod/
            |-- account.hcl
            |-- us-east-1/
            |    |-- (same structure, production sizing)
            |-- eu-west-1/
                 |-- (same structure, EU region)

Remote State per component:
  s3://company-terraform-state/dev/us-east-1/vpc/terraform.tfstate
  s3://company-terraform-state/prod/us-east-1/eks/terraform.tfstate

DynamoDB: company-terraform-locks (single table, all states)
```

### Terraform Cloud Organization

```
Terraform Cloud Organization: company-infra
  |
  +-- Project: Platform
  |     |-- Workspace: platform-vpc-dev        (auto-apply, VCS: main branch, path: modules/vpc)
  |     |-- Workspace: platform-vpc-prod       (manual apply, VCS: main branch, path: modules/vpc)
  |     |-- Workspace: platform-eks-dev        (run trigger: after vpc-dev)
  |     |-- Workspace: platform-eks-prod       (run trigger: after vpc-prod, Sentinel policies)
  |
  +-- Project: Applications
  |     |-- Workspace: app-frontend-dev
  |     |-- Workspace: app-frontend-prod
  |     |-- Workspace: app-backend-dev
  |     |-- Workspace: app-backend-prod
  |
  +-- Variable Sets:
  |     |-- AWS Credentials (applied to all workspaces, env vars: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
  |     |-- Common Tags (applied to all, TF vars: project, owner, cost_center)
  |     |-- Production Overrides (applied to *-prod, TF vars: instance sizes, replica counts)
  |
  +-- Policy Sets (Sentinel):
        |-- cost-control: deny if monthly_cost_delta > $500
        |-- security-baseline: deny if aws_s3_bucket without encryption
        |-- tagging-enforcement: deny if required tags missing
```

### CI/CD Pipeline (GitHub Actions)

```
Workflow: terraform.yml
  |
  +-- On: pull_request (paths: terraform/**)
  |     |-- Job: validate
  |     |     terraform fmt -check
  |     |     terraform init -backend=false
  |     |     terraform validate
  |     |     tflint --recursive
  |     |     checkov -d . --framework terraform
  |     |
  |     |-- Job: plan
  |           terraform init (with backend)
  |           terraform plan -out=tfplan
  |           Post plan summary as PR comment (tfcmt or custom script)
  |
  +-- On: push to main (paths: terraform/**)
        |-- Job: apply
              terraform init
              terraform apply tfplan
              (tfplan artifact from approved PR)
              Post apply summary to Slack
```
