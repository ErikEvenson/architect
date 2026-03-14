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
