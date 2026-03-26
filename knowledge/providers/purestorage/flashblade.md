# Pure Storage FlashBlade

## Scope

Pure Storage FlashBlade unified fast file and object storage (UFFO): FlashBlade//S (performance-tier, all-NVMe) and FlashBlade//E (capacity-tier, QLC), Purity//FB operating environment, NFS/SMB file services, S3 object storage, rapid restore, data hub architecture, snapshots and replication, multi-protocol access, and integration with AI/ML pipelines, analytics, backup targets, and Kubernetes (Pure CSI).

## Checklist

- [ ] **[Critical]** Is the FlashBlade model selected for the workload profile? (//S for high-throughput unstructured data and performance-sensitive workloads — up to 17 blades, 75GB/s throughput, all-NVMe DirectFlash — //E for capacity-dense workloads like backup targets, archive, and secondary data — QLC flash, lower cost-per-TB, up to 5PB raw per chassis)
- [ ] **[Critical]** Is the data protocol selected for each workload? (NFS v3/v4.1 for Linux/UNIX file shares and VMware datastores, SMB 3.x for Windows file shares, S3 for object storage — FlashBlade supports all three concurrently on the same system, but each file system or bucket is protocol-specific)
- [ ] **[Critical]** Is network connectivity designed for the required throughput? (FlashBlade uses blade-level Ethernet connectivity — each blade provides 2x 25GbE or 2x 50GbE depending on model, aggregated across blades — design fabric bandwidth to match aggregate blade throughput, not just single-client needs)
- [ ] **[Critical]** Are file system and object store sizing policies defined? (file systems support thin provisioning with optional hard limits, S3 buckets support quotas — plan for growth with provisioned vs consumed capacity, data reduction applies to both file and object)
- [ ] **[Critical]** Is snapshot and replication strategy configured? (file system snapshots for point-in-time recovery, snapshot replication to a second FlashBlade or FlashArray for DR — configure snapshot scheduling per file system, set retention policies, test restore procedures)
- [ ] **[Critical]** Is the rapid restore use case sized correctly? (FlashBlade is commonly used as a backup target for Veeam, Commvault, and similar tools — rapid restore throughput depends on blade count and network bandwidth, size for the required RTO by calculating restore rate vs dataset size)
- [ ] **[Recommended]** Is multi-dimensional performance understood? (FlashBlade scales throughput, IOPS, and capacity independently by adding blades — unlike traditional NAS where controllers are the bottleneck, each blade adds compute, network, and flash capacity linearly)
- [ ] **[Recommended]** Is Pure1 Meta connected for monitoring and analytics? (provides capacity trending, performance monitoring, predictive support, and workload analysis — essential for identifying hot file systems and planning blade additions)
- [ ] **[Recommended]** Are access policies and export rules configured for security? (NFS export rules per file system with client IP/subnet restrictions, SMB access via Active Directory integration, S3 access via IAM-style policies with access keys — do not leave default open export rules in production)
- [ ] **[Recommended]** Is the data hub architecture pattern evaluated? (FlashBlade as a central data hub consolidating file and object workloads from analytics, AI/ML training, genomics, EDA, and media — reduces data copies and movement by serving multiple consumers from one namespace)
- [ ] **[Recommended]** Is SafeMode configured for object lock and snapshot immutability? (SafeMode for snapshots prevents deletion by administrators — S3 Object Lock provides WORM compliance for object data with governance or compliance retention modes — required for SEC 17a-4, FINRA, and similar regulations)
- [ ] **[Recommended]** Are Kubernetes PersistentVolumes using the Pure CSI driver for FlashBlade? (supports dynamic provisioning of NFS-backed PVs, ReadWriteMany access mode for shared storage across pods — configure StorageClass with FlashBlade backend for file workloads distinct from FlashArray block workloads)
- [ ] **[Optional]** Is SMB multi-channel configured for Windows workloads? (Purity//FB 4.x+ supports SMB multi-channel for increased per-client throughput — requires compatible Windows clients and multiple NIC paths)
- [ ] **[Optional]** Is S3 versioning and lifecycle management configured? (bucket versioning for object history, lifecycle rules for automatic tiering or expiration — useful for log archives and data lake management)
- [ ] **[Optional]** Is Active Directory and LDAP integration configured for file services? (AD join for SMB authentication, LDAP for NFS user mapping — configure Kerberos for NFS v4.1 security, test failover between domain controllers)

## Why This Matters

FlashBlade addresses the unstructured data challenge — file and object workloads that traditional block arrays handle poorly. The architecture scales throughput linearly with blade count, making it uniquely suited for parallel I/O workloads like AI/ML training datasets, genomics pipelines, media rendering, and backup/restore operations where traditional NAS controllers become bottlenecks.

The rapid restore capability is frequently the primary driver for FlashBlade adoption — organizations deploy FlashBlade as a Veeam or Commvault target specifically to meet aggressive RTOs. A FlashBlade with 10 blades can deliver 15+ GB/s restore throughput, recovering a 100TB dataset in under 2 hours. Sizing the blade count and network fabric for the restore throughput target is critical — undersizing means missed RTOs during actual disaster recovery.

The //S vs //E selection significantly impacts both cost and performance. Deploying //S for cold archive data wastes budget; deploying //E for latency-sensitive AI training data creates performance bottlenecks. Some organizations deploy both tiers — //S for hot data and //E for capacity — with replication between them.

## Common Decisions (ADR Triggers)

- **FlashBlade model selection** — //S (performance-tier, NVMe, high throughput for AI/ML, analytics, rapid restore) vs //E (capacity-tier, QLC, cost-optimized for backup targets, archive, secondary data) vs both (tiered architecture with replication between tiers) — workload throughput and cost requirements determine the model
- **Primary use case** — rapid restore target (Veeam, Commvault, HYCU backup target with fast RTO) vs data hub (consolidated file/object for analytics and AI/ML) vs traditional NAS replacement (file shares for Windows/Linux) — determines sizing, protocol, and network design
- **File protocol** — NFS v3 (simplest, widest compatibility, stateless) vs NFS v4.1 (stateful, Kerberos security, pNFS) vs SMB 3.x (Windows ecosystems, AD-integrated) — client OS and security requirements drive protocol choice
- **Object storage approach** — FlashBlade S3 (integrated, fast, no separate infrastructure) vs external S3 (MinIO, Ceph RGW, cloud S3) — consolidation benefit vs scale-out flexibility
- **Backup target architecture** — FlashBlade as primary backup target (fast backup and restore) vs FlashBlade as secondary target with tape/cloud for long-term (cost-optimized retention) — RTO requirements and retention policies determine approach
- **Multi-protocol access** — single protocol per file system (simpler, fewer permission conflicts) vs multi-protocol NFS+SMB (shared data, complex ACL mapping) — operational complexity vs data sharing needs
- **Kubernetes storage backend** — FlashBlade NFS for ReadWriteMany shared volumes vs FlashArray iSCSI/FC for ReadWriteOnce block volumes — workload access pattern determines backend

## Reference Links

- [Pure Storage FlashBlade Documentation](https://support.purestorage.com/FlashBlade) — official FlashBlade administration and configuration guides
- [Purity//FB REST API Reference](https://support.purestorage.com/FlashBlade/Purity_FB/Purity_FB_REST_API) — REST API v2.x reference for FlashBlade automation
- [FlashBlade S3 Object Store Guide](https://support.purestorage.com/FlashBlade/Purity_FB/FlashBlade_Object_Store) — S3-compatible object storage configuration
- [FlashBlade Best Practices for Backup](https://support.purestorage.com/Solutions/FlashBlade/FlashBlade_Backup) — Veeam, Commvault, and other backup integration guides
- [Pure Storage FlashBlade for AI](https://www.purestorage.com/solutions/infrastructure/ai-infrastructure.html) — AI/ML training data pipeline architecture
- [Pure Storage Ansible Collection for FlashBlade](https://galaxy.ansible.com/purestorage/flashblade) — Ansible modules for FlashBlade automation
- [FlashBlade SafeMode and Object Lock](https://support.purestorage.com/FlashBlade/Purity_FB/FlashBlade_Security) — immutable snapshots and S3 Object Lock configuration

## See Also

- `general/storage.md` — general storage architecture patterns
- `general/disaster-recovery.md` — DR strategy and RPO/RTO planning
- `general/enterprise-backup.md` — enterprise backup architecture and target selection
- `general/ransomware-resilience.md` — ransomware protection including immutable snapshots and object lock
- `providers/purestorage/flasharray.md` — FlashArray block storage
- `providers/purestorage/portworx.md` — Portworx Kubernetes-native storage
- `providers/veeam/backup.md` — Veeam backup integration with FlashBlade targets
- `providers/commvault/backup.md` — Commvault backup integration
