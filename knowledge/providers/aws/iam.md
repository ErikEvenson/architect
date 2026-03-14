# AWS IAM

## Checklist

- [ ] Are IAM roles used instead of long-lived IAM user access keys for all service and application access?
- [ ] Is the principle of least privilege enforced with scoped-down policies rather than AWS managed policies like AdministratorAccess?
- [ ] Are permission boundaries attached to roles created by delegated admins to cap maximum privileges?
- [ ] Is cross-account access implemented via IAM role assumption (sts:AssumeRole) with external ID conditions rather than sharing credentials?
- [ ] Are service-linked roles used where AWS services support them (e.g., ECS, RDS, Auto Scaling)?
- [ ] Is IRSA (IAM Roles for Service Accounts) or EKS Pod Identity configured for Kubernetes workloads instead of node-level instance profiles?
- [ ] Are IAM policies using condition keys to restrict by source IP, VPC endpoint, MFA status, or organization ID where appropriate?
- [ ] Is AWS Organizations SCP (Service Control Policies) in place to set guardrails across all accounts?
- [ ] Are unused roles and policies identified and removed regularly using IAM Access Analyzer and credential reports?
- [ ] Is IAM Access Analyzer enabled to detect resources shared with external accounts or the public?
- [ ] Are inline policies avoided in favor of managed (customer) policies for reusability and auditability?
- [ ] Is MFA enforced for all human IAM users and root account access, with hardware MFA for root?
- [ ] Are session duration limits set appropriately for assumed roles (1 hour default, extended only when justified)?
- [ ] Is a tagging strategy applied to IAM roles for cost allocation and ownership tracking?

## Why This Matters

IAM is the single most critical security control in AWS. Overly permissive policies are the root cause of most cloud breaches. Long-lived access keys get leaked in code repositories. Missing permission boundaries allow privilege escalation. Without SCPs, a single compromised account can affect the entire organization.

## Common Decisions (ADR Triggers)

- **Identity provider integration** -- AWS SSO (Identity Center) vs federated SAML/OIDC vs IAM users
- **Cross-account access model** -- role chaining vs direct assumption, hub-spoke vs mesh trust
- **Permission boundary strategy** -- per-team boundaries vs per-environment, maximum permission scope
- **SCP governance model** -- deny-list (block specific actions) vs allow-list (permit only approved services)
- **EKS IAM integration** -- IRSA vs Pod Identity vs node-level instance profiles
- **Automation credentials** -- OIDC federation for CI/CD (GitHub Actions, GitLab) vs long-lived keys in secrets manager
- **Policy management** -- Terraform-managed policies vs AWS-managed policies vs custom policy-as-code
