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

## See Also

- `general/enterprise-backup.md` — Backup strategy, 3-2-1-1-0 rule, product comparison
- `general/ransomware-resilience.md` — Ransomware defense, immutable storage, recovery workflows

## Reference Links

- [Cohesity Documentation](https://docs.cohesity.com/) -- cluster architecture, protection policies, DataLock WORM, and SmartFiles
- [Cohesity FortKnox](https://docs.cohesity.com/ui/login) -- SaaS-managed cyber vault for isolated backup copies
- [Cohesity REST API Reference](https://developer.cohesity.com/) -- API documentation for automation and integration
