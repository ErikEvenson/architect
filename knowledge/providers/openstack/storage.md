# OpenStack Storage (Cinder, Swift, Manila, Glance)

## Checklist

- [ ] Is the Cinder backend selected and configured? (Ceph RBD for scale-out unified storage, LVM/iSCSI for simple single-node, NetApp ONTAP for enterprise NAS/SAN, Pure Storage for all-flash, Dell PowerStore/PowerFlex for HCI -- backend defined in `cinder.conf` `[backend_name]` sections with `enabled_backends`)
- [ ] Are Cinder volume types defined to expose different storage tiers? (`openstack volume type create --property volume_backend_name=ceph-ssd ssd-tier`) with QoS specs for IOPS/throughput limits (`read_iops_sec`, `write_iops_sec`, `total_bytes_sec`)
- [ ] Is Cinder multi-attach configured for volumes shared between instances? (requires backend support -- Ceph RBD supports it, requires cluster-aware filesystem like GFS2 or OCFS2 on instances, `multiattach = True` in volume type extra specs)
- [ ] Is Cinder volume encryption enabled? (LUKS encryption via Barbican key management, `volume_encryption_key_id` stored in Barbican, encryption type created per volume type with `openstack volume type set --encryption-provider luks`)
- [ ] Are Cinder backup targets configured separately from primary storage? (`backup_driver` set to `cinder.backup.drivers.swift`, `cinder.backup.drivers.ceph`, or `cinder.backup.drivers.nfs` -- backup storage should be in a different failure domain)
- [ ] Is Swift deployed with appropriate ring topology? (minimum 3 zones for replica policy, 5+ zones recommended, `swift-ring-builder` with partition power sized for growth -- partition power cannot be changed after deployment without data migration)
- [ ] Is Swift replication policy chosen? (3x replication for durability and read performance, erasure coding `ec_type=liberasurecode_rs_vand` for storage efficiency at ~1.5x overhead -- EC has higher CPU cost and latency for small objects)
- [ ] Is Manila deployed for shared filesystem needs? (CephFS backend for scale-out, NetApp ONTAP for enterprise NFS/CIFS, generic driver with Cinder for simple NFS shares -- share types and access rules per project)
- [ ] Is Glance configured with appropriate storage backend? (Ceph RBD for copy-on-write cloning with Cinder/Nova, Swift for object-based storage, filesystem for simple deployments -- `[glance_store]` in `glance-api.conf`)
- [ ] Is Glance image import workflow configured? (`web-download` and `glance-direct` import methods, `image_import_plugins` for format conversion and introspection, image size limits via `image_size_cap`)
- [ ] Are Cinder snapshot quotas set per project? (`snapshots`, `gigabytes`, `volumes`, `backups`, `backup_gigabytes` -- default quotas are often too generous for shared environments)
- [ ] Is data lifecycle management defined? (snapshot retention policies, backup rotation schedules, Swift container lifecycle policies with `X-Delete-After` or `X-Delete-At` headers)
- [ ] Is Swift container sync configured for cross-site replication if multi-region? (`X-Container-Sync-To` and `X-Container-Sync-Key` headers, or global clusters with separate regions for read affinity)
- [ ] Are Cinder consistency groups or generic volume groups used for coordinated multi-volume snapshots? (important for database workloads spanning multiple volumes)

## Why This Matters

Storage decisions in OpenStack are among the hardest to reverse. Cinder backend selection determines performance characteristics, data protection capabilities, and operational procedures for the life of the deployment. Ceph RBD provides copy-on-write cloning between Glance images and Cinder volumes (instant VM provisioning) but requires Ceph operational expertise. LVM backends are simple but limited to single-node failure domains. Swift partition power is set at ring creation and cannot be changed without a full data migration -- undersizing it caps cluster growth. Volume encryption requires Barbican to be operational before any encrypted volume can be mounted, creating a boot dependency. Manila share filesystem choice affects whether tenants can use NFS, CIFS, or CephFS native protocol, each with different performance and security characteristics.

## Common Decisions (ADR Triggers)

- **Cinder backend** -- Ceph RBD (scale-out, unified with Glance/Nova, CoW cloning) vs commercial SAN (NetApp, Pure, Dell -- enterprise support, existing investment) vs LVM/iSCSI (simple, single-node) -- performance, scale, and operational model trade-off
- **Object storage** -- Swift (native OpenStack, mature, proven at scale) vs Ceph RGW (S3 + Swift API, unified with block storage) vs MinIO (S3-native, simpler) -- API compatibility and operational unification considerations
- **Replication vs erasure coding** -- 3x replication (lower latency, higher read throughput, 3x storage cost) vs EC (1.4-1.8x storage cost, higher CPU, higher latency for small objects) -- cost vs performance for different workload profiles
- **Shared filesystem** -- Manila with CephFS (scale-out, POSIX) vs Manila with NetApp (enterprise NFS/CIFS) vs no shared filesystem (tenant-managed NFS in VMs) -- depends on workload requirements for shared data
- **Image storage** -- Glance on Ceph RBD (CoW clone to Cinder, instant boot) vs Glance on Swift (decoupled, simpler) vs Glance on local filesystem (single-node, no HA) -- boot performance vs architecture simplicity
- **Volume encryption** -- Barbican-managed LUKS (transparent, per-volume keys) vs no encryption (simpler, no Barbican dependency) vs tenant-managed encryption (dm-crypt inside VM) -- compliance requirements vs operational complexity
- **Backup target** -- Swift (native integration) vs NFS (simple, external) vs S3 (off-cluster, cloud-compatible) vs Ceph secondary pool (same cluster, faster) -- durability and isolation requirements
- **Storage tiering** -- multiple Cinder backends with volume types (SSD tier, HDD tier, replication tier) vs single backend with QoS policies -- granularity of storage service offering

## Version Notes

| Feature | Pike (16) Oct 2017 | Queens (17) Feb 2018 | Rocky (18) Aug 2018 | Stein (19) Apr 2019 | Train (20) Oct 2019 | Ussuri (21) May 2020 | Victoria (22) Oct 2020 | Wallaby (23) Apr 2021 | Xena (24) Oct 2021 | Yoga (25) Mar 2022 | Zed (26) Oct 2022 | 2023.1 Antelope (27) | 2023.2 Bobcat (28) | 2024.1 Caracal (29) | 2024.2 Dalmatian (30) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Cinder multi-attach | Not available | Introduced (tech preview) | GA (Ceph RBD, some backends) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder image volume cache | GA | GA | GA | GA (improved) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder backup drivers | Swift, NFS, Ceph | Swift, NFS, Ceph, S3 | GA (S3 improvements) | GA (incremental backup) | GA | GA (Google Cloud backup) | GA | GA | GA | GA | GA | GA (improved chunked backup) | GA | GA | GA |
| Cinder generic volume groups | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder volume revert to snapshot | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder backend drivers (new) | HPE 3PAR, Huawei | NetApp improvements | Pure Storage updates | Dell EMC PowerStore | Infinidat, TOYOU | LightOS NVMe-oF | Yadro Tatlin | DataCore SANsymphony | HPE Primera | Various updates | Various updates | Various updates | Various updates | Various updates | Various updates |
| Cinder volume transfer improvements | Basic | GA | GA | GA | GA (transfer with snapshots) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Cinder active-active HA | Tech Preview | Tech Preview | GA (limited backends) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Swift container sync | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Swift erasure coding | GA | GA | GA (improved) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Swift S3 API (s3api) | Middleware | Middleware (improved) | GA (s3api middleware) | GA | GA | GA | GA (improved compatibility) | GA | GA | GA | GA | GA | GA | GA | GA |
| Manila share migration | Tech Preview | GA | GA | GA (driver-assisted) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Manila share replication | Tech Preview | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Manila share groups | Not available | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Manila access rules (cephx, IP) | GA | GA | GA | GA | GA | GA | GA (metadata-based) | GA | GA | GA | GA | GA | GA | GA | GA |
| Glance image import | Basic | Interoperable import (introduced) | GA (web-download) | GA (glance-direct) | GA (copy-existing) | GA | GA | GA | GA | GA | GA | GA (improved plugins) | GA | GA | GA |
| Glance multi-store | Not available | Not available | Not available | Tech Preview | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |

**Key changes across releases:**
- **Cinder multi-attach (Queens+):** Multi-attach volumes were introduced in Queens and reached GA in Rocky. This allows a single Cinder volume to be attached to multiple instances simultaneously, which is required for clustered filesystems (GFS2, OCFS2) and shared database storage. Requires backend support (Ceph RBD supports it natively). Instances must use a cluster-aware filesystem to avoid data corruption.
- **Cinder backup improvements:** S3 backup driver was added in Queens. Incremental backup support improved in Stein. Google Cloud Storage backup driver was added in Ussuri. Chunked backup performance improved in 2023.1. Backup targets should always be in a different failure domain from primary Cinder storage.
- **Cinder active-active HA:** Active-active HA for Cinder services (allowing multiple c-vol workers for the same backend) progressed from tech preview in Pike/Queens to GA in Rocky for supported backends. This eliminates the single-point-of-failure for volume management operations.
- **Swift container sync:** Container sync has been stable and GA throughout all releases from Pike onward. It enables cross-cluster replication for geo-distributed object storage. Global clusters with region-based read affinity became the preferred approach for multi-site Swift deployments.
- **Swift S3 API:** The s3api middleware (replacing the older swift3 middleware) was improved across releases, reaching high S3 API compatibility. This enables applications using S3 SDKs to work against Swift without modification.
- **Manila share migration:** Share migration reached GA in Queens with driver-assisted migration improving in Stein. Share replication (GA in Queens) enables DR for shared filesystems. Share groups (Rocky+) allow coordinated operations on related shares.
- **Glance multi-store (Train+):** Glance multi-store support (GA in Train) allows a single Glance deployment to manage images across multiple backend stores (e.g., Ceph for local, Swift for archival), with the ability to copy images between stores.
- **New Cinder backend drivers:** Each release adds and updates backend drivers. Notable additions include Dell EMC PowerStore (Stein), NVMe-oF backends (Ussuri+), and continuous improvements to Ceph, NetApp, Pure Storage, and HPE drivers. Always verify driver compatibility with the target OpenStack release.
