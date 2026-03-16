# Datacenter Relocation Pattern

## Scope

This file covers **full datacenter relocation** -- moving all workloads from one or more source facilities to different target facilities. Distinct from in-place hypervisor migration (covered in `patterns/hypervisor-migration.md`) where VMs stay in the same facility. Relocation means every VM moves regardless of hypervisor, network redesign is mandatory, and facility procurement timelines gate the program. For cutover execution mechanics, see `patterns/migration-cutover.md`. For hypervisor-specific migration tooling, see the relevant provider migration files.

## Checklist

### Facility Planning

- [ ] **[Critical]** Are target facility locations identified for each region? Nothing starts until target facilities have rack space, power, cooling, and network connectivity.
- [ ] **[Critical]** Is the facility procurement timeline documented? Colo procurement can take 3-6 months for space, power, and cross-connects. This is often the critical path for the entire program.
- [ ] **[Critical]** Is site consolidation evaluated? Multiple source sites may consolidate into fewer target facilities (e.g., 5 source sites to 3 regional facilities). Consolidation saves facility costs but concentrates risk and increases per-site VM density.
- [ ] **[Critical]** Are lease expiration dates documented for all source sites? These are hard deadlines -- all workloads must be out before the lease ends.
- [ ] **[Recommended]** Is a facility build-out checklist prepared? (Rack installation, PDU provisioning, network switch deployment, out-of-band management, physical security, fire suppression verification)
- [ ] **[Recommended]** Are environmental requirements documented per target facility? (Power per rack, cooling capacity, floor loading, cable pathway capacity)
- [ ] **[Optional]** Is a facility comparison matrix prepared for vendor selection? (Cost per kW, connectivity options, carrier neutrality, compliance certifications, proximity to customer offices)

### Network Design

- [ ] **[Critical]** Is the IP addressing strategy defined? New facility = new IP space. Options: full re-IP (cleanest, most work), L2 stretch during migration (complex but preserves IPs temporarily), or VLAN extension (vendor-specific, adds latency).
- [ ] **[Critical]** Is dedicated network connectivity provisioned between source and target facilities? Migration data transfer requires bandwidth. This is not production traffic -- it is temporary, migration-period only.
- [ ] **[Critical]** Is DNS cutover strategy defined? Options: reduce TTL before each wave, update DNS records during cutover window, use GSLB for gradual traffic shift. DNS propagation time affects application downtime.
- [ ] **[Critical]** Is firewall rule migration planned? New facility requires a new firewall rule set. Derive from current rules plus network flow analysis to catch undocumented flows.
- [ ] **[Recommended]** Is a network topology diagram created for the target facility before migration begins? Teams need to know VLAN assignments, subnet allocations, and routing before the first VM arrives.
- [ ] **[Recommended]** Is the migration network sized for the data volume? Calculate transfer duration: `Data Volume (TB) / Bandwidth (Gbps) / 0.8 utilization / 86400 = Days`. Multiple circuits or bonded links reduce duration linearly.
- [ ] **[Optional]** Is network monitoring deployed on migration circuits to track transfer progress and detect bottlenecks?

### Data Transfer Strategy

- [ ] **[Critical]** Is the total data volume calculated? Sum used storage across all VMs at all source sites. This is the minimum data that must transfer (provisioned storage may be larger but thin provisioning reduces actual transfer).
- [ ] **[Critical]** Is the data transfer method selected based on volume and available bandwidth? Options: dedicated circuits (steady-state replication), physical media transport (bulk seeding for large volumes), VPN over internet (small volumes only), or hybrid (physical seed + circuit for deltas).
- [ ] **[Critical]** Is the transfer duration estimated and validated against the program timeline? If 10 Gbps circuit transfers 8 PB in 100 days but the lease expires in 90 days, the plan doesn't work.
- [ ] **[Recommended]** Is physical media transport evaluated for initial bulk seeding? For multi-PB volumes, shipping encrypted disks can be faster than network transfer. Seed the bulk data physically, then use network circuits for ongoing deltas and final sync.
- [ ] **[Recommended]** Is bandwidth throttling configured to prevent migration traffic from impacting production at source sites during business hours?
- [ ] **[Optional]** Are data compression and deduplication ratios estimated? In-flight compression can reduce effective transfer volume by 30-50% depending on workload type.

### Migration Scope

- [ ] **[Critical]** Are ALL VMs in scope, including those already on the target hypervisor? In relocation, even VMs that don't need a hypervisor change must physically move to the new facility.
- [ ] **[Critical]** Is the migration scope broken into categories by effort type? (Hypervisor change + relocate, same-hypervisor relocate, re-deploy from image, decommission rather than move)
- [ ] **[Critical]** Are VMs that should NOT move identified? (Decommission candidates, test/temp VMs, infrastructure VMs that get rebuilt at the target like CVMs, vCenter, management tools)
- [ ] **[Recommended]** Is a two-phase approach evaluated? Phase 1: complete any hypervisor migration at the current site (simpler, no network complexity). Phase 2: relocate all VMs to the new facility (same-hypervisor move, simpler). This decouples two sources of risk.
- [ ] **[Recommended]** Are application groups maintained during relocation? All tiers of a multi-tier application should move in the same wave to avoid cross-site latency between tiers.

### Source Site Decommission

- [ ] **[Critical]** Is a source site decommission plan documented per site? (Final VM cutover, validation period, hardware power-down, data sanitization, hardware removal, lease termination, facility handback)
- [ ] **[Critical]** Is data sanitization performed before hardware leaves the facility? Follow NIST 800-88 or equivalent standard. Drives containing customer data must be sanitized or destroyed.
- [ ] **[Recommended]** Is the decommission timeline aligned with lease termination? Allow 2-4 weeks between last VM cutover and lease end for hardware removal logistics.
- [ ] **[Recommended]** Is hardware disposition planned? (Vendor buyback, resale, recycling, destruction) See `general/hardware-asset-disposition.md`.
- [ ] **[Optional]** Is a post-decommission verification performed? Confirm no orphaned resources (DNS records, monitoring entries, backup jobs, firewall rules) pointing to the decommissioned site.

## Why This Matters

Datacenter relocation is frequently underestimated because teams plan it as "migration plus a truck." In reality, relocation changes the fundamental assumptions of migration planning:

1. **Every VM is in scope.** In-place migration only moves VMs that need a hypervisor change. Relocation moves everything -- including VMs already on the target platform. A project that was "7,000 VMs to migrate" becomes "12,000 VMs to relocate" when the facility changes.

2. **Network is the bottleneck, not compute.** In-place migration is limited by target cluster capacity. Relocation is limited by the bandwidth between facilities. Multi-PB transfers over WAN circuits take months. Physical media transport is not a workaround -- it's a legitimate strategy.

3. **Facility procurement is the critical path.** Hardware can be ordered in weeks. Colo space with power, cooling, and connectivity takes months. If the program starts with "migrate VMs" instead of "secure target facility," it will stall when the VMs are ready to move but have nowhere to go.

4. **Re-IP is unavoidable.** In-place migration can preserve IP addresses. Relocation to a different facility means different subnets, different VLANs, different firewall contexts. Every VM needs DNS updates, potentially application configuration changes, and firewall rule updates. This is the hidden scope that blows timelines.

5. **Two-phase is almost always better.** Completing the hypervisor migration at the current site first (Phase 1) means the relocation (Phase 2) is a simpler same-hypervisor move. Trying to change hypervisor and relocate simultaneously doubles the variables and the risk of each cutover.

## Common Decisions (ADR Triggers)

- **Site consolidation** -- consolidate N source sites into M target facilities (M < N) or maintain 1:1 mapping; consolidation saves cost but concentrates risk and complicates network design
- **Two-phase vs single-phase** -- complete hypervisor migration in place first, then relocate (lower risk, longer total duration) vs. migrate and relocate simultaneously (faster, higher risk per cutover)
- **Data transfer method** -- dedicated circuits (predictable, ongoing cost), physical media (fast for bulk, one-time), or hybrid; choice depends on data volume, available bandwidth, and timeline
- **IP addressing strategy** -- full re-IP (clean, most work), L2 stretch (temporary, complex), or gradual re-IP during migration waves; affects application configuration scope
- **Source site decommission timing** -- decommission immediately after last wave vs. maintain for rollback period; lease cost vs. safety tradeoff

## See Also

- `patterns/hypervisor-migration.md` -- In-place hypervisor change (VMs stay in same facility)
- `patterns/migration-cutover.md` -- Cutover execution mechanics (applies to each wave)
- `general/facility-lifecycle.md` -- Facility lease management and lifecycle planning
- `general/colocation-constraints.md` -- Colo facility constraints and planning
- `general/hardware-asset-disposition.md` -- Hardware end-of-life, buyback, decommission
- `general/networking-physical.md` -- Physical network design at target facilities
- `general/multi-site-migration-sequencing.md` -- Wave sequencing across multiple sites
