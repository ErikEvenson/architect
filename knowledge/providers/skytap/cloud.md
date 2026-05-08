# Skytap on Azure (Kyndryl Cloud Uplift)

## Scope

Skytap on Azure -- rebranded as **Kyndryl Cloud Uplift** following Kyndryl's May 2024 acquisition of Skytap -- is a specialty cloud platform that runs IBM Power (AIX, IBM i, Linux on Power) and x86 workloads on bare-metal hardware sited inside Microsoft Azure data centers. It preserves on-premises VM and LPAR semantics (LPAR sizing, entitled capacity, multi-NIC environments, broadcast-domain-preserving networks, environment cloning) so legacy workloads can lift-and-shift to Azure without refactoring. This file covers region/SKU selection, IBM Power LPAR sizing, the Azure Marketplace subscription model, networking (VPN, ExpressRoute, public IPs), connectivity to native Azure services, identity, migration on-ramps, DR, and licensing/cost. For broader hybrid patterns see `patterns/hybrid-cloud.md`. For native Azure compute alternatives (IBM Power Virtual Server, Azure Bare Metal) see `providers/azure/compute.md`. For migration tooling that lands in Skytap see `general/workload-migration.md`.

## Checklist

### Workload Fit and Brand Awareness

- [ ] **[Critical]** Is the workload one Skytap is actually built for -- IBM Power (AIX, IBM i / AS/400, Linux on Power) or x86 environments that require preserved L2 networking, multi-NIC topology, broadcast domains, or full environment-clone semantics? (Native Azure VMs and IBM Power Virtual Server cover most other cases at lower cost. Skytap's value is preserving on-prem network and VM behavior verbatim, not raw IaaS.)
- [ ] **[Critical]** Are stakeholders aware that "Skytap on Azure" is now branded **Kyndryl Cloud Uplift**, and that procurement, support, and Marketplace listings use the Kyndryl name? (Acquisition closed May 2024. The product, help docs at help.skytap.com, and APIs are unchanged, but Marketplace listings, pricing pages, and renewal contracts now read "Kyndryl Cloud Uplift" -- procurement teams searching for "Skytap" alone will miss them.)

### Region and Capacity Selection

- [ ] **[Critical]** Is a Skytap region selected in an Azure geography that satisfies data-residency and latency requirements? (As of 2026, Skytap runs in 14 Azure regions: East US, South Central US, Canada Central, North Europe, West Europe, UK South, Australia East, Japan East, Southeast Asia, Central India, East Asia. Some Azure geographies have two zones -- e.g. `US-Virginia-M-1` and `US-Virginia-M-2` -- treated as independent failure domains.)
- [ ] **[Critical]** Is it understood that environments, templates, and assets are **region-locked** -- once created, they cannot be moved to another Skytap region without copy/export? (Plan multi-region deployments up front. A misplaced template in the wrong region requires a full template copy across the region boundary, which is bandwidth-billed.)
- [ ] **[Recommended]** Is LPAR sizing planned within Skytap's capacity envelope -- up to 44,000 CPWs and 512 GB RAM per LPAR for general IBM Power workloads, and up to 60,000 CPWs for IBM i (an IBM-imposed P10 processor-group ceiling)? (Workloads that exceed these limits cannot be hosted as a single LPAR and must be split or kept on-prem / IBM PowerVS where larger sizes are available.)
- [ ] **[Recommended]** Is entitled capacity vs vCPU sharing mode set deliberately for each LPAR -- AIX/Linux on Power can run uncapped (e.g. 2.0 entitled, 8 vCPU burst), but **IBM i partitions are always capped** so set entitled capacity to the actual workload requirement, not a low value with hopes of bursting? (`EC = MIN(vcpu_count, FLOOR(MAX(GB_ram/50, 0.05), 0.005))` is the floor formula; under-entitling capped IBM i LPARs causes immediate performance degradation under load.)

### Azure Subscription, Identity, and Billing

- [ ] **[Critical]** Is Skytap procured through the Azure Marketplace using a subscription model where billing accrues to the customer's Azure subscription (Marketplace billing, not direct invoice)? (This is a meaningful procurement decision: Marketplace billing means Skytap consumption counts toward the customer's Azure spend rather than a separate Skytap invoice. MACC eligibility for Marketplace offers depends on the specific Marketplace listing classification -- confirm with Microsoft account team before assuming MACC offset.)
- [ ] **[Critical]** Is recurring billing left **enabled** and is the operational team aware that disabling it triggers permanent deletion of all environments, templates, and assets at period end? (This is the single most common Skytap incident: a finance or admin user disables auto-renew thinking it pauses billing -- it does not, it schedules destruction.)
- [ ] **[Recommended]** Is identity strategy documented -- Skytap uses Azure account email for the Marketplace owner, but in-product user accounts, RBAC, departments, and SSO are configured separately inside Skytap? (Skytap supports SAML SSO for federated identity; it does not natively integrate with Entra ID groups for role assignment. User lifecycle is a separate process from Azure RBAC.)
- [ ] **[Recommended]** Are Skytap subscriptions **named with the region** (e.g. `prod-canada-central`, `dr-east-us`) when multiple regions are in use? (Skytap subscriptions are region-specific. Without naming discipline, multi-region accounts become impossible to administer correctly.)

### Networking

- [ ] **[Critical]** Is the connectivity model selected -- site-to-site IPsec VPN (IKEv1 or IKEv2, AES-256, PFS, static public IP per VPN, supports NAT for environment cloning), Azure ExpressRoute (standard or customer-managed, preferred for production throughput and latency), or both for resiliency? (ExpressRoute is the production-grade path. VPN suffices for dev/test or initial migration, but a single VPN endpoint is a throughput and availability bottleneck.)
- [ ] **[Critical]** Is integration with the customer's native Azure VNets planned -- Skytap environments do not live inside the customer's VNet, so traffic between Skytap LPARs and native Azure VMs/PaaS flows through the VPN or ExpressRoute boundary? (This surprises teams expecting Skytap to behave like a delegated subnet. Plan for the latency, throughput, and firewall rules of an inter-network hop, including Azure Private Link patterns for secure access to Blob/SQL/etc.)
- [ ] **[Recommended]** Is environment-level NAT enabled where multiple cloned environments need to attach to the same external network? (Cloning a Skytap environment duplicates internal IPs by design -- preserving the topology is the point. NAT lets multiple clones coexist on one VPN. Without it, only one clone can be attached at a time.)
- [ ] **[Recommended]** Are public IPs allocated only where required, and is it understood that a public IP attached to a VPN is consumed exclusively by that VPN and cannot be shared across environments? (Public IPs are a metered resource. Audit attachments before scaling out VPNs.)

### Storage, Backup, and DR

- [ ] **[Recommended]** Is the storage tier appropriate -- Skytap's native SSD-backed storage for LPAR boot and primary disks, and Azure NetApp Files (mounted via NFS into the Skytap environment) for high-throughput shared filesystems where native storage is insufficient? (ANF integration is documented in Microsoft's Azure Architecture Center reference for IBM Power on Skytap. Choose tier per IOPS/latency requirement, not by default.)
- [ ] **[Recommended]** Is the IBM i / AIX backup path defined -- BRMS or GoSave for IBM i, mksysb for AIX, written to Skytap-attached storage and replicated to Azure Blob Storage via FTP proxy + Azure Data Box Gateway, with Azure Private Link to keep traffic off the public internet? (This is Microsoft's reference architecture for IBM i backup off Skytap. Without an explicit backup target outside Skytap, a Skytap region failure is a data-loss event.)
- [ ] **[Recommended]** Is DR strategy chosen -- template-based cold DR (snapshot environments to templates, restore in another region; cheapest, longest RTO), warm standby (running LPARs in a second Skytap region with periodic data sync), or near-real-time HA (IBM i journal replication or AIX-level replication over ExpressRoute/VPN, role-swap failover, near-immediate RTO)? (Skytap does not provide built-in cross-region replication for IBM Power; replication is an OS/application-layer responsibility -- IBM i journals, MIMIX, AIX HACMP/PowerHA equivalents.)

### Migration On-Ramps

- [ ] **[Recommended]** Is the source platform mapped to a supported migration on-ramp -- on-prem IBM Power (BRMS/GoSave + Data Box for IBM i; mksysb + Data Box for AIX), VMware x86 (image export and re-import as Skytap templates), or other clouds (block-level replication via third-party tools like Hystax)? (Skytap does not provide a Move-style automated migration for x86; expect a backup/restore or image-conversion process. For VMware-to-Skytap x86, plan extra time vs typical hyperscaler migration tooling.)
- [ ] **[Optional]** For dev/test or training scenarios, is the template/clone workflow used to package multi-VM environments (database + app + web tier with their original IPs and network topology) for repeatable provisioning? (This is Skytap's classic strength outside the IBM Power use case. Use templates instead of scripted re-provisioning when network state matters.)

### Cost Management

- [ ] **[Recommended]** Is the always-on vs suspended-environment cost model understood -- Skytap bills running environments at full rate, suspended environments at a reduced storage-only rate, and templates at storage rate only? (The single biggest cost surprise: dev/test environments left running over weekends and holidays. Build suspend automation or schedules from day one.)
- [ ] **[Recommended]** Are licensing implications documented for IBM software -- BYOL via IBM ILMT for sub-capacity licensing on Skytap LPARs, or full-capacity licensing where ILMT is not deployed? (Without ILMT properly configured, IBM holds licensees to full-capacity charging on the underlying processor group, which can be vastly more expensive than the entitled capacity actually consumed.)

## Why This Matters

Skytap occupies a specific niche that public hyperscalers do not natively fill: workloads that depend on IBM Power (AIX, IBM i) hardware semantics or x86 network topology that AWS/Azure/GCP cannot preserve. For an architecture that includes AS/400, AIX, or any application whose multi-tier networking depends on broadcast domains, multicast, or specific MAC/IP layouts, the realistic options are (1) keep it on-prem, (2) move to IBM Power Virtual Server, or (3) move to Skytap. Skytap is the only one of those that runs inside Microsoft Azure data centers, so it is typically the right answer when the surrounding modern application estate is on Azure and ExpressRoute/VNet-adjacent latency to legacy systems matters.

The Kyndryl rebrand is not just cosmetic. Skytap as an independent product had a roadmap and pricing model set by Skytap; under Kyndryl, the offering is now packaged with Kyndryl's managed services (migration assessment, ongoing operations, modernization). Customers buying "Skytap on Azure" today are typically buying a Kyndryl-managed engagement, not a self-service SaaS subscription, and procurement, SLAs, and support escalation paths reflect that. Architects scoping a Skytap project should engage Kyndryl early -- the unmanaged self-service pattern that worked under independent Skytap is not the default path now.

The cost model is a frequent source of project failure. Skytap is not cheap on a per-vCPU-hour basis -- it is priced as a specialty cloud, not a commodity hyperscaler -- and IBM software licensing layered on top can dwarf the infrastructure cost. Without sub-capacity licensing (ILMT properly configured), without environment suspension automation, and without right-sized LPARs (capped IBM i partitions especially), bills routinely run 2-3x what was budgeted at proof-of-concept. The DR cost question is also non-obvious: a warm-standby Skytap environment in a second region is a second running subscription, not a discounted replica.

The recurring-billing trap deserves explicit callout because it is operationally severe. Disabling Marketplace recurring billing on a Skytap subscription deletes every environment, template, and asset at period end, irreversibly. There is no grace period restore. Document this in runbook and access controls.

## Common Decisions (ADR Triggers)

- **Skytap vs IBM Power Virtual Server vs on-prem retention** -- Skytap (sits inside Azure, lowest-latency to Azure-native services, preserves L2 environment semantics, Kyndryl-managed) vs IBM PowerVS (sits inside IBM Cloud, larger LPAR ceilings, IBM-managed, requires Azure-to-IBM-Cloud network hop) vs on-prem retention (no migration risk, preserves existing operations, defers but does not solve the cloud question). The Azure-adjacency case for Skytap is strongest when modern services in Azure call IBM i / AIX systems frequently.
- **Skytap vs native Azure VMs for x86** -- Skytap (preserves L2, multi-NIC, broadcast domains, environment cloning, slower & more expensive) vs Azure VMs (no L2 preservation, native Azure VNet integration, vastly cheaper, faster). Use Skytap for x86 only when network or VM-state preservation is genuinely required; default to Azure VMs otherwise.
- **VPN vs ExpressRoute** -- VPN (faster to set up, lower cost, single-endpoint throughput bottleneck, sufficient for dev/test) vs ExpressRoute (production-grade throughput and latency, higher cost, longer provisioning). Production IBM Power workloads with on-prem callbacks should default to ExpressRoute.
- **Marketplace billing vs direct/Kyndryl-managed contract** -- Marketplace (billed via Azure subscription, may count toward MACC depending on listing classification, self-service) vs Kyndryl-managed contract (bundled migration and operations services, separate invoice, professional services baked in). Kyndryl-managed is the default path post-acquisition for new enterprise engagements.
- **DR pattern** -- template snapshots in second region (cheapest, longest RTO, manual restore) vs warm standby with running LPARs and periodic sync (medium cost and RTO) vs IBM i journal replication / AIX HACMP-equivalent over ExpressRoute (highest cost, near-immediate role swap). Pick based on application-tier RTO, not infrastructure preference.
- **ILMT vs full-capacity IBM licensing** -- deploying ILMT on Skytap (requires ongoing IBM licensing operations work, reports sub-capacity usage, large cost reduction) vs full-capacity licensing (no ILMT operations overhead, IBM bills against the entire processor group). For any non-trivial IBM Power footprint on Skytap, ILMT pays for itself within months -- but only if it is actually deployed and reporting correctly.

## Reference Links

- [Kyndryl Cloud Uplift product page](https://www.kyndryl.com/us/en/services/cloud-uplift) -- post-acquisition product positioning
- [Skytap (Kyndryl Cloud Uplift) help and documentation](https://help.skytap.com/) -- still the canonical product documentation
- [Understanding Skytap regions](https://help.skytap.com/understanding-regions.html) -- current region list, region locality semantics
- [Skytap VPN overview](https://help.skytap.com/wan-vpn-overview.html) -- IPsec VPN, NAT, ExpressRoute connectivity
- [Skytap VPN configuration parameters](https://help.skytap.com/wan-vpn-configuration-parameters.html) -- IKEv1/IKEv2, AES-256, PFS configuration
- [Skytap Well-Architected Framework](https://skytap.github.io/well-architected-framework/) -- vendor-published architecture guidance covering connectivity, security, performance, operations
- [Microsoft Learn: Migrate IBM i series to Azure with Skytap](https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/migrate-ibm-i-series-to-azure-with-skytap) -- Microsoft reference architecture for IBM i + Azure backup integration
- [Microsoft Learn: Use Azure NetApp Files to deploy IBM Power in Skytap on Azure](https://learn.microsoft.com/en-us/azure/architecture/example-scenario/mainframe/deploy-ibm-power-workloads) -- ANF storage tier integration with Skytap LPARs
- [Editing vCPUs and RAM for AIX and Linux on Power VMs](https://help.skytap.com/editing-vm-cpus-ram-power.html) -- entitled-capacity formula and capped/uncapped sharing mode

## See Also

- `providers/azure/compute.md` -- Azure-native compute alternatives including bare metal
- `providers/azure/networking.md` -- Azure VNet, ExpressRoute, vWAN, Private Link patterns Skytap connects to
- `providers/kyndryl/` -- Kyndryl as managed service provider; engagement model implications
- `patterns/hybrid-cloud.md` -- hybrid cloud architecture patterns
- `patterns/hypervisor-migration.md` -- hypervisor and platform conversion patterns
- `patterns/application-modernization.md` -- modernization paths for legacy workloads, including the strangler-fig pattern around an IBM i / AIX core
- `general/workload-migration.md` -- migration wave methodology and cutover planning
- `general/disaster-recovery.md` -- DR architecture patterns including replication-based DR
- `providers/hystax/migration.md` -- third-party migration tooling that can target Skytap for x86 sources
