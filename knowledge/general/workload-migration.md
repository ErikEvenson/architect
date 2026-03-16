# Workload Migration

## Scope

This file covers **cloud migration strategy and execution**: the 6 Rs framework, assessment tools, migration waves, cutover planning, and rollback procedures. For database-specific migration, see `general/database-migration.md`. For disaster recovery, see `general/disaster-recovery.md`.

## Checklist

- [ ] **[Critical]** Has each workload been categorized using the 6 Rs? (rehost, replatform, refactor, repurchase, retire, retain)
- [ ] **[Critical]** Is there a workload discovery and dependency mapping completed? (network flows, application dependencies, data flows)
- [ ] **[Critical]** Are migration waves defined based on dependencies and complexity? (start with low-risk, build confidence)
- [ ] **[Critical]** Is a cutover plan documented for each wave? (sequence, timing, validation steps, communication plan)
- [ ] **[Critical]** Is a rollback plan tested for each migrated workload? (revert procedure, data sync back, DNS failback)
- [ ] **[Recommended]** Are assessment tools deployed? (AWS MGN, Azure Migrate, Google Migrate for Compute Engine)
- [ ] **[Critical]** Is hybrid coexistence architecture designed? (connectivity, DNS split, data replication during migration period)
- [ ] **[Critical]** Are performance baselines captured before migration? (latency, throughput, error rates — for comparison post-migration)
- [ ] **[Critical]** Is there a database migration strategy per workload? (online vs offline, replication lag tolerance, schema changes)
- [ ] **[Critical]** Are compliance and data residency requirements mapped? (which data can move where, regulatory constraints)
- [ ] **[Recommended]** Is there a training plan for operations teams? (cloud-native operations differ from on-prem)
- [ ] **[Recommended]** Is cost modeling done for post-migration state? (avoid surprises — cloud costs are operational, not capital)

## Why This Matters

Migration failures are rarely technical — they are planning failures. Teams that skip dependency mapping discover critical connections during cutover. Teams without rollback plans are trapped in a broken state. Teams that migrate without performance baselines cannot tell whether degradation is a migration bug or pre-existing.

The biggest risk in migration is **extended hybrid coexistence**: running workloads in both environments for too long, doubling costs and operational complexity. A clear wave plan with firm cutover dates prevents migration from becoming a permanent state.

## The 6 Rs Framework

| Strategy | Description | Effort | Risk | When to Use |
|----------|-------------|--------|------|-------------|
| **Rehost** (Lift & Shift) | Move as-is to cloud VMs | Low | Low | Quick migration, limited cloud skills, legacy apps |
| **Replatform** (Lift & Reshape) | Minor modifications for cloud services | Medium | Low-Medium | Replace OS-managed databases with managed services, containerize |
| **Refactor** (Re-architect) | Redesign for cloud-native | High | Medium-High | Strategic apps, need elasticity, long-term investment |
| **Repurchase** (Drop & Shop) | Replace with SaaS | Medium | Medium | COTS software with SaaS equivalent (CRM, ITSM, email) |
| **Retire** | Decommission | Low | Low | Unused or redundant applications |
| **Retain** | Keep on-premises | None | Low | Regulatory constraints, near-EOL, too complex to move now |

### Decision Flow

1. **Is the app still needed?** No → **Retire**
2. **Is there a SaaS replacement that fits?** Yes → **Repurchase**
3. **Must it stay on-prem?** (regulation, hardware dependency, EOL soon) Yes → **Retain**
4. **Is it strategic and worth investing in?** Yes → **Refactor**
5. **Can it benefit from managed services with minor changes?** Yes → **Replatform**
6. **Default** → **Rehost** (get to cloud fast, optimize later)

## Migration Waves

### Wave Planning Principles

- **Wave 0 — Foundation:** Landing zone, networking, security, identity, CI/CD (no workloads)
- **Wave 1 — Pilot:** 1-3 low-risk, low-dependency applications (build confidence, validate process)
- **Wave 2-N — Execution:** Group workloads by dependency clusters, migrate together
- **Final Wave — Cleanup:** Decommission source systems, terminate hybrid connectivity if no longer needed

### Dependency Mapping

| Approach | Tool | What It Discovers |
|----------|------|-------------------|
| **Agent-based** | AWS Application Discovery Agent, Azure Migrate Appliance | Processes, connections, performance data |
| **Agentless** | AWS Agentless Discovery, Azure Migrate (agentless), vCenter-based | VM inventory, basic dependencies |
| **Network flow analysis** | VPC Flow Logs, NSG Flow Logs, NetFlow | Communication patterns between workloads |
| **Application interviews** | Architecture reviews, team interviews | Business logic dependencies, data flows |

### Wave Grouping Rules

- Applications that communicate heavily should migrate **together** (avoid cross-environment latency)
- Shared databases migrate **after** all dependent applications, or use replication during transition
- External-facing applications need **DNS cutover planning**
- Applications with compliance requirements may need **dedicated waves** with extra validation

## Assessment Tools

| Provider | Tool | Capabilities |
|----------|------|-------------|
| **AWS** | Migration Hub + Application Discovery Service | Inventory, dependency mapping, migration tracking |
| **AWS** | Migration Evaluator (formerly TSO Logic) | Cost modeling, right-sizing recommendations |
| **AWS** | MGN (Application Migration Service) | Continuous replication, non-disruptive testing, cutover automation |
| **Azure** | Azure Migrate | Discovery, assessment, dependency visualization, migration execution |
| **Azure** | Database Migration Service (DMS) | Database migration with minimal downtime |
| **GCP** | Migrate for Compute Engine | VM migration with streaming replication |
| **GCP** | Migrate for Anthos | Container-based migration, fit assessment |
| **Independent** | Cloudamize, RISC Networks, Turbonomic | Multi-cloud assessment, cost modeling |

## VM Migration Approaches

### Agent-Based Migration (AWS MGN, Azure Migrate)

1. Install replication agent on source server
2. Continuous block-level replication to cloud (staging area)
3. Run test instances from replicated data (non-disruptive)
4. Perform cutover: launch production instance, update DNS/routing
5. Rollback: revert DNS, source server still running

**Pros:** Minimal downtime (minutes), continuous sync, test before cutover
**Cons:** Agent installation required, network bandwidth for replication

### Agentless Migration (VMware-based)

1. Connect migration tool to vCenter/ESXi
2. Snapshot-based replication to cloud
3. Periodic sync of changed blocks
4. Cutover: final sync, launch cloud instance

**Pros:** No agent installation, good for VM estates managed by vCenter
**Cons:** Requires vCenter access, coarser-grained replication

## Database Migration

| Scenario | Approach | Downtime | Tools |
|----------|----------|----------|-------|
| **Homogeneous** (same engine) | Native replication | Minutes | pg_dump/restore, mysqldump, Oracle Data Guard, AWS DMS |
| **Heterogeneous** (engine change) | Schema conversion + data migration | Hours | AWS SCT + DMS, Azure DMS, ora2pg, pgloader |
| **Large databases** (>1 TB) | Continuous replication with cutover | Minutes | AWS DMS with CDC, Azure DMS online mode, GoldenGate |
| **Minimal downtime required** | Change data capture (CDC) | Seconds-Minutes | Debezium, AWS DMS CDC, Azure DMS online, GCP Datastream |

### Database Migration Steps

1. **Assess** — Schema compatibility, data types, stored procedures, triggers
2. **Convert schema** — If changing engines, convert and test schema first
3. **Full load** — Bulk transfer of existing data
4. **CDC / Ongoing replication** — Capture and replicate changes during migration window
5. **Validate** — Row counts, checksums, application-level validation
6. **Cutover** — Switch application connection strings, stop replication
7. **Monitor** — Watch for errors, performance degradation, data inconsistencies

## Application Modernization Paths

```
On-Premises VM
    │
    ├── Rehost ──→ Cloud VM (IaaS)
    │                  │
    │                  ├── Containerize ──→ Containers (ECS/AKS/GKE)
    │                  │                        │
    │                  │                        └── Decompose ──→ Microservices
    │                  │
    │                  └── Replatform ──→ Managed Services (RDS, managed K8s)
    │
    └── Refactor ──→ Cloud-Native (serverless, event-driven, managed everything)
```

### Modernization Sequence (Recommended)

1. **Rehost first** — Get to cloud, reduce data center costs
2. **Containerize** — Package in containers for portability, improve density
3. **Adopt managed services** — Replace self-managed databases, caches, queues
4. **Decompose if justified** — Break monolith only when team structure and velocity demand it

**Do not refactor during migration.** Migration and modernization are separate projects. Combining them doubles risk and timeline.

## Hybrid Coexistence Architecture

During migration, workloads exist in both environments. Design for this explicitly:

### Connectivity

| Pattern | Technology | Latency | Cost |
|---------|-----------|---------|------|
| **VPN** | IPSec site-to-site | 10-50ms | Low |
| **Direct connection** | AWS Direct Connect, Azure ExpressRoute, GCP Interconnect | 1-5ms | High (but required for large data volumes) |
| **Transit architecture** | Transit Gateway, Azure Virtual WAN, GCP Network Connectivity Center | Varies | Medium-High |

### DNS During Migration

- Use **split-horizon DNS** or **weighted routing** to gradually shift traffic
- Keep TTLs low (60-300 seconds) during cutover windows
- Validate DNS propagation before decommissioning source systems

### Data Replication

- **Database replication** for shared data stores (source → cloud replica)
- **File sync** for shared storage (AWS DataSync, Azure File Sync, rsync)
- **Message bridging** for event-driven systems (replicate messages between on-prem and cloud brokers)

## Cutover Planning

### Cutover Checklist

1. **Pre-cutover validation** — Verify all replication is current, test instances pass smoke tests
2. **Communication** — Notify stakeholders of maintenance window
3. **Freeze changes** — No deployments or data changes in source during cutover
4. **Final sync** — Last replication cycle, verify data consistency
5. **Switch traffic** — Update DNS, load balancers, or connection strings
6. **Validate** — Run automated smoke tests, verify monitoring dashboards
7. **Monitor** — Watch error rates, latency, and throughput for 24-48 hours
8. **Declare success** — Or execute rollback within the rollback window

### Rollback Planning

- **Define rollback window** — How long after cutover can you still roll back? (typically 24-72 hours)
- **Keep source systems running** — Do not decommission until rollback window closes
- **Data sync back** — If cloud writes occurred, plan how to sync data back to source
- **DNS revert** — Low TTLs make DNS rollback fast; high TTLs trap you
- **Test rollback** — Practice the rollback procedure at least once before the real cutover

## Common Decisions (ADR Triggers)

- **Migration strategy per workload** — which R for each application, justification
- **Wave composition** — how to group workloads, wave sequence, timeline
- **Connectivity model** — VPN vs Direct Connect, bandwidth requirements
- **Database migration approach** — homogeneous vs heterogeneous, downtime tolerance
- **Modernization timing** — during migration vs post-migration (recommend post)
- **Cutover model** — big-bang vs phased per wave, maintenance window vs zero-downtime
- **Rollback criteria** — what constitutes a failed migration, who decides to roll back

## See Also

- `general/database-migration.md` — Detailed database migration patterns
- `general/disaster-recovery.md` — DR planning for migrated workloads
- `general/networking.md` — Cloud networking and connectivity patterns
- `general/cost.md` — Cost modeling for cloud vs on-premises
