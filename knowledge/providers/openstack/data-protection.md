# OpenStack Data Protection and Disaster Recovery

## Checklist

- [ ] Are Cinder volume snapshots used for point-in-time recovery? (snapshots are dependent on the parent volume in Ceph RBD and LVM backends -- they are not independent backups; snapshot quota limits set per project; application-consistent snapshots require quiescing via QEMU guest agent `--force` flag)
- [ ] Are Cinder backups configured to a separate storage target? (`cinder-backup` service with `backup_driver` pointing to Swift, NFS, S3, or a secondary Ceph pool -- backup target must be in a different failure domain from primary Cinder storage)
- [ ] Is backup encryption enabled for Cinder backups? (`backup_ceph_user` with restricted Ceph permissions, or encrypted backup target; Cinder backup does not automatically encrypt -- volume-level LUKS encryption carries through to backups)
- [ ] Is a backup retention policy defined? (automated cleanup of old Cinder backups based on age or count, scheduled via cron or Heat autoscaling alarm actions -- Cinder has no native retention policy engine)
- [ ] Is Swift replication validated across zones? (3x replication across distinct failure zones, `swift-recon --replication` to verify replication lag, ring placement validation with `swift-ring-builder <ring> validate`)
- [ ] Is Swift geo-replication configured for multi-site durability? (container sync for active-active with `X-Container-Sync-To`, or global clusters with region affinity; understand eventual consistency implications for geo-replicated reads)
- [ ] Is Masakari deployed for instance high availability? (monitors compute host failures via `masakari-hostmonitor`, `masakari-instancemonitor`, and `masakari-processmonitor`; auto-evacuates instances from failed hosts to healthy hosts; requires shared storage or boot-from-volume)
- [ ] Is the evacuate vs live-migrate distinction understood and procedures documented? (`nova evacuate` is for failed/unreachable hosts and rebuilds the instance on a new host; `nova live-migrate` is for planned maintenance on healthy hosts -- using evacuate on a healthy host risks data corruption)
- [ ] Is Freezer evaluated for backup and DR? (`freezer-agent` for file-level, volume-level, and database-level backups; supports incremental backups with rsync or tar; `freezer-scheduler` for job scheduling; backup targets include Swift, S3, SSH, local filesystem)
- [ ] Are Trove database instance backups configured? (Trove supports automated full and incremental backups to Swift, backup schedules per database instance, point-in-time recovery for MySQL/MariaDB via binary log position)
- [ ] Is a disaster recovery strategy defined for multi-site OpenStack? (active-passive with Cinder replication to secondary site, active-active with shared Ceph stretched cluster, pilot light with Glance image replication and Heat stack re-creation)
- [ ] Are Nova instance snapshots used for golden image capture and not treated as backups? (instance snapshots upload to Glance and are suitable for image templates but are not application-consistent backups -- they capture disk state, not in-memory state)
- [ ] Is boot-from-volume enforced for instances requiring HA and evacuate capability? (ephemeral disk instances lose data on evacuate; boot-from-volume instances with Cinder survive host failure because the volume is on shared storage)

## Why This Matters

OpenStack does not provide data protection by default -- it provides the building blocks (snapshots, backups, replication) that must be deliberately configured into a protection strategy. Cinder snapshots are commonly mistaken for backups, but they typically share the same storage backend and failure domain as the parent volume (a Ceph pool failure loses both volumes and snapshots). Masakari provides instance HA similar to VMware HA, but only works with boot-from-volume instances on shared storage -- ephemeral instances are rebuilt with empty disks. The evacuate command is destructive on the source host and must only be used when the source host is confirmed down. Without Freezer or an external backup tool, there is no built-in way to perform application-consistent, scheduled, retained backups of instance filesystems. Multi-site DR requires explicit configuration of every layer (Keystone, Glance, Cinder, Neutron) and is not an out-of-the-box capability.

## Common Decisions (ADR Triggers)

- **Snapshot vs backup** -- Cinder snapshots (fast, same storage, dependent on parent) vs Cinder backups (slower, independent copy, separate storage) vs external backup tools (Freezer, Veeam, Commvault) -- RPO requirements and failure domain isolation drive this
- **Instance HA strategy** -- Masakari auto-evacuate (automated, requires shared storage) vs manual evacuate procedures (simpler, operator-driven) vs application-level HA (no platform dependency, workload manages own failover) -- SLA requirements and workload architecture
- **Backup scope** -- volume-level only (Cinder backup) vs file-level (Freezer agent inside instance) vs application-level (database dump + Trove backups) -- granularity of recovery requirements
- **Multi-site DR model** -- active-passive (Cinder replication, DNS failover, longer RTO) vs active-active (stretched Ceph cluster, complex, low RTO/RPO) vs pilot light (minimal standby infrastructure, Heat re-creation, longest RTO) -- cost vs recovery time
- **Boot disk strategy** -- boot-from-volume (survives host failure, Cinder manages lifecycle) vs ephemeral boot disk (faster provisioning, data lost on evacuate, simpler) -- instance HA requirements determine this
- **Backup retention** -- time-based (keep 30 days) vs count-based (keep last 10) vs GFS rotation (daily/weekly/monthly) -- compliance and storage cost constraints
- **Backup orchestration** -- Freezer scheduler (native OpenStack integration) vs external tools (Veeam, Commvault, Rubrik with OpenStack plugins) vs custom scripts with cron -- existing tooling and support requirements
- **Database protection** -- Trove managed backups (automated, integrated) vs application-managed backups (mysqldump/pg_dump in cron) vs Cinder snapshot of database volume (crash-consistent only) -- recovery granularity and consistency requirements

## Version Notes

| Feature | Pike (16) Oct 2017 | Queens (17) Feb 2018 | Rocky (18) Aug 2018 | Stein (19) Apr 2019 | Train (20) Oct 2019 | Ussuri (21) May 2020 | Victoria (22) Oct 2020 | Wallaby (23) Apr 2021 | Xena (24) Oct 2021 | Yoga (25) Mar 2022 | Zed (26) Oct 2022 | 2023.1 Antelope (27) | 2023.2 Bobcat (28) | 2024.1 Caracal (29) | 2024.2 Dalmatian (30) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Masakari (instance HA) | Introduced (incubated) | GA (basic host monitoring) | GA (process monitoring) | GA (recovery workflows) | GA (improved evacuation) | GA | GA (improved host monitor) | GA | GA | GA | GA | GA | GA | GA (improved notifications) | GA |
| Cinder backup (Swift driver) | GA | GA | GA | GA (incremental improvements) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder backup (Ceph driver) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder backup (S3 driver) | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder backup (GCS driver) | Not available | Not available | Not available | Not available | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder backup chunked improvements | Basic | Basic | Improved | Improved | Improved | Improved | Improved | Improved | Improved | Improved | Improved | GA (improved chunked) | GA | GA | GA |
| Cinder volume revert to snapshot | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Freezer (backup/DR) | GA (incubated) | GA | GA | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Retired discussion | Retired discussion | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Effectively retired |
| Nova evacuate | GA | GA | GA | GA (improved error handling) | GA | GA (improved reporting) | GA | GA | GA | GA | GA | GA (improved rebuild) | GA | GA (force options) | GA |
| Nova live-migrate (TLS) | Not available | Not available | Not available | Introduced (QEMU native TLS) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Trove automated backups | GA | GA | GA | GA | GA | GA (redesigned Trove) | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder replication v2.1 | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Boot-from-volume (evacuate support) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Swift geo-replication | GA (container sync) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |

**Key changes across releases:**
- **Masakari evolution (Pike+):** Masakari was incubated in Pike and became an official project in Queens. It provides instance HA by monitoring compute host failures (hostmonitor), instance failures (instancemonitor), and process failures (processmonitor). Recovery workflows improved in Stein with better orchestration of evacuate operations. Masakari requires shared storage or boot-from-volume instances -- ephemeral instances are rebuilt with empty disks on evacuate.
- **Cinder backup driver improvements:** The S3 backup driver was added in Queens, enabling backup to any S3-compatible object store. Google Cloud Storage driver arrived in Ussuri. Chunked backup performance improvements in 2023.1 reduced backup time for large volumes. The backup service should always target storage in a different failure domain from primary Cinder backends.
- **Freezer status changes:** Freezer was an incubated backup and DR project that entered maintenance mode around Stein. Community activity declined significantly, and the project is effectively retired as of Zed/2023.1. Organizations needing file-level backup should consider external tools (Veeam, Commvault, Rubrik with OpenStack plugins) or custom solutions using Cinder backup APIs.
- **Nova evacuate improvements:** Evacuate error handling improved in Stein, reporting improved in Ussuri, and rebuild behavior improved in 2023.1. The `--force` option was added in 2024.1 (Caracal). Evacuate must only be used when the source host is confirmed down -- using it on a healthy host risks data corruption. Boot-from-volume instances survive evacuate because the volume is on shared storage.
- **Nova live-migrate with TLS (Stein+):** QEMU native TLS for live migration was introduced in Stein, encrypting the migration data stream. This eliminates the need for SSH tunnelling (`live_migration_tunnelled`) and provides better performance for encrypted live migration.
- **Trove redesign (Ussuri):** Trove was significantly redesigned in Ussuri with a simplified architecture, improved guest agent, and better integration with modern OpenStack services. Automated backups to Swift with configurable retention continue to be the primary database protection mechanism.
- **Cinder replication v2.1:** Volume replication has been stable across all releases from Pike onward. It enables asynchronous replication between Cinder backends for DR scenarios. Combined with Masakari for compute HA and Cinder replication for storage DR, a comprehensive active-passive DR strategy can be built.
