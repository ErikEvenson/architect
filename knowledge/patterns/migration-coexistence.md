# Hybrid Coexistence During Datacenter Relocation

## Scope

This file covers the **architecture and operational model for the coexistence period** when workloads run simultaneously at source and target sites during a multi-site datacenter relocation. During this period (weeks to months per site), both environments are fully operational, workloads at each site depend on services at the other, and the migration team must manage bidirectional connectivity, DNS resolution, identity services, and data protection across both locations. Distinct from steady-state multi-site architecture -- coexistence is temporary and asymmetric (one site is being emptied). For datacenter relocation planning, see `patterns/datacenter-relocation.md`. For multi-site sequencing, see `general/multi-site-migration-sequencing.md`. For migration cutover, see `patterns/migration-cutover.md`.

## Checklist

### Network Architecture

- [ ] **[Critical]** Is dedicated network connectivity provisioned between each source-target site pair? (Dedicated circuit, MPLS, VPN, or dark fiber. Shared internet is not acceptable for production coexistence. Bandwidth must support both migration data transfer and production traffic simultaneously.)
- [ ] **[Critical]** Is L3 routing configured between source and target VLANs so that workloads at both sites can communicate? (VMs at the target need to reach services still at the source, and vice versa. This is not optional -- it is a prerequisite for migration.)
- [ ] **[Critical]** Is the bandwidth sized for both migration seeding AND production coexistence traffic? (Migration seeding consumes bandwidth continuously. Production cross-site traffic adds to it. If the circuit is saturated by seeding, production latency increases.)
- [ ] **[Recommended]** Is QoS configured to prioritize production traffic over migration seeding? (Seeding is bulk background transfer -- it should yield to production traffic on shared circuits.)
- [ ] **[Recommended]** Is latency between source and target measured and documented? (Cross-site latency affects application performance for workloads that depend on services at the other site. Typical dedicated circuit latency: 1-5ms intra-metro, 10-30ms inter-region, 50-150ms intercontinental.)
- [ ] **[Optional]** Is L2 stretch considered for the migration period? (L2 stretch keeps the same IP addresses temporarily, avoiding re-IP during migration. Adds network complexity but simplifies application configuration. Usually not recommended for cross-geography relocations.)

### DNS Strategy

- [ ] **[Critical]** Is the DNS cutover approach defined per migration wave? (Reduce TTL to 300s at least 48 hours before cutover. Update DNS records during cutover window. Validate resolution from both sites before marking cutover complete.)
- [ ] **[Critical]** Is DNS infrastructure deployed at both source and target sites? (Infoblox DDI, Microsoft DNS, or equivalent must be operational at the target before workloads arrive. Conditional forwarding or split-horizon may be needed during coexistence.)
- [ ] **[Recommended]** Is reverse DNS (PTR) updated alongside forward DNS? (Applications and monitoring tools that perform reverse lookups will fail if PTR records point to old IPs.)
- [ ] **[Recommended]** Is DNS propagation validated after each wave cutover? (Automated checks from both sites confirming forward and reverse resolution for all migrated VMs.)

### Identity and Authentication

- [ ] **[Critical]** Are Active Directory domain controllers (or read-only DCs) operational at the target site before any workloads migrate there? (VMs depend on AD for authentication, DNS, group policy. Without AD at the target, migrated workloads cannot authenticate. This is the #1 sequencing constraint.)
- [ ] **[Critical]** Is the AD Sites and Services topology updated to include target subnets? (Without site-subnet mapping, workloads at the target authenticate against source DCs across the WAN instead of local target DCs, causing latency and WAN dependency.)
- [ ] **[Recommended]** Is FSMO role placement planned for the coexistence period? (FSMO roles remain at source until the final wave. Transfer to target DCs only after all workloads are migrated. PDC Emulator placement affects time synchronization.)
- [ ] **[Recommended]** Is Kerberos authentication tested across sites? (Kerberos tickets issued by source DCs must be valid at the target and vice versa. Clock skew > 5 minutes causes authentication failures.)

### Firewall and Security

- [ ] **[Critical]** Are firewall rules deployed at both source and target to permit cross-site communication? (Migrated VMs at the target need to reach services still at the source. Source VMs need to reach services already migrated to the target. Rules must be bidirectional.)
- [ ] **[Critical]** Is the firewall rule set for the target derived from the source? (Export current rules, augment with network flow analysis from 30+ days of production traffic. Do not rely solely on documented rules -- undocumented flows are common.)
- [ ] **[Recommended]** Are firewall rules validated per wave before cutover? (Smoke test: can a migrated VM at the target reach all its dependencies? Test before production cutover, not after.)
- [ ] **[Recommended]** Is a firewall rule cleanup plan defined for post-migration? (Cross-site rules are temporary. After all workloads migrate, remove source-to-target rules and decommission source firewall infrastructure.)

### Application Dependencies

- [ ] **[Critical]** Are application dependency groups migrated together within each wave? (Multi-tier applications -- web, app, database -- must migrate as a unit. Split-state where the web tier is at the target and the database is at the source creates cross-site latency for every transaction.)
- [ ] **[Recommended]** Are latency-sensitive dependencies identified? (Database connections, RPC calls, file shares, real-time data feeds. These may not tolerate cross-site latency during split-state.)
- [ ] **[Recommended]** Is a dependency map available? (CMDB, network flow analysis, or application documentation. Without a dependency map, migration waves risk breaking application stacks.)

### Data Protection

- [ ] **[Critical]** Is backup operational at both sites during coexistence? (Veeam or equivalent must back up VMs at the target from the moment they are migrated. Do not wait for all VMs to migrate before establishing backup.)
- [ ] **[Recommended]** Is the backup target at the source, the target, or both? (Backup to local storage at each site is simplest. Cross-site backup during coexistence adds WAN traffic.)
- [ ] **[Recommended]** Is DR configuration updated as VMs migrate? (Protection domains, replication targets, and recovery plans must be updated per wave.)

### Monitoring and Operations

- [ ] **[Recommended]** Is monitoring active at both sites during coexistence? (Prism Central, Veeam, ITSM alerts -- all must cover both source and target. Monitoring gaps during coexistence are the highest-risk window.)
- [ ] **[Recommended]** Is an incident response plan defined for cross-site issues? (If a migrated VM at the target cannot reach a service at the source, who troubleshoots? Network team, migration team, or application team?)
- [ ] **[Optional]** Is a coexistence dashboard deployed? (Single view showing: VMs at source, VMs at target, cross-site circuit utilization, DNS resolution status, AD replication health, backup status at both sites.)

### Duration and Exit Criteria

- [ ] **[Recommended]** Is the maximum coexistence duration defined per site? (Coexistence has ongoing costs: dual monitoring, dual firewall management, circuit costs, split-state risk. Define when coexistence must end.)
- [ ] **[Recommended]** Are exit criteria defined? (Last VM migrated, hypercare complete, source VMs powered off, DNS TTLs restored, firewall cross-site rules removed, backup at source decommissioned, circuit disconnected.)

## Why This Matters

The coexistence period is the highest-risk phase of a datacenter relocation. During this window, workloads depend on infrastructure at two locations connected by a WAN link. Any failure in the cross-site connectivity -- circuit outage, DNS misconfiguration, firewall rule gap, AD replication failure -- can cause production impact at both sites.

The most common failure: **not deploying AD at the target before migrating workloads.** Every Windows VM authenticates against Active Directory. If the target site has no domain controller, every authentication request traverses the WAN to the source. If the WAN fails, all migrated workloads lose authentication. This is a single point of failure that is entirely preventable.

The second most common failure: **undocumented firewall rules.** The source site has years of accumulated firewall rules, many undocumented. When the target site is built with a "clean" rule set, legitimate traffic flows are blocked. Network flow analysis (30+ days of production traffic) before migration is the mitigation.

## Common Decisions (ADR Triggers)

- **DNS strategy** -- TTL reduction + per-wave update vs GSLB vs L2 stretch (same IPs); determines application configuration change scope
- **AD deployment at target** -- full DCs vs read-only DCs vs Sites & Services subnet mapping only; determines authentication resilience
- **Firewall rule derivation** -- export from source vs flow analysis vs rebuild from scratch; determines rule completeness and effort
- **Coexistence network design** -- dedicated circuit vs shared MPLS vs VPN; determines bandwidth, latency, and reliability
- **Application grouping granularity** -- per-VM, per-application, per-tier, per-site; determines wave complexity and split-state risk

## Reference Links

- [Infoblox Documentation](https://docs.infoblox.com/) -- Infoblox DDI (DNS, DHCP, IPAM) documentation for network infrastructure management during coexistence
- [Microsoft AD Sites and Services](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/creating-a-site-design) -- Microsoft documentation for Active Directory site design and subnet-to-site mapping

## See Also

- `patterns/datacenter-relocation.md` -- Datacenter relocation planning and execution
- `patterns/migration-cutover.md` -- Per-wave cutover procedures
- `general/multi-site-migration-sequencing.md` -- Multi-site wave planning and sequencing
- `general/tier0-security-enclaves.md` -- Tier 0 / AD deployment considerations
- `general/virtual-appliance-migration.md` -- Appliance re-deployment at target sites
