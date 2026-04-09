# AWS Security Groups

## Scope

AWS Security Groups (SGs) are stateful firewalls attached to elastic network interfaces (ENIs) that govern ingress and egress at the instance and endpoint level. Covers SG stacking semantics, source-based references vs. CIDR rules, customer-managed prefix list references, the default-SG anti-pattern, SG-per-role separation, NLB target group `preserve_client_ip` interaction with target SGs, audit characteristics of broad rules, hygiene tagging, and the relationship to VPC Flow Logs and Network ACLs. SGs are the most-touched layer in any AWS audit and the single largest source of "looks reasonable, is actually broken" findings.

## Checklist

- [ ] **[Critical]** The default VPC security group must not be in use by any resource. Customizing the default SG pollutes every newly created resource that does not specify an SG explicitly. The default SG should be left at "no rules" and every workload should reference an explicitly named SG.
- [ ] **[Critical]** Use source-SG references (referencing another SG by ID as the source of an ingress rule) instead of CIDR-based source rules wherever the source is also an AWS resource in the same VPC or peered VPC. CIDR sources are the single largest generator of audit findings ("0.0.0.0/0", "10.0.0.0/8", or any wide range pasted in as a workaround).
- [ ] **[Critical]** Apply one SG per role (target instance, VPC endpoint, application tier, database tier, jump host, monitoring agent), not shared SGs across host classes. Shared SGs make rule changes load-bearing across unrelated workloads and turn every audit into a dependency-graph traversal.
- [ ] **[Critical]** When multiple SGs are attached to the same ENI, the effective ingress permission is the **union** of all attached SGs, not the intersection. A "deny" SG does not exist — there is no way to subtract permissions by adding another SG. Every SG attached widens the allow-list. Audit any ENI with more than two attached SGs as a high-risk shape.
- [ ] **[Critical]** For NLB target groups configured with `preserve_client_ip: true`, the target SG must admit the actual consumer client source IPs, not the NLB or VPC CIDR. With `preserve_client_ip` on, the target instance sees the consumer ENI source IP, so the SG hygiene rules must be designed against the consumer set. SGs that "look correct" with VPC-CIDR ingress are silently broken on `preserve_client_ip` targets. (See `providers/aws/networking.md` NLB target group section.)
- [ ] **[Critical]** `-1:0-0` rules (any protocol, any port range) and `0.0.0.0/0:22` / `0.0.0.0/0:3389` / `0.0.0.0/0:any-database-port` rules must be justified or removed. There are legitimate cases (e.g., a public-facing CloudFront origin SG admitting the AWS-published CloudFront prefix list, or a production NLB on `0.0.0.0/0:443`), but every instance of these patterns should have a documented reason and an owner. Default to "find them all and require justification per rule."
- [ ] **[Recommended]** Where the same set of CIDRs is referenced from multiple SG rules, replace the CIDR list with a customer-managed prefix list and reference the prefix list from the SG rules. Single source of truth, atomic updates, fewer drift failures. Document who owns the prefix list and what its semantic meaning is — see prefix list section below for the audit gotcha.
- [ ] **[Recommended]** Tag every SG with at minimum: `Name` (descriptive, role-based), `Environment` (prod/non-prod/sandbox), `CostCenter` or `Owner`, and a `Purpose` or `Justification` field for any rule that allows broad CIDRs. Hygiene tags are how an audit can answer "who do I ask before I delete this" and "is this still in use".
- [ ] **[Recommended]** SG egress is `0.0.0.0/0:all` by default and is rarely tightened. For workloads in regulated environments or workloads that should never originate outbound calls (e.g., a database instance, an internal-only application server), restrict egress explicitly to the actual destinations. This is the pattern that catches data exfiltration via compromised workloads.
- [ ] **[Recommended]** Use SG references in egress rules the same way as ingress: an application tier's SG should egress to the database tier's SG (referenced by ID), not to the database subnet CIDR. This keeps the permission graph addressable in terms of roles, not addresses.
- [ ] **[Recommended]** Audit SG rule descriptions. Empty descriptions or stale descriptions ("temporary access for migration", "test rule, remove later") are findings. SG rules support per-rule descriptions; use them and require them via SCPs or AWS Config rules where possible.
- [ ] **[Recommended]** For VPC interface endpoints (PrivateLink consumer side), the endpoint's SG should be locked down to admit only the workloads that are supposed to use the endpoint, not the entire VPC CIDR. Endpoint SGs are often left at default-VPC-CIDR which makes the endpoint policy the only enforcement layer.
- [ ] **[Optional]** Use AWS Firewall Manager to apply baseline SG policies across an Organization (e.g., "no SG with `0.0.0.0/0:22`", "every SG must have a specific tag"). Firewall Manager is the right tool for org-wide enforcement; per-account Config rules work for smaller environments.
- [ ] **[Optional]** Where the workload requires defense-in-depth at the subnet level on top of SGs (regulatory requirement, broad emergency-block capability), pair SGs with NACLs. NACLs are stateless and per-subnet, and should be used as a coarse secondary layer, not a substitute for tight SGs. (See `providers/aws/networking.md` for the SG vs NACL split.)

## Why This Matters

Security Groups are the most-touched and most-misunderstood layer in any AWS account. They are the load-bearing primitive for every workload's network exposure, and the single largest source of "looks reasonable, is actually broken" findings in real audits. The reasons compound:

1. **Stacking semantics are additive, not subtractive.** New engineers often expect that adding an SG to an ENI can restrict it. It cannot. Every additional SG only widens the permission set. Multi-SG ENIs are the place where unintended exposure accumulates over time as different teams attach their own SGs without reviewing what the others do.
2. **CIDR-based rules drift.** A rule that was "the IP of the CI server" at creation becomes "an IP that nothing on the team owns anymore" within a year. CIDR sources have no symbol resolution — there is no "go to definition." Source-SG references make the permission graph navigable.
3. **Default SG pollution is invisible.** The default VPC SG attaches automatically to any resource that does not specify an SG. If anyone has ever added a rule to the default SG ("just for a quick test"), every new resource silently inherits it. The default SG should always be empty and never be explicitly used.
4. **`preserve_client_ip` is silently load-bearing.** NLB target group SGs with the wrong source assumption look correct on inspection but admit traffic from the wrong place (or block traffic from the right place). This is invisible without specifically checking the target group attribute.
5. **Customer-managed prefix lists hide their contents.** An SG rule that references a prefix list cannot be evaluated by reading the rule alone — the prefix list contents are a separate API call (`get-managed-prefix-list-entries`) that most introspection scripts and most reviewers do not make. A prefix list named "pen-test allowlist" can be silently repurposed to carry production traffic and the SG rule referencing it will never change.

The cost of cleaning up SG sprawl after the fact is much higher than the cost of getting the design right early. SG hygiene is not a polish layer — it is a foundational input to every other AWS security control (IAM policies, KMS key policies, VPC endpoint policies, data perimeter controls) because they all assume that the network layer correctly identifies who is talking to what.

## Common Decisions (ADR Triggers)

- **Source-SG references vs CIDR sources** — default to source-SG references for any AWS-internal source. CIDR sources are appropriate only for: external public IPs (with ownership documented), AWS-published service prefix lists (e.g., CloudFront, S3 gateway endpoints), and on-premises networks reaching in via Direct Connect or VPN. Every CIDR-source rule should answer: "what does this CIDR represent, who owns it, how do we know it has not changed."
- **Number of SGs attached per ENI** — favor one SG per role and one role per SG. Two SGs on the same ENI is acceptable when one is "baseline" (e.g., monitoring agent egress, SSM access) and the other is workload-specific. More than two SGs on the same ENI is a smell that warrants review.
- **Customer-managed prefix list as rule source** — use a prefix list when the same CIDR set is referenced from three or more rules, OR when the CIDR set is expected to change over time (CI runners, vendor IPs). Document the prefix list owner and add the prefix list to the introspection bundle for audits — see prefix list section below.
- **Egress rule strategy** — default-allow-all egress (`0.0.0.0/0`) is acceptable for internet-facing workloads that legitimately need to reach arbitrary destinations. For internal-only workloads, regulated workloads, and database tiers, restrict egress to specific SG references and AWS service prefix lists. The decision should be made per workload class, not per SG.
- **Firewall Manager vs Config rules vs manual review** — Firewall Manager when there is an Organization with five or more accounts and the policy is the same across accounts. Config rules for per-account enforcement of "no `0.0.0.0/0:22`" type rules. Manual review only for environments smaller than three accounts where the cadence of new SGs is low.
- **NLB target group `preserve_client_ip`** — turn it on when the target needs to log or authorize based on the actual client IP. When on, the target SG design changes completely (must admit consumer source IPs, not NLB or VPC CIDR). This decision belongs in an ADR because it is invisible from the SG rules alone.

## Customer-Managed VPC Prefix Lists

A customer-managed VPC prefix list is a named list of up to 1,000 CIDR entries that can be referenced from SG rules, route tables, or other prefix lists. Two flavors exist:

- **AWS-managed prefix lists** are maintained by AWS and represent service IP ranges (e.g., `com.amazonaws.us-east-1.s3`, `com.amazonaws.global.cloudfront.origin-facing`). They cannot be edited and are safe to reference.
- **Customer-managed prefix lists** are owned by an account, can be edited, and can be shared across accounts via AWS RAM.

**Why they matter for audits:** a referenced prefix list is a hidden surface for granted access. The SG rule that references it stays the same as the prefix list grows, shrinks, or gets repurposed. A reviewer who reads only the SG rule cannot tell what the rule actually permits — they need a separate `aws ec2 get-managed-prefix-list-entries --prefix-list-id pl-...` call. Most introspection scripts do not capture prefix list contents by default, and most reviewers do not know to ask. The result is that "this rule references a pen-test allowlist" can mean anything from "five CIDR entries representing a known pen-test platform" to "production traffic was added a year ago and never removed".

**Audit checklist for prefix lists:**

- Enumerate all customer-managed prefix lists: `describe-managed-prefix-lists --filters Name=owner-id,Values=<account>`
- For each, capture the entries: `get-managed-prefix-list-entries --prefix-list-id <id>`
- For each, list what references it: SGs (`describe-security-groups` and grep), route tables (`describe-route-tables` and grep), other prefix lists
- Compare the prefix list name to its actual contents. A name like "pen-test allowlist" should contain only pen-test infrastructure CIDRs. A mismatch is a finding.
- Check the modification history (CloudTrail `ModifyManagedPrefixList`) for the last year. Frequent changes by inconsistent principals are a flag.

**Hygiene rules:**

- Name prefix lists by what they contain, not what they were originally intended for. Rename when contents change.
- Tag prefix lists with `Owner` and `Justification`.
- Restrict who can call `ModifyManagedPrefixList` via SCPs or IAM policies — prefix list modifications are network policy changes and should be treated as such.

## Reference Architectures

### Three-tier application

- **Web tier SG** — ingress `:443` from `0.0.0.0/0` (or from the CloudFront prefix list if behind CloudFront only); egress to App tier SG on the application port; egress to AWS service prefix lists (S3, KMS, Secrets Manager) for assets and config; no other egress.
- **App tier SG** — ingress on application port from Web tier SG (by reference); egress to DB tier SG on the database port; egress to AWS service prefix lists for KMS, Secrets Manager, CloudWatch Logs; no other egress.
- **DB tier SG** — ingress on database port from App tier SG (by reference); egress nothing except AWS service prefix lists for KMS, monitoring, and backup.
- **Bastion / SSM SG** — no SSH ingress at all if Session Manager is in use; egress to SSM endpoints prefix list and to other workload SGs by reference.

### PrivateLink producer with `preserve_client_ip`

- **Target SG (the workload behind the NLB)** — ingress on the application port from the consumer source IPs (a customer-managed prefix list of consumer ENI CIDRs is the right pattern), NOT from the NLB and NOT from the VPC CIDR. The NLB itself does not have an SG; the target SG is where access control happens.
- **NLB target group attribute** — `preserve_client_ip = true`, documented as the load-bearing semantic for the SG design.
- **Endpoint service** — explicit allowed-principal list, manual acceptance for cross-account consumers, private DNS verification.
- See `providers/aws/networking.md` NLB target group section for the full pattern.

### VPC interface endpoint (PrivateLink consumer)

- **Endpoint SG** — ingress on `:443` from the workload SGs that are supposed to use the endpoint (by reference), NOT from the entire VPC CIDR. Default-VPC-CIDR ingress on an endpoint SG turns the endpoint policy into the only enforcement layer, which is the wrong layering.
- **Endpoint policy** — explicit `Principal` and `Resource` constraints, with a data-perimeter `Condition` block (`aws:PrincipalOrgID`, `aws:ResourceOrgID`). See `patterns/aws-data-perimeter.md`.

---

## Reference Links

- [Security Groups for your VPC](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html) — semantics, limits, and rule structure
- [Working with managed prefix lists](https://docs.aws.amazon.com/vpc/latest/userguide/working-with-managed-prefix-lists.html) — customer-managed and AWS-managed prefix lists
- [NLB target groups: client IP preservation](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-target-groups.html#client-ip-preservation) — `preserve_client_ip` semantics

## See Also

- `providers/aws/vpc.md` — VPC design, subnetting, NACLs, Flow Logs
- `providers/aws/networking.md` — Transit Gateway, PrivateLink, NLB target groups
- `providers/aws/security.md` — GuardDuty, Security Hub, Config Rules, Firewall Manager
- `providers/aws/iam.md` — identity-based controls that complement network controls
- `patterns/aws-data-perimeter.md` — data perimeter pattern using endpoint policies and SGs together
- `patterns/network-segmentation.md` — segmentation patterns at the architecture level
