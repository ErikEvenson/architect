# Read-Only AWS Account Audit Methodology

## Scope

A reusable methodology for performing a read-only audit of an AWS account: comprehensive introspection capture, offline per-area review, and a consolidated finding deliverable. Covers the introspection script pattern (read-only credentials capturing ~100 services into a single bundle), the per-area slice format (frozen checklist → extract → match → write), the limits of what read-only auditing can surface, common bundle hygiene gotchas (notably the BGP MD5 cleartext exposure in `directconnect describe-virtual-interfaces`), the diagnostic patterns for old shared-services / multi-tenant accounts, and guidance on what additional captures are needed when the read-only baseline is insufficient.

## Why a methodology page

Read-only audit work is a recurring pattern: a customer grants read-only credentials, the reviewer captures everything they can, then walks the account offline against a checklist. The materials for doing this well (the script, the slice format, the per-area knowledge files) tend to live in engagement-specific notes and one-off tool repositories, not as a reusable pattern. Putting the methodology in the knowledge base does three things:

1. Makes the script and the review pattern reusable across engagements
2. Gives reviewers a concrete starting point ("here is the playbook, here is the script, here is the per-area slice format")
3. Provides a place to document the limits — what read-only auditing can and cannot surface, and what additional captures are needed for follow-up

## The overall pattern

```
read-only credentials  ->  introspection bundle  ->  offline per-area review  ->  consolidated deliverable
```

Each arrow has its own discipline:

- **Read-only credentials → bundle.** A single script run by a reviewer (or by the customer, with the reviewer watching) that calls every relevant `Describe*` / `Get*` / `List*` API across every region the account uses, packs the JSON output into a tarball, and hands it back. This is the "expensive" step in clock time (typically 15–60 minutes) but the only way to get a snapshot. Design choices that matter: which services are captured, which regions, how output is structured, and what to strip from the captures before they leave the account.
- **Bundle → offline per-area review.** The reviewer takes the bundle and walks it against a checklist for each area of interest (networking, IAM, KMS, S3, security groups, CloudTrail, Config, GuardDuty, Security Hub, etc.). The checklist comes from the relevant knowledge base file (`providers/aws/*.md`); the bundle provides the facts; the output is a per-area finding list. This is offline work and can happen days or weeks after the capture without any further customer involvement.
- **Per-area lists → consolidated deliverable.** The per-area finding lists are merged into a single document with a severity-scored summary, an executive overview, and per-area detail sections. This is the customer-facing deliverable.

## The introspection script

The script is the load-bearing artifact of the methodology. It needs four properties:

1. **Comprehensive.** Every service that matters for security or operations (typically 80–120 AWS services depending on which APIs are read). Missing services create blind spots that the reviewer will not know about until the offline phase, which is too late.
2. **Read-only.** Every API called must be a `Describe*`, `Get*`, or `List*`. No mutations. The script should run successfully with a credential that has only read permissions (e.g., the AWS managed `ReadOnlyAccess` policy or the more restrictive `ViewOnlyAccess`). If the script needs higher privilege, that is a script bug.
3. **Multi-region by default.** Most accounts use 2–4 regions. The script must enumerate enabled regions and run the per-region calls in each. Account-level / global services (IAM, Organizations, Route 53, CloudFront, S3 bucket list) run once.
4. **Defensive about secrets.** Some Describe APIs return secrets in their response payload. The script must strip these before writing to the bundle. The most notable trap is `aws directconnect describe-virtual-interfaces`, which returns `bgpAuthKey` (the BGP MD5 key) in cleartext. A script that captures this without stripping it leaks credentials in the bundle and on every storage hop the bundle passes through. There may be others — review the response shape of every captured API for any field with `Key`, `Secret`, `Token`, `Password`, or similar in the name and strip them explicitly.

### Captured surface area (typical)

The exact list varies by engagement, but a comprehensive bundle for a security/operations audit covers at least:

- **Identity & access:** IAM (users, groups, roles, policies, instance profiles, access keys, MFA devices, password policy), IAM Access Analyzer findings, Organizations structure, IAM Identity Center configuration, SCPs
- **Network:** VPCs, subnets, route tables, internet gateways, NAT gateways, VPC endpoints, endpoint policies, Transit Gateways, peering connections, prefix lists (with entries — see prefix list section in `providers/aws/security-groups.md`), VPN connections, Direct Connect, Network Firewall, Route 53 zones and records
- **Compute:** EC2 instances, AMIs, snapshots, EBS volumes, Auto Scaling groups, launch templates, key pairs, ECS clusters/services/tasks, EKS clusters, Lambda functions and configs
- **Storage:** S3 buckets and bucket policies, EFS file systems, FSx file systems, Storage Gateway
- **Database:** RDS instances and parameter groups, Aurora clusters, DynamoDB tables, ElastiCache clusters, Redshift clusters, Neptune, DocumentDB
- **Security:** Security groups (all rules), NACLs, KMS keys (and aliases, tags, rotation status, key policies), Secrets Manager secrets (metadata only, NOT values), ACM certificates, GuardDuty detectors, Security Hub configuration, Inspector configuration, Macie configuration, Config recorders and rules, CloudTrail trails, CloudWatch alarms
- **Operations:** Systems Manager (parameter store metadata, patch baselines, inventory), CloudWatch Logs groups, Backup plans and vaults, Resource Groups
- **Governance:** Service Quotas, Trusted Advisor checks, Cost Explorer (where API access exists), Tag Editor / Resource Groups Tagging API output, Health events

The actual list of API calls is captured in the script itself. A maintained version is the right place to track v1.x improvements; do not let the canonical list live only in someone's head.

## Bundle hygiene

Two failure modes recur and both are avoidable:

**1. Secrets in the bundle.** As noted above, `directconnect describe-virtual-interfaces` returns BGP MD5 keys in cleartext. This is the highest-impact one because it is non-obvious — the reviewer reads "Direct Connect" and thinks "network config" rather than "credential capture". Other Describe APIs that warrant a strip pass:

- `cloudformation describe-stacks` — `Parameters` array can include sensitive values that the stack accepted in cleartext
- `lambda get-function-configuration` — `Environment.Variables` can contain credentials
- `ecs describe-task-definition` — `containerDefinitions[].environment` can contain credentials
- `ec2 describe-launch-templates` — `LaunchTemplateData.UserData` is base64-encoded but contains arbitrary content
- `ssm describe-parameters` plus `get-parameters-by-path` — capture metadata but never `--with-decryption`

The right pattern: build a strip pass that runs over the bundle JSON before the tarball is created. Field names matching `(?i)(key|secret|token|password|credential|bgp.*auth)` get redacted to a fixed string. Better to over-strip than to leak.

**2. Bundle handling on the customer side.** A bundle can be 50–500 MB depending on account size. Customers will reasonably ask "how do I get this to you" and the answer must not be "email it" or "drop it in this Slack channel". The right answers are: encrypted upload to a known location, hand-off via a customer-controlled storage system, or in-person USB hand-off if the engagement warrants it. The bundle should also be encrypted at rest before it leaves the customer's machine — `gpg --symmetric` is the simplest approach.

## The per-area slice format

For each area of interest, the offline review follows the same shape:

1. **Frozen checklist** — load the relevant knowledge base file (`providers/aws/*.md`, `compliance/*.md`, etc.), and use its checklist as the frozen list of questions to answer for this area. Do not improvise the questions during the review — that is a recipe for missing things.
2. **Extract** — pull the relevant slice of the bundle for this area. For Security Groups, that is `describe-security-groups` output for every region. For KMS, it is `list-keys`, `describe-key`, `get-key-rotation-status`, `get-key-policy`, and `list-aliases` output. The extract step is mechanical and scriptable.
3. **Match** — for each checklist item, check the extracted slice against the question. The answer is one of: "compliant", "non-compliant", "not applicable", or "cannot determine from this bundle". The last category is important — it tracks the gaps in the read-only methodology and points at follow-up work.
4. **Write** — for each non-compliant item, write a finding with severity, the specific resources affected (with names, not just IDs), the recommended remediation, and a reference to the knowledge base item it violates. Use the SG/KMS naming-as-finding pattern: a finding that says "rotation disabled on `prod-customer-pii`" lands harder than "rotation disabled on a CMK in account 1234".

The slice format is symmetrical across areas, which means a reviewer can move from networking to KMS to S3 without re-learning the format. The knowledge base files are the input checklists; the bundle is the input data; the slice format is the consistent output shape.

## What read-only auditing cannot surface

The methodology is complete for configuration but incomplete for behavior. Things the read-only baseline does not capture:

- **VPC Flow Logs contents.** The bundle captures whether flow logs are enabled and where they go. It does not capture the actual log records. Investigating "is this NLB target actually receiving consumer traffic" requires reading the flow logs (often via CloudWatch Logs Insights — see `providers/aws/observability.md`), which is a separate query that needs runtime access.
- **CloudTrail contents.** Same shape: the bundle captures trail configuration but not the events themselves. Investigating "who did this and when" is a CloudTrail Lake or Athena query against the trail destination.
- **IAM credential reports.** `generate-credential-report` is async and returns the actual credential report on a second call. Most read-only scripts do not implement the wait loop. The credential report is the load-bearing data for "MFA enabled per user" and "password age per user" and is worth specifically capturing.
- **BGP routes received over Direct Connect.** Direct Connect virtual interfaces have a list of advertised routes and a list of received routes. The advertised list is in the bundle. The received list (what the customer is getting from the AWS edge) is not — it requires CloudWatch metrics or a runtime query against the BGP table.
- **Effective IAM permissions for a given principal.** IAM Access Analyzer's policy analysis can surface this for some cases, but the general "what can this role actually do, transitively, given all attached policies and group memberships and trust relationships" question requires either a tool like `iam-policy-resolver` or careful manual evaluation. The bundle has the raw policies; the synthesis is offline work.
- **Workload behavior under load.** Anything that requires running the workload (capacity, latency, error rates) is not in scope.
- **The actual contents of S3 buckets, databases, or message queues.** The bundle captures metadata (bucket policies, table schemas, queue policies). It does not capture data. Specific data inspection is a separate, much higher-trust authorization.

A good audit deliverable explicitly acknowledges these limits in the executive section, so the customer understands what was checked and what was not.

## Diagnostic patterns: old shared-services / multi-tenant accounts

A common shape in real engagements is "this account is doing more than it looks like it should be doing". Three diagnostic patterns are worth knowing:

### "Account is acting as a central transit hub"

Symptoms in the bundle:

- One or more Transit Gateways with a high attachment count (often 10+ VPC attachments, sometimes from multiple AWS accounts via RAM)
- A small number of TGW route tables (often just one) doing routing for many attachments — no environment segmentation
- Significant cross-account principals in IAM policies, often from accounts that no longer exist in the current Organization
- CloudTrail destinations referencing buckets in accounts the current org cannot resolve

What it means: the account was set up as a shared transit hub for an earlier multi-account architecture, possibly under a different Organization, possibly before Control Tower / IAM Identity Center existed. It accumulated cross-account references over time. Some of those references point to current production tenants. Some point to retired infrastructure that no one remembers.

What to look for:

- Are the TGW route tables actually segmented by environment (production / non-production / shared services / inspection)?
- Are there RAM shares with stale principals (accounts that no longer exist)?
- Are there CloudTrail trails pointing to buckets that the bundle cannot resolve (bucket exists in another account, account ownership unknown)?
- Are there KMS keys with key policies that reference principals the current org cannot resolve?

The output of this pattern is usually a "retired multi-account residue" finding cluster: orphaned references that should be cleaned up plus active references that should be re-justified.

### "Account has three eras of IAM federation"

Symptoms in the bundle:

- IAM users (era 1: pre-federation)
- SAML providers and SAML-federated roles (era 2: federation via ADFS or similar)
- IAM Identity Center configuration (era 3: AWS Identity Center / SSO)

All three coexist. The IAM users have access keys that were last used in different decades. The SAML roles have trust relationships to identity providers no one currently administers. The Identity Center configuration is the only one with current activity but the older eras have not been removed.

What to look for: which principals have credentials that have been used in the last 90 days, and which have not. The "not" set is the cleanup backlog. The "yes" set is the live access pattern; if any of the live principals are IAM users with access keys, that is its own finding.

### "Old CloudTrail destinations referencing accounts that do not exist"

Symptoms:

- CloudTrail trails with destination S3 buckets in accounts the current Organization does not contain
- Bucket policies in those destination buckets (where readable) that reference cross-account principals from accounts that no longer exist

This pattern indicates that the account was previously part of a multi-account log aggregation architecture that has since been retired. The trail itself is still emitting (CloudTrail charges accumulate, and the destination may still exist and accept the writes), but no one is reading the destination. The right outcome is usually: confirm the destination is or is not still in active use, then either point the trail at the current log archive account or stop the trail.

## Suggested scope of an audit deliverable

A typical read-only audit deliverable contains:

- **Executive summary** — top-N findings with severity, the methodology, the scope (which account, which regions, when captured), the explicit limits
- **Per-area sections** — one per checklist area (networking, IAM, KMS, S3, security groups, CloudTrail, Config, GuardDuty/Security Hub, KMS, Multi-account residue, etc.). Each section includes the slice extract summary, the findings, and the "could not determine from this bundle" gaps.
- **Findings index** — sortable list of every individual finding with severity, area, recommended remediation, and effort estimate
- **Appendix: bundle metadata** — script version used, regions enumerated, total API calls made, calls that failed (and why), service-by-service capture status

## Reference Links

- [AWS ReadOnlyAccess managed policy](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/ReadOnlyAccess.html) — the broadest read-only policy AWS publishes
- [AWS ViewOnlyAccess managed policy](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/ViewOnlyAccess.html) — narrower read-only policy that excludes some `Get*` calls
- [Generating IAM credential reports](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_getting-report.html) — the async credential report that needs special handling

## See Also

- `providers/aws/security-groups.md` — the SG checklist driven by the audit
- `providers/aws/kms.md` — the KMS checklist driven by the audit
- `providers/aws/networking.md` — networking checklist
- `providers/aws/iam.md` — IAM checklist
- `providers/aws/multi-account.md` — multi-account architecture for comparison against multi-tenant audit findings
- `providers/aws/observability.md` — CloudWatch Logs Insights query patterns for the runtime/behavior questions the bundle cannot answer
- `patterns/aws-data-perimeter.md` — the data perimeter pattern, frequently surfaced during the endpoint policy review slice
- `general/governance.md` — broader governance context for the deliverable
