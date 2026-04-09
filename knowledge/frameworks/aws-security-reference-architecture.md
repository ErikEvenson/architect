# AWS Security Reference Architecture

## Scope

The AWS Security Reference Architecture (SRA) is AWS's prescriptive multi-account architecture for security services, published as part of AWS Prescriptive Guidance. It defines the recommended account structure for AWS Organizations, the delegated administrator pattern for security services, the centralized log archive account, the security tooling account, and the workload account model. SRA is the standard reference for "what does good multi-account security architecture look like in AWS" and is cited from FedRAMP authorizations, customer security reviews, and AWS Well-Architected Framework reviews. Covers the OU structure, the seven recommended account types, the security service deployment patterns (delegated admin), the log aggregation pattern, the cross-account access model, and the relationship to AWS Control Tower / AWS Landing Zone Accelerator.

## The Recommended OU Structure

SRA recommends a layered Organizational Unit structure under the AWS Organizations management account:

```
Management (root org account)
└── Security (OU)
    ├── Security Tooling (account)
    └── Log Archive (account)
└── Infrastructure (OU)
    ├── Network (account)
    └── Shared Services (account)
└── Workloads (OU)
    ├── SDLC (OU)
    │   └── Development workload accounts
    │   └── Test workload accounts
    │   └── Production workload accounts
    └── Sandbox (OU)
        └── Sandbox accounts
└── Suspended (OU)
    └── Decommissioned accounts pending deletion
```

The structure is layered so that policies (SCPs) can be applied at the OU level and inherited by all child accounts. The Security and Infrastructure OUs are populated with platform accounts that are operated by central teams; the Workloads OU is populated with application accounts operated by workload teams.

## The Seven Recommended Account Types

### 1. Management Account

The AWS Organizations root account. It owns the organization, controls billing for all member accounts, and is the source of truth for organizational structure. **Critical**: nothing else runs in the management account. No workloads, no security tooling, no shared services. The management account is the riskiest account in the org and must have the smallest possible attack surface.

### 2. Log Archive Account

A dedicated account that holds the immutable, long-retention copies of all security and audit logs from the entire organization. It receives:

- **CloudTrail** logs from every account via the organization trail
- **AWS Config** snapshots and history from every account
- **VPC Flow Logs** from every workload VPC
- **Route 53 Resolver query logs** from every workload account
- **S3 access logs** for sensitive buckets
- **Application logs** for high-value applications

The Log Archive account has very few human users — typically only the security team has read access, and write access is restricted to the AWS service principals that deliver the logs. The S3 buckets that hold the logs use Object Lock and bucket policies that prevent deletion, ensuring log integrity even in the event of an account compromise.

### 3. Security Tooling Account

The delegated administrator account for AWS-native security services. It runs and aggregates findings from:

- **AWS Security Hub** — central findings aggregation across the organization
- **Amazon GuardDuty** — threat detection across the organization
- **Amazon Inspector** — vulnerability scanning across the organization
- **Amazon Macie** — sensitive data discovery across the organization
- **AWS Audit Manager** — compliance evidence collection
- **AWS Detective** — security investigation and incident response
- **IAM Access Analyzer** — identity access analysis

By delegating these services to a dedicated account, the security team has a single console for findings and can investigate without needing access to every workload account. The delegation also means that workload accounts cannot disable security services in their own account — the delegation is enforced at the org level.

### 4. Network Account

A dedicated account that owns the shared network infrastructure: Transit Gateway, Direct Connect Gateway, Network Firewall, Route 53 Private Hosted Zones, and the AWS Resource Access Manager (RAM) shares that distribute the network resources to workload accounts. Workload accounts attach to the shared TGW via RAM, which gives them connectivity to other workload accounts and to on-premises networks without giving them control of the network infrastructure itself.

The Network account enforces network policy at the central layer. Workload accounts can configure their own VPCs and security groups but cannot bypass the central inspection (Network Firewall) or modify the shared TGW route tables.

### 5. Shared Services Account

Holds infrastructure that is shared across workloads but is not strictly security or networking: Active Directory / Entra ID Connect, AMI factory, monitoring infrastructure, CI/CD shared resources, and other workload-adjacent platform services.

### 6. Workload Accounts

The accounts where actual workloads run. Each workload account holds the application infrastructure, application data, and workload-specific configuration. SRA recommends one account per (workload × environment) — a "production app A" account, a "development app A" account, a "production app B" account, and so on. The strict separation means that a compromise in one workload account does not directly affect any other workload.

### 7. Sandbox / Exploration Accounts

Accounts for engineers to experiment without affecting any other workload or any shared infrastructure. Sandbox accounts have aggressive cost controls (auto-stop, budget limits), no production data, and minimal connectivity to the rest of the organization. They are wiped on a regular schedule (e.g., monthly) to prevent the accumulation of forgotten resources.

## The Delegated Administrator Pattern

AWS supports delegating the administration of certain security services from the management account to a member account. The Security Tooling account is the standard delegate for:

- Security Hub
- GuardDuty
- Inspector
- Macie
- Audit Manager
- Detective
- IAM Access Analyzer
- Firewall Manager (also delegates to a separate account in some setups)
- Resource Access Manager (for org-wide RAM shares)

The delegation gives the Security Tooling account the ability to enable, configure, and view findings for the service across all member accounts, without giving it any other access to those accounts. Workload accounts cannot disable the service in their own account because the configuration is owned by the delegate.

To enable a delegated admin: from the management account, run `aws organizations register-delegated-administrator --account-id <security-tooling-account-id> --service-principal <service>.amazonaws.com`. The service must support delegation; most modern AWS security services do.

## Centralized Logging Pattern

Every account in the organization sends its logs to the Log Archive account via cross-account delivery:

- **CloudTrail organization trail** — created in the management account, delivers to a bucket in the Log Archive account, captures management events from every account in the organization in a single trail
- **CloudTrail data events** — configurable per service (S3 data events, Lambda data events, KMS data events) and delivered to the same bucket
- **AWS Config aggregator** — created in the Security Tooling account or Log Archive account, aggregates Config snapshots and history from every account
- **VPC Flow Logs** — delivered to a bucket in the Log Archive account, with the workload account as the source
- **GuardDuty findings** — published to the Security Hub aggregator in the Security Tooling account, which is the operational view; the underlying GuardDuty data is also archived
- **Application logs** — for high-value applications, log delivery to the Log Archive account is part of the workload's deployment configuration

The Log Archive account's S3 buckets use:

- **S3 Object Lock** in compliance mode for the highest-value logs (CloudTrail management events, Config snapshots)
- **MFA Delete** as a defense in depth
- **Bucket policies** that deny deletion for any principal except specific recovery roles
- **KMS encryption** with a customer-managed key in the same account
- **Cross-region replication** to a second region for disaster recovery

The Log Archive account is the single most important account in the organization to protect. Its data is the audit trail of everything that has ever happened.

## SCPs and Guardrails

Service Control Policies (SCPs) are applied at the OU level to enforce security boundaries that workload accounts cannot disable:

- **Deny disabling of CloudTrail, Config, GuardDuty** — workload accounts cannot turn off security services
- **Deny modification of log destination buckets** — workload accounts cannot point logs elsewhere
- **Deny creation of resources in non-approved regions** — restrict deployment to specific regions for data residency
- **Deny use of root account** — workload accounts cannot use the root account for routine operations
- **Deny cross-account role assumption from outside the org** — prevents cross-org access via STS
- **Require encryption for new resources** — deny creation of unencrypted EBS volumes, RDS instances, S3 buckets

SCPs are deny-only — they can prevent actions but cannot grant them. The combination of SCPs (deny) at the OU level and IAM policies (allow) at the account level produces the effective permission set.

## Relationship to AWS Control Tower

AWS Control Tower is AWS's managed multi-account setup service. It implements much of the SRA automatically, including:

- The OU structure (Security and Workloads OUs by default)
- The Log Archive and Security Tooling accounts (called "Audit" in Control Tower)
- A baseline set of guardrails (preventive SCPs and detective Config rules)
- Account vending via Account Factory
- Centralized identity via IAM Identity Center

Control Tower is the right starting point for organizations that are establishing their first AWS Organization and want a guided setup. Organizations with existing AWS Organizations can adopt Control Tower retroactively, though the migration requires careful planning.

The **AWS Landing Zone Accelerator (LZA)** is the alternative for organizations that need more customization than Control Tower provides — typically organizations subject to FedRAMP, DoD SRG, or other specialized compliance regimes. LZA is a CloudFormation-based deployment that implements the SRA with extensive configurability.

## Common Implementation Patterns

### Adopting SRA in an existing AWS environment

1. **Inventory current accounts** — what exists, what is in scope, what should be in each OU
2. **Establish the OU structure** — create the Security, Infrastructure, Workloads, and Suspended OUs in the management account
3. **Create the Log Archive and Security Tooling accounts** — new accounts in the Security OU
4. **Migrate existing logs to the Log Archive account** — set up CloudTrail organization trail, Config aggregator, S3 cross-account log delivery
5. **Delegate security services to the Security Tooling account** — Security Hub, GuardDuty, Inspector, Macie, Detective
6. **Move existing accounts into the Workloads OU** — categorize each account by environment and move it into the appropriate sub-OU
7. **Apply SCPs progressively** — start with the most permissive SCPs and tighten over time, validating that workload accounts continue to function

The adoption is incremental and is typically a multi-quarter project for a large organization.

### Reporting on SRA adoption

A common dashboard shows:

- **OU coverage** — percentage of accounts that are in the correct OU
- **Delegated admin coverage** — percentage of security services delegated to the Security Tooling account
- **Logging coverage** — percentage of accounts delivering logs to the Log Archive account
- **SCP coverage** — which guardrails are deployed and which accounts they apply to
- **Drift detection** — accounts that have moved away from the baseline configuration

## Common Decisions

- **Control Tower vs Landing Zone Accelerator vs custom** — Control Tower for organizations starting fresh and willing to accept its opinions. LZA for organizations subject to specialized compliance regimes. Custom for organizations with very specific requirements that neither tool meets.
- **Single Log Archive account vs per-region** — single account is the standard. Per-region is appropriate only when data residency requires it (specific compliance regimes that prohibit cross-region log delivery).
- **Audit account naming** — Control Tower uses "Audit" for the Security Tooling account; SRA uses "Security Tooling". They are the same account in practice. Pick one naming convention and stick with it.
- **Sandbox account model** — one shared sandbox vs per-engineer sandbox. Per-engineer is cleaner but harder to manage at scale; shared sandbox with strict cost controls and auto-cleanup is the practical compromise for most organizations.

## Reference Links

- [AWS Security Reference Architecture (SRA)](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/welcome.html)
- [AWS SRA examples (GitHub)](https://github.com/aws-samples/aws-security-reference-architecture-examples)
- [AWS Control Tower documentation](https://docs.aws.amazon.com/controltower/)
- [AWS Landing Zone Accelerator](https://aws.amazon.com/solutions/implementations/landing-zone-accelerator-on-aws/)
- [AWS Organizations Service Control Policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)

## See Also

- `providers/aws/multi-account.md` — multi-account strategy with detailed SCP examples
- `providers/aws/security.md` — AWS security services overview
- `providers/aws/iam.md` — IAM and the foundation for cross-account access
- `frameworks/aws-well-architected.md` — Well-Architected Security pillar references SRA
- `frameworks/nist-sp-800-53.md` — SP 800-53 controls that the SRA implementations satisfy
- `compliance/fedramp.md` — FedRAMP authorizations that use SRA as the reference architecture
- `general/aws-readonly-audit.md` — read-only audit methodology, frequently used to validate SRA adoption
