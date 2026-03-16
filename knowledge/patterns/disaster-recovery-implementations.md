# Disaster Recovery Implementations

## Overview

This file covers **implementation details** for the four DR strategies, including step-by-step failover procedures, cost comparisons, and testing approaches. For general DR planning concepts (RPO/RTO definitions, DR planning checklist), see `general/disaster-recovery.md`.

## Checklist

- [ ] **[Critical]** Is the DR strategy matched to business RTO/RPO requirements? (do not over-engineer or under-engineer)
- [ ] **[Critical]** Is the cost of the DR strategy understood and budgeted? (DR infrastructure is insurance — size it to the risk)
- [ ] **[Critical]** Are failover procedures documented as runbooks? (step-by-step, no ambiguity, tested)
- [ ] **[Critical]** Is DR failover automated or semi-automated? (manual failover under pressure leads to mistakes)
- [ ] **[Critical]** Is DR tested on a regular schedule? (quarterly minimum, annually is insufficient)
- [ ] **[Critical]** Is data replication monitored for lag? (replication lag = data loss in a failover)
- [ ] **[Recommended]** Are DNS TTLs configured for fast failover? (low TTLs in production, verify propagation)
- [ ] **[Critical]** Is the DR environment kept in sync with production? (IaC drift detection, same AMIs/images, same configurations)
- [ ] **[Critical]** Is there a clear decision authority for declaring a disaster? (who can trigger failover, escalation path)
- [ ] **[Recommended]** Is failback (returning to primary) planned and tested? (failback is often harder than failover)
- [ ] **[Recommended]** Are third-party dependencies included in DR planning? (SaaS providers, payment processors, DNS providers)
- [ ] **[Recommended]** Is there a communication plan for DR events? (status page, customer notification, internal escalation)

## Why This Matters

Most organizations have a DR plan. Few have tested it. Untested DR plans fail when needed — during the most stressful moment your team will face. The difference between a 4-hour outage and a 4-day outage is whether failover was practiced.

DR strategy selection is fundamentally a **business decision**, not a technical one. The question is: "How much does downtime cost per hour, and how much are we willing to spend to reduce it?" A $10M/year business losing $50K/hour in an outage justifies Warm Standby. A $100M/year business losing $500K/hour justifies Active-Active.

## Strategy Comparison

| Strategy | RTO | RPO | Monthly Cost (% of prod) | Complexity |
|----------|-----|-----|--------------------------|------------|
| **Backup & Restore** | 12-24 hours | 1-24 hours | 5-10% | Low |
| **Pilot Light** | 1-4 hours | Minutes-1 hour | 10-20% | Medium |
| **Warm Standby** | 15-60 minutes | Seconds-Minutes | 30-50% | Medium-High |
| **Active-Active** | Near-zero | Near-zero | 80-100%+ | High |

---

## 1. Backup & Restore

### Architecture

```
Primary Region                          DR Region
┌───────────────────┐                  ┌───────────────────┐
│  App Servers       │                  │  (nothing running) │
│  Databases         │                  │                     │
│  Storage           │                  │  Backups stored:    │
│                    │ ───backups───▶   │  - DB snapshots     │
│                    │                  │  - AMIs/images      │
│                    │                  │  - IaC templates    │
│                    │                  │  - Config backups   │
└───────────────────┘                  └───────────────────┘
```

### How It Works

- Automated backups of databases, storage, and configurations replicated to DR region
- Infrastructure-as-code templates stored and versioned (can recreate entire environment)
- No compute running in DR region during normal operations
- On disaster declaration: provision infrastructure from IaC, restore data from backups

### Implementation Steps

1. **Configure cross-region backup replication**
   - AWS: RDS automated backups with cross-region replication, S3 cross-region replication
   - Azure: Geo-redundant storage (GRS), Azure Backup with cross-region restore
   - GCP: Cloud SQL cross-region replicas (for backup), multi-region Cloud Storage

2. **Maintain IaC templates for DR region**
   - Same Terraform/CloudFormation with region parameter
   - Test `terraform plan` against DR region monthly (verify template validity)
   - Store AMI/image copies in DR region

3. **Document backup schedule and retention**
   - Database: Daily full, hourly incremental (minimum)
   - Application artifacts: Replicate on every release
   - Configuration: Replicate on every change

### Failover Procedure

| Step | Action | Expected Duration |
|------|--------|-------------------|
| 1 | Declare disaster, assemble incident team | 15-30 min |
| 2 | Run IaC to provision DR infrastructure | 30-60 min |
| 3 | Restore databases from latest backup | 1-4 hours (size-dependent) |
| 4 | Deploy application code | 15-30 min |
| 5 | Validate with smoke tests | 15-30 min |
| 6 | Update DNS to point to DR region | 5-15 min (depends on TTL) |
| 7 | Monitor and validate | Ongoing |
| **Total** | | **2-6 hours** (best case) |

### Testing Strategy

- **Monthly:** Verify backups can be restored (restore to a test database, validate data)
- **Quarterly:** Full DR drill — provision infrastructure in DR region, restore data, run smoke tests, tear down
- **Verify:** Backup completeness (are all databases included?), restore time (how long does the largest database take?), IaC validity (does `terraform apply` succeed?)

### When to Use

- Non-revenue-generating internal applications
- Development/staging environments
- Applications tolerating hours of downtime
- Budget-constrained environments

---

## 2. Pilot Light

### Architecture

```
Primary Region                          DR Region
┌───────────────────┐                  ┌───────────────────┐
│  App Servers (N)   │                  │  (no app servers)  │
│  Database (active) │ ──replication──▶ │  Database (replica) │
│  Cache (active)    │                  │  (no cache)         │
│  Load Balancer     │                  │  (no LB)            │
└───────────────────┘                  └───────────────────┘
```

### How It Works

- Core data layer runs in DR region (database replicas with continuous replication)
- Compute, caching, and networking layers are **not** provisioned until failover
- On disaster declaration: provision compute and networking from IaC, promote database replica, route traffic
- "Pilot light" metaphor: the flame is kept burning (data replication), but the furnace (compute) is off

### Implementation Steps

1. **Set up continuous data replication**
   - AWS: RDS cross-region read replica, Aurora Global Database, DynamoDB Global Tables
   - Azure: Azure SQL Geo-Replication, Cosmos DB multi-region
   - GCP: Cloud SQL cross-region replica, Cloud Spanner (multi-region by design)

2. **Pre-stage compute artifacts in DR region**
   - AMIs/container images replicated to DR region
   - Launch templates / instance configurations ready
   - Auto-scaling groups defined (min=0 in normal state)

3. **Pre-configure networking**
   - VPC/VNet created in DR region
   - Security groups, NACLs, and firewall rules configured
   - Load balancer defined but no targets registered

### Failover Procedure

| Step | Action | Expected Duration |
|------|--------|-------------------|
| 1 | Declare disaster, assemble incident team | 15-30 min |
| 2 | Promote database replica to primary | 5-15 min |
| 3 | Scale up compute (auto-scaling min from 0 to N) | 5-15 min |
| 4 | Provision cache and warm it | 10-30 min |
| 5 | Register targets with load balancer | 2-5 min |
| 6 | Run smoke tests | 10-15 min |
| 7 | Update DNS / Route 53 health check failover | 5-10 min |
| **Total** | | **1-2 hours** |

### Testing Strategy

- **Continuously:** Monitor replication lag (alert if lag > threshold)
- **Monthly:** Promote DR replica to standalone (test), validate data integrity, terminate test instance
- **Quarterly:** Full failover drill — promote replica, spin up compute, route traffic, validate, fail back
- **Key metric:** Time from declaration to serving traffic

### When to Use

- Applications requiring 1-4 hour RTO
- Moderate RPO tolerance (minutes, based on replication lag)
- Desire to minimize DR cost while maintaining faster recovery than Backup & Restore
- Databases that support cross-region replication

---

## 3. Warm Standby

### Architecture

```
Primary Region                          DR Region
┌───────────────────┐                  ┌───────────────────┐
│  App Servers (N)   │                  │  App Servers (N/4)  │
│  Database (active) │ ──replication──▶ │  Database (replica) │
│  Cache (full)      │                  │  Cache (reduced)    │
│  Load Balancer     │                  │  Load Balancer      │
└───────────────────┘                  └───────────────────┘
       ▲                                       ▲
       │                                       │
  100% traffic                          0% traffic (standby)
```

### How It Works

- DR region runs a **scaled-down copy** of the entire production stack
- All layers are live: compute, database, cache, load balancing, networking
- DR environment is continuously deployed alongside production (same CI/CD pipeline)
- On failover: scale up DR compute, promote database, shift traffic
- Significantly faster failover because everything is already running

### Implementation Steps

1. **Deploy full stack in DR region at reduced scale**
   - App servers: 25-50% of production capacity
   - Database: Read replica with same engine/version
   - Cache: Smaller instance, same configuration
   - Load balancer: Active, health checks running

2. **Include DR region in CI/CD pipeline**
   - Every production deployment deploys to DR simultaneously
   - DR environment runs same application version as production
   - Configuration drift detection between regions

3. **Route synthetic traffic to DR**
   - Run synthetic monitors against DR environment
   - Validates that DR is functional, not just provisioned
   - Catches configuration drift, expired certificates, stale credentials

### Failover Procedure

| Step | Action | Expected Duration |
|------|--------|-------------------|
| 1 | Declare disaster (or automated health check triggers) | 0-15 min |
| 2 | Promote database replica to primary | 2-5 min |
| 3 | Scale up DR compute to production capacity | 5-15 min |
| 4 | Shift traffic (Route 53 failover, Global Accelerator, Traffic Manager) | 2-5 min |
| 5 | Validate with automated tests | 5-10 min |
| **Total** | | **15-45 minutes** |

### Testing Strategy

- **Continuously:** Synthetic monitors validating DR environment functionality
- **Monthly:** Scale-up test — increase DR capacity to production level, run load test, scale back down
- **Quarterly:** Full traffic shift — route production traffic to DR for 1-4 hours, monitor performance
- **Key insight:** Warm Standby enables **routine** failover testing because the environment is always live

### When to Use

- Applications requiring <1 hour RTO
- Near-zero RPO (seconds of replication lag)
- Business-critical applications justifying 30-50% additional infrastructure cost
- Teams ready to maintain two live environments

---

## 4. Active-Active (Multi-Region)

### Architecture

```
Region A                                Region B
┌───────────────────┐                  ┌───────────────────┐
│  App Servers (N)   │                  │  App Servers (N)   │
│  Database (R/W)    │ ◀──sync──▶      │  Database (R/W)    │
│  Cache (full)      │                  │  Cache (full)      │
│  Load Balancer     │                  │  Load Balancer     │
└───────────────────┘                  └───────────────────┘
       ▲                                       ▲
       │                                       │
  ~50% traffic ◀── Global Load Balancer ──▶ ~50% traffic
  (or geo-routed)    (Route 53, CloudFront,   (or geo-routed)
                      Global Accelerator,
                      Traffic Manager,
                      Cloud Load Balancing)
```

### How It Works

- Both (or all) regions serve production traffic simultaneously
- Data is replicated bidirectionally (multi-master) or via conflict-free data structures
- Global load balancing distributes traffic by geography, latency, or weight
- On region failure: global load balancer removes unhealthy region; remaining region(s) absorb traffic
- **No failover procedure** — traffic automatically flows to healthy regions

### Implementation Steps

1. **Choose a multi-region data strategy**

   | Approach | Technology | Conflict Handling |
   |----------|-----------|-------------------|
   | **Multi-master database** | Aurora Global (write forwarding), Cosmos DB, Cloud Spanner, CockroachDB | Last-writer-wins or custom resolution |
   | **Event sourcing** | Kafka MirrorMaker, EventBridge cross-region | Ordered event streams, idempotent consumers |
   | **CQRS with regional writes** | Write to local region, replicate reads globally | No conflicts (each record has a home region) |

2. **Deploy identical stacks in all regions**
   - Same IaC, same CI/CD pipeline, same configuration
   - All regions are production — no "secondary" region
   - Capacity planning must account for one region absorbing all traffic

3. **Configure global traffic management**
   - AWS: Route 53 latency/geolocation routing + Global Accelerator
   - Azure: Traffic Manager + Front Door
   - GCP: Cloud Load Balancing (global, anycast)

4. **Handle data conflicts**
   - Design for **eventual consistency** (users may see stale data briefly)
   - Use **conflict-free replicated data types (CRDTs)** where possible
   - Implement **last-writer-wins** with vector clocks for simple cases
   - Route writes for the same entity to the **same region** (conflict avoidance > conflict resolution)

### Failover Procedure

| Step | Action | Expected Duration |
|------|--------|-------------------|
| 1 | Health check detects region failure | 10-30 seconds |
| 2 | Global load balancer stops routing to failed region | 10-60 seconds |
| 3 | Healthy region(s) absorb increased traffic | Automatic (auto-scaling) |
| 4 | Operations team is alerted, investigates | Ongoing |
| **Total** | | **30-90 seconds** (automated) |

### Testing Strategy

- **Continuously:** Global load balancer health checks validating both regions
- **Weekly:** Shift 100% traffic to one region for 1 hour (validates single-region capacity)
- **Monthly:** Simulate region failure (block health checks for one region), validate automatic failover
- **Quarterly:** Full chaos exercise — fail a region, fail it back, verify data consistency
- **Critical test:** After failover, verify no data was lost and no conflicts corrupted data

### When to Use

- Near-zero RTO/RPO is a hard business requirement
- Global user base benefiting from latency reduction via geographic routing
- Revenue loss during downtime exceeds the cost of dual infrastructure
- Team has maturity to handle distributed data consistency

---

## Cost Comparison (Illustrative)

Based on a production environment costing $10,000/month:

| Strategy | DR Monthly Cost | Annual DR Cost | Effective RTO |
|----------|----------------|----------------|---------------|
| **Backup & Restore** | $500-1,000 | $6,000-12,000 | 4-24 hours |
| **Pilot Light** | $1,000-2,000 | $12,000-24,000 | 1-4 hours |
| **Warm Standby** | $3,000-5,000 | $36,000-60,000 | 15-60 min |
| **Active-Active** | $8,000-12,000 | $96,000-144,000 | <2 min |

**The decision framework:** Compare DR cost against hourly cost of downtime. If an outage costs $10,000/hour and Warm Standby reduces RTO from 4 hours (Pilot Light) to 30 minutes, the savings from one incident ($35,000) pay for a year of Warm Standby.

## Failback Planning

Failback (returning to the primary region after it recovers) is often harder than failover because data has been written to the DR region during the outage.

### Failback Steps

1. **Restore primary region infrastructure** (if it was destroyed)
2. **Replicate data from DR back to primary** (reverse replication)
3. **Validate data consistency** between regions
4. **Shift traffic gradually** (weighted routing: 10% → 25% → 50% → 100%)
5. **Monitor for issues** at each traffic percentage
6. **Scale down DR** to normal standby levels (if not Active-Active)

### Failback Anti-Patterns

- **Rushing failback** before primary region is fully stable
- **Forgetting to re-establish replication** from primary to DR after failback
- **Big-bang failback** instead of gradual traffic shift
- **Not testing failback** — practice it with the same rigor as failover

## Common Decisions (ADR Triggers)

- **DR strategy selection** — which of the four strategies, with business justification (RTO/RPO requirements vs cost)
- **DR region selection** — which region, distance from primary, regulatory constraints
- **Data replication method** — synchronous vs asynchronous, replication technology
- **Failover automation** — fully automated vs semi-automated vs manual (recommend semi-automated: detect automatically, require human approval to execute)
- **Failover authority** — who can declare a disaster and trigger failover
- **Testing frequency** — how often to test each component, full drill frequency
- **Active-Active data consistency** — eventual vs strong consistency, conflict resolution strategy

## See Also

- `general/disaster-recovery.md` — DR planning concepts, RPO/RTO definitions
- `general/networking.md` — Cross-region connectivity and DNS management
- `general/data.md` — Data replication and consistency patterns
- `general/deployment.md` — Multi-region deployment strategies
