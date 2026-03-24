# On-Premises to Nutanix Cloud Clusters (NC2) Migration Pattern

## Scope

This file covers **migrating on-premises infrastructure (Nutanix AHV, VMware ESXi) to Nutanix Cloud Clusters (NC2) on Azure or AWS**. NC2 runs the Nutanix HCI stack (AOS, AHV, Prism) on bare-metal instances in public cloud, providing operational consistency with on-premises Nutanix while eliminating physical datacenter dependencies. This pattern addresses end-to-end migration planning including network connectivity provisioning, bulk data transfer strategies, hybrid coexistence during migration, re-IP requirements, wave planning, and cutover execution. For in-place hypervisor migration without facility change, see `patterns/hypervisor-migration.md`. For general datacenter relocation mechanics, see `patterns/datacenter-relocation.md`. For cutover execution details, see `patterns/migration-cutover.md`.

## Checklist

### NC2 Target Environment

- [ ] **[Critical]** Is the target cloud provider selected (Azure or AWS) and NC2 cluster sizing completed? NC2 runs on bare-metal instances — select instance types based on CPU, memory, and storage requirements derived from source VM inventory. NC2 supports AHV only — VMware VMs must convert during migration.
- [ ] **[Critical]** Is NC2 cluster provisioning sequenced per migration wave? Do not provision all NC2 clusters upfront — provision per wave to avoid unnecessary cloud spend during migration. Each NC2 cluster takes 1-2 hours to deploy via Prism Central.
- [ ] **[Critical]** Is Prism Central deployed in the target cloud environment? Prism Central is required for NC2 management, Nutanix Move orchestration, and cross-cluster visibility during migration.
- [ ] **[Critical]** Are NC2 licensing and subscription models selected? Options: BYO licenses (port existing on-prem Pro or Ultimate licenses), PAYG (hourly consumption during migration), or Cloud Commit (term-based). Use PAYG during migration to avoid overcommitment, then convert to Reserved Instances or Cloud Commit post-migration for cost optimization.
- [ ] **[Recommended]** Is a two-phase approach evaluated? Phase 1: consolidate onto a single hypervisor at the source site (e.g., migrate VMware VMs to AHV on-premises using Nutanix Move). Phase 2: migrate AHV-to-AHV from on-premises to NC2 (simpler, faster, lower risk). This decouples hypervisor conversion from cloud migration.
- [ ] **[Recommended]** Are NC2 cluster resource limits documented? Understand maximum nodes per cluster, maximum VMs per cluster, and storage capacity limits to prevent over-subscription during wave planning.
- [ ] **[Optional]** Is NC2 on multiple cloud providers evaluated for multi-cloud resilience? NC2 supports Azure, AWS, and Google Cloud — licenses are portable across clouds.

### Network Connectivity (Critical Path)

- [ ] **[Critical]** Is Azure ExpressRoute (or AWS Direct Connect) provisioned? This is typically the critical path item with 2-4 weeks lead time for circuit provisioning. ExpressRoute provides private, dedicated connectivity between on-premises and Azure — migration data transfer must not traverse the public internet. Order circuits early — this is a hard dependency for migration start.
- [ ] **[Critical]** Is the ExpressRoute circuit sized for migration bandwidth requirements? Available bandwidths: 50 Mbps to 10 Gbps. Calculate required bandwidth: `Data Volume (TB) * 1024 * 8 / Transfer Window (seconds) / 0.8 utilization = Required Gbps`. For petabyte-scale migrations, 10 Gbps circuits are typical — consider multiple circuits or ExpressRoute Direct (100 Gbps) for massive volumes.
- [ ] **[Critical]** Is the ExpressRoute connectivity model selected? Options: colocation at an exchange (if source datacenter is at an exchange provider), point-to-point Ethernet (dedicated cross-connect), any-to-any IPVPN (via MPLS provider). The model depends on source site connectivity options and carrier availability.
- [ ] **[Critical]** Is ExpressRoute redundancy configured? Microsoft requires dual connections to two MSEEs (Microsoft Enterprise Edge routers) at each peering location. For maximum resiliency, connect to two ExpressRoute circuits in two different peering locations.
- [ ] **[Critical]** Is the seeding time calculated and validated against the migration timeline? Formula: `Data Volume (PB) * 1024 * 1024 / (Bandwidth Gbps * 0.8 * 86400 / 8) = Days`. Example: 5 PB over 10 Gbps = ~61 days for initial seed. If the seeding duration exceeds the available migration window, network-only transfer is insufficient — evaluate Azure Data Box for initial bulk seeding.
- [ ] **[Recommended]** Is bandwidth throttling configured for migration traffic? Prevent migration replication from saturating the ExpressRoute circuit during business hours — production workloads at the source site still need connectivity. Schedule heavy replication for off-hours or implement QoS policies.
- [ ] **[Recommended]** Is network monitoring deployed on the ExpressRoute circuit? Track utilization, packet loss, and latency throughout the migration to detect bottlenecks early.

### Bulk Data Transfer (Azure Data Box)

- [ ] **[Critical]** Is Azure Data Box evaluated for initial bulk data seeding? For multi-petabyte migrations where network transfer duration exceeds the timeline, Data Box provides physical media transfer. Next-gen devices offer 120 TB or 525 TB usable capacity with up to 100 Gbps network interfaces and ~7 GB/s copy speeds via SMB Direct on RDMA.
- [ ] **[Critical]** If using Data Box, is the seed-then-sync strategy planned? Ship Data Box units for initial bulk data, then use ExpressRoute for ongoing delta replication and final sync via Nutanix Move. The bulk seed reduces the volume of data that must transfer over the network by orders of magnitude.
- [ ] **[Recommended]** Is the Data Box ordering lead time accounted for? Azure prepares and ships devices — factor in order processing, shipping, on-site data copy time, return shipping, and Azure-side upload time. Plan 2-4 weeks end-to-end per Data Box cycle.
- [ ] **[Recommended]** Are multiple Data Box units ordered for parallel loading if the total volume exceeds single-device capacity? For petabyte-scale transfers, multiple 525 TB units may be needed simultaneously.

### IP Addressing and DNS

- [ ] **[Critical]** Is full re-IP planned for all migrated workloads? NC2 on Azure or AWS uses cloud-native networking — L2 stretch from on-premises to NC2 is not available. Every VM receives a new IP address in the target cloud subnet. This is non-negotiable and affects every application, firewall rule, monitoring configuration, and hardcoded IP reference.
- [ ] **[Critical]** Is the target subnet design completed before migration begins? Define VNet/VPC structure, subnet allocations per application tier, and VLAN-to-subnet mapping from the source environment. NC2 clusters connect to Azure VNets or AWS VPCs via the cloud provider's networking layer.
- [ ] **[Critical]** Is DNS cutover strategy defined per migration wave? Reduce TTLs before each wave (24-48 hours prior), update DNS records during the cutover window to point to new IPs, and verify propagation. Applications using hardcoded IPs require configuration changes — identify these before migration.
- [ ] **[Critical]** Are Active Directory domain controllers deployed in the target cloud environment before workload migration? DCs must be operational in Azure/AWS (either on NC2 or as cloud-native VMs) before migrating domain-joined workloads. AD Sites and Services must be configured for the new subnets. Migrate DCs in the earliest wave — they are a dependency for everything else.
- [ ] **[Recommended]** Is a comprehensive audit of hardcoded IP references completed? Check application configurations, scripts, monitoring tools, backup configurations, firewall rules, and load balancer configs for hardcoded IPs that must change during re-IP.
- [ ] **[Recommended]** Is split-DNS configured for the coexistence period? During migration, some workloads are at the source and some at the target — DNS must resolve correctly from both locations. Internal DNS zones may need conditional forwarding between on-premises and cloud DCs.

### Migration Tooling and Execution

- [ ] **[Critical]** Is Nutanix Move deployed and configured? Move is the primary migration tool for both VMware-to-AHV and AHV-to-AHV migrations. It handles VM discovery, data replication (initial seed + incremental deltas), network mapping, and one-click cutover. Deploy Move at both source and target sites.
- [ ] **[Critical]** Is the migration wave plan defined? Group VMs by application, dependency, and site. Options: per-site waves (migrate one source site at a time), per-application waves (migrate all tiers of an application together), or hybrid. All tiers of a multi-tier application must move in the same wave to avoid cross-site latency between tiers.
- [ ] **[Critical]** Are migration waves sized to fit within maintenance windows? Each wave's cutover requires: final delta sync (minutes to hours depending on change rate), source VM shutdown, target VM boot, validation. Size waves so that cutover completes within the available window.
- [ ] **[Critical]** Is the Nutanix Move replication schedule configured? Start data seeding (initial replication) days or weeks before the planned cutover date. Move performs continuous delta replication after the initial seed, keeping the target close to current. The longer the seeding period, the smaller the final delta and the shorter the cutover downtime.
- [ ] **[Recommended]** Is a pilot wave of 3-5 non-critical VMs planned before production waves? Validate the entire process end-to-end: Move replication, ExpressRoute bandwidth, re-IP, DNS cutover, application validation. Use pilot results to refine estimates for production waves.
- [ ] **[Recommended]** Is the migration velocity calculated? Factors: ExpressRoute bandwidth, number of concurrent Move replications (Move supports multiple simultaneous migrations), average VM size, daily change rate. Use pilot wave metrics to project production wave durations.

### Virtual Appliance and Infrastructure Services

- [ ] **[Critical]** Are virtual appliances identified for fresh deployment at the target? Load balancers (F5 BIG-IP), DNS/DHCP/IPAM appliances (Infoblox), firewalls (Palo Alto VM-Series), and similar virtual appliances typically cannot be migrated — they require fresh installation on NC2 with configuration exported from source and imported to target.
- [ ] **[Critical]** Are appliance configurations exported and validated before migration? Export running configurations from F5, Infoblox, Palo Alto, and similar devices. Adjust for new IP addressing scheme before importing to target instances. Test thoroughly in the target environment before cutover.
- [ ] **[Recommended]** Are cloud-native alternatives evaluated for on-premises appliances? Azure Application Gateway or Azure Load Balancer may replace F5 in some cases. Azure Firewall or Azure-hosted Palo Alto may replace on-premises firewalls. Evaluate whether cloud-native services reduce operational overhead.

### Hybrid Coexistence

- [ ] **[Critical]** Is the hybrid coexistence architecture documented? During migration, source on-premises infrastructure and target NC2 clusters operate simultaneously. Applications at the source must communicate with applications already migrated to NC2, and vice versa, via the ExpressRoute circuit. This coexistence period can last weeks to months.
- [ ] **[Critical]** Is routing between source and target environments configured for bidirectional communication? BGP routes must be exchanged between on-premises and Azure/AWS via ExpressRoute or Direct Connect. Verify that all required traffic flows work before the first production wave.
- [ ] **[Critical]** Are firewall rules updated for cross-site communication during coexistence? Applications split across source and target need firewall rules permitting traffic over the ExpressRoute circuit. Derive rules from application dependency maps and network flow analysis.
- [ ] **[Recommended]** Is monitoring deployed at both source and target to track application health during coexistence? Unified monitoring across both environments ensures rapid detection of connectivity or performance issues during the migration period.

### Cutover and Rollback

- [ ] **[Critical]** Is the cutover procedure documented per wave? Standard sequence: final delta sync via Nutanix Move, source VM shutdown, target VM startup on NC2, IP/DNS updates, application validation, stakeholder sign-off.
- [ ] **[Critical]** Is the rollback strategy defined? Keep source VMs powered off (not deleted) during the validation period. If a migrated workload fails validation, rollback means: revert DNS to source IPs, power on source VMs, confirm application functionality. Source infrastructure must remain operational and accessible throughout the migration program.
- [ ] **[Critical]** Is a validation checklist prepared per wave? Include: application accessibility, database connectivity, authentication (AD/LDAP), monitoring agent check-in, backup job configuration, load balancer health checks, end-user acceptance testing.
- [ ] **[Recommended]** Is a rollback time limit defined? Source infrastructure has ongoing costs (power, licensing, facility lease). Define how long source remains available for rollback per wave (typically 5-10 business days) before decommissioning.

### Cost Optimization

- [ ] **[Critical]** Is the migration-period cost model understood? During migration, costs include: source infrastructure (ongoing), NC2 PAYG or BYO licensing, ExpressRoute circuit charges, Azure Data Box charges (if used), and any temporary cloud resources. Total cost peaks during the coexistence period when both environments are running.
- [ ] **[Critical]** Is post-migration cost optimization planned? After all workloads are migrated and validated: convert PAYG to Reserved Instances (1-year or 3-year) or Nutanix Cloud Commit for significant savings, right-size NC2 clusters based on actual utilization, decommission ExpressRoute circuits no longer needed for migration.
- [ ] **[Recommended]** Is a cost comparison prepared between PAYG, Reserved Instances, and Cloud Commit? RI and Cloud Commit offer 30-60% savings over PAYG but require commitment. Do not commit until migration is complete and target resource requirements are validated.

### Timeline Estimation

- [ ] **[Critical]** Are all critical path items identified and sequenced? Typical critical path: ExpressRoute provisioning (2-4 weeks) -> NC2 cluster deployment (hours) -> initial data seeding (weeks to months depending on volume) -> migration waves (weeks to months) -> validation and decommission. ExpressRoute provisioning and initial seeding are almost always the longest items.
- [ ] **[Critical]** Is the total migration duration estimated based on concrete factors? Key variables: total data volume (TB/PB), available bandwidth (Gbps), number of VMs, average VM size, daily change rate, number of concurrent Move replications, maintenance window duration and frequency, application testing requirements. Provide a range, not a single date.
- [ ] **[Recommended]** Is a migration timeline Gantt chart maintained with dependencies? Visualize the critical path and identify schedule risks early. Key dependencies: ExpressRoute must be active before seeding starts, DCs must be migrated before domain-joined workloads, all tiers of an application must be in the same wave.

## Why This Matters

Migrating from on-premises infrastructure to NC2 combines elements of datacenter relocation, cloud migration, and (often) hypervisor migration into a single program. Teams underestimate it because NC2 provides operational consistency with on-premises Nutanix — "it's the same Prism, the same AHV" — but the migration itself introduces challenges that do not exist in either pure cloud migration or pure datacenter relocation:

1. **ExpressRoute is the critical path, not compute.** NC2 clusters can be provisioned in hours. ExpressRoute circuits take weeks. Teams that start cluster planning before ordering circuits lose weeks of timeline. The circuit must be active before any data replication can begin, and for petabyte-scale environments, the initial seed over a 10 Gbps circuit takes months.

2. **L2 stretch is not available.** Unlike VMware HCX or NSX, NC2 does not support L2 extension between on-premises and cloud. Every VM gets a new IP address. This means every application configuration, firewall rule, monitoring entry, backup job, and hardcoded reference must be updated. Re-IP is the hidden scope that dominates cutover complexity and post-migration troubleshooting.

3. **Azure Data Box changes the math for petabyte-scale.** Transferring 5 PB over a 10 Gbps circuit takes approximately 61 days at 80% utilization. If the migration window is 90 days, that leaves only 29 days for all migration waves after seeding completes. Shipping 10 Data Box 525 TB units can transfer the same volume in 2-4 weeks including logistics, freeing the entire migration window for wave execution over the circuit.

4. **Two-phase migration reduces risk dramatically.** If the source environment runs both VMware and Nutanix AHV, completing the VMware-to-AHV conversion on-premises first (Phase 1) means Phase 2 is a same-hypervisor AHV-to-AHV migration to NC2. This eliminates driver injection, guest OS compatibility issues, and VMware tooling dependencies from the cloud migration, which is already complex enough with re-IP and network changes.

5. **Virtual appliances cannot be migrated — they must be redeployed.** F5 load balancers, Infoblox DDI appliances, Palo Alto firewalls, and similar virtual network functions are tied to their source network context (IP addresses, routes, interfaces). They require fresh installation on NC2 with configurations adapted for the new network design. This is not a Move migration task — it is a parallel workstream that must complete before application workloads that depend on these services can cut over.

6. **AD and DNS are migration wave zero.** Domain controllers and DNS infrastructure must be operational in the target environment before any domain-joined workload migrates. Deploying DCs in Azure (on NC2 or as native Azure VMs) and configuring AD Sites and Services for the new subnets is a prerequisite that gates every subsequent wave. Overlooking this creates authentication failures during cutover.

7. **Cost peaks during coexistence.** The migration period requires running both source and target infrastructure simultaneously. For a large environment, this can mean months of double infrastructure costs. Using PAYG licensing during migration and converting to Reserved Instances or Cloud Commit afterward prevents locking in costs before the target environment is validated and right-sized.

## Common Decisions (ADR Triggers)

- **Target cloud provider** — Azure vs. AWS vs. Google Cloud for NC2 deployment; driven by existing cloud presence, ExpressRoute/Direct Connect availability at source sites, compliance requirements, and Azure/AWS service dependencies
- **Two-phase vs. single-phase migration** — convert VMware to AHV on-premises first, then migrate AHV-to-AHV to NC2 (lower risk, longer total duration) vs. migrate directly from VMware to NC2 AHV in one step (faster, higher cutover complexity)
- **Data transfer method** — ExpressRoute only (predictable, constrained by bandwidth and time), Azure Data Box for bulk seeding + ExpressRoute for deltas (faster for large volumes), or ExpressRoute Direct 100 Gbps (highest bandwidth, highest cost)
- **Wave strategy** — per-site (migrate all workloads from one source site before starting the next), per-application (migrate all tiers of an application regardless of source site), or hybrid; affects coexistence duration and cross-site dependency management
- **Licensing model** — PAYG during migration with post-migration conversion to RI/Cloud Commit (flexible, slightly higher migration-period cost) vs. upfront commitment (lower unit cost, risk of overcommitment if sizing changes)
- **Virtual appliance strategy** — redeploy existing appliance vendors on NC2 (operational consistency, licensing cost) vs. adopt cloud-native equivalents (Azure Load Balancer, Azure Firewall — potentially lower cost, different operational model)
- **DNS and AD deployment** — deploy DCs directly on NC2 AHV VMs (consistent management, uses NC2 capacity) vs. deploy as Azure-native VMs (independent of NC2 cluster lifecycle, leverages Azure availability)
- **ExpressRoute circuit sizing** — single 10 Gbps circuit (sufficient for most migrations) vs. multiple circuits or ExpressRoute Direct 100 Gbps (required for petabyte-scale with tight timelines); balance cost against migration velocity

## Reference Links

- [Nutanix Cloud Clusters (NC2)](https://www.nutanix.com/products/nutanix-cloud-clusters) — NC2 product overview covering supported cloud providers, deployment model, and licensing options
- [Nutanix Move](https://www.nutanix.com/products/move) — Nutanix Move migration tool for automated VM migration between hypervisors and cloud targets
- [Azure ExpressRoute Overview](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-introduction) — Azure private connectivity service covering bandwidth options (50 Mbps to 10 Gbps), peering models, and redundancy requirements
- [Azure ExpressRoute Direct](https://learn.microsoft.com/en-us/azure/expressroute/expressroute-erdirect-about) — 100 Gbps and 400 Gbps direct connectivity for massive data ingestion scenarios
- [Azure Data Box Overview](https://learn.microsoft.com/en-us/azure/databox/data-box-overview) — Physical data transfer devices (80 TB, 120 TB, 525 TB) for offline bulk data seeding to Azure
- [Nutanix Move Documentation](https://portal.nutanix.com/page/documents/details?targetId=Nutanix-Move-v5:top-nutanix-move-guide-v50.html) — Nutanix Move administration guide covering deployment, configuration, and migration operations

## See Also

- `patterns/datacenter-relocation.md` — General datacenter relocation pattern (facility planning, data transfer, decommission)
- `patterns/hypervisor-migration.md` — In-place hypervisor migration (VMware to AHV without facility change)
- `patterns/migration-cutover.md` — Cutover execution mechanics (applies to each migration wave)
- `patterns/migration-coexistence.md` — Managing hybrid coexistence during multi-wave migrations
- `patterns/convert-before-move.md` — Two-phase pattern: convert hypervisor first, then relocate
- `patterns/hybrid-cloud.md` — Hybrid cloud architecture patterns (on-prem + public cloud ongoing operations)
- `general/networking-physical.md` — Physical network design and connectivity
- `general/workload-migration.md` — General workload migration planning and assessment
