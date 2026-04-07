# NetApp ONTAP Storage

## Scope

NetApp ONTAP storage platforms and design decisions for on-premises deployments. Covers platform selection (FAS hybrid, AFF all-flash, ASA SAN-only, C-series capacity flash), ONTAP cluster topology (HA pairs, scale-out clusters, MetroCluster), Storage Virtual Machines (SVMs) for multi-tenancy, FlexVol and FlexGroup volumes, multi-protocol access (NFS, SMB/CIFS, iSCSI, FC, NVMe-oF), data protection (Snapshots, SnapMirror, SnapVault, SnapRestore, SnapCenter), storage efficiency (inline dedupe, compression, compaction, thin provisioning), encryption (NVE, NAE, self-encrypting drives), QoS policies, Active IQ Unified Manager and Active IQ Digital Advisor, and integration patterns with VMware, Kubernetes (Trident CSI), and backup vendors.

## Checklist

- [ ] **[Critical]** Is the correct ONTAP platform selected for the workload? (FAS for hybrid HDD+SSD value tier, AFF A-series for all-NVMe performance, AFF C-series for capacity flash with QLC, ASA for SAN-only all-flash with simplified provisioning, MetroCluster for synchronous metro-distance HA)
- [ ] **[Critical]** Is the cluster designed as HA pairs with non-disruptive operations in mind? (each node has a partner; planned and unplanned takeovers transparently move workloads; never deploy a single-controller "cluster" for production)
- [ ] **[Critical]** Are Storage Virtual Machines (SVMs, formerly Vservers) used to provide tenant isolation, protocol separation, and namespace boundaries? (one SVM per tenant or workload class; SVMs own their own LIFs, volumes, and protocol configuration independent of physical nodes)
- [ ] **[Critical]** Are SnapMirror replication relationships configured with appropriate RPO and topology? (async SnapMirror for typical DR with minutes-to-hours RPO; SnapMirror Synchronous for zero-RPO use cases requiring metro-distance latency; cascade or fan-out topologies for multi-site DR)
- [ ] **[Critical]** Are Snapshot schedules configured with retention that aligns with both RPO requirements and ransomware recovery windows? (frequent short-retention snapshots for operational recovery + longer-retention snapshots for ransomware rollback; SnapLock can immutably lock snapshots when compliance requires WORM)
- [ ] **[Critical]** Is the network design correct for the chosen protocols? (NFS/SMB on dedicated data VLANs with jumbo frames; iSCSI on isolated VLANs with MPIO; FC on redundant SAN fabrics with proper zoning; LIFs configured with failover groups for non-disruptive node operations)
- [ ] **[Critical]** Is multi-pathing configured on every host accessing block storage? (DSM for Windows, native MPIO for Linux with `multipathd` and the NetApp recommended config, ESXi NMP with appropriate SATP/PSP rules)
- [ ] **[Recommended]** Is the volume layout designed using FlexGroup volumes for large-scale parallel workloads (rendering, EDA, AI/ML training data) and FlexVol for general-purpose use? (FlexGroup distributes a single namespace across multiple constituents on multiple aggregates for parallelism beyond a single FlexVol's limits)
- [ ] **[Recommended]** Are storage efficiency features (inline deduplication, compression, compaction, thin provisioning) enabled with realistic data reduction expectations? (AFF arrays apply all efficiency features by default; FAS hybrid arrays may benefit from selective compression depending on workload; verify ratios with NetApp's Storage Efficiency Calculator before sizing)
- [ ] **[Recommended]** Are QoS policies (minimum, maximum, and adaptive QoS) applied to enforce performance isolation between workloads on shared aggregates? (adaptive QoS scales IOPS limits with allocated capacity; static QoS enforces fixed ceilings or floors; without QoS a single noisy workload can starve neighbors)
- [ ] **[Recommended]** Is encryption at rest enabled? (NetApp Volume Encryption (NVE) for per-volume keys, NetApp Aggregate Encryption (NAE) for aggregate-wide keys, or self-encrypting drives (SEDs) for hardware-level encryption; key management via Onboard Key Manager for small deployments or external KMIP for enterprise scale)
- [ ] **[Recommended]** Is Active IQ Unified Manager deployed for fleet-level monitoring, capacity planning, and performance analysis, with Active IQ Digital Advisor (cloud-based predictive analytics) connected for AutoSupport telemetry and proactive case management?
- [ ] **[Recommended]** Are SnapCenter or SnapManager plug-ins used for application-consistent snapshots of databases (SQL Server, Oracle, SAP HANA) and virtualization platforms (VMware, Hyper-V) rather than crash-consistent storage-only snapshots?
- [ ] **[Recommended]** Are ONTAP firmware (ONTAP version) and disk firmware updates planned using Active IQ-recommended upgrade paths, with non-disruptive controller takeover tested in a maintenance window before production cutover?
- [ ] **[Optional]** Is FlexCache used to provide read-mostly caching of remote volumes at edge sites or in front of slower aggregates? (transparent to clients; cache invalidates on origin writes; useful for content distribution and latency reduction)
- [ ] **[Optional]** Is FabricPool tiering configured to move cold blocks from SSD aggregates to a capacity tier (S3, Azure Blob, GCS, or on-prem object storage)? (transparent tiering; significant cost reduction for backup and archive data; verify network bandwidth and egress costs to the object tier)
- [ ] **[Optional]** Is MetroCluster (MCC IP or MCC FC) deployed for site-level synchronous replication with automatic switchover, when zero-RPO and near-zero-RTO across two sites within metro distance is required?
- [ ] **[Optional]** Is the Trident CSI driver deployed for Kubernetes persistent volume provisioning, with storage classes mapped to ONTAP backends (NFS, iSCSI, NVMe-oF) and snapshot/clone integration for stateful workloads?

## Why This Matters

ONTAP's clustered architecture provides non-disruptive operations as a core design principle -- controller upgrades, disk replacements, and even hardware refreshes can happen without taking the data offline. Organizations that treat ONTAP like a traditional dual-controller appliance and schedule downtime for routine operations are leaving the primary operational advantage of the platform on the table. The flip side is that ONTAP's flexibility creates many configuration choices, and naive defaults can produce a working but inefficient deployment.

SnapMirror is the most powerful and most over-applied feature. Configuring SnapMirror to every other ONTAP system in the environment "just in case" creates network and capacity overhead that frequently exceeds the actual DR value. Mirror schedules and retention should be derived from explicit RPO targets per workload, not from default templates. Synchronous SnapMirror in particular adds latency to every write and should only be used when zero-RPO is a hard requirement.

Storage efficiency claims are workload-dependent. AFF arrays advertise high data reduction ratios that hold for typical mixed workloads but collapse on already-compressed or encrypted data (backups, video, encrypted databases). Capacity sizing based on optimistic data-reduction assumptions is the leading cause of unexpected capacity exhaustion in NetApp deployments.

QoS misconfiguration is the leading cause of multi-tenant interference complaints. Without QoS policies, a single high-throughput workload can saturate a controller and degrade every other workload sharing the aggregates. Adaptive QoS is the lowest-friction option for general-purpose multi-tenant deployments.

Active IQ telemetry feeds NetApp's predictive analytics, similar in spirit to HPE InfoSight. Disabling AutoSupport or running disconnected eliminates proactive case creation, firmware recommendations, and performance benchmarks against the installed base.

## Common Decisions (ADR Triggers)

- **Platform tier** -- FAS hybrid for value tier with mixed workloads vs AFF A-series for all-NVMe performance vs AFF C-series for capacity flash with QLC economics vs ASA for SAN-only simplified deployments vs MetroCluster for synchronous site-level HA
- **Protocol selection** -- NFS for Linux/Unix and VMware NFS datastores vs SMB/CIFS for Windows file shares vs iSCSI for block on Ethernet vs FC for block on dedicated fabric vs NVMe-oF for ultra-low-latency block on supported AFF platforms
- **Volume design** -- FlexVol for general-purpose volumes vs FlexGroup for massive parallel workloads beyond a single FlexVol's scale ceiling
- **Replication topology** -- async SnapMirror for typical DR (minutes-to-hours RPO, single primary + DR replica) vs cascade SnapMirror for multi-hop replication vs SnapMirror Synchronous for zero-RPO metro-distance vs MetroCluster for site-level synchronous HA with automatic switchover
- **Data protection layering** -- Snapshots only (operational recovery, ransomware rollback) vs Snapshots + SnapVault (long-term retention) vs Snapshots + SnapVault + third-party backup (Veeam, Commvault, Rubrik) for offsite air-gapped copies
- **Storage efficiency** -- always-on inline efficiency (AFF default) vs selective compression (FAS hybrid) vs disabled efficiency for latency-sensitive workloads or already-compressed data
- **Encryption strategy** -- NVE per-volume keys (granular control) vs NAE aggregate-wide keys (simpler operations) vs SEDs (hardware-level, requires SED-capable drives); key management via OKM (small deployments) vs external KMIP (enterprise scale)
- **Tiering strategy** -- all-flash with no tiering (highest performance, highest cost) vs FabricPool to object storage (significant cost reduction for cold data) vs hybrid FAS with SSD cache + HDD tier (legacy approach)
- **Multi-tenancy boundary** -- shared SVM with volume-level isolation (simplest) vs SVM per tenant (strong protocol and namespace isolation) vs separate clusters (strongest isolation, highest cost)

## Reference Links

- [NetApp ONTAP Documentation](https://docs.netapp.com/us-en/ontap/) -- comprehensive reference for ONTAP features, configuration, and administration
- [ONTAP 9 Cluster Administration](https://docs.netapp.com/us-en/ontap/system-admin/index.html) -- cluster setup, HA pairs, SVMs, and node operations
- [SnapMirror Documentation](https://docs.netapp.com/us-en/ontap/data-protection/snapmirror-replication-concept.html) -- async, synchronous, cascade, and fan-out replication topologies
- [Active IQ Unified Manager](https://docs.netapp.com/us-en/active-iq-unified-manager/) -- fleet management, capacity planning, and performance monitoring
- [NetApp Active IQ Digital Advisor](https://activeiq.netapp.com/) -- cloud-based predictive analytics, AutoSupport, and proactive case management
- [Trident CSI for Kubernetes](https://docs.netapp.com/us-en/trident/) -- persistent volume provisioning, snapshot/clone integration, and storage class mapping
- [NetApp Hardware Universe](https://hwu.netapp.com/) -- platform specifications, supported configurations, and interoperability matrix
- [SnapCenter](https://docs.netapp.com/us-en/snapcenter/) -- application-consistent backup and recovery for SQL Server, Oracle, SAP HANA, VMware, and Hyper-V

## See Also

- `general/storage.md` -- general storage architecture patterns and protocol selection
- `general/disaster-recovery.md` -- DR strategy patterns and RPO/RTO planning
- `providers/netapp/cloud-volumes.md` -- NetApp cloud offerings (CVO, ANF, FSx for ONTAP) and hybrid replication patterns
- `providers/vmware/networking.md` -- VMware NFS and iSCSI datastore design patterns
- `providers/hpe/nimble-alletra.md` -- HPE storage as an alternative enterprise array vendor
- `providers/dell/powerstore.md` -- Dell PowerStore as an alternative enterprise array vendor
- `providers/purestorage/flasharray.md` -- Pure Storage FlashArray as an alternative all-flash vendor
