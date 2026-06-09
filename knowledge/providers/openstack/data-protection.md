# OpenStack Data Protection and Disaster Recovery

## Scope

Covers OpenStack data protection and disaster recovery: Cinder volume snapshots and backups, Swift replication, Masakari instance HA, Nova evacuate and live migration, Freezer backup (retired), Trove database backups, multi-site DR strategies, and boot-from-volume considerations.

## Checklist

- [ ] **[Critical]** Are Cinder volume snapshots used for point-in-time recovery? (snapshots are dependent on the parent volume in Ceph RBD and LVM backends -- they are not independent backups; snapshot quota limits set per project; application-consistent snapshots require quiescing via QEMU guest agent `--force` flag)
- [ ] **[Critical]** Are Cinder backups configured to a separate storage target? (`cinder-backup` service with `backup_driver` pointing to Swift, NFS, S3, or a secondary Ceph pool -- backup target must be in a different failure domain from primary Cinder storage)
- [ ] **[Critical]** Is the evacuate vs live-migrate distinction understood and procedures documented? (`nova evacuate` is for failed/unreachable hosts and rebuilds the instance on a new host; `nova live-migrate` is for planned maintenance on healthy hosts -- using evacuate on a healthy host risks data corruption)
- [ ] **[Critical]** Is boot-from-volume enforced for instances requiring HA and evacuate capability? (ephemeral disk instances lose data on evacuate; boot-from-volume instances with Cinder survive host failure because the volume is on shared storage)
- [ ] **[Recommended]** Is backup encryption enabled for Cinder backups? (`backup_ceph_user` with restricted Ceph permissions, or encrypted backup target; Cinder backup does not automatically encrypt -- volume-level LUKS encryption carries through to backups)
- [ ] **[Recommended]** Is a backup retention policy defined? (automated cleanup of old Cinder backups based on age or count, scheduled via cron or Heat autoscaling alarm actions -- Cinder has no native retention policy engine)
- [ ] **[Recommended]** Is Swift replication validated across zones? (3x replication across distinct failure zones, `swift-recon --replication` to verify replication lag, ring placement validation with `swift-ring-builder <ring> validate`)
- [ ] **[Recommended]** Is Masakari deployed for instance high availability? (monitors compute host failures via `masakari-hostmonitor`, `masakari-instancemonitor`, and `masakari-processmonitor`; auto-evacuates instances from failed hosts to healthy hosts; requires shared storage or boot-from-volume)
- [ ] **[Recommended]** Are Trove database instance backups configured? (Trove supports automated full and incremental backups to Swift, backup schedules per database instance, point-in-time recovery for MySQL/MariaDB via binary log position)
- [ ] **[Recommended]** Are Nova instance snapshots used for golden image capture and not treated as backups? (instance snapshots upload to Glance and are suitable for image templates but are not application-consistent backups -- they capture disk state, not in-memory state)
- [ ] **[Critical]** Is the **dependent vs independent** nature of each protection artifact understood and reflected in deletion order? (Cinder *volume snapshots* are **dependent** -- they live on the parent volume's storage and **block volume deletion** until released; Cinder *backups* and Nova→Glance *image snapshots* are **independent** -- separate storage, survive the source, and **become orphans**. Mixing these up causes both "cannot delete volume, has dependent snapshots" failures and silent orphan accumulation.)
- [ ] **[Critical]** Are **snapshot trees** (clone-from-snapshot / child volumes created from a snapshot) mapped before any cascade delete? (`openstack volume delete --cascade` and delete-with-snapshots behavior is **backend-specific**: Ceph RBD enforces parent/child via COW clones and `flatten`, LVM uses thin-pool dependencies, and vendor drivers vary -- a naive cascade can fail mid-chain or, worse, remove a snapshot another volume still depends on. Confirm what `--cascade` actually does on the deployed backend.)
- [ ] **[Critical]** Is **Nova→Glance image-snapshot orphan reclamation** implemented? (an instance snapshot uploads a full, independent image to Glance that **persists after the source instance is deleted** -- driving image-store growth and cost; identify images with no referencing instance, but treat `protected`, `public`/`community`/`shared`, and in-use base images as do-not-delete, and key reclamation on the image/instance UUID, never the name.)
- [ ] **[Recommended]** Are **array-managed snap copies** from third-party Cinder snapshot integrations (IntelliSnap-style hardware snapshots, vendor SnapMirror/SnapVault-backed snapshots) treated as **dependent** objects that must be released through Cinder, not deleted directly on the array? (deleting on the array out-of-band leaves Cinder's catalog referencing a snapshot that no longer exists -- a state mismatch requiring `cinder reset-state` to repair.)
- [ ] **[Recommended]** Is the **boot-disk strategy** recognized as the hinge that determines which lifecycle failure mode dominates per instance? (boot-from-volume → Cinder volume + snapshot tree → the *dependent/blocking* path dominates, release snapshots before deleting the VM; ephemeral → no Cinder volume to snapshot → Nova→Glance images + external backups → the *independent/orphan* path dominates. A mixed estate carries **both** failure modes, selected per VM by boot-disk type.)
- [ ] **[Recommended]** Are **immutable / WORM targets** configured for Cinder backups where ransomware or preservation requirements apply? (Swift object versioning or Ceph RGW S3 **Object Lock** on the backup container for WORM; Barbican-managed keys for encrypted backup targets; placement in a separate failure domain -- the OpenStack mapping of the general patterns in `general/ransomware-resilience.md`.)
- [ ] **[Critical]** Does any automated snapshot/image/backup reclamation **consult the legal-hold gate before deleting**? (an object under preservation must not be aged out or reclaimed even when it is a dependent snapshot blocking a delete or an independent orphan costing money -- see `general/legal-hold.md`; reclamation must fail safe to no-delete-and-escalate when hold status is unknown.)
- [ ] **[Optional]** Is Swift geo-replication configured for multi-site durability? (container sync for active-active with `X-Container-Sync-To`, or global clusters with region affinity; understand eventual consistency implications for geo-replicated reads)
- [ ] **[Optional]** Is Freezer evaluated for backup and DR? (Retired -- effectively retired since Zed/2023.1; for file-level backups use external tools such as Veeam, Commvault, Rubrik with OpenStack plugins, or custom solutions using Cinder backup APIs)
- [ ] **[Optional]** Is a disaster recovery strategy defined for multi-site OpenStack? (active-passive with Cinder replication to secondary site, active-active with shared Ceph stretched cluster, pilot light with Glance image replication and Heat stack re-creation)

## Why This Matters

OpenStack does not provide data protection by default -- it provides the building blocks (snapshots, backups, replication) that must be deliberately configured into a protection strategy. Cinder snapshots are commonly mistaken for backups, but they typically share the same storage backend and failure domain as the parent volume (a Ceph pool failure loses both volumes and snapshots). Masakari provides instance HA similar to VMware HA, but only works with boot-from-volume instances on shared storage -- ephemeral instances are rebuilt with empty disks. The evacuate command is destructive on the source host and must only be used when the source host is confirmed down. Without an external backup tool, there is no built-in way to perform application-consistent, scheduled, retained backups of instance filesystems (Freezer is retired). Multi-site DR requires explicit configuration of every layer (Keystone, Glance, Cinder, Neutron) and is not an out-of-the-box capability.

## Snapshot and Image Lifecycle: Dependent vs Independent Artifacts

OpenStack creates several kinds of protection artifact, and the single most useful axis for reasoning about their lifecycle is **dependent vs independent**. It determines deletion order, which failure mode an estate suffers, and how reclamation must behave. This is the OpenStack-native half of the lifecycle that the third-party-backup pattern (`patterns/backup-lifecycle-synchronization.md`) does not cover: the snapshots and images OpenStack itself produces.

| Artifact | Class | Storage | On source delete |
|---|---|---|---|
| Cinder volume snapshot | **Dependent** | Same backend as parent volume | **Blocks** parent volume deletion until released |
| Array-managed snap copy (vendor integration) | **Dependent** | On the array, referenced by Cinder | Blocks until released *through Cinder* |
| Cinder backup | **Independent** | Separate target (Swift/NFS/S3/secondary Ceph) | Survives → **orphan** |
| Nova→Glance image snapshot | **Independent** | Glance image store | Survives → **orphan** |

### Dependent artifacts -- release first, they block deletion

A **Cinder volume snapshot** lives on the parent volume's storage and is dependent on it; the volume cannot be deleted while it has snapshots (`Cannot delete volume ...: has dependent snapshots`). The lifecycle rule is therefore *release dependents before deleting the parent*: enumerate and delete (or detach into independence) the snapshots first.

**Snapshot trees** make this non-trivial. A snapshot can be the parent of a *clone* (`openstack volume create --snapshot <snap>`), and on copy-on-write backends the clone depends on the snapshot's blocks. The dependency graph is backend-specific:
- **Ceph RBD** -- snapshots and clones are COW; a snapshot with children cannot be removed until the children are `flatten`ed (copied to independence) or deleted. `--cascade` orchestrates this but can be expensive (flatten copies data).
- **LVM** -- thin-pool dependencies; deleting in the wrong order can fail or leave dangling thin devices.
- **Vendor drivers** -- each implements snapshot/clone dependency differently; `--cascade` and delete-with-snapshots semantics vary, so verify against the deployed driver rather than assuming.

The practical guidance: never issue a naive `--cascade` against a tree you have not mapped, and never delete an array snapshot **out-of-band on the array** -- release it through Cinder so the Cinder catalog stays consistent (an out-of-band delete leaves a phantom snapshot record needing `cinder reset-state` to repair).

### Independent artifacts -- they become orphans

A **Nova instance snapshot** uploads a **full, independent image to Glance**. It does not depend on the instance and is not freed when the instance is deleted -- it simply persists in the image store, accumulating cost. Orphan reclamation means identifying Glance images with no referencing instance and no role as a base image, with caveats: `protected` images cannot be deleted until unprotected; `public`/`community`/`shared` images may serve other projects; and base images backing running instances must not be touched. Key the reclamation on the image and instance **UUID**, never the display name (a reused name mis-correlates -- the same join-key discipline as the backup-lifecycle pattern).

A **Cinder backup** is likewise independent (its whole purpose is a separate-failure-domain copy) and likewise orphans when its source volume is deleted, since Cinder has no native retention engine (see the retention checklist item) -- the backup persists until something explicitly prunes it.

### Boot-disk strategy is the hinge

Which failure mode dominates is selected per instance by its boot disk:
- **Boot-from-volume** → a Cinder volume (often with a snapshot tree) → the **dependent/blocking** path dominates: snapshots must be released before the VM/volume can be deleted, and cascade order matters.
- **Ephemeral boot disk** → no Cinder volume to snapshot → protection is Nova→Glance images plus external backups → the **independent/orphan** path dominates: nothing blocks deletion, but images and backups linger.

A real estate runs both, so it carries **both** failure modes simultaneously, keyed off each VM's boot-disk type -- the deletion runbook and any reclamation automation must branch on boot-disk type rather than assuming one model.

### OpenStack-specific immutability

The immutability concepts in `general/ransomware-resilience.md` map onto OpenStack targets: **Swift object versioning** (`X-Versions-Location` / `X-History-Location`) and **Ceph RGW S3 Object Lock** provide WORM for Cinder backup containers; **Barbican** supplies managed keys for encrypted backup targets; and the backup target must sit in a **separate failure domain** from primary Cinder storage. For preservation (not just ransomware), an immutable backup target in legal-hold mode is the storage-enforced implementation of the hold gate described in `general/legal-hold.md`.

## Common Decisions (ADR Triggers)

- **Snapshot vs backup** -- Cinder snapshots (fast, same storage, dependent on parent) vs Cinder backups (slower, independent copy, separate storage) vs external backup tools (Veeam, Commvault) -- Freezer is retired; RPO requirements and failure domain isolation drive this
- **Dependent-snapshot deletion order** -- release snapshots before parent volume; map snapshot trees and choose flatten-to-independence vs cascade-delete (backend-specific: Ceph RBD COW + flatten, LVM thin-pool, vendor drivers) -- naive `--cascade` risk vs explicit ordered teardown
- **Image-orphan reclamation policy** -- automatically reclaim unreferenced Glance instance-snapshot images vs retain (protected/public/base-image caveats); UUID-keyed identification; whether reclamation is gated by approval and legal hold
- **Boot-disk strategy as lifecycle driver** -- boot-from-volume (dependent/blocking path, snapshot release before delete) vs ephemeral (independent/orphan path, image+backup cleanup) -- HA needs and lifecycle-cleanup model both follow from this single choice
- **Instance HA strategy** -- Masakari auto-evacuate (automated, requires shared storage) vs manual evacuate procedures (simpler, operator-driven) vs application-level HA (no platform dependency, workload manages own failover) -- SLA requirements and workload architecture
- **Backup scope** -- volume-level only (Cinder backup) vs file-level (external agent inside instance) vs application-level (database dump + Trove backups) -- granularity of recovery requirements
- **Multi-site DR model** -- active-passive (Cinder replication, DNS failover, longer RTO) vs active-active (stretched Ceph cluster, complex, low RTO/RPO) vs pilot light (minimal standby infrastructure, Heat re-creation, longest RTO) -- cost vs recovery time
- **Boot disk strategy** -- boot-from-volume (survives host failure, Cinder manages lifecycle) vs ephemeral boot disk (faster provisioning, data lost on evacuate, simpler) -- instance HA requirements determine this
- **Backup retention** -- time-based (keep 30 days) vs count-based (keep last 10) vs GFS rotation (daily/weekly/monthly) -- compliance and storage cost constraints
- **Backup orchestration** -- external tools (Veeam, Commvault, Rubrik with OpenStack plugins) vs custom scripts with cron -- Freezer is retired; existing tooling and support requirements drive this
- **Database protection** -- Trove managed backups (automated, integrated) vs application-managed backups (mysqldump/pg_dump in cron) vs Cinder snapshot of database volume (crash-consistent only) -- recovery granularity and consistency requirements

## Version Notes

| Feature | Pike (16) Oct 2017 | Queens (17) Feb 2018 | Rocky (18) Aug 2018 | Stein (19) Apr 2019 | Train (20) Oct 2019 | Ussuri (21) May 2020 | Victoria (22) Oct 2020 | Wallaby (23) Apr 2021 | Xena (24) Oct 2021 | Yoga (25) Mar 2022 | Zed (26) Oct 2022 | 2023.1 Antelope (27) | 2023.2 Bobcat (28) | 2024.1 Caracal (29) | 2024.2 Dalmatian (30) | 2025.1 Epoxy (31) | 2025.2 Flamingo (32) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Masakari (instance HA) | Introduced (incubated) | GA (basic host monitoring) | GA (process monitoring) | GA (recovery workflows) | GA (improved evacuation) | GA | GA (improved host monitor) | GA | GA | GA | GA | GA | GA | GA (improved notifications) | GA | GA | GA |
| Cinder backup (Swift driver) | GA | GA | GA | GA (incremental improvements) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder backup (Ceph driver) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder backup (S3 driver) | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder backup (GCS driver) | Not available | Not available | Not available | Not available | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder backup chunked improvements | Basic | Basic | Improved | Improved | Improved | Improved | Improved | Improved | Improved | Improved | Improved | GA (improved chunked) | GA | GA | GA | GA | GA |
| Cinder volume revert to snapshot | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Freezer (backup/DR) | GA (incubated) | GA | GA | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Retired discussion | Retired discussion | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Retired | Retired |
| Nova evacuate | GA | GA | GA | GA (improved error handling) | GA | GA (improved reporting) | GA | GA | GA | GA | GA | GA (improved rebuild) | GA | GA (force options) | GA | GA | GA |
| Nova live-migrate (TLS) | Not available | Not available | Not available | Introduced (QEMU native TLS) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Trove automated backups | GA | GA | GA | GA | GA | GA (redesigned Trove) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder replication v2.1 | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Boot-from-volume (evacuate support) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Swift geo-replication | GA (container sync) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |

**Key changes across releases:**
- **Masakari evolution (Pike+):** Masakari was incubated in Pike and became an official project in Queens. It provides instance HA by monitoring compute host failures (hostmonitor), instance failures (instancemonitor), and process failures (processmonitor). Recovery workflows improved in Stein with better orchestration of evacuate operations. Masakari requires shared storage or boot-from-volume instances -- ephemeral instances are rebuilt with empty disks on evacuate.
- **Cinder backup driver improvements:** The S3 backup driver was added in Queens, enabling backup to any S3-compatible object store. Google Cloud Storage driver arrived in Ussuri. Chunked backup performance improvements in 2023.1 reduced backup time for large volumes. The backup service should always target storage in a different failure domain from primary Cinder backends.
- **Freezer retirement:** Freezer was an incubated backup and DR project that entered maintenance mode around Stein. Community activity declined significantly, and the project is effectively retired as of Zed/2023.1 and fully retired in Epoxy (2025.1). Organizations needing file-level backup should use external tools (Veeam, Commvault, Rubrik with OpenStack plugins) or custom solutions using Cinder backup APIs.
- **Nova evacuate improvements:** Evacuate error handling improved in Stein, reporting improved in Ussuri, and rebuild behavior improved in 2023.1. The `--force` option was added in 2024.1 (Caracal). Evacuate must only be used when the source host is confirmed down -- using it on a healthy host risks data corruption. Boot-from-volume instances survive evacuate because the volume is on shared storage.
- **Nova live-migrate with TLS (Stein+):** QEMU native TLS for live migration was introduced in Stein, encrypting the migration data stream. This eliminates the need for SSH tunnelling (`live_migration_tunnelled`) and provides better performance for encrypted live migration.
- **Trove redesign (Ussuri):** Trove was significantly redesigned in Ussuri with a simplified architecture, improved guest agent, and better integration with modern OpenStack services. Automated backups to Swift with configurable retention continue to be the primary database protection mechanism.
- **Cinder replication v2.1:** Volume replication has been stable across all releases from Pike onward. It enables asynchronous replication between Cinder backends for DR scenarios. Combined with Masakari for compute HA and Cinder replication for storage DR, a comprehensive active-passive DR strategy can be built.
- **Epoxy (2025.1) data protection changes:** Freezer fully retired. Continued Cinder backup performance improvements. Masakari stability improvements.
- **Flamingo (2025.2) data protection changes:** Continued improvements to Cinder replication and backup reliability. No major new data protection features.

## Reference Links

- [OpenStack backup and recovery guide](https://docs.openstack.org/operations-guide/ops-backup-recovery.html) -- control plane and data backup strategies for OpenStack
- [Cinder backup service](https://docs.openstack.org/cinder/latest/admin/backup.html) -- volume backup to Swift, NFS, or Ceph and restore procedures

## See Also

- `general/disaster-recovery.md` -- general DR planning (RPO/RTO, tiering)
- `general/enterprise-backup.md` -- enterprise backup architecture patterns
- `providers/openstack/storage.md` -- Cinder snapshots and Swift replication
- `providers/openstack/control-plane-ha.md` -- control plane HA and recovery
- `patterns/backup-lifecycle-synchronization.md` -- third-party-backup lifecycle sync; this file is the OpenStack-native (snapshot/image) companion
- `providers/openstack/operations.md` -- consuming `instance.delete.end` to trigger snapshot/image reclamation workflows
- `general/legal-hold.md` -- the preservation gate any snapshot/image/backup reclamation must consult before deleting
- `general/ransomware-resilience.md` -- immutable/WORM and failure-domain isolation patterns mapped onto Cinder backup targets above
