# Cohesity DataProtect

## Scope

This file covers **Cohesity architecture and design** including cluster architecture (nodes, storage domains, Views), protection policies and protection groups, DataLock WORM compliance, SmartFiles for unstructured data consolidation, FortKnox cyber vault (SaaS-managed isolated backup copy), cloud tiering to public cloud storage targets, and integration with existing infrastructure. It does not cover general backup strategy; for that, see `general/enterprise-backup.md`.

## Checklist

- [ ] **[Critical]** Size the Cohesity cluster (number of nodes, storage capacity, node type) based on total protected data, daily change rate, ingest throughput, and retention requirements
- [ ] **[Critical]** Define protection policies with snapshot frequency, local retention, replication targets, and archival targets aligned to application tier RPO/RTO requirements
- [ ] **[Critical]** Enable DataLock (WORM) on critical protection policies to make backup snapshots immutable for a defined retention period — preventing deletion even by cluster administrators
- [ ] **[Critical]** Plan network architecture with separate VLANs for data ingestion, replication, and cluster internal traffic to avoid bandwidth contention
- [ ] **[Recommended]** Deploy a minimum 3-node cluster for production workloads to maintain the Cohesity distributed file system (SpanFS) resilience and erasure coding requirements
- [ ] **[Recommended]** Configure FortKnox cyber vault for an isolated, SaaS-managed copy of critical backups that is unreachable from the production network
- [ ] **[Recommended]** Use Cohesity Helios (SaaS management plane) for centralized multi-cluster monitoring, global search, and compliance reporting
- [ ] **[Recommended]** Configure RBAC with distinct roles for backup administration, restore operations, and compliance auditing — restrict DataLock override capabilities to a security officer role
- [ ] **[Recommended]** Validate source-side throttling settings to prevent backup operations from consuming excessive production storage IOPS or network bandwidth
- [ ] **[Optional]** Consolidate secondary storage workloads (file shares, test/dev, analytics) onto the Cohesity cluster using SmartFiles to reduce infrastructure sprawl
- [ ] **[Optional]** Configure cloud tiering to move aged snapshots to S3, Azure Blob, or GCS based on retention policy age-off rules
- [ ] **[Optional]** Leverage Cohesity marketplace apps for anti-virus scanning, compliance monitoring, or custom analytics running directly on the cluster
- [ ] **[Optional]** Evaluate Cohesity virtual edition (VE) for remote office or cloud-deployed backup targets where physical appliances are impractical

## Why This Matters

Cohesity consolidates backup storage, file shares, test/dev copies, and analytics onto a single hyperconverged platform, reducing the number of secondary storage silos in the data center. This consolidation can dramatically simplify operations, but it also concentrates risk — a poorly sized or misconfigured Cohesity cluster becomes a single point of failure for multiple secondary data services, not just backup.

DataLock and FortKnox represent Cohesity's primary ransomware resilience features. DataLock enforces WORM immutability at the cluster level, preventing even rogue administrators from deleting protected snapshots. FortKnox extends this with an air-gapped SaaS vault that is operationally isolated from on-premises infrastructure. Without these features enabled, Cohesity backups face the same ransomware risks as any other network-accessible storage. Organizations that deploy Cohesity without DataLock policies or FortKnox integration miss the platform's most valuable security capabilities.

## Common Decisions (ADR Triggers)

### ADR: Cohesity Cluster Sizing and Node Type

**Context:** Cohesity offers multiple node types (all-flash, hybrid, compute-heavy) and cluster sizes must account for both data protection and secondary workload consolidation.

**Options:**

| Criterion | 3-Node Hybrid | 4-Node All-Flash | 6+ Node Hybrid | Virtual Edition |
|---|---|---|---|---|
| Protected data (typical) | Up to 30 TB FE | Up to 50 TB FE | 50+ TB FE | Up to 10 TB FE |
| Performance | Good | High (NVMe) | Good (scale-out) | Limited by VM resources |
| SmartFiles workloads | Limited | Good | Best | Not recommended |
| Use case | SMB / single workload | Performance-sensitive | Multi-workload consolidation | Remote office / cloud |

### ADR: Immutability Strategy

**Context:** Cohesity supports multiple immutability mechanisms; the organization must decide which to deploy and for which data.

**Options:**

| Criterion | DataLock (Local WORM) | FortKnox (SaaS Vault) | Both |
|---|---|---|---|
| Protection scope | Local cluster snapshots | Isolated cloud copy | Full coverage |
| Admin bypass risk | None (time-locked) | None (Cohesity-managed) | None |
| Connectivity required | None | Outbound HTTPS | Outbound HTTPS |
| Cost | Included in license | Additional subscription | Additional subscription |
| Recovery from cluster loss | No (data on same cluster) | Yes (independent copy) | Yes |

### ADR: Secondary Workload Consolidation

**Context:** Cohesity can serve as a target for file shares, test/dev clones, and analytics workloads alongside data protection.

**Decision factors:** Volume of unstructured data currently on NAS/file servers, test/dev environment provisioning frequency, analytics data pipeline requirements, and whether consolidation reduces total infrastructure cost or creates unacceptable risk concentration.

## Day-2 Operations: Source-Object Lifecycle

The architecture decisions above (cluster sizing, protection policies, DataLock) determine *how* data is protected. Implementing backup-lifecycle synchronization (`patterns/backup-lifecycle-synchronization.md`) requires the Cohesity-specific mechanics for unprotecting a source object and reclaiming its snapshots. These map onto the pattern's soft and hard action paths.

- **Unprotect an object (soft path).** Removing a source object (VM, database, NAS share) from its **protection group** stops new snapshots while **leaving existing snapshots to age out under the protection policy's retention**. This is soft reclamation: protection stops now, snapshots recede as retention expires. Whether to also remove the object's entry depends on the protection-group definition (explicitly listed objects vs auto-protected sets, below).
- **Retention aging (soft enforcement).** Cohesity protection policies define local-snapshot retention plus replication/archival retention; snapshots are garbage-collected once they exceed it. After an object is unprotected, its snapshots reclaim automatically. Confirm the policy retention equals the intended reclamation deadline -- a long compliance retention means an unprotected object's data lingers accordingly.
- **Explicit snapshot deletion (hard path).** For immediate reclamation or right-to-erasure, **delete the specific protection-run snapshots** for the object (UI per-object snapshot delete, or the REST API). This is irreversible. Note the interaction with **DataLock**: a DataLock/WORM snapshot **cannot** be deleted until its lock expires -- by design, this is the legal-hold/compliance-lock gate enforced at the storage layer, and the reclamation loop must treat a DataLock-protected object as non-reclaimable rather than erroring on a failed delete.
- **Auto-protection (governs re-protection).** Cohesity **Auto Protect** can include sources by vCenter folder/tag or hierarchy, so newly created (or recreated) objects are picked up automatically, and excludes can hold objects out. A deleted-then-recreated source with a reused name can be auto-reprotected; key the reclamation loop on the source's stable UUID (the pattern's join-key discipline) so a name-reuse does not cause the new object's snapshots to be reclaimed against the old object's deletion.
- **Automation surface.** The Cohesity REST API and Helios drive unprotect, snapshot deletion, and protection-group membership programmatically, so the reclamation loop can act on Cohesity without manual UI steps. DataLock-override remains restricted to the security-officer role, keeping the legal-hold gate out of the automation's reach by design.

## See Also

- `general/enterprise-backup.md` — Backup strategy, 3-2-1-1-0 rule, product comparison
- `general/ransomware-resilience.md` — Ransomware defense, immutable storage, recovery workflows
- `patterns/backup-lifecycle-synchronization.md` — end-to-end source-deletion → backup-reclamation pattern these mechanics implement

## Reference Links

- [Cohesity Documentation](https://docs.cohesity.com/) -- cluster architecture, protection policies, DataLock WORM, and SmartFiles
- [Cohesity FortKnox](https://docs.cohesity.com/ui/login) -- SaaS-managed cyber vault for isolated backup copies
- [Cohesity REST API Reference](https://developer.cohesity.com/) -- API documentation for automation and integration
