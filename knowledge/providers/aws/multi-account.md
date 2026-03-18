# AWS Multi-Account Strategy

## Checklist

- [ ] **[Critical]** Create a dedicated management account that handles billing and Organizations only — never deploy workloads here, as compromising this account compromises every account in the organization
- [ ] **[Critical]** Define an OU hierarchy that reflects your governance boundaries: at minimum Security OU, Infrastructure OU, Workloads OU (with child OUs for prod/non-prod), and Sandbox OU
- [ ] **[Critical]** Implement SCPs at each OU level to enforce invariants — deny regions outside your approved set, deny disabling CloudTrail/GuardDuty/Config, deny leaving the organization, and deny root user API calls in all accounts except management
- [ ] **[Critical]** Establish a dedicated logging account in the Security OU with immutable S3 buckets (Object Lock) receiving organization CloudTrail, Config snapshots, and VPC Flow Logs — no one except the security team should have write or delete access
- [ ] **[Critical]** Create a security/audit account as the delegated administrator for GuardDuty, Security Hub, and AWS Config, aggregating findings across all accounts into a single pane of glass
- [ ] **[Critical]** Set up cross-account access exclusively through IAM role assumption (sts:AssumeRole) or IAM Identity Center permission sets — never share long-lived credentials or access keys between accounts
- [ ] **[Recommended]** Deploy AWS Control Tower Landing Zone to automate account provisioning, apply baseline guardrails (preventive SCPs and detective Config rules), and enforce consistent account configuration
- [ ] **[Recommended]** Centralize shared networking in an Infrastructure/Network account: Transit Gateway (shared via RAM), Direct Connect termination, DNS resolution (Route 53 Private Hosted Zones), and egress inspection via Network Firewall
- [ ] **[Recommended]** Use Account Factory for Terraform (AFT) or Customizations for Control Tower (CfCT) to codify account baselines — each new account should automatically receive VPC configuration, IAM roles, logging agents, and security tooling
- [ ] **[Recommended]** Implement mandatory cost allocation tags (Environment, Team, Application, CostCenter) enforced by SCP or tag policies, with per-account budgets and anomaly detection alerts
- [ ] **[Recommended]** Configure IAM Identity Center (successor to AWS SSO) with your identity provider (Okta, Entra ID, etc.) to provide centralized, federated access with permission sets scoped per account and OU
- [ ] **[Recommended]** Set up OIDC federation for CI/CD pipelines (GitHub Actions, GitLab CI) so they assume short-lived roles in target accounts rather than storing static credentials in pipeline secrets
- [ ] **[Optional]** Create sandbox accounts with automated resource cleanup (aws-nuke or custom Lambda) on a schedule, allowing developers to experiment without accumulating cost or risk
- [ ] **[Optional]** Implement a shared services account for ECR repositories, CI/CD tooling (CodePipeline/CodeBuild), and internal package registries, with cross-account resource policies granting pull access to workload accounts

## Why This Matters

A single AWS account is a single blast radius. One misconfigured IAM policy, one compromised access key, and an attacker has lateral access to production databases, billing configuration, audit logs, and every other resource you own. There is no meaningful boundary to contain the damage.

AWS multi-account architecture creates hard isolation boundaries. Each account has its own IAM principal namespace, its own service quotas, its own billing dimension, and its own blast radius. A compromised staging account cannot reach production resources because they exist in a separate account with no trust relationship. A runaway development workload cannot exhaust production service quotas because quotas are per-account. A cost anomaly in one team's account is visible and containable without affecting other teams.

Organizations operating at any non-trivial scale — more than one team, more than one environment, or any compliance requirement — need a multi-account strategy. AWS Organizations, Control Tower, and IAM Identity Center make this operationally tractable. The cost of setting this up correctly on day one is a fraction of the cost of untangling a single-account deployment later, which typically involves migrating every resource, recreating every IAM relationship, and re-establishing every network path.

The management account deserves special attention. It is the root of the organization and can create or delete any account, apply or remove any SCP, and access consolidated billing. If an attacker compromises the management account, they own the entire organization. This is why the management account must run zero workloads, have the fewest possible IAM users (ideally none, with access via Identity Center federation), and have MFA enforced on the root credentials with the root credentials physically secured.

## Common Decisions (ADR Triggers)

### OU structure: flat vs. nested

A flat OU structure (Security, Infrastructure, Workloads, Sandbox at the top level) is simpler and sufficient for organizations with fewer than 50 accounts. Nested OUs (Workloads > Prod, Workloads > Non-Prod, Workloads > Data) allow more granular SCP application but add governance complexity. Record the chosen structure and the rationale — changing OU hierarchy later requires moving accounts and re-validating SCP inheritance.

### Account-per-environment vs. account-per-application

Account-per-environment (one dev account, one staging account, one prod account shared by all applications) is simpler and works for small organizations. Account-per-application (each application gets its own dev, staging, and prod accounts) provides stronger blast radius isolation and clearer cost attribution, but multiplies the number of accounts rapidly. Most organizations start with account-per-environment and move to account-per-application as they grow. The choice affects networking design, CI/CD pipeline structure, and IAM role architecture.

### Transit Gateway vs. VPC peering

Transit Gateway provides hub-and-spoke connectivity with centralized route management, inspection points, and scales to thousands of VPCs. It costs $0.05/GB for inter-VPC traffic plus hourly attachment fees. VPC peering is free for same-region traffic and has no bandwidth limits, but is point-to-point (does not support transitive routing) and becomes unmanageable beyond 10-15 VPCs. For most multi-account architectures, Transit Gateway is the correct choice despite the cost premium.

### Control Tower vs. custom Organizations setup

Control Tower provides opinionated defaults: a Landing Zone with logging and audit accounts, managed guardrails, and Account Factory. It reduces initial setup time significantly but constrains some design choices (e.g., Control Tower manages certain SCPs and Config rules, and modifying them outside Control Tower can cause drift). Organizations with unique compliance requirements or existing automation may prefer to build on raw Organizations with custom SCPs and Config rules, accepting the higher initial effort for greater flexibility.

### Identity Center vs. per-account IAM federation

IAM Identity Center provides centralized access management with permission sets that deploy IAM roles to target accounts automatically. Per-account IAM federation (configuring SAML or OIDC identity providers in each account individually) offers more control but requires managing federation configuration across every account. Identity Center is the strong default for organizations using AWS Organizations.

### Centralized egress vs. distributed egress

Centralized egress routes all outbound internet traffic through a shared egress VPC with NAT Gateways and optionally Network Firewall for inspection. This reduces NAT Gateway costs (one set instead of one per VPC), enables centralized logging and filtering of outbound traffic, but introduces a single point of failure and a bandwidth bottleneck. Distributed egress (NAT Gateways in each VPC) is simpler and more resilient but costs more and makes outbound traffic inspection harder.

## Reference Architectures

### Recommended OU and Account Structure

```
Organization Root
|
+-- Management Account (billing, Organizations API — NO workloads)
|
+-- Security OU
|   +-- Log Archive Account
|   |   - Organization CloudTrail (S3 with Object Lock, 365-day retention)
|   |   - AWS Config delivery channel (org-wide)
|   |   - VPC Flow Logs from all accounts (central S3 bucket)
|   |   - Access restricted to security team (read-only)
|   |
|   +-- Security Tooling Account (Delegated Administrator)
|       - GuardDuty administrator (all member accounts enrolled)
|       - Security Hub administrator (aggregating all regions/accounts)
|       - AWS Config aggregator
|       - Detective, Inspector, Macie as needed
|       - Security team investigation workspace
|
+-- Infrastructure OU
|   +-- Network Account
|   |   - Transit Gateway (shared via AWS RAM to workload accounts)
|   |   - Direct Connect gateway and VIFs
|   |   - Route 53 Private Hosted Zones (shared via RAM)
|   |   - Network Firewall for centralized egress/inspection
|   |   - VPN termination
|   |
|   +-- Shared Services Account
|       - ECR repositories (cross-account pull via resource policy)
|       - CI/CD pipelines (CodePipeline, CodeBuild, or Jenkins)
|       - Internal DNS (Route 53 Resolver rules)
|       - Artifact repositories (CodeArtifact, S3)
|       - Shared AMI management
|
+-- Workloads OU
|   +-- Prod OU
|   |   +-- App-A Prod Account
|   |   +-- App-B Prod Account
|   |   +-- Data Platform Prod Account
|   |
|   +-- Non-Prod OU
|       +-- App-A Staging Account
|       +-- App-A Dev Account
|       +-- App-B Staging Account
|       +-- App-B Dev Account
|       +-- Data Platform Dev Account
|
+-- Sandbox OU
    +-- Developer Sandbox Account (auto-nuke weekly)
    +-- Experiment Account (auto-nuke monthly)
```

### SCP Examples

#### Deny Regions Outside Approved Set

Applied at the Organization Root (except excluded accounts for global services):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnapprovedRegions",
      "Effect": "Deny",
      "NotAction": [
        "budgets:*",
        "ce:*",
        "chime:*",
        "cloudfront:*",
        "cur:*",
        "globalaccelerator:*",
        "health:*",
        "iam:*",
        "kms:*",
        "organizations:*",
        "pricing:*",
        "route53:*",
        "route53domains:*",
        "route53-recovery-readiness:*",
        "route53-recovery-cluster:*",
        "route53-recovery-control-config:*",
        "s3:GetBucketLocation",
        "s3:ListAllMyBuckets",
        "shield:*",
        "sts:*",
        "support:*",
        "trustedadvisor:*",
        "waf-regional:*",
        "waf:*",
        "wafv2:*",
        "wellarchitected:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "us-east-1",
            "us-west-2",
            "eu-west-1"
          ]
        }
      }
    }
  ]
}
```

#### Deny Disabling Security Services

Applied at the Security OU and Workloads OU:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyDisablingCloudTrail",
      "Effect": "Deny",
      "Action": [
        "cloudtrail:StopLogging",
        "cloudtrail:DeleteTrail",
        "cloudtrail:UpdateTrail"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyDisablingGuardDuty",
      "Effect": "Deny",
      "Action": [
        "guardduty:DeleteDetector",
        "guardduty:DisassociateFromAdministratorAccount",
        "guardduty:UpdateDetector"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyDisablingConfig",
      "Effect": "Deny",
      "Action": [
        "config:StopConfigurationRecorder",
        "config:DeleteConfigurationRecorder",
        "config:DeleteDeliveryChannel"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyDisablingSecurityHub",
      "Effect": "Deny",
      "Action": [
        "securityhub:DisableSecurityHub",
        "securityhub:DeleteMembers",
        "securityhub:DisassociateMembers"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Deny Root User API Calls

Applied at all OUs except management account:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyRootUserActions",
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringLike": {
          "aws:PrincipalArn": "arn:aws:iam::*:root"
        }
      }
    }
  ]
}
```

#### Deny Leaving the Organization and Deny Public S3

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyLeavingOrg",
      "Effect": "Deny",
      "Action": "organizations:LeaveOrganization",
      "Resource": "*"
    },
    {
      "Sid": "DenyPublicS3",
      "Effect": "Deny",
      "Action": [
        "s3:PutBucketPublicAccessBlock",
        "s3:PutAccountPublicAccessBlock"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "s3:PublicAccessBlockConfiguration/BlockPublicAcls": "true",
          "s3:PublicAccessBlockConfiguration/BlockPublicPolicy": "true",
          "s3:PublicAccessBlockConfiguration/IgnorePublicAcls": "true",
          "s3:PublicAccessBlockConfiguration/RestrictPublicBuckets": "true"
        }
      }
    }
  ]
}
```

### Cross-Account Role Assumption Pattern

Workload accounts trust the CI/CD role in the shared services account:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111111111111:role/cicd-deployment-role"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "deploy-app-a-prod"
        }
      }
    }
  ]
}
```

GitHub Actions OIDC federation (no stored credentials):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::222222222222:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

### Centralized Logging Architecture

```
All Accounts                          Log Archive Account
+------------------+                  +-----------------------------+
| CloudTrail       | ---org trail---> | S3: org-cloudtrail-logs     |
| (auto-enabled)   |                  |   Object Lock (Governance)  |
+------------------+                  |   Lifecycle: IA @ 90d,      |
                                      |   Glacier @ 365d            |
+------------------+                  +-----------------------------+
| AWS Config       | ---delivery----> | S3: org-config-snapshots    |
| (org-wide)       |   channel        |   Versioning enabled        |
+------------------+                  +-----------------------------+

+------------------+                  +-----------------------------+
| VPC Flow Logs    | ---central--->   | S3: org-vpc-flow-logs       |
| (all VPCs)       |   destination    |   Partitioned by account/   |
+------------------+                  |   region/date for Athena    |
                                      +-----------------------------+

                                      Security Tooling Account
+------------------+                  +-----------------------------+
| GuardDuty        | ---member------> | GuardDuty Administrator     |
| (per account)    |   association    |   Aggregated findings       |
+------------------+                  +-----------------------------+

+------------------+                  +-----------------------------+
| Security Hub     | ---member------> | Security Hub Administrator  |
| (per account)    |   association    |   Cross-account dashboard   |
+------------------+                  +-----------------------------+

+------------------+                  +-----------------------------+
| AWS Config       | ---aggregator--> | Config Aggregator           |
| (per account)    |                  |   Org-wide compliance view  |
+------------------+                  +-----------------------------+
```

### Transit Gateway Hub-and-Spoke Networking

```
                        Network Account
                    +---------------------+
                    |   Transit Gateway   |
                    |   (shared via RAM)  |
                    +-----+-----+--------+
                          |     |     |
           +--------------+     |     +---------------+
           |                    |                     |
    +------+-------+    +------+-------+    +--------+-----+
    | Egress VPC   |    | Shared Svc   |    | Inspection   |
    | NAT GW x2   |    | VPC          |    | VPC          |
    | (AZ-a, AZ-b)|    | DNS, ECR     |    | Network FW   |
    +--------------+    +--------------+    +--------------+

    TGW Route Tables:
    - Workload RT: 0.0.0.0/0 -> Inspection VPC -> Egress VPC
    - Shared Services RT: 10.0.0.0/8 -> respective VPC attachments
    - Egress RT: 10.0.0.0/8 -> Inspection VPC

           |                    |                     |
    +------+-------+    +------+-------+    +--------+-----+
    | App-A Prod   |    | App-B Prod   |    | Data Prod    |
    | VPC          |    | VPC          |    | VPC          |
    | 10.1.0.0/16  |    | 10.2.0.0/16  |    | 10.3.0.0/16  |
    +--------------+    +--------------+    +--------------+

    CIDR Allocation Strategy:
    - 10.0.0.0/16  — Shared Services
    - 10.1.0.0/16  — App-A Prod
    - 10.2.0.0/16  — App-B Prod
    - 10.3.0.0/16  — Data Platform Prod
    - 10.128.0.0/16 — App-A Dev
    - 10.129.0.0/16 — App-B Dev
    - 172.16.0.0/12 — Reserved for future / on-prem
```

### Consolidated Billing and Cost Governance

```
Management Account
+--------------------------------------------------+
| AWS Organizations — Consolidated Billing          |
|                                                   |
| Mandatory Cost Allocation Tags (Tag Policies):    |
|   - Environment: [dev, staging, prod, sandbox]    |
|   - Team: [platform, data, frontend, backend]     |
|   - Application: [app-a, app-b, data-platform]    |
|   - CostCenter: [CC-1001, CC-1002, CC-2001]       |
|                                                   |
| Per-Account Budgets:                              |
|   - Sandbox accounts: $500/month hard limit       |
|   - Dev accounts: $2,000/month alert at 80%       |
|   - Prod accounts: anomaly detection (10% spike)  |
|                                                   |
| Cost Anomaly Detection:                           |
|   - Monitor: per-account and per-service          |
|   - Alert: SNS -> Slack/PagerDuty                 |
|   - Threshold: 10% above expected spend           |
+--------------------------------------------------+
```

### Common Mistakes

**Running workloads in the management account.** The management account has implicit permissions over all member accounts. If it is compromised through a vulnerable workload, the attacker gains control of the entire organization. The management account should contain only Organizations configuration and billing resources.

**No SCPs applied anywhere.** Without SCPs, any IAM principal with sufficient permissions in any account can disable CloudTrail, open S3 buckets to the public, launch resources in any region, or leave the organization entirely. SCPs are the only mechanism that can restrict even administrator-level principals within member accounts.

**Operating everything in a single account.** A single account means a single blast radius, shared service quotas, entangled IAM permissions, and no meaningful cost attribution. Migrating out of a single account is one of the most painful AWS operations — it requires moving resources, re-establishing network paths, and re-creating IAM trust relationships.

**Sharing credentials instead of using role assumption.** Embedding access keys from Account A into Account B's applications creates long-lived, unauditable, and unrotatable cross-account access. Role assumption with sts:AssumeRole provides short-lived credentials, CloudTrail-logged access, and condition-based restrictions (external ID, source IP, MFA).

**No centralized logging.** Without an organization CloudTrail in a dedicated logging account, individual accounts can delete their own trails, Security cannot investigate cross-account incidents, and there is no immutable audit record. Centralized logging with Object Lock is a compliance requirement for most frameworks (SOC 2, PCI-DSS, HIPAA).

**Overlapping CIDR ranges.** When each account's VPC is created independently, CIDR ranges inevitably overlap, making Transit Gateway peering or VPN routing impossible without re-IPing workloads. Allocate CIDR ranges centrally from the network account using IPAM before creating any VPC.

**Not using permission boundaries.** Without permission boundaries, a developer with IAM permissions in a sandbox account can create an administrator role and escalate privileges. Permission boundaries cap the maximum permissions that any role in the account can have, regardless of the policies attached to it.
