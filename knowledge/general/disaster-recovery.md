# Disaster Recovery

## Scope

This file covers disaster recovery strategy decisions: RPO/RTO definition per workload tier, failure scenario classification, failover model selection, data replication strategy, DR testing methodology, and DR cost optimization. For backup tool selection and backup architecture, see `enterprise-backup.md`. For provider-specific data protection implementation, see the provider files.

## Checklist

- [ ] **[Critical]** Define RPO and RTO targets per workload tier based on business impact analysis — Tier 1 (mission-critical: minutes RPO, < 1 hour RTO), Tier 2 (business-important: hours RPO, < 4 hours RTO), Tier 3 (non-critical: 24 hours RPO, next business day RTO); these numbers must come from business stakeholders, not engineering assumptions, and drive every subsequent DR architecture decision
- [ ] **[Critical]** Classify failure scenarios the architecture must survive and design accordingly — single instance failure (handled by auto-scaling and health checks), availability zone failure (requires multi-AZ deployment), region failure (requires cross-region replication and failover), provider-level failure (requires multi-cloud or hybrid architecture); each level adds significant cost and complexity, so only design for scenarios the business actually requires
- [ ] **[Critical]** Select a failover model that matches RTO requirements and budget constraints — active-active (lowest RTO, traffic served from multiple regions simultaneously, highest cost, requires conflict resolution for writes), active-passive (standby environment receives replicated data but serves no traffic until failover, moderate cost, minutes-to-hours RTO), warm standby (scaled-down copy of production running in DR region, faster failover than pilot light, moderate cost), or pilot light (minimal infrastructure running in DR region with data replication only, lowest cost, longest RTO as infrastructure must scale up during failover)
- [ ] **[Critical]** Define the data replication strategy for each stateful service — synchronous replication (zero data loss, RPO = 0, but adds write latency proportional to distance, only viable within a metro region), asynchronous replication (replication lag means potential data loss equal to the lag interval, viable across any distance, monitor lag as an SLI), or periodic snapshot replication (lowest cost, highest RPO, acceptable for Tier 3 workloads)
- [ ] **[Critical]** Establish DR testing frequency and methodology — tabletop exercises quarterly (review runbooks, identify gaps, low cost), planned failover tests semi-annually (actually execute failover to DR, measure RTO/RPO, moderate disruption risk), chaos engineering continuously (inject failures in production to verify resilience, requires mature observability), and unannounced DR tests annually (most realistic validation, highest organizational disruption)
- [ ] **[Critical]** Document and maintain DR runbooks for each failure scenario — include step-by-step procedures, responsible roles, communication templates, escalation paths, and decision criteria for when to declare a disaster vs. wait for recovery; runbooks must be stored outside the primary infrastructure (printed copies, separate cloud account, or DR site) so they are accessible when needed
- [ ] **[Critical]** Define backup location strategy to ensure recoverability when the primary region is unavailable — backups stored in a different region from production (at minimum), cross-provider backup copies for critical data (S3 to Azure Blob, or cloud to on-prem), and ensure backup restore procedures have been tested from the DR location specifically (not just from the primary region)
- [ ] **[Recommended]** Design DR for stateful services with service-specific strategies — databases (native replication such as PostgreSQL streaming replication, MySQL GTID replication, or managed cross-region replicas), message queues (MirrorMaker for Kafka, shovel/federation for RabbitMQ, or managed multi-region), object storage (cross-region replication with versioning), and file systems (rsync, DRBD, or storage-level replication); each stateful service has different consistency and failover characteristics that must be individually addressed
- [ ] **[Recommended]** Implement DNS-based failover with appropriate TTLs and health checking — Route 53 health checks, Cloudflare load balancing, or global server load balancing (GSLB); set DNS TTLs low enough for timely failover (60-300 seconds) but not so low that DNS query volume becomes a cost or performance issue; consider that client-side DNS caching may extend effective TTL beyond what is configured
- [ ] **[Recommended]** Determine whether failover is automated or manual and define the decision criteria — automated failover reduces RTO but risks false positives (split-brain, flapping); manual failover adds human judgment but increases RTO; hybrid approach uses automated detection with manual approval (pager duty notification with one-click failover); for databases, automated failover is standard (Patroni, RDS Multi-AZ) but cross-region failover is typically manual due to the blast radius of a wrong decision
- [ ] **[Recommended]** Define the failback procedure after DR recovery — failback is often harder than failover because the DR site has now accumulated new data that must be replicated back; plan for reverse replication, data reconciliation, and a controlled cutback to the primary site; schedule failback during a maintenance window, not under pressure during an ongoing incident
- [ ] **[Recommended]** Optimize DR costs by right-sizing the standby environment — use smaller instance types in DR that can be scaled up during failover, leverage reserved capacity or savings plans for always-on DR infrastructure, use spot/preemptible instances for non-critical DR workloads, and periodically review whether DR spending aligns with actual business risk (over-engineering DR for non-critical workloads wastes budget that could protect critical ones)
- [ ] **[Optional]** Address compliance and regulatory requirements for DR — some industries mandate specific RPO/RTO (financial services, healthcare), geographic data residency requirements may constrain DR region selection, audit requirements may demand evidence of DR testing and results, and some regulations require DR sites to be a minimum physical distance from production (e.g., 200+ miles for certain financial regulations)
- [ ] **[Optional]** Evaluate third-party DR orchestration tools for complex environments — Zerto (continuous replication with journal-based recovery, near-zero RPO, VM-level protection), AWS Elastic Disaster Recovery (block-level replication to AWS, cost-effective pilot light), Azure Site Recovery (Hyper-V and VMware to Azure), or CloudEndure (acquired by AWS, agent-based replication); these tools simplify DR automation but add licensing cost and vendor dependency

## Why This Matters

Disaster recovery planning is fundamentally a business decision disguised as a technical one. The cost of DR infrastructure scales directly with how aggressive the RPO and RTO targets are — an active-active multi-region deployment can cost 3-5x more than a single-region deployment with periodic backups. Without explicit business input on acceptable downtime and data loss, engineering teams either over-spend on DR for non-critical workloads or under-invest in DR for critical ones. Both are expensive mistakes — one wastes budget, the other risks the business.

The most dangerous DR plan is the one that has never been tested. Organizations routinely discover during an actual disaster that their replication was silently failing, their runbooks reference infrastructure that no longer exists, their failover scripts have undocumented dependencies on the primary site, or their RTO calculation did not account for the time required to make a decision, notify stakeholders, and coordinate the failover. Regular DR testing is the only way to convert a theoretical plan into a validated capability.

Modern distributed systems introduce DR challenges that traditional backup-and-restore approaches do not address. A microservices architecture may span dozens of stateful services, each with different replication mechanisms, consistency guarantees, and failover behaviors. Failing over a database without also failing over the dependent cache, queue, and search index produces an inconsistent system that may be worse than being completely down. DR planning for distributed systems must address service dependencies, data consistency across services, and the order of operations for failover and failback.

## Common Decisions (ADR Triggers)

### ADR: Failover Model Selection

**Context:** The organization must select a DR architecture that balances RTO requirements against infrastructure cost and operational complexity.

**Options:**

| Criterion | Active-Active | Active-Passive | Warm Standby | Pilot Light |
|---|---|---|---|---|
| RTO | Near-zero (traffic already flowing) | Minutes to hours (DNS switch + warm-up) | Minutes (scale up + DNS switch) | Hours (provision + scale + DNS switch) |
| RPO | Near-zero (multi-master or conflict resolution) | Depends on replication lag | Depends on replication lag | Depends on backup/replication frequency |
| Steady-State Cost | 2x+ (full capacity in both regions) | 1.5-2x (full standby environment) | 1.2-1.5x (reduced standby) | 1.05-1.2x (minimal infrastructure) |
| Complexity | Very high (data consistency, conflict resolution, global routing) | Moderate (replication, failover automation) | Moderate (scaling automation, replication) | Low-moderate (provisioning automation) |
| Data Consistency | Requires conflict resolution strategy (last-write-wins, CRDTs, application-level merge) | Single primary, straightforward | Single primary, straightforward | Single primary, potential for higher data loss |
| Best Fit | Zero-downtime SLA, global user base, revenue-critical applications | Most production workloads with < 1 hour RTO | Budget-conscious with moderate RTO (< 2 hours) | Non-critical workloads, development/staging DR |

**Decision drivers:** SLA commitments (contractual downtime penalties), revenue impact per hour of downtime, data consistency requirements, team's operational maturity with multi-region architectures, and infrastructure budget.

### ADR: Data Replication Strategy

**Context:** Stateful services require data replication to the DR site, and the replication method determines both RPO and production performance impact.

**Options:**
- **Synchronous replication:** Every write is confirmed at both primary and DR before acknowledging to the application. RPO = 0 (zero data loss). Adds write latency equal to round-trip time to DR site. Only practical within a metro area (< 5ms RTT). Example: PostgreSQL synchronous standby, storage-level synchronous replication.
- **Asynchronous replication:** Writes are acknowledged at the primary and replicated to DR in the background. RPO = replication lag (typically seconds to minutes). No production performance impact. Viable at any distance. Risk of data loss equal to uncommitted transactions during failure. Example: PostgreSQL streaming replication (async), MySQL binary log replication, S3 cross-region replication.
- **Semi-synchronous replication:** Write is acknowledged after at least one replica confirms receipt but before it is applied. Compromise between sync and async — lower data loss risk than async, lower latency impact than sync. Example: MySQL semi-synchronous replication.
- **Periodic snapshot replication:** Point-in-time snapshots replicated on a schedule (hourly, daily). Highest RPO (equal to snapshot interval). Lowest cost and complexity. Acceptable for Tier 3 workloads, development environments, or compliance archives. Example: EBS snapshot copy, VM snapshot replication.

**Decision drivers:** RPO requirements per workload tier, distance between primary and DR sites, acceptable production write latency impact, and database engine capabilities.

### ADR: DR Testing Strategy

**Context:** DR plans must be validated through testing, but testing disrupts operations and carries risk.

**Options:**
- **Tabletop exercises:** Walk through runbooks verbally with the team. Identifies documentation gaps and knowledge silos. No infrastructure risk. Does not validate technical capability. Quarterly cadence recommended.
- **Planned failover tests:** Actually fail over to DR during a scheduled maintenance window. Validates full technical stack. Carries risk of extended outage if failback fails. Semi-annual cadence for critical workloads.
- **Chaos engineering:** Continuously inject controlled failures in production (instance termination, network partition, latency injection). Validates resilience in realistic conditions. Requires mature observability and blast radius controls. Tools: Chaos Monkey, Litmus, Gremlin.
- **Game days:** Full-scale simulated disaster with cross-team participation, including incident management, communication, and executive notification. Most comprehensive validation. Highest organizational effort. Annual cadence.

**Decision drivers:** Organizational risk tolerance, operational maturity, downtime budget for testing, regulatory requirements for DR validation evidence, and whether the application architecture supports partial failure injection.

### ADR: Automated vs. Manual Failover

**Context:** The failover trigger mechanism must balance speed (RTO) against the risk of false-positive failovers.

**Options:**
- **Fully automated:** Health checks trigger failover without human intervention. Lowest RTO. Risk of split-brain if health checks are unreliable (network partition may cause both sites to assume primary role). Requires robust quorum mechanisms and fencing. Standard for single-service database failover (Patroni, RDS Multi-AZ).
- **Automated detection, manual execution:** Monitoring detects the failure and pages the on-call engineer, who evaluates the situation and executes a pre-built failover script. Adds 5-30 minutes to RTO. Prevents false-positive failovers. Most common for cross-region failover.
- **Fully manual:** On-call engineer detects the issue, assesses impact, and follows the runbook step by step. Longest RTO (30 minutes to hours). Appropriate for complex failovers with many dependencies where human judgment is essential.

**Recommendation:** Automate detection universally. Automate execution for well-understood, single-service failovers (database, cache). Require manual approval for cross-region or full-stack failovers where the blast radius of a false positive is comparable to the disaster itself.

## See Also

- `general/enterprise-backup.md` — Backup tool selection, storage tiering, and ransomware protection
- `general/deployment.md` — Deployment strategies and rollback procedures
- `providers/nutanix/data-protection.md` — Nutanix backup and replication
- `providers/vmware/data-protection.md` — VMware backup and replication
- `providers/openstack/data-protection.md` — OpenStack backup and recovery
- `providers/openshift/data-protection.md` — OpenShift data protection
- `general/ransomware-resilience.md` — Ransomware-specific resilience controls, backup isolation, and recovery playbooks
