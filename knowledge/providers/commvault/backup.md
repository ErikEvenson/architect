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

## Day-2 Operations: Source-Object Lifecycle

The architecture decisions above (CommServe sizing, storage policies, dedup) determine *how* data is protected. Implementing backup-lifecycle synchronization (`patterns/backup-lifecycle-synchronization.md`) requires the *operational* mechanics of removing a source object's protection and reclaiming its data. These are the Commvault-specific controls that the pattern's soft and hard action paths map onto.

- **Deconfigure vs Delete a client (soft path).** *Deconfigure* a client or VSA virtual machine (Client → Deconfigure, or `qoperation execute` against the client) releases its license and stops new backups while **leaving existing backup data intact to age out under the storage policy's retention rules**. This is the soft-reclamation action: protection stops immediately, data recedes gradually, and the recovery points remain restorable until retention expires. Deleting the client outright removes the client record but, depending on configuration, can orphan its backup data under the storage policy -- which is why deconfigure-then-age-out is the controlled soft path.
- **Retention aging (the soft path's enforcement).** Backup data is pruned by the **Data Aging** job, which deletes recovery points that have exceeded their storage-policy-copy retention (basic retention `n days / m cycles`, plus any extended-retention rules). After a source object is deconfigured, its data is reclaimed automatically as Data Aging runs -- no explicit delete needed. Verify the copy's retention actually matches the intended reclamation deadline; an over-long retention rule means a deconfigured object's data persists far longer than the cost or erasure target.
- **Explicit "delete backup data" (hard path).** For immediate reclamation or a right-to-erasure request, browse the object's backup data and **delete the specific job(s)/contents**, or delete the subclient/backupset, then let the next Data Aging job physically prune the deduplicated blocks (logical delete marks data aged; physical space returns when the DDB prunes). This is irreversible and is the hard-reclamation action -- gate it behind the pattern's legal-hold and approval checks before running it.
- **Auto-discovery / subclient content rules (governs re-protection).** VSA subclients use **auto-discovery rules** (by VM name pattern, by vCenter folder/resource-pool/tag, or rule-based) plus do-not-back-up filters to decide which source VMs are protected. These rules are why a *re-presented* source object behaves predictably: a deleted-then-recreated VM with the same name can be auto-rediscovered and re-protected. Key lifecycle automation on the VM's **stable GUID/instance UUID**, not the display name, and ensure auto-discovery rules and the reclamation loop agree on identity (this is the join-key discipline from the pattern).
- **Compliance lock (the legal-hold gate, vendor side).** Worm/immutable storage (hardware WORM, cloud Object Lock on an auxiliary copy) and Commvault **legal hold** prevent the hard path from deleting data even when cost/erasure logic requests it -- the vendor-side implementation of the pattern's compliance-lock gate. Reclamation automation must check for an active hold before issuing any delete.
- **Automation surface.** `qoperation`/`qcommand`, the Command Line interface, and the Commvault REST API expose deconfigure, browse-and-delete, and job operations, so the reclamation loop can drive Commvault programmatically rather than through Command Center clicks.

## See Also

- `general/enterprise-backup.md` — Backup strategy, 3-2-1-1-0 rule, product comparison
- `general/disaster-recovery.md` — DR site design, failover orchestration
- `patterns/backup-lifecycle-synchronization.md` — end-to-end source-deletion → backup-reclamation pattern these mechanics implement

## Reference Links

- [Commvault Documentation (LTS 11.44)](https://documentation.commvault.com/11.44/software/index.html) -- CommServe, MediaAgent, storage policies, and IntelliSnap configuration
- [CommCell Logical Architecture](https://documentation.commvault.com/11.44/commcell-console/commcell_logical_architecture.html) -- CommServe, MediaAgent, and client components; agents, backup sets, subclients, and storage policies
- [Commvault SaaS Backup](https://documentation.commvault.com/saas/) -- cloud-managed backup service documentation (formerly branded Metallic)
