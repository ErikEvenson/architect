# Multi-Site Migration Sequencing

## Scope

This file covers **sequencing and coordination of migrations across multiple physical sites**: pilot selection, wave ordering, staffing models, inter-site dependencies, and go/no-go governance. For single-site migration mechanics (6 Rs, cutover, rollback), see `general/workload-migration.md`. For disaster recovery pairing, see `general/disaster-recovery.md`.

## Checklist

- [ ] **[Critical]** Has a pilot site been selected based on low risk, representative workloads, and cooperative local staff?
- [ ] **[Critical]** Are inter-site dependencies mapped? (DR pairs, AD/LDAP replication, shared databases, cross-site backup targets)
- [ ] **[Critical]** Are go/no-go criteria defined and agreed upon between migration waves?
- [ ] **[Critical]** Is a rollback plan defined at the appropriate scope for each wave? (per-VM, per-application, per-site)
- [ ] **[Critical]** Is there a site readiness checklist that must be completed before each site's migration begins?
- [ ] **[Recommended]** Is urgency-based sequencing factored in? (lease expiry, licensing deadlines, end-of-support dates, contract renewals)
- [ ] **[Recommended]** Is the staffing model decided? (dedicated team per site, traveling team, hub-and-spoke)
- [ ] **[Recommended]** Are hardware procurement lead times mapped per site and factored into the schedule?
- [ ] **[Recommended]** Is a lessons-learned feedback loop established between waves? (retrospective after each wave, process updates before next)
- [ ] **[Recommended]** Are regional constraints accounted for? (timezone coverage, local team availability, language, regulatory differences)
- [ ] **[Recommended]** Is the parallel vs sequential execution model decided based on staff capacity and risk tolerance?
- [ ] **[Optional]** Are site-local stakeholders identified and briefed on their responsibilities during migration?
- [ ] **[Optional]** Is there a shared dashboard or tracking tool for cross-site migration status?

## Why This Matters

Multi-site migrations fail when treated as independent single-site projects. Sites share dependencies — DR replication, Active Directory forests, centralized backup, shared WAN links — and migrating one site without understanding its relationship to others causes outages at sites that were not even being migrated. Sequencing mistakes compound: a botched early wave erodes organizational trust and makes later waves politically harder to execute.

The pilot site sets the tone for the entire program. Choosing a site that is too complex, too politically charged, or staffed by a team that is resistant to change turns the pilot into a cautionary tale rather than a confidence builder. Choosing a site that is too simple teaches nothing applicable to the harder sites that follow.

Hardware procurement is the most common schedule-breaker in on-premises migrations. A 12-week lead time for server delivery means the migration schedule is set by the supply chain, not the project plan. Sites that require new hardware must be identified early enough for procurement to complete before the migration window opens.

## Pilot Site Selection

### Selection Criteria

| Factor | Ideal Pilot Characteristics |
|--------|---------------------------|
| **Workload complexity** | Small number of workloads (10-50 VMs), representative of the broader estate |
| **Business risk** | Non-revenue-critical applications, tolerant of brief disruptions |
| **Local team** | Cooperative, technically capable, willing to participate actively |
| **Dependencies** | Minimal cross-site dependencies, no shared databases with other sites |
| **Infrastructure age** | Old enough to benefit clearly from migration, not so old that tooling fails |
| **Size** | Small enough to complete in one wave, large enough to exercise the full process |
| **Geography** | Same timezone or overlapping hours as the core migration team |

### Pilot Anti-Patterns

- **Headquarters as pilot** — Too much political pressure, too many stakeholders, too many critical workloads
- **Smallest site as pilot** — If it has only 3 VMs, the pilot teaches nothing about wave management or dependency handling
- **Most troubled site as pilot** — Fixing years of technical debt during a migration pilot guarantees failure
- **Remote site with no local staff** — Cannot validate the remote execution model until the process itself is proven

## Sequencing Strategies

### Urgency-Based Sequencing

External deadlines override all other sequencing preferences. Map every site against hard deadlines:

| Urgency Driver | Typical Lead Time | Impact of Missing Deadline |
|---------------|-------------------|---------------------------|
| **Data center lease expiry** | 6-18 months notice | Forced emergency move or expensive lease extension |
| **Hardware end-of-support** | Known years in advance | No vendor support, no replacement parts, compliance risk |
| **Software licensing deadlines** | Annual renewal cycles | Unexpected license costs if workloads are still running at renewal |
| **Regulatory compliance dates** | Varies by jurisdiction | Fines, audit failures, operating restrictions |
| **Vendor contract renewals** | Annual or multi-year | Renewal locks in costs for workloads that should have been migrated |

**Rule:** Sites with immovable deadlines within the next 6 months go first, regardless of other factors.

### Size-Based Sequencing

After urgency constraints are satisfied, sequence from small to large:

1. **Small sites (< 50 VMs)** — Build confidence, refine runbooks, train the team
2. **Medium sites (50-200 VMs)** — Test wave management, parallel execution, dependency handling
3. **Large sites (200+ VMs)** — Apply proven process with full staffing, longest cutover windows

This approach builds organizational muscle memory. Each wave is harder than the last, but the team is also more experienced.

### Regional Considerations

| Factor | Impact on Sequencing |
|--------|---------------------|
| **Timezone** | Migration cutovers during off-hours require either local staff or travel; cluster sites by timezone to minimize travel |
| **Local team availability** | Sites with strong local teams can run more independently; sites without local expertise need core team presence |
| **Language** | Documentation, communication plans, and training materials may need translation; factor this into preparation time |
| **Local regulations** | Some jurisdictions require data residency, notification periods, or union consultation before infrastructure changes |
| **Network connectivity** | Sites with poor WAN links take longer for data replication; schedule extra time or ship data physically |

## Execution Models

### Parallel vs Sequential

| Model | Pros | Cons | When to Use |
|-------|------|------|-------------|
| **Strictly sequential** | Maximum learning between waves, lowest staff requirement, simplest coordination | Slowest overall timeline | Early waves, small teams, first multi-site migration |
| **Parallel (2-3 sites)** | Faster overall timeline, keeps momentum | Requires more staff, harder to incorporate lessons learned, higher coordination overhead | Mid-program after process is proven, adequate staffing |
| **Fully parallel (all sites)** | Fastest possible timeline | Extremely high risk, no feedback loop, massive staffing requirement | Almost never appropriate; only under extreme deadline pressure with experienced team |

**Recommended progression:** Start sequential for waves 1-2, move to limited parallelism (2 sites) for waves 3-5, scale up only if the team and process support it.

### Staffing Models

| Model | Description | Pros | Cons |
|-------|-------------|------|------|
| **Dedicated team per site** | Each site gets its own migration team for the duration | Deep site knowledge, single point of accountability | Expensive, inconsistent process across sites, no knowledge sharing |
| **Traveling team** | One core team moves from site to site | Consistent process, deep expertise, strong feedback loop | Travel fatigue, single point of failure, sequential only |
| **Hub-and-spoke** | Central architecture/planning team + local execution teams per site | Scales to parallel execution, consistent standards, local knowledge | Requires strong local teams, coordination overhead, potential for drift |

**Hub-and-spoke is the most common model for large programs.** The central team owns the runbooks, tooling, and standards. Local teams execute with central oversight. The central team travels for cutovers and complex phases.

## Hardware Procurement Planning

For on-premises target environments, hardware procurement is on the critical path:

| Phase | Duration | Activities |
|-------|----------|------------|
| **Specification** | 2-4 weeks | Capacity planning, vendor selection, quote requests |
| **Procurement** | 1-2 weeks | Purchase orders, contract negotiation, payment |
| **Manufacturing/shipping** | 4-16 weeks | Vendor build time, shipping, customs (international) |
| **Receiving and racking** | 1-2 weeks | Physical installation, cabling, power verification |
| **Burn-in and base config** | 1-2 weeks | Firmware updates, BIOS configuration, OS installation, network configuration |

**Total: 9-26 weeks from specification to ready-for-workloads.** Start procurement for each site at least 6 months before its planned migration window. For international shipments, add time for customs and import regulations.

## Inter-Site Dependencies

### Common Cross-Site Dependencies

| Dependency | Migration Impact | Mitigation |
|-----------|-----------------|------------|
| **DR pairs** | Migrating the primary site without the DR site breaks disaster recovery | Migrate DR pairs together, or establish temporary DR at the target before migrating the primary |
| **Active Directory replication** | AD sites and services must reflect the new topology | Add new AD sites before migration, adjust replication topology, update DNS forwarders |
| **Centralized backup** | Backup targets at one site may serve other sites | Establish new backup targets at the destination before migrating backup sources |
| **Shared databases** | Applications at site A may depend on databases at site B | Map all cross-site data flows; co-migrate tightly coupled applications or implement replication |
| **WAN-dependent applications** | Some applications are designed for LAN latency and break over WAN | Identify latency-sensitive cross-site communication; co-locate or re-architect |
| **Centralized services** | DHCP, DNS, NTP, SIEM, log aggregation, certificate authorities | Deploy local instances at the target before migrating workloads that depend on them |

### Dependency Mapping Process

1. **Inventory cross-site network flows** — Firewall logs, NetFlow data, application documentation
2. **Identify shared infrastructure services** — DNS, AD, backup, monitoring, certificate services
3. **Map DR relationships** — Which sites are paired, what replication technology, what RPO/RTO
4. **Interview application owners** — Cross-site dependencies are often undocumented
5. **Build a dependency matrix** — Sites as rows and columns, dependencies in cells, migration sequence constraints as output

## Feedback Loop Between Waves

### Post-Wave Retrospective (Mandatory)

After each wave, before the next wave begins:

1. **What worked** — Identify process steps that went smoothly, tools that performed well
2. **What failed** — Document every issue, root cause, time to resolve
3. **What was missing** — Checklist items that should have been there but were not
4. **Runbook updates** — Incorporate lessons into the runbook before the next wave uses it
5. **Tooling updates** — Fix scripts, automation, monitoring gaps discovered during the wave
6. **Timeline recalibration** — Adjust estimates for remaining waves based on actual durations

### Metrics to Track Across Waves

| Metric | Purpose |
|--------|---------|
| **Cutover duration** (planned vs actual) | Are estimates improving? |
| **Rollback count** | Are rollbacks decreasing wave over wave? |
| **Unplanned issues per wave** | Is the team catching problems earlier? |
| **Time to resolve unplanned issues** | Is the team getting faster at recovery? |
| **Stakeholder satisfaction** | Are site teams confident in the process? |
| **Post-migration incident rate** | Are migrated workloads stable? (measure for 2-4 weeks post-cutover) |

## Go/No-Go Governance

### Go/No-Go Criteria Between Waves

| Category | Go Criteria | No-Go Trigger |
|----------|------------|---------------|
| **Previous wave stability** | All workloads from previous wave stable for defined soak period (typically 2-4 weeks) | Active incidents from previous wave unresolved |
| **Site readiness** | Site readiness checklist 100% complete | Hardware not staged, network not prepared, or local team not briefed |
| **Staffing** | Migration team available and not fatigued from back-to-back waves | Key personnel unavailable, team burnout indicators |
| **Stakeholder approval** | Site owner and business sponsor have signed off | Unresolved objections from site stakeholders |
| **Rollback readiness** | Rollback plan reviewed, rollback resources available | No tested rollback path |
| **External factors** | No conflicting change freezes, business events, or regulatory deadlines | Conflicts with year-end freeze, audit period, or peak business season |

### Decision Authority

Define clearly before the program begins:

- **Who can declare Go** — Program manager with concurrence from site owner and technical lead
- **Who can declare No-Go** — Any of the above, plus security, compliance, or infrastructure leads
- **Who can override No-Go** — Executive sponsor only, with documented risk acceptance
- **Escalation path** — If Go/No-Go decision is disputed, who arbitrates and on what timeline

## Site Readiness Checklist

Before any workload migration begins at a site, every item must be confirmed:

- [ ] Target hardware staged, racked, cabled, powered, and burn-in complete
- [ ] Target network configured (VLANs, firewall rules, routing, WAN connectivity verified)
- [ ] Target infrastructure services operational (DNS, DHCP, NTP, AD site configured)
- [ ] Monitoring and alerting configured for target environment
- [ ] Backup infrastructure at target site operational and tested
- [ ] Local team briefed on migration plan, schedule, and their responsibilities
- [ ] Local team trained on new environment operations (if different from source)
- [ ] Communication plan distributed to all affected users at the site
- [ ] Maintenance windows approved and communicated
- [ ] Rollback plan reviewed with local team and tested where feasible
- [ ] Escalation contacts confirmed and available for the cutover window
- [ ] Source environment performance baselines captured for post-migration comparison

## Rollback Scope

### Rollback Granularity Options

| Scope | Description | Complexity | When Appropriate |
|-------|-------------|-----------|-----------------|
| **Per-VM** | Revert a single VM to source | Low | Individual VM fails validation; all others are fine |
| **Per-application** | Revert all VMs/components of one application | Medium | Application-level failure (e.g., multi-tier app, one tier has issues) |
| **Per-wave** | Revert all workloads in the current migration wave | High | Systemic issue affecting multiple workloads in the wave |
| **Per-site** | Revert the entire site migration | Very High | Fundamental infrastructure problem at the target site (network, storage, power) |

### Rollback Design Principles

- **Decide rollback scope before cutover** — Do not decide during an incident
- **Keep source systems running** through the soak period — Do not decommission until rollback window closes
- **Data sync-back is the hardest problem** — If the migrated workload accepted writes, rolling back means those writes must be replayed or reconciled at the source
- **DNS TTLs must be low** during the rollback window — High TTLs make traffic redirection slow
- **Test the rollback procedure** at least once per execution model (first VM rollback, first application rollback, first wave rollback)
- **Define the rollback decision authority** — Same person who declares Go should have authority to declare rollback
- **Time-box the rollback window** — Typically 24-72 hours post-cutover; after that, fix-forward is the only option

## Common Decisions (ADR Triggers)

- **Pilot site selection** — which site and why, what makes it representative without being risky
- **Site sequencing rationale** — urgency vs size vs regional grouping, trade-offs documented
- **Parallel vs sequential execution** — how many sites in parallel, what triggers scaling up
- **Staffing model** — dedicated vs traveling vs hub-and-spoke, cost and risk trade-offs
- **Inter-site dependency resolution** — how DR pairs, AD replication, and shared services are handled during migration
- **Go/no-go governance** — who has authority, what criteria are mandatory vs advisory
- **Rollback scope per wave** — at what granularity rollback is planned, how data sync-back works
- **Feedback loop cadence** — retrospective format, mandatory vs optional attendees, how runbook updates are enforced

## See Also

- `general/workload-migration.md` — Single-site migration mechanics, 6 Rs, cutover planning
- `general/disaster-recovery.md` — DR pairing and replication strategies
- `general/hardware-sizing.md` — Capacity planning and hardware specification
- `general/networking-physical.md` — Physical network design and WAN connectivity
- `general/governance.md` — Change management and approval processes
