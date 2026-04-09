# GCP VPC Firewall Rules

## Scope

GCP has two firewall systems that overlap and can confuse anyone migrating from AWS or Azure: **VPC firewall rules** (the original, per-VPC rule set) and **hierarchical firewall policies** (the newer, organization/folder-level rule set that takes precedence over VPC rules). Covers both systems, the priority and evaluation order, the implied default rules, target tags vs target service accounts as the source/destination model, network tags, ingress vs egress semantics, **firewall logging** (enabling and querying), the audit characteristics of broad rules, the relationship to Cloud Armor (the L7 WAF) and Cloud NGFW (the new managed firewall service), and the diagnostic patterns for firewall rule sprawl. Does not cover Cloud Armor in depth (separate L7 service for HTTP/S protection).

## The Two Firewall Systems

### VPC Firewall Rules (the original)

VPC firewall rules are stateful firewalls applied at the VPC level. Each rule has:

- **Direction** — `INGRESS` or `EGRESS`
- **Action** — `ALLOW` or `DENY`
- **Priority** — 0 to 65535, lower number wins
- **Source / Destination** — IP ranges (CIDR), source tags (legacy), source service accounts, or VPC ranges
- **Protocol and ports** — `tcp:22`, `udp:53`, `icmp`, `all`
- **Targets** — which instances the rule applies to (target tags, target service accounts, or all instances in the VPC)

Each VPC has implied default rules that **cannot be deleted**:

- **Implied allow egress** — egress to any destination is allowed by default (priority 65535)
- **Implied deny ingress** — ingress from any source is denied by default (priority 65535)

The implied rules are at the lowest priority, so any explicit rule overrides them.

### Hierarchical Firewall Policies (the newer model)

Hierarchical firewall policies are firewall rule sets attached to the **organization** or **folder** level. They evaluate **before** VPC firewall rules and **take precedence** — a hierarchical policy that denies traffic cannot be overridden by a VPC firewall rule that allows it.

This is the GCP equivalent of Azure's AVNM security admin rules: org-level guardrails that cannot be overridden by individual workload firewall rules. Use hierarchical policies for:

- "No inbound RDP/SSH from the internet across the entire organization"
- "Always allow management traffic from the corporate IP ranges"
- "Block known malicious IP ranges from threat intelligence"

Hierarchical policies have their own priority space (separate from VPC rule priority) and their own action set (`ALLOW`, `DENY`, `GOTO_NEXT` — to delegate to the next layer).

### Evaluation Order

For ingress to an instance, the evaluation order is:

1. Hierarchical firewall policies (org level, then folder level, in order from top to bottom of the hierarchy)
2. VPC firewall rules (in priority order)
3. Implied deny ingress (catch-all if nothing matches)

For egress from an instance, the evaluation order is:

1. Hierarchical firewall policies
2. VPC firewall rules
3. Implied allow egress (catch-all)

The first matching rule wins. A `GOTO_NEXT` action in a hierarchical policy delegates evaluation to the next layer.

## Source Models: Tags vs Service Accounts vs CIDR

GCP firewall rules can use three different "source" models, each with different audit characteristics:

### Network Tags (legacy, but still common)

Network tags are arbitrary string labels attached to instances. A firewall rule with `sourceTags: ["web"]` applies to traffic from any instance with the `web` tag. A rule with `targetTags: ["db"]` applies to instances with the `db` tag.

**Audit problem**: tags are project-scoped strings with no enforcement. Any user with `compute.instances.setTags` permission can add or remove a tag from any instance, which immediately changes the firewall behavior. There is no audit log entry that says "user X changed the firewall by tagging instance Y" — only the tag change is logged.

### Source Service Accounts (the recommended model)

Service account-scoped rules use the instance's runtime service account as the identifier. A firewall rule with `sourceServiceAccounts: ["web-sa@<project>.iam.gserviceaccount.com"]` applies to traffic from instances running as that service account.

**Audit advantage**: changing the service account on a running instance requires `compute.instances.setServiceAccount`, which is logged and can be restricted via IAM. The service account is also a stronger identity binding than a string tag — it cannot be changed accidentally.

The right pattern in 2024+ is to use **target service accounts** for the destination and **source service accounts** for the source wherever possible. Target tags / source tags should be reserved for the cases where service accounts are not appropriate (e.g., legacy instances).

### CIDR ranges

For traffic from outside the VPC (the public internet, on-premises networks reached via Cloud VPN or Interconnect, or peered VPCs), CIDR ranges are the only option. CIDR sources have the same drift problem as in AWS: a rule that was "the office IP" five years ago is now an IP nobody owns.

Use CIDR sources only when no service-account-based identification is possible.

## Firewall Logging

VPC firewall rules can have **logging** enabled per rule, which writes a log entry to Cloud Logging for every connection that matches the rule. Logging is **disabled by default** and must be enabled explicitly per rule. Without it, the answer to "is this rule actually being matched" is "we don't know".

Enable logging on:

- All `DENY` rules — to see what is being blocked, both for security investigation and for finding legitimate traffic that is being blocked accidentally
- All `ALLOW` rules with broad sources — to verify that the broad allow is actually needed
- The implied deny — by creating an explicit catch-all `DENY` rule with logging enabled at priority 65000 (just above the implied deny)

Firewall logs go to Cloud Logging by default, where they can be queried with Logs Explorer. For long-term retention, use a log sink to export them to a Cloud Storage bucket or BigQuery dataset.

## Common Implementation Patterns

### Three-tier application with service-account-scoped firewall rules

Service accounts:
- `web-sa@<project>.iam` — web tier
- `app-sa@<project>.iam` — application tier
- `db-sa@<project>.iam` — database tier
- `mgmt-sa@<project>.iam` — management instances (jump hosts)

Firewall rules:
- **Allow ingress** `:443` from `0.0.0.0/0` to `targetServiceAccounts: [web-sa]` (or restrict source to the load balancer IP range if using Cloud Load Balancing)
- **Allow ingress** application port from `sourceServiceAccounts: [web-sa]` to `targetServiceAccounts: [app-sa]`
- **Allow ingress** database port from `sourceServiceAccounts: [app-sa]` to `targetServiceAccounts: [db-sa]`
- **Allow ingress** `:22` from `sourceServiceAccounts: [mgmt-sa]` to `targetServiceAccounts: [web-sa, app-sa, db-sa]` (or use IAP TCP forwarding instead)
- **Default deny all** at priority 65000 with logging enabled

### Hierarchical policy for org-wide guardrails

Hierarchical firewall policy at the organization level:

- **Priority 100**: Deny ingress `:22` and `:3389` from `0.0.0.0/0` to all instances (with `GOTO_NEXT` for traffic from approved source ranges)
- **Priority 200**: Deny ingress from known-malicious IP ranges (updated via threat intel feed)
- **Priority 300**: Allow ingress from corporate IP ranges to all instances on management ports
- **Catch-all**: `GOTO_NEXT` (delegates to the project-level VPC firewall rules)

This ensures the org-wide guardrails are enforced regardless of what individual project owners do with their VPC firewall rules.

### Identity-Aware Proxy (IAP) for SSH access

Instead of opening port 22 to specific IP ranges, use **IAP TCP forwarding**:

- IAP authenticates the user via Cloud Identity / Workspace SSO
- IAP forwards the SSH connection to the target instance via Google's edge network
- The instance only needs to allow ingress on `:22` from the IAP source range (`35.235.240.0/20`)
- Engineers connect via `gcloud compute ssh` which uses IAP automatically

This is the equivalent of AWS Session Manager and is the preferred pattern for SSH access in GCP.

## Common Decisions (ADR Triggers)

- **Tags vs service accounts** — service accounts for any new firewall rule. Tags only for legacy instances or when service accounts are not feasible.
- **VPC firewall rules vs hierarchical firewall policies** — VPC rules for workload-specific access. Hierarchical policies for org-wide guardrails that should not be overridable.
- **Logging on every rule vs logging on selected rules** — logging on all `DENY` rules (always). Logging on `ALLOW` rules with broad sources (always). Logging on narrow `ALLOW` rules (skip — too much volume).
- **IAP vs SSH source allowlist** — IAP for any production SSH access. Source allowlist only for legacy use cases.
- **Cloud NGFW vs traditional VPC firewall** — Cloud NGFW (the newer managed firewall service) for workloads that need L7 inspection, threat detection, or TLS inspection. Traditional VPC firewall for the L3/L4 stateful filtering most workloads need.

## Why This Matters

GCP firewall rules are the per-instance security boundary and the equivalent layer to AWS security groups and Azure NSGs. The same kind of misconfigurations recur:

1. **Tag-based rules drift** because tags can be changed without leaving an audit trail of what they affect.
2. **CIDR-based rules drift** because IP ranges become orphaned over time.
3. **Logging is off by default** so the team has no visibility into what the rules are actually doing.
4. **The default-allow-egress rule** is a finding for any environment that should not allow outbound to arbitrary destinations.
5. **Hierarchical policies are underused** because they are newer and require organization-level access to manage.

The combination of service-account-scoped rules, hierarchical policies for org-wide guardrails, and firewall logging on all denials gives a posture that is auditable, enforceable, and understandable. Without all three, the rules become a tangle that nobody can clean up.

## Reference Links

- [VPC firewall rules documentation](https://cloud.google.com/vpc/docs/firewalls)
- [Hierarchical firewall policies](https://cloud.google.com/vpc/docs/firewall-policies)
- [Firewall rules logging](https://cloud.google.com/vpc/docs/firewall-rules-logging)
- [Cloud NGFW](https://cloud.google.com/firewall/docs/about-firewalls)
- [Identity-Aware Proxy TCP forwarding](https://cloud.google.com/iap/docs/using-tcp-forwarding)

## See Also

- `providers/gcp/networking.md` — broader GCP networking
- `providers/gcp/security.md` — broader GCP security service set
- `providers/gcp/iam-organizations.md` — IAM and resource hierarchy
- `providers/aws/security-groups.md` — equivalent service in AWS
- `providers/azure/network-security-groups.md` — equivalent in Azure
