# VMware Data Protection

## Scope

This document covers VMware data protection capabilities including vSphere Replication, VCF Live Site Recovery (formerly Site Recovery Manager / SRM), backup integration via VADP, snapshot management, and DR planning.

## Checklist

- [ ] **[Critical]** Is vSphere Replication configured for VMs requiring asynchronous replication to a secondary site, with RPO settings appropriate to the workload (minimum 5 minutes for critical, 15-60 minutes for standard) and network bandwidth sized for the replication throughput?
- [ ] **[Critical]** Is VCF Live Site Recovery (formerly VMware Site Recovery Manager / SRM) deployed for orchestrated disaster recovery with documented recovery plans, including VM startup order, IP address re-mapping, and pre/post recovery scripts for application consistency?
- [ ] **[Critical]** Are VCF Live Site Recovery recovery plans tested on a scheduled basis (quarterly minimum) using non-disruptive test failover to an isolated network, with test results documented for compliance and DR readiness validation?
- [ ] **[Critical]** Is the backup solution (Veeam, Commvault, Dell Avamar, Cohesity, Rubrik) integrated via VADP (vStorage APIs for Data Protection) using Changed Block Tracking (CBT) for incremental-forever backup with minimal impact on production VMs?
- [ ] **[Critical]** Are VM snapshots used only as short-term recovery points (during patching, upgrades) and actively monitored for snapshot sprawl, with alerts at 24-48 hours age and automated deletion policies to prevent snapshot chains from degrading performance and consuming datastore space?
- [ ] **[Recommended]** Is application-consistent quiescing configured for backup snapshots (VMware Tools quiescing or application-specific VSS/pre-freeze/post-thaw scripts) to ensure database and application integrity at recovery time?
- [ ] **[Critical]** Are RPO and RTO targets documented per application tier, with backup/replication schedules validated against those targets and gap analysis performed for workloads where current protection does not meet the stated objectives?
- [ ] **[Critical]** Is the 3-2-1 backup rule followed (3 copies of data, on 2 different media types, with 1 offsite) with at least one copy air-gapped or immutable to protect against ransomware encryption of backup repositories?
- [ ] **[Recommended]** Are vSAN native snapshots (available in vSAN ESA / vSAN 8+) evaluated as an alternative to traditional VM snapshots, offering improved performance with no snapshot chain penalty and better space efficiency?
- [ ] **[Recommended]** Is backup proxy architecture designed for scale -- dedicated physical or virtual backup proxies with Hot-Add transport mode (for SAN-less environments) or Direct SAN transport mode (for block storage) to avoid NBD (Network Block Device) bottlenecks?
- [ ] **[Recommended]** Are backup retention policies aligned with regulatory and business requirements, with separate tiers for operational recovery (7-30 days, fast storage), compliance (1-7 years, object storage or tape), and legal hold (indefinite, immutable)?
- [ ] **[Optional]** Is VM-level backup exclusion configured to skip ephemeral VMs (test/dev, CI/CD runners) and large data disks that are protected by other means (database-native replication, object storage), reducing backup window and storage costs?
- [ ] **[Recommended]** Is VCF Live Site Recovery paired with vSphere Replication (for small-scale, no SAN requirement) or array-based replication (NetApp SnapMirror, Pure ActiveCluster, Dell SRDF) for large-scale DR with storage-level efficiency?

## Why This Matters

Data protection failures are discovered at the worst possible time -- during recovery. Untested VCF Live Site Recovery (formerly SRM) recovery plans frequently fail due to stale configurations (removed VMs, changed networks, expired credentials), making regular non-disruptive testing essential rather than optional. VM snapshots are the most misunderstood vSphere feature: they are not backups, they degrade VM performance proportionally to chain length, and a snapshot chain consuming an entire datastore causes all VMs on that datastore to pause. CBT (Changed Block Tracking) bugs have historically caused silent backup corruption (KB 2090639, KB 86234), requiring periodic CBT resets as a preventive measure. Backup proxy sizing directly determines the backup window -- insufficient proxies extend backup jobs into production hours. Ransomware increasingly targets backup infrastructure itself, making immutable or air-gapped backup copies a requirement rather than a best practice.

## Common Decisions (ADR Triggers)

- **vSphere Replication vs array-based replication** -- vSphere Replication for storage-agnostic, per-VM replication with 5-minute RPO vs array-based replication (SnapMirror, SRDF) for sub-minute RPO, storage-level deduplication, and lower ESXi host overhead at scale
- **VCF Live Site Recovery vs manual DR runbooks** -- VCF Live Site Recovery (formerly SRM) for automated, tested, repeatable DR orchestration vs manual runbooks for environments too small to justify licensing or with non-VMware DR targets
- **Backup platform selection** -- Veeam (market leader, broad feature set, per-VM licensing) vs Commvault (enterprise breadth, complex) vs Cohesity/Rubrik (scale-out, immutable by design) vs Dell Avamar/NetWorker (Dell ecosystem integration)
- **Backup transport mode** -- Hot-Add (backup proxy mounts VM disks, no SAN required, good for vSAN) vs Direct SAN (fastest, requires SAN zoning to proxy) vs NBD/NBDSSL (network-based, slowest, most flexible)
- **Snapshot policy enforcement** -- automated snapshot age monitoring with auto-delete vs manual review; VMware recommends no snapshot older than 72 hours and no chain deeper than 3 levels
- **Immutable backup architecture** -- Linux hardened repository (XFS, immutable flag) vs object storage with object lock (S3, MinIO) vs purpose-built appliance (Cohesity, Rubrik) vs tape for air-gap
- **RPO/RTO tiering** -- Tier 1 (RPO <15min, RTO <1hr, synchronous replication + VCF Live Site Recovery) vs Tier 2 (RPO <1hr, RTO <4hr, async replication + backup) vs Tier 3 (RPO <24hr, RTO <24hr, daily backup only)
- **vSAN native snapshots vs traditional snapshots** -- vSAN ESA native snapshots for improved snapshot performance without chain penalty vs traditional snapshots for vSAN OSA and non-vSAN environments
