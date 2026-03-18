# AWS IAM

## Scope

AWS identity and access management. Covers IAM roles, least-privilege policies, permission boundaries, SCPs, cross-account access, IRSA/Pod Identity for EKS, IAM Access Analyzer, MFA enforcement, and CI/CD OIDC federation.

## Checklist

- [ ] **[Critical]** Are IAM roles used instead of long-lived IAM user access keys for all service and application access?
- [ ] **[Critical]** Is the principle of least privilege enforced with scoped-down policies rather than AWS managed policies like AdministratorAccess?
- [ ] **[Recommended]** Are permission boundaries attached to roles created by delegated admins to cap maximum privileges?
- [ ] **[Critical]** Is cross-account access implemented via IAM role assumption (sts:AssumeRole) with external ID conditions rather than sharing credentials?
- [ ] **[Recommended]** Are service-linked roles used where AWS services support them (e.g., ECS, RDS, Auto Scaling)?
- [ ] **[Critical]** Is IRSA (IAM Roles for Service Accounts) or EKS Pod Identity configured for Kubernetes workloads instead of node-level instance profiles?
- [ ] **[Recommended]** Are IAM policies using condition keys to restrict by source IP, VPC endpoint, MFA status, or organization ID where appropriate?
- [ ] **[Critical]** Is AWS Organizations SCP (Service Control Policies) in place to set guardrails across all accounts?
- [ ] **[Recommended]** Are unused roles and policies identified and removed regularly using IAM Access Analyzer and credential reports?
- [ ] **[Recommended]** Is IAM Access Analyzer enabled to detect resources shared with external accounts or the public?
- [ ] **[Recommended]** Are inline policies avoided in favor of managed (customer) policies for reusability and auditability?
- [ ] **[Critical]** Is MFA enforced for all human IAM users and root account access, with hardware MFA for root?
- [ ] **[Recommended]** Are session duration limits set appropriately for assumed roles (1 hour default, extended only when justified)?
- [ ] **[Optional]** Is a tagging strategy applied to IAM roles for cost allocation and ownership tracking?

## Why This Matters

IAM is the single most critical security control in AWS. Overly permissive policies are the root cause of most cloud breaches. Long-lived access keys get leaked in code repositories. Missing permission boundaries allow privilege escalation. Without SCPs, a single compromised account can affect the entire organization.

## Common Decisions (ADR Triggers)

- **Identity provider integration** -- IAM Identity Center (formerly AWS SSO) vs federated SAML/OIDC vs IAM users
- **Cross-account access model** -- role chaining vs direct assumption, hub-spoke vs mesh trust
- **Permission boundary strategy** -- per-team boundaries vs per-environment, maximum permission scope
- **SCP governance model** -- deny-list (block specific actions) vs allow-list (permit only approved services)
- **EKS IAM integration** -- IRSA vs Pod Identity vs node-level instance profiles
- **Automation credentials** -- OIDC federation for CI/CD (GitHub Actions, GitLab) vs long-lived keys in secrets manager
- **Policy management** -- Terraform-managed policies vs AWS-managed policies vs custom policy-as-code

## Reference Architectures

- [AWS Well-Architected Framework: Security Pillar - Identity and Access Management](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/identity-and-access-management.html) -- IAM best practices within the Well-Architected Framework
- [AWS Architecture Center: Security, Identity, & Compliance](https://aws.amazon.com/architecture/security-identity-compliance/) -- reference architectures for multi-account IAM, federation, and access control
- [AWS Prescriptive Guidance: IAM best practices for multi-account environments](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/) -- AWS Security Reference Architecture (SRA) covering IAM at scale
- [AWS Well-Architected Labs: Identity and Access Management](https://www.wellarchitectedlabs.com/security/) -- hands-on labs for implementing least-privilege IAM policies and cross-account access
- [AWS IAM Identity Center (SSO) architecture](https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html) -- reference architecture for centralized identity management across AWS accounts

---

## See Also

- `general/identity.md` -- General identity and access management patterns
- `providers/aws/multi-account.md` -- SCPs, IAM Identity Center, and cross-account role assumption
- `providers/aws/secrets-manager.md` -- Credential storage and rotation for service accounts
- `providers/aws/containers.md` -- IRSA and Pod Identity for EKS workload authentication
