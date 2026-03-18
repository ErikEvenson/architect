# OpenShift Storage

## Scope

OpenShift storage: OpenShift Data Foundation (ODF/Ceph), cloud-native CSI drivers, vSphere CSI, StorageClasses, dynamic provisioning, volume snapshots, local storage operator, and platform component storage (registry, logging, monitoring).


## Checklist

- [ ] **[Critical]** Select primary storage backend: OpenShift Data Foundation (ODF/Ceph), cloud-native CSI (EBS, Azure Disk, GCE PD), vSphere CSI, NFS, or third-party (NetApp Trident, Pure Storage, Dell CSI)
- [ ] **[Critical]** Define StorageClasses with appropriate reclaim policies (Retain for production data, Delete for ephemeral)
- [ ] **[Recommended]** Configure dynamic provisioning for all storage classes; avoid manual PV creation
- [ ] **[Critical]** Plan access mode requirements: ReadWriteOnce (RWO) for databases, ReadWriteMany (RWX) for shared filesystems, ReadOnlyMany (ROX) for content distribution
- [ ] **[Critical]** Size ODF cluster if using Ceph: minimum 3 nodes, 30+ CPU cores and 72+ GB RAM for ODF services, raw disk capacity planning with replication factor
- [ ] **[Critical]** Configure storage for platform components: internal registry (S3 or ODF RWX), logging (block or object storage for Loki), monitoring (block storage for Prometheus TSDB)
- [ ] **[Recommended]** Set ResourceQuotas for PVC counts and total storage per namespace to prevent runaway provisioning
- [ ] **[Recommended]** Enable CSI volume snapshots (`VolumeSnapshot`, `VolumeSnapshotClass`) for backup and cloning
- [ ] **[Optional]** Configure volume cloning for fast provisioning of database test environments
- [ ] **[Optional]** Plan local storage operator deployment for bare metal nodes requiring direct-attached NVMe/SSD
- [ ] **[Recommended]** Define data migration strategy for moving workloads between storage backends or clusters
- [ ] **[Critical]** Evaluate encryption at rest: ODF encryption (dm-crypt), cloud KMS integration, or storage-layer encryption
- [ ] **[Critical]** Configure storage topology constraints to ensure PVs are provisioned in the same zone as pods

## Why This Matters

Storage is the stateful foundation of OpenShift workloads. Wrong storage choices lead to performance bottlenecks, data loss, or vendor lock-in that is expensive to reverse. OpenShift Data Foundation (ODF) -- based on Rook-Ceph -- provides block (RBD), file (CephFS), and object (S3-compatible via MCG/NooBaa) storage from a single platform, but it requires significant dedicated resources (3+ nodes with substantial CPU, RAM, and raw disks).

Access modes are a common source of architecture errors. Most cloud block storage (EBS, Azure Disk) only supports RWO -- a single node can mount the volume. Applications requiring shared filesystem access (CMS, legacy apps, build caches) need RWX, which typically requires CephFS (ODF), NFS, or a file-storage CSI driver. Using RWO storage for workloads that need RWX causes pod scheduling failures and data corruption.

StorageClass configuration determines performance, cost, and data protection. The `volumeBindingMode: WaitForFirstConsumer` setting is critical in multi-zone clusters -- it delays PV provisioning until a pod is scheduled, ensuring the volume is created in the same zone as the pod. Without this, pods can become unschedulable if they are assigned a PV in a different zone.

The internal registry requires persistent storage for production (emptyDir is default and loses images on pod restart). Logging with Loki requires object storage (S3, ODF MCG). Prometheus monitoring requires block storage with sufficient IOPS for time-series writes.

## Common Decisions (ADR Triggers)

- **ODF vs cloud-native storage vs third-party CSI**: ODF provides platform independence and RWX but consumes significant cluster resources (dedicated nodes recommended). Cloud-native CSI is simpler and cheaper for RWO-only workloads. Third-party CSI (NetApp, Pure) integrates with existing enterprise storage investments.
- **Storage for databases**: Block storage (RBD, EBS) with high IOPS for databases (PostgreSQL, MongoDB). Avoid NFS for database workloads due to lock contention and performance. Consider local storage operator for lowest latency (at the cost of data locality coupling).
- **Backup strategy for PVs**: CSI snapshots (fast, storage-level) vs OADP/Velero (application-consistent, portable). CSI snapshots are tied to the storage backend; OADP provides cross-cluster portability.
- **Encryption at rest**: ODF cluster-wide encryption (dm-crypt on OSDs) vs per-PV encryption vs relying on infrastructure-level encryption (AWS EBS encryption, vSphere VM encryption). Compliance requirements (FIPS, HIPAA) may mandate specific approaches.
- **Local storage vs distributed storage**: Local storage (NVMe, SSD) provides lowest latency but couples pods to specific nodes. Distributed storage (ODF, cloud block) provides flexibility but adds network latency. Use local storage for etcd, Kafka, and performance-sensitive databases.
- **Multi-cluster storage**: ODF Disaster Recovery (Regional-DR with async mirroring, Metro-DR with sync replication) vs application-level replication vs backup-and-restore for cross-cluster data protection.

## Reference Architectures

- **ODF production cluster**: 3 dedicated ODF nodes (16 vCPU / 64 GB RAM each), 3x replication for block, 2+1 erasure coding for object, CephFS for RWX, MCG/NooBaa for S3-compatible object storage, monitoring via ODF dashboard.
- **Cloud-native storage on AWS**: gp3 EBS for general workloads (StorageClass with `volumeBindingMode: WaitForFirstConsumer`), io2 for high-IOPS databases, EFS CSI for RWX, S3 for registry and Loki object storage.
- **Bare metal high-performance**: Local storage operator for NVMe (etcd, databases), ODF for distributed block and file, MetalLB for storage network traffic, dedicated storage VLAN via Multus.
- **vSphere enterprise**: vSphere CSI driver with StoragePolicy-based management, VMFS or vSAN datastores, thin-provisioned VMDKs, vSphere snapshots integrated with CSI VolumeSnapshot.
- **Hybrid / multi-cluster**: ODF with Regional-DR (async mirroring between clusters), MCG federation for object storage, consistent StorageClass names across clusters for GitOps portability, OADP for cross-cluster backup and restore.

## See Also

- `general/data.md` -- general data architecture patterns
- `providers/kubernetes/storage.md` -- Kubernetes storage patterns (upstream)
- `providers/ceph/storage.md` -- Ceph storage cluster configuration (ODF backend)
- `providers/openshift/data-protection.md` -- backup and snapshot strategies
