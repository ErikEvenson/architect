# OpenShift Data Protection

## Checklist

- [ ] **[Critical]** Deploy OADP operator (OpenShift API for Data Protection) with Velero and appropriate plugins (AWS, Azure, GCP, CSI)
- [ ] **[Critical]** Configure backup storage location (BSL): S3-compatible object storage (AWS S3, MinIO, ODF MCG)
- [ ] **[Critical]** Configure volume snapshot location (VSL): CSI snapshots for block storage, Restic/Kopia for filesystem-level backup
- [ ] **[Critical]** Define scheduled backup policies via `Schedule` CRDs: daily application backups, weekly full-cluster backups
- [ ] **[Critical]** Implement etcd backup and restore procedures: automated CronJob or manual `etcdctl snapshot save` via debug pod
- [ ] **[Recommended]** Design namespace-level backup strategy: label selectors for application grouping, include/exclude resource filters
- [ ] **[Critical]** Test restore procedures regularly: full namespace restore, single resource restore, cross-cluster restore
- [ ] **[Recommended]** Plan PV backup approach: CSI VolumeSnapshot (fast, storage-level) vs Restic/Kopia (portable, file-level, slower)
- [ ] **[Critical]** Configure backup encryption: Velero supports server-side encryption (SSE-S3, SSE-KMS) for backup artifacts
- [ ] **[Recommended]** Set retention policies: backup TTL per schedule, snapshot lifecycle, storage cost management
- [ ] **[Critical]** Document disaster recovery runbook: cluster rebuild, etcd restore, application restore priorities (RPO/RTO targets)
- [ ] **[Optional]** Evaluate RHACM for multi-cluster failover: managed cluster backup, hub recovery, application DR policies
- [ ] **[Recommended]** Plan GitOps-based DR: rebuild cluster from Git (infrastructure-as-code + GitOps manifests) vs restore from backup
- [ ] **[Critical]** Back up cluster configuration: OAuth, certificates, custom CRDs, operator configurations, cluster-scoped resources

## Why This Matters

Data protection in OpenShift spans two distinct domains: cluster-level protection (etcd, certificates, cluster configuration) and application-level protection (namespaces, deployments, PVs, secrets). Losing etcd means losing the entire cluster state -- every API object, every secret, every certificate. OADP handles application-level backup and restore but does not back up etcd or cluster-scoped configuration. These are complementary, not substitutes.

OADP is built on Velero and provides `Backup`, `Restore`, and `Schedule` CRDs. A backup captures Kubernetes resources (stored as JSON in object storage) and optionally snapshots persistent volumes. The CSI plugin uses `VolumeSnapshot` objects for fast, storage-level snapshots (seconds for block storage). The Restic/Kopia integration provides file-level backup for storage backends that do not support CSI snapshots -- it is portable across storage providers but significantly slower for large volumes.

etcd backup is a separate concern. The recommended approach is to run `etcdctl snapshot save` from a control plane node debug pod or automate it via a CronJob that mounts the etcd data directory. The backup produces a single file that can restore the full cluster state. etcd backups should be stored off-cluster (S3, NFS) and tested regularly.

Disaster recovery strategy depends on RPO (how much data loss is acceptable) and RTO (how quickly recovery must complete). GitOps-based DR (rebuild from Git + restore PV data) is slower but more reliable for complex environments. Backup-based DR (OADP restore to a standby cluster) is faster but requires consistent backup schedules and tested restore procedures. RHACM adds managed cluster backup and application failover policies for multi-cluster architectures.

A common failure mode is backing up everything but never testing restores. Backup validation -- including periodic restore drills to a non-production cluster -- is as important as the backup itself. OADP supports backup validation via the `Restore` CRD with namespace mapping (restore to a different namespace for validation).

## Common Decisions (ADR Triggers)

- **CSI snapshots vs Restic/Kopia**: CSI snapshots are fast and atomic but tied to the storage provider (cannot restore to a different storage backend). Restic/Kopia is slower but portable. Many organizations use CSI snapshots for operational recovery (fast rollback) and Restic/Kopia for disaster recovery (cross-cluster portability).
- **Backup scope**: Namespace-level (fine-grained, team-managed) vs cluster-level (coarse, platform-managed). Namespace-level backups are easier to test and restore. Cluster-level backups capture cross-namespace dependencies but are harder to partially restore.
- **DR strategy**: Active-passive (standby cluster with OADP restore) vs active-active (application-level replication) vs rebuild-from-Git (GitOps + PV restore). Active-passive is simplest. Active-active requires application-level replication (database replication, event streaming). Rebuild-from-Git is slowest but most resilient to infrastructure-level failures.
- **etcd backup frequency**: Hourly (low RPO, more storage) vs daily (higher RPO, less storage). etcd backups are typically small (hundreds of MB) so hourly is feasible. Critical to take a backup before cluster upgrades.
- **RHACM for DR**: RHACM provides `ManagedClusterBackup` for hub cluster DR and `ApplicationDRPlacement` for workload failover. Evaluate whether the RHACM subscription cost is justified vs manual DR procedures.
- **Backup storage location**: Same region (fast backup, shared failure domain) vs cross-region (slower backup, independent failure domain). Cross-region is recommended for true DR. Consider multi-cloud backup (e.g., on-prem cluster backing up to AWS S3) for infrastructure independence.

## Reference Architectures

- **Standard production DR**: OADP with daily scheduled backups (CSI snapshots for PVs, 30-day retention), etcd backup CronJob every 4 hours to S3, GitOps repo as source of truth for cluster configuration, quarterly restore drills, RPO 4 hours / RTO 4 hours.
- **Regulated environment (finance, healthcare)**: OADP with hourly backups, CSI snapshots with cross-region replication (ODF Regional-DR), etcd backup every hour, encrypted backup storage (SSE-KMS), documented restore runbook with compliance attestation, RPO 1 hour / RTO 2 hours.
- **Multi-cluster DR with RHACM**: Hub cluster with ManagedClusterBackup, spoke clusters with OADP, ApplicationDRPlacement policies for automated failover, ODF Metro-DR for synchronous PV replication (RPO ~0), application placement rules for active-passive failover.
- **GitOps-first DR**: Cluster infrastructure defined in Terraform/Ansible, all application manifests in Git (ArgoCD), OADP only for stateful PV data, restore procedure: provision new cluster -> bootstrap ArgoCD -> sync from Git -> restore PV snapshots from S3. RTO 2-4 hours depending on cluster size.
- **Edge / remote site DR**: SNO (Single Node OpenShift) clusters managed by RHACM, OADP with Restic to central S3 (no CSI snapshots on some edge storage), application state replicated to hub via Kafka/MQTT, edge rebuild via ZTP (Zero Touch Provisioning) from hub cluster, RPO 24 hours / RTO 4 hours.
