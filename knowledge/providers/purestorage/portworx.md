# Pure Storage Portworx

## Scope

Portworx Enterprise Kubernetes-native storage platform: PX-Store (software-defined storage layer), PX-Backup (application-aware backup), PX-DR (zero-RPO disaster recovery for Kubernetes), PX-Security (RBAC and encryption), PX-Autopilot (capacity automation), storage pools, volume replication, cloud drives, bare-metal and cloud deployment, CSI integration, Stork (Storage Orchestrator for Kubernetes), and multi-cluster management via PX-Central.

## Checklist

- [ ] **[Critical]** Is the Portworx deployment model selected? (on-premises bare-metal with local disks, on-premises VMs with virtual disks, cloud VMs with cloud drives — each model has different disk provisioning, performance characteristics, and operational procedures — cloud drives enable dynamic capacity expansion via cloud APIs)
- [ ] **[Critical]** Are storage pools designed for workload isolation? (Portworx aggregates disks into storage pools — separate NVMe pools from HDD pools, assign different StorageClasses to different pools — a single pool mixing fast and slow media causes unpredictable latency)
- [ ] **[Critical]** Is the volume replication factor set correctly? (replication factor 1 for ephemeral workloads, 2 for standard resilience, 3 for production databases — Portworx synchronously replicates across nodes, higher replication factor means more cross-node network traffic and storage consumption)
- [ ] **[Critical]** Is the minimum node count met for the replication factor? (replication factor N requires at least N+1 Portworx nodes for data placement and recovery — a 3-node cluster with replication factor 3 has zero fault tolerance, minimum 4 nodes recommended for RF=3)
- [ ] **[Critical]** Is the internal Portworx network (KVDB and data) separated from application traffic? (Portworx uses a separate data network for volume replication and an internal KVDB for metadata — configure `dataInterface` and `managementInterface` in the Portworx spec to avoid contention with application pods)
- [ ] **[Critical]** Is KVDB (key-value database) deployment decided? (internal KVDB runs on Portworx nodes automatically — external KVDB using etcd provides better fault isolation but adds operational overhead — internal KVDB is recommended for most deployments, external KVDB for clusters >50 nodes or strict control-plane separation requirements)
- [ ] **[Recommended]** Is PX-Backup deployed for application-consistent Kubernetes backup? (application-aware backups of PVCs, ConfigMaps, Secrets, and custom resources — supports backup to S3, Azure Blob, Google Cloud Storage, and NFS — schedule-based with retention policies, test restores regularly)
- [ ] **[Recommended]** Is PX-DR configured for multi-cluster disaster recovery? (synchronous DR for zero RPO within metro distances, asynchronous DR for longer distances — uses ClusterPair CRD to link clusters, migrates volumes and application specs together — requires dedicated bandwidth between clusters)
- [ ] **[Recommended]** Is PX-Autopilot configured for capacity automation? (monitors storage pool utilization, automatically expands pools by adding cloud drives or resizing disks — define AutopilotRule CRDs with capacity thresholds and growth policies — critical for cloud deployments to prevent storage exhaustion)
- [ ] **[Recommended]** Is PX-Security enabled for multi-tenant clusters? (volume access control via Kubernetes RBAC integration, volume encryption with per-volume keys using an external KMS like Vault or AWS KMS — required for shared clusters with multiple teams or compliance requirements)
- [ ] **[Recommended]** Is Stork (Storage Orchestrator for Kubernetes) deployed and configured? (Stork provides hyperconvergence — schedules pods on nodes where their data resides, reducing network hops for storage I/O — also provides volume snapshots, application-consistent migration, and health monitoring)
- [ ] **[Recommended]** Are StorageClasses defined for each workload tier? (create distinct StorageClasses for databases (RF=3, io_profile=db), streaming (io_profile=sequential), shared volumes (sharedv4), and ephemeral workloads (RF=1) — avoid a single default StorageClass for all workloads)
- [ ] **[Recommended]** Is the Portworx license model understood? (Portworx Enterprise requires per-node licensing — PX-Essentials is free up to 5 nodes and 500 volumes but lacks DR, backup, and security features — ensure the license tier covers all planned features including PX-DR and PX-Backup)
- [ ] **[Optional]** Are io_profiles configured per volume for workload optimization? (db for random I/O like databases, sequential for streaming workloads, cms for content management, auto for mixed — io_profile tunes internal caching and I/O coalescing behavior per volume)
- [ ] **[Optional]** Is PX-Central deployed for multi-cluster management? (centralized monitoring, alerting, and management UI for multiple Portworx clusters — provides capacity views, performance dashboards, and license management across all clusters)
- [ ] **[Optional]** Are shared volumes (sharedv4) configured correctly? (Portworx sharedv4 volumes provide ReadWriteMany access via NFS — a single Portworx node acts as the NFS server for the volume, creating a potential bottleneck — for high-throughput shared workloads, consider FlashBlade NFS instead)
- [ ] **[Optional]** Is cloud drive management automated for cloud deployments? (Portworx can provision, attach, and manage cloud drives (EBS, Azure Managed Disks, GCE PDs) automatically — configure `cloudStorage` in the StorageCluster spec to define drive templates and max drives per node)

## Why This Matters

Portworx solves the persistent storage challenge for Kubernetes — stateful workloads like databases, message queues, and AI/ML pipelines require durable, replicated storage that survives pod rescheduling and node failures. Without a proper storage layer, organizations either run stateful workloads outside Kubernetes (negating the platform's benefits) or accept data loss risk with local volumes.

The storage pool design is the most impactful early decision. Mixing NVMe and HDD in the same pool means a database volume might be placed on HDD, causing severe latency spikes. Once data is placed on a pool, migrating to a different pool requires volume recreation. Similarly, the replication factor cannot be increased after volume creation without data migration — setting RF=1 for a production database because "we'll increase it later" is a common mistake that leads to data loss during node failures.

PX-DR's synchronous mode is fundamentally different from asynchronous — synchronous DR adds write latency equal to the round-trip time between clusters. Enabling synchronous DR between geographically distant clusters (>10ms RTT) makes database write latency unacceptable. The DR mode must match the distance and latency between sites.

Portworx licensing is per-node and can become expensive at scale. The free PX-Essentials tier lacks critical enterprise features (DR, backup, encryption), so organizations that start with Essentials often hit a wall when they need production-grade data protection.

## Common Decisions (ADR Triggers)

- **Storage layer selection** — Portworx (feature-rich, enterprise, licensed) vs Rook-Ceph (open-source, complex operations) vs OpenEBS (simple, per-node) vs Longhorn (lightweight, Rancher-native) vs cloud-native CSI (EBS CSI, Azure Disk CSI — cloud-only, no portability) — depends on features needed, budget, and operational maturity
- **Deployment model** — bare-metal with local NVMe/SSD (highest performance, requires disk management) vs VM-based with virtual disks (simpler provisioning, hypervisor overhead) vs cloud drives (dynamic scaling, higher latency, cloud API dependency) — infrastructure type determines model
- **KVDB topology** — internal KVDB (simpler, recommended <50 nodes) vs external etcd (operational overhead, better isolation for large clusters) — cluster scale and control-plane isolation requirements determine choice
- **DR strategy** — PX-DR synchronous (zero RPO, metro distance only, write latency impact) vs PX-DR asynchronous (configurable RPO, any distance, no write latency impact) vs PX-Backup to object storage (backup/restore, higher RPO, lower cost) — RPO/RTO requirements and inter-site latency determine approach
- **Multi-tenancy model** — namespace-level StorageClass restrictions via ResourceQuotas vs PX-Security volume ownership and encryption vs dedicated Portworx clusters per tenant — isolation requirements and operational complexity tradeoffs
- **Shared storage approach** — Portworx sharedv4 NFS volumes (integrated, single-node bottleneck) vs FlashBlade NFS via CSI (dedicated NAS hardware, higher throughput) vs CephFS via Rook (distributed, complex) — throughput requirements and infrastructure availability determine choice
- **License tier** — PX-Essentials (free, limited features, up to 5 nodes) vs PX-Enterprise (full features, per-node cost) vs PX-Enterprise via Pure Storage bundle (included with FlashArray/FlashBlade purchase) — budget, feature requirements, and existing Pure Storage relationship determine tier

## Reference Links

- [Portworx Documentation](https://docs.portworx.com/) — official Portworx installation, configuration, and operations guides
- [Portworx on Kubernetes](https://docs.portworx.com/portworx-enterprise/install-portworx/) — installation guide for various Kubernetes distributions
- [PX-Backup Documentation](https://docs.portworx.com/portworx-backup-on-prem/) — application-aware backup for Kubernetes
- [PX-DR Documentation](https://docs.portworx.com/portworx-enterprise/operations/operate-kubernetes/disaster-recovery/) — synchronous and asynchronous disaster recovery
- [Portworx StorageClass Parameters](https://docs.portworx.com/portworx-enterprise/operations/operate-kubernetes/storage-operations/create-pvcs/dynamic-provisioning/) — volume parameters including replication factor, io_profile, and encryption
- [Stork Documentation](https://docs.portworx.com/portworx-enterprise/operations/operate-kubernetes/stork/) — storage orchestrator for hyperconvergence and migration
- [PX-Autopilot](https://docs.portworx.com/portworx-enterprise/operations/operate-kubernetes/autopilot/) — automated capacity management rules
- [Portworx with Pure Storage FlashArray](https://docs.portworx.com/portworx-enterprise/install-portworx/on-premises/other/pure-flash-array/) — FlashArray as backend storage for Portworx

## See Also

- `general/container-orchestration.md` — Kubernetes platform design and operations
- `general/storage.md` — general storage architecture patterns
- `general/disaster-recovery.md` — DR strategy and RPO/RTO planning
- `general/enterprise-backup.md` — enterprise backup architecture
- `providers/purestorage/flasharray.md` — FlashArray block storage backend for Portworx
- `providers/purestorage/flashblade.md` — FlashBlade file/object storage
- `providers/kubernetes/storage.md` — Kubernetes CSI and persistent storage patterns
- `providers/ceph/storage.md` — Ceph distributed storage (alternative to Portworx)
