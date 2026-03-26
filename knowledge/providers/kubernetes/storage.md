# Kubernetes Storage

## Scope

Kubernetes storage: StorageClasses, CSI drivers, StatefulSet storage patterns, access modes (RWO, RWX, ROX), volume snapshots, dynamic provisioning, volume expansion, reclaim policies, local persistent volumes, and backup strategies (Velero).


## Checklist

- [ ] **[Recommended]** Define StorageClasses for each tier: high-performance SSD (io2/pd-ssd), general-purpose (gp3/pd-balanced), cost-optimized HDD (sc1/pd-standard), and set a default StorageClass
- [ ] **[Recommended]** Select and deploy CSI drivers for target storage backends: cloud-native (EBS CSI, GCE PD CSI, Azure Disk CSI), distributed (Ceph/Rook, Longhorn, OpenEBS), or NFS (NFS CSI)
- [ ] **[Critical]** Design StatefulSet storage patterns: VolumeClaimTemplates for per-pod volumes, naming convention (data-{statefulset}-{ordinal}), plan PVC lifecycle on scale-down
- [ ] **[Recommended]** Plan access mode requirements: ReadWriteOnce (block storage, single-node), ReadWriteMany (NFS, EFS, CephFS for shared access), ReadOnlyMany (shared config/data)
- [ ] **[Recommended]** Configure volume snapshots: VolumeSnapshotClass, scheduled snapshots via external tools (Velero, Kasten), snapshot-based cloning for dev/test environments
- [ ] **[Recommended]** Evaluate dynamic provisioning vs pre-provisioned volumes: dynamic for cloud environments, static PVs for on-premises with existing storage arrays
- [ ] **[Recommended]** Plan volume expansion strategy: enable allowVolumeExpansion in StorageClass, understand that expansion is online for some drivers (EBS, GCE PD) but requires restart for others
- [ ] **[Recommended]** Configure reclaim policies: Retain for production data (prevents accidental deletion), Delete for ephemeral/dev environments
- [ ] **[Recommended]** Assess local PV requirements for latency-sensitive workloads (databases, caches): local PVs provide direct disk access but lose data on node failure
- [ ] **[Recommended]** Design backup strategy: Velero for PV snapshots + Kubernetes resource backup, application-level backups (pg_dump, mongodump) for consistency
- [ ] **[Recommended]** Plan storage capacity tracking: enable CSIStorageCapacity for topology-aware scheduling, monitor PVC usage vs capacity for alerting
- [ ] **[Recommended]** Evaluate ephemeral volumes (emptyDir, generic ephemeral) for temporary data: set sizeLimit on emptyDir to prevent node disk exhaustion

## Why This Matters

Storage is the most stateful component in Kubernetes and the hardest to change after deployment. Incorrect StorageClass configuration leads to either performance problems (IOPS-limited applications on HDD-backed storage) or cost waste (SSD-backed storage for cold data). PersistentVolumeClaim lifecycle management is a common source of data loss: deleting a StatefulSet does not delete its PVCs, but deleting a namespace deletes everything including PVCs with Retain policy. Access mode mismatches cause pod scheduling failures that are difficult to diagnose. Volume snapshots and backup strategies are frequently neglected until a data loss incident forces their adoption. The choice between local PVs and network-attached storage fundamentally affects availability: local PVs are faster but create node-level single points of failure.

## Common Decisions (ADR Triggers)

- **Network-attached storage vs local PVs**: Network-attached (EBS, GCE PD, Ceph) allows pod rescheduling to any node and survives node failure. Local PVs (direct-attached SSD) provide lower latency and higher IOPS but tie pods to specific nodes and lose data on node failure. Use local PVs only for workloads that handle replication at the application level (Cassandra, Elasticsearch, CockroachDB). Never use local PVs for single-instance databases.
- **Rook/Ceph vs Longhorn vs cloud-native storage**: Rook/Ceph provides enterprise-grade distributed storage (block, file, object) but is complex to operate and requires dedicated storage nodes. Longhorn is simpler with built-in backup/DR but lower performance ceiling. Cloud-native CSI drivers are simplest but lock you into one cloud. Use Rook/Ceph for on-premises or multi-cloud with demanding requirements; Longhorn for simpler on-premises; cloud-native for single-cloud.
- **ReadWriteOnce vs ReadWriteMany**: RWO (block storage) is performant and widely available but limits pods to a single node. RWX (NFS, EFS, CephFS) allows multi-node access but with lower performance and POSIX compliance caveats. Avoid RWX unless genuinely needed (shared uploads, CMS content); refactor applications to use object storage (S3/R2) instead of shared filesystems where possible.
- **Volume snapshots vs application-level backups**: Volume snapshots are fast (copy-on-write) and storage-agnostic but may capture inconsistent state if the application is mid-write. Application-level backups (pg_dump, mongodump with --oplog) ensure consistency but are slower and application-specific. Use both: application-level for guaranteed consistency, volume snapshots for fast point-in-time recovery.
- **Retain vs Delete reclaim policy**: Retain prevents PV deletion when PVC is deleted but creates orphaned PVs that require manual cleanup. Delete automates cleanup but risks accidental data loss. Use Retain for production stateful workloads; Delete for development/ephemeral environments. Implement alerting on orphaned PVs.

## Reference Architectures

### Multi-Tier Storage Configuration
```yaml
# High-performance tier (databases)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: high-perf-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: io2
  iopsPerGB: "50"
  encrypted: "true"
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer

# General-purpose tier (application state)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: general-purpose
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  encrypted: "true"
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer

# Cost-optimized tier (logs, archives)
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: cold-storage
provisioner: ebs.csi.aws.com
parameters:
  type: sc1
  encrypted: "true"
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```
WaitForFirstConsumer delays PV provisioning until a pod is scheduled, enabling topology-aware placement (correct AZ). Encryption enabled on all tiers. Retain policy on production tiers prevents accidental data loss.

### StatefulSet with Volume Claim Templates
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
spec:
  replicas: 3
  serviceName: postgresql
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: high-perf-ssd
        resources:
          requests:
            storage: 100Gi
    - metadata:
        name: wal
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: high-perf-ssd
        resources:
          requests:
            storage: 20Gi
  template:
    spec:
      containers:
        - name: postgresql
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
            - name: wal
              mountPath: /var/lib/postgresql/wal
```
Separate PVCs for data and WAL (write-ahead log) allow independent IOPS tuning. PVCs are named `data-postgresql-0`, `data-postgresql-1`, etc. On StatefulSet deletion, PVCs persist (Retain policy) and reattach when StatefulSet is recreated. Scale-down preserves PVCs for future scale-up.

### Backup and Recovery Pipeline
```
[Velero] --> [Scheduled Backup]
                  |
        +---------+---------+
        |                   |
  [K8s Resource Backup]  [Volume Snapshots]
  (etcd objects to S3)   (CSI VolumeSnapshot)
        |                   |
  [Restore Target]     [Snapshot Clone]
  (new namespace/cluster)  (dev/test from prod snapshot)
        |
  [Application-Level Backup (parallel)]
  - PostgreSQL: pg_basebackup + WAL archiving to S3
  - MongoDB: mongodump --oplog to S3
  - Elasticsearch: snapshot API to S3 repository
```
Velero handles both Kubernetes resource backup (Deployments, ConfigMaps, Secrets) and PV snapshots via CSI. Application-level backups run in parallel for consistency guarantees. Snapshot cloning enables fast dev/test environment creation from production data (with data masking applied post-clone).

## Reference Links

- [Kubernetes Storage](https://kubernetes.io/docs/concepts/storage/) -- PersistentVolumes, PersistentVolumeClaims, StorageClasses, and CSI drivers
- [Volume Snapshots](https://kubernetes.io/docs/concepts/storage/volume-snapshots/) -- VolumeSnapshot, VolumeSnapshotClass, and snapshot-based cloning
- [Dynamic Volume Provisioning](https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/) -- StorageClass configuration and automatic PV provisioning

## See Also

- `general/data.md` -- general data architecture patterns
- `providers/kubernetes/compute.md` -- StatefulSet workload patterns
- `providers/ceph/storage.md` -- Ceph/Rook CSI storage backend
- `providers/kubernetes/operations.md` -- backup and restore procedures
