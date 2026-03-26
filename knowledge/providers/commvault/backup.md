# Commvault

## Scope

This file covers **Commvault architecture and design** including CommServe server sizing, MediaAgent deployment, client agent configuration, storage policies, IntelliSnap hardware snapshot integration, Command Center management, HyperScale X converged infrastructure, Metallic SaaS backup, licensing models, and cloud integration for tiering and DR. It does not cover general backup strategy; for that, see `general/enterprise-backup.md`.

## Checklist

- [ ] **[Critical]** Size the CommServe server (CPU, RAM, SQL Server database) based on total number of clients, subclients, and storage policies — the CommServe database is the single point of failure for the entire environment
- [ ] **[Critical]** Deploy MediaAgents with dedicated storage pools close to the data sources they protect — avoid routing all backup traffic through a single centralized MediaAgent
- [ ] **[Critical]** Define storage policies with appropriate copy precedence: primary (fast), secondary (deduplicated), and auxiliary (cloud or tape) to meet RPO and retention requirements
- [ ] **[Critical]** Plan and test CommServe disaster recovery — maintain a DR CommServe copy or use CommServe LiveSync to ensure the backup environment itself can be recovered
- [ ] **[Recommended]** Configure deduplication at the MediaAgent level using DDB (Deduplication Database) partitions sized to available RAM — undersized DDB causes severe performance degradation
- [ ] **[Recommended]** Use IntelliSnap for storage-array-integrated snapshots where supported (NetApp, Pure, Dell) to reduce backup windows for large databases and file systems
- [ ] **[Recommended]** Deploy Command Center for centralized management, SLA monitoring, and self-service restore capabilities across all CommCells
- [ ] **[Recommended]** Separate backup data traffic from management traffic — MediaAgent data interfaces should be on a dedicated backup network
- [ ] **[Recommended]** Configure alert policies for job failures, storage pool thresholds, and CommServe database growth to enable proactive management
- [ ] **[Optional]** Evaluate HyperScale X for branch office or edge deployments where converged backup infrastructure simplifies management
- [ ] **[Optional]** Integrate Metallic SaaS for protecting cloud-native workloads (Microsoft 365, Salesforce, cloud VMs) without deploying on-premises infrastructure
- [ ] **[Optional]** Configure Commvault cloud tiering to move aged data to S3, Azure Blob, or GCS based on access patterns and retention requirements
- [ ] **[Optional]** Enable content indexing and compliance search for environments with eDiscovery or regulatory retention obligations

## Why This Matters

Commvault provides one of the most comprehensive data protection platforms available, capable of protecting virtually any workload type across on-premises and cloud environments. However, its flexibility comes with architectural complexity — a poorly designed Commvault environment with undersized CommServe databases, misconfigured storage policies, or inadequate MediaAgent distribution will suffer from slow backups, failed restores, and operational fragility.

The CommServe is a critical single point of failure. If the CommServe and its database are lost without a recovery plan, the entire backup catalog — potentially representing years of backup metadata — is gone. Organizations that skip CommServe DR planning discover this during compound failure scenarios when they need their backups most. Proper architecture, storage policy design, and deduplication sizing are the difference between a manageable environment and one that consumes disproportionate operational effort.

## Common Decisions (ADR Triggers)

### ADR: Commvault Deployment Model

**Context:** The organization must choose between traditional on-premises Commvault, HyperScale X appliances, or Metallic SaaS.

**Options:**

| Criterion | Traditional (CommServe + MediaAgent) | HyperScale X | Metallic SaaS |
|---|---|---|---|
| Workload coverage | Broadest | On-premises focused | Cloud and SaaS workloads |
| Infrastructure required | Dedicated servers | Converged nodes | None (cloud-hosted) |
| Scalability | Manual (add MediaAgents) | Scale-out (add nodes) | Elastic |
| Operational complexity | High | Medium | Low |
| Cost model | CapEx (perpetual or term) | CapEx (appliance) | OpEx (subscription) |

### ADR: Deduplication Strategy

**Context:** Deduplication reduces storage consumption but requires careful sizing of DDB partitions.

**Decision factors:** Source data size, daily change rate, available MediaAgent RAM (minimum 2 GB per 1 TB of deduplicated front-end data), number of DDB partitions, and whether source-side or target-side dedup is appropriate for WAN-connected remote offices.

### ADR: Storage Policy Hierarchy

**Context:** Storage policies control data flow from clients through MediaAgents to storage. Policy design affects backup performance, retention compliance, and restore speed.

**Decision factors:** Number of application tiers, RPO per tier, retention requirements (short-term vs. long-term), copy precedence order, auxiliary copy scheduling, and cloud tiering triggers.

## See Also

- `general/enterprise-backup.md` — Backup strategy, 3-2-1-1-0 rule, product comparison
- `general/disaster-recovery.md` — DR site design, failover orchestration

## Reference Links

- [Commvault Documentation](https://documentation.commvault.com/2024e/essential/overview.html) -- CommServe, MediaAgent, storage policies, and IntelliSnap configuration
- [Commvault Architecture Guide](https://documentation.commvault.com/2024e/essential/architecture_overview.html) -- deployment topologies, component sizing, and network requirements
- [Metallic SaaS Backup](https://documentation.commvault.com/metallic/) -- cloud-managed backup service documentation
