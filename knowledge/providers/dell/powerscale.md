# Dell PowerScale (Isilon)

## Scope

Dell PowerScale (formerly Isilon) scale-out NAS platform: cluster architecture and node selection (all-flash F-series, hybrid H-series, archive A-series), OneFS distributed file system, SmartPools tiered storage, data protection (N+M/mirroring), multi-protocol access (NFS, SMB, HDFS, S3, HTTP), performance tuning, and enterprise use cases (media and entertainment, genomics, AI/ML data lakes, home directories, general file shares).

## Checklist

- [ ] [Critical] Is the correct PowerScale node tier selected for the workload? (F-series all-flash for high-IOPS workloads like databases and AI/ML training, H-series hybrid for mixed workloads and home directories, A-series archive for cold data and compliance retention)
- [ ] [Critical] Is the cluster sized with a minimum of 3 nodes (4 recommended) and is the protection level set correctly? (N+1 minimum for small clusters, N+2 for production, N+2d:1n for 6+ node clusters to survive simultaneous node and drive failure)
- [ ] [Critical] Is the OneFS protection level configured to match the cluster size and data criticality? (mirroring 2x-4x for small files/metadata-heavy workloads, FEC N+M for large sequential workloads -- protection overhead varies from 25% to 67%)
- [ ] [Critical] Are access zones configured to provide multi-tenant isolation? (separate authentication providers, share namespaces, and IP address pools per access zone for security boundaries)
- [ ] [Critical] Is authentication configured correctly per protocol? (Active Directory/Kerberos for SMB, LDAP or NIS for NFS with ID mapping between UNIX and Windows identities, avoid mixing auth providers without a mapping strategy)
- [ ] [Critical] Is the network configured with dedicated subnets and SmartConnect zones for client-facing traffic? (SmartConnect provides DNS-based load balancing across nodes -- requires delegated DNS zone, SSIP pool per subnet)
- [ ] [Recommended] Are SmartPools policies configured to tier data automatically between node pools based on age, access patterns, or file attributes? (e.g., move files untouched for 90 days from F-series to H-series to A-series)
- [ ] [Recommended] Is SmartQuotas configured to enforce storage quotas on directories and users, with advisory, soft, and hard limits to prevent uncontrolled growth?
- [ ] [Recommended] Is SyncIQ configured for asynchronous replication to a secondary PowerScale cluster for disaster recovery, with RPO validated against the dataset change rate?
- [ ] [Recommended] Is SnapshotIQ configured with snapshot schedules for point-in-time recovery, with snapshot reserve space allocated (typically 20-30% of used capacity)?
- [ ] [Recommended] Is InsightIQ or DataIQ deployed for performance monitoring, capacity trending, and data analytics to identify hot spots, cold data, and growth trends?
- [ ] [Recommended] Are NFS exports configured with correct security options? (sys/krb5/krb5i/krb5p authentication, root squashing, read-write vs read-only per subnet, NFSv3 vs NFSv4.x based on client requirements)
- [ ] [Recommended] Is HDFS or S3 protocol access configured if the cluster serves as a data lake for analytics or AI/ML workloads? (HDFS transparent redirect, S3 with IAM-style access keys)
- [ ] [Optional] Is SmartDedupe enabled for workloads with high data redundancy? (effective for home directories, VDI profiles, software repositories -- not recommended for media, compressed, or encrypted data)
- [ ] [Optional] Is CloudPools configured to tier cold data to public cloud object storage (AWS S3, Azure Blob, Google Cloud Storage) while maintaining a local stub for transparent recall?
- [ ] [Optional] Is NDMP backup configured for large-scale file system backups to tape or third-party backup targets, using parallel NDMP streams for throughput?
- [ ] [Optional] Is antivirus scanning (ICAP integration) configured for SMB shares serving Windows clients to scan files on access or on write?

## Why This Matters

PowerScale is the industry-leading scale-out NAS platform, handling the largest unstructured data workloads globally. Its distributed architecture (OneFS) stripes data across all nodes, so cluster sizing and protection level directly determine both capacity and performance. The most common mistake is under-protecting data -- N+1 means a single drive or node failure consumes all rebuild capacity, and a second failure during rebuild causes data loss. SmartConnect misconfiguration is the second most common issue, leading to uneven client distribution and hot nodes. Identity mapping between Windows and UNIX namespaces is notoriously complex and must be planned before deployment -- retrofitting access zones and authentication changes on a production cluster is disruptive.

## Common Decisions (ADR Triggers)

- **Node tier selection** -- F-series (all-flash, highest throughput) vs H-series (hybrid, cost-effective) vs A-series (archive, lowest cost per TB) -- mixed-tier clusters use SmartPools for automatic tiering
- **Protection level** -- N+1 (1 failure tolerance), N+2 (2 failures), N+3 (3 failures), mirroring 2x-4x -- balance protection overhead against usable capacity
- **Multi-protocol strategy** -- NFS-only (Linux/VMware) vs SMB-only (Windows) vs multi-protocol (both, requires identity mapping) vs HDFS/S3 for analytics
- **Data tiering** -- SmartPools between node tiers (on-cluster) vs CloudPools to public cloud (off-cluster) vs manual archival workflows
- **DR strategy** -- SyncIQ async replication (RPO minutes to hours) vs SyncIQ with accelerated failover vs backup/restore (RPO hours to days) -- SyncIQ license is per-cluster
- **Quotas and governance** -- SmartQuotas (built-in) vs third-party quota management -- advisory vs hard limits, per-user vs per-directory vs per-group
- **Performance optimization** -- concurrent I/O streaming for large files (media) vs IOPS optimization for small files (home directories) -- L3 cache sizing on all-flash nodes
- **Cluster vs multiple clusters** -- single large cluster (simpler management, single namespace) vs multiple clusters (isolation, separate failure domains, separate SyncIQ relationships)

## Reference Links

- [Dell PowerScale Documentation](https://www.dell.com/support/home/en-us/product-support/product/isilon/docs) -- official OneFS administration and configuration guides
- [OneFS Best Practices Guide](https://infohub.delltechnologies.com/en-us/t/powerscale-isilon/) -- Dell InfoHub with white papers and best practices for PowerScale
- [PowerScale SmartConnect Guide](https://www.dell.com/support/kbdoc/en-us/000021938/isilon-smartconnect-overview) -- DNS-based load balancing configuration and troubleshooting
- [PowerScale SyncIQ Replication Guide](https://infohub.delltechnologies.com/en-us/t/powerscale-isilon/) -- asynchronous replication configuration for DR
- [PowerScale Security Configuration Guide](https://www.dell.com/support/kbdoc/en-us/000021933/isilon-authentication-and-access-control) -- authentication, access zones, and RBAC configuration
- [PowerScale for AI/ML Data Pipelines](https://infohub.delltechnologies.com/en-us/t/powerscale-isilon/) -- reference architectures for NVIDIA GPU clusters with PowerScale storage

## See Also

- `general/storage.md` -- general storage architecture patterns
- `general/disaster-recovery.md` -- DR strategy and RPO/RTO planning
- `providers/dell/powerstore.md` -- Dell PowerStore for block/unified storage
- `patterns/ai-ml-infrastructure.md` -- AI/ML infrastructure patterns including data lake storage
- `providers/vmware/storage.md` -- VMware NFS datastore integration with PowerScale
