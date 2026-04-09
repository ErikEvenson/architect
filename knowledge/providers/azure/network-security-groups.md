# Azure Network Security Groups

## Scope

Azure Network Security Groups (NSGs) are stateful firewalls that can be attached to subnets and individual NICs. Covers NSG rule structure (priority, source / destination, port, protocol, action), application security groups (ASGs) as a referenceable abstraction over NIC sets, augmented security rules, service tags (Microsoft-maintained address ranges for Azure services), the per-NIC vs per-subnet attachment model and how the two interact, NSG Flow Logs (v1 vs v2), Traffic Analytics, the audit characteristics of broad rules, and the relationship to Azure Firewall and the newer Azure Virtual Network Manager (AVNM) security admin rules. NSGs are the most-touched layer in any Azure audit and the equivalent of the security group review for AWS.

## Checklist

- [ ] **[Critical]** Use **application security groups (ASGs)** as the source / destination of NSG rules wherever possible, instead of CIDR-based rules. ASGs are referenceable groups of NICs, and an ASG-referencing rule remains correct as NICs are added or removed. CIDR-based rules drift over time and become the primary source of "looks reasonable, is actually broken" findings.
- [ ] **[Critical]** Use **service tags** (e.g., `Storage`, `Sql`, `AzureKeyVault`, `AzureMonitor`) instead of hardcoded Microsoft IP ranges. Service tags are maintained by Microsoft and update automatically as Azure expands. Hardcoded Microsoft IP ranges go stale and either over-allow (permitting newer ranges that should not be open) or break the workload (failing to permit ranges Microsoft added).
- [ ] **[Critical]** Understand the per-NIC and per-subnet NSG interaction. Both NSGs are evaluated for ingress (subnet first, then NIC) and egress (NIC first, then subnet). A flow is permitted only if both NSGs allow it. The most common audit confusion is "the rule is in the NIC NSG, why is the traffic blocked" — and the answer is usually that the subnet NSG denies it. Document both layers when designing.
- [ ] **[Critical]** Avoid the "AllowVNetInBound" / "AllowAzureLoadBalancerInBound" / "DenyAllInBound" default rules being the only rules in the NSG. These exist by default and should be supplemented by explicit allow rules for the workload's actual traffic, not relied on as the entire policy. The default rules are the floor, not the design.
- [ ] **[Critical]** Lower-priority numbers win. A `Deny` at priority 100 beats an `Allow` at priority 200. The mental model "first match wins" is correct, but the order is by priority number ascending, not by file order or creation order. Audit any rule with priority < 200 carefully — those are the rules that override everything else.
- [ ] **[Critical]** `*` (any) rules — `Source = *`, `Destination = *`, or `DestinationPortRange = *` — must be justified. A rule with all three at `*` is effectively no policy at all. Inventory every NSG rule with any combination of `*` and require a documented owner and justification per rule.
- [ ] **[Critical]** `RDP` / `SSH` from any source (`Source = *` or `Source = Internet`) is the highest-frequency Azure security finding. Use Azure Bastion or Just-in-Time (JIT) VM access via Defender for Cloud instead of opening management ports to the internet directly.
- [ ] **[Recommended]** Enable **NSG Flow Logs v2** for every NSG that protects production workloads. Flow Logs v2 captures the same flow data as v1 plus the action (allowed / denied) and the rule that matched. Forward to a storage account for long-term retention and to **Traffic Analytics** for visualization and per-flow query. Flow logs without Traffic Analytics are technically compliant but operationally hard to use.
- [ ] **[Recommended]** Tag NSGs and NSG rules with `Owner`, `Environment`, `Purpose`, and `JustificationRef` for any rule that allows broader-than-default access. Tag-based access control via ABAC (preview) lets you scale per-NSG governance.
- [ ] **[Recommended]** Use **Azure Virtual Network Manager (AVNM)** security admin rules for organization-wide NSG rules that should always apply (e.g., "no inbound RDP from Internet across the entire org"). Security admin rules are evaluated *before* NSGs and cannot be overridden by an NSG, which makes them the right tool for tenant-wide guardrails.
- [ ] **[Recommended]** For workloads that require defense-in-depth at multiple layers, pair NSGs with **Azure Firewall** (or a third-party NVA via UDR-forced routing). NSGs are the per-NIC / per-subnet layer; Azure Firewall is the centralized inspection layer. The two are complementary, not redundant.
- [ ] **[Recommended]** Audit **augmented security rules** — rules that combine multiple sources, multiple destinations, multiple ports, and multiple service tags into a single rule. Augmented rules are useful for reducing rule count but make the policy harder to read; use sparingly.
- [ ] **[Optional]** Use **Azure Policy** to enforce NSG hygiene at the management group level: "no NSG rule with `Source = *` and `DestinationPortRange = 22 or 3389`", "every NSG must have flow logs enabled", "every NSG must be attached to a subnet or NIC". Drift detection is more reliable than periodic manual audit.

## Why This Matters

NSGs are the most-touched layer in any Azure environment and the most common source of "the rule looks correct, the traffic is wrong" findings. The reasons compound, and several are unique to Azure:

1. **The per-NIC + per-subnet evaluation model is non-obvious.** Engineers familiar with AWS security groups (which are per-ENI only) often miss the subnet-level NSG when troubleshooting. The audit consequence is that subnet NSGs accumulate broad rules that "have to be there" because they were placed in the wrong layer.
2. **CIDR-based rules drift in the same way as in AWS.** A rule that was "the IP of the on-prem CI server" becomes "an IP that nothing on the team owns anymore" within a year. Service tags and ASGs make the rule navigable; CIDR rules do not.
3. **Service tags are not used enough.** Azure publishes service tags for every Azure service, every region, every region pair, and several aggregations (`Internet`, `VirtualNetwork`, `AzureLoadBalancer`). Many existing NSGs hardcode IP ranges that service tags would represent more correctly. Migrating to service tags is one-time work and prevents the silent breakage when Microsoft adds new IPs.
4. **NSG Flow Logs are off by default.** Without flow logs, the answer to "is this rule actually being matched" is "we do not know". Flow logs are not free (storage cost + Traffic Analytics cost) but the operational visibility is the only way to drive NSG cleanup.
5. **The default rules give a false sense of security.** Every NSG has `AllowVNetInBound`, `AllowAzureLoadBalancerInBound`, and `DenyAllInBound` by default. The first one allows any traffic from anywhere in the VNet — which is fine if VNet means "everything in the VNet should be able to talk to everything else", but is wrong for any environment that wants intra-VNet segmentation. Reviewers who do not check the default rules miss the most important rule of all.

The cost of NSG sprawl is the same as security group sprawl in AWS — it accumulates over time and is much more expensive to clean up after the fact than to design correctly upfront.

## Common Decisions (ADR Triggers)

- **ASG references vs CIDR rules** — default to ASG references for any intra-VNet source. CIDR rules are appropriate for: external on-prem networks reached via ExpressRoute or VPN, public internet sources (with documented ownership), and Azure service tags as sources. Every CIDR rule should answer: what does this CIDR represent, who owns it, how do we know it has not changed.
- **Subnet NSG vs NIC NSG** — subnet NSG for broad rules that apply to everything in the subnet (e.g., "deny inbound RDP from any source", "allow outbound to AzureMonitor service tag"). NIC NSG for workload-specific rules that apply to a specific resource. Avoid duplicating rules between the two layers — pick one for each rule and document.
- **NSG vs Azure Firewall vs AVNM security admin rules** — NSGs at the per-NIC / per-subnet layer for workload-specific rules. Azure Firewall for centralized inspection (FQDN filtering, threat intelligence, DNS proxy). AVNM security admin rules at the org level for guardrails that cannot be overridden. The three are layered, not alternatives.
- **NSG Flow Logs v1 vs v2** — v2 is strictly better (captures action and rule matched). Use v1 only if a downstream tool specifically requires v1 format. v2 is the default for new deployments.
- **Service tag granularity** — broad tags (`Storage`) are simpler but allow access to every storage account in every region. Regional tags (`Storage.WestUS2`) are tighter. Resource-specific service tags via Private Link are the tightest. Pick the granularity that matches the security intent.

## Reference Architectures

### Three-tier application with subnet-per-tier NSGs

- **Web subnet NSG** — ingress `:443` from `Internet` service tag (or from the Application Gateway subnet only, if behind App Gateway); egress to App ASG on the application port; egress to AzureMonitor and Storage service tags
- **App subnet NSG** — ingress on application port from Web ASG (by reference); egress to DB ASG on the database port; egress to AzureKeyVault, AzureMonitor service tags
- **DB subnet NSG** — ingress on database port from App ASG (by reference); egress to AzureKeyVault, AzureMonitor service tags only
- **Management subnet NSG** — ingress from `AzureBastionSubnet` only on `:22` / `:3389`; egress to all internal subnets for management traffic
- All four NSGs have flow logs enabled with Traffic Analytics

### NSG + Azure Firewall layered design

- Subnet NSGs allow only intra-VNet traffic and traffic to/from the AzureFirewallSubnet
- Default route (`0.0.0.0/0`) on each subnet points to the Azure Firewall internal IP via UDR
- Azure Firewall inspects all egress traffic (FQDN filtering, threat intelligence, application rules)
- Internet ingress only via Azure Firewall public IP (or via App Gateway in front of Firewall for L7)
- NSGs handle the per-flow allow/deny based on identity (ASG); Firewall handles the FQDN and content filtering

### AVNM security admin rules (org-wide)

- AVNM connected to all subscriptions in the tenant via management group scope
- Security admin rules at AVNM level (`AlwaysAllow` / `Allow` / `Deny`):
  - **Always-deny** inbound RDP / SSH from `Internet` to all VNets (cannot be overridden by NSG)
  - **Always-deny** inbound from known malicious IP ranges (updated via threat intel feed)
  - **Allow** management traffic from the corporate IP ranges
- Per-VNet NSGs handle the workload-specific rules underneath

---

## Reference Links

- [Network security groups overview](https://learn.microsoft.com/azure/virtual-network/network-security-groups-overview)
- [Application security groups](https://learn.microsoft.com/azure/virtual-network/application-security-groups)
- [Service tags for Azure services](https://learn.microsoft.com/azure/virtual-network/service-tags-overview)
- [NSG Flow Logs](https://learn.microsoft.com/azure/network-watcher/network-watcher-nsg-flow-logging-overview)
- [Traffic Analytics](https://learn.microsoft.com/azure/network-watcher/traffic-analytics)
- [Azure Virtual Network Manager security admin rules](https://learn.microsoft.com/azure/virtual-network-manager/concept-security-admins)

## See Also

- `providers/azure/networking.md` — broader Azure networking (VNet, hub-spoke, vWAN, ExpressRoute, Private Link)
- `providers/azure/security.md` — Defender for Cloud, Microsoft Sentinel, broader Azure security services
- `providers/azure/landing-zones.md` — NSG rules as part of the platform / connectivity subscription baseline
- `providers/aws/security-groups.md` — equivalent service in AWS, similar audit patterns
- `patterns/network-segmentation.md` — segmentation patterns at the architecture level
