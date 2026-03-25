# Storage Architecture

## Scope

Storage tier selection, protocol decisions, capacity planning, performance requirements, data lifecycle management, and integration with compute and backup infrastructure. This file covers **what** storage decisions need to be made and the trade-offs involved. For provider-specific **how**, see the provider storage files. For backup strategy and tooling, see `general/enterprise-backup.md`. For database-specific storage considerations, see `general/data.md`.

## Checklist

- [ ] **[Critical]** What storage tier does each workload require? (block storage for databases and transactional workloads requiring consistent low-latency IOPS; object storage for unstructured data, media, backups, and archive; file storage for shared access across multiple compute instances and legacy applications; archive/cold storage for compliance retention and infrequently accessed data — most architectures use multiple tiers, so classify each data set separately by access pattern and performance requirement)
- [ ] **[Critical]** What storage protocol is required for each workload? (NFS for shared file access across Linux workloads with simplicity and broad compatibility; SMB/CIFS for Windows workloads and end-user file shares; iSCSI for block-level access over Ethernet when Fibre Channel is unavailable or cost-prohibitive; Fibre Channel for latency-sensitive database workloads requiring dedicated storage networking with guaranteed bandwidth; S3-compatible API for object storage with cloud-native or hybrid access patterns — protocol choice constrains vendor options and networking requirements)
- [ ] **[Critical]** What are the IOPS and throughput requirements for each storage tier? (database workloads typically require 3,000-20,000 IOPS with sub-millisecond latency; application logs and analytics tolerate higher latency but need sustained throughput of 100+ MB/s; media streaming requires sequential read throughput; measure baseline requirements from existing monitoring data or vendor reference architectures before sizing — over-provisioning IOPS wastes budget, under-provisioning causes cascading application latency)
- [ ] **[Critical]** What is the replication and redundancy strategy for stored data? (local redundancy within a single site protects against drive and node failures; synchronous replication across sites provides zero RPO but adds write latency proportional to distance; asynchronous replication provides near-zero RPO with eventual consistency; erasure coding provides space-efficient redundancy compared to full replication — define the RPO and RTO targets first, then select the replication model that meets them at acceptable cost and latency)
- [ ] **[Critical]** Is encryption at rest required, and who manages the keys? (provider-managed encryption is the default for cloud storage and requires zero operational effort; customer-managed keys in KMS provide revocation control and audit trail; on-premises storage encryption via self-encrypting drives or controller-level encryption requires key escrow and recovery procedures — some compliance frameworks mandate specific key management models; key loss means permanent data loss, so key backup and rotation procedures are non-negotiable)
- [ ] **[Critical]** What are the data residency and retention requirements? (regulatory mandates may require data to remain within specific geographic boundaries; retention policies must define minimum and maximum hold periods per data classification; litigation hold capability must be available for legal discovery; immutable storage or WORM compliance may be required for financial, healthcare, or government data — these requirements constrain which storage platforms and regions are eligible)
- [ ] **[Recommended]** What is the capacity planning model and projected growth rate? (establish current capacity utilization and annualized growth rate from historical trends; plan for 18-24 months of growth in on-premises environments with hardware procurement lead times; cloud storage scales on demand but costs scale linearly — a 50 TB dataset growing 20% annually becomes 86 TB in three years; factor in snapshot and replication overhead which can double effective capacity consumption)
- [ ] **[Recommended]** What data lifecycle and tiering policies apply? (hot tier for frequently accessed data with highest IOPS; warm tier for data accessed weekly or monthly at reduced cost; cold tier for data accessed rarely but requiring retrieval within hours; archive tier for compliance-only data with retrieval times of hours to days — automate tiering based on last-access timestamps or creation date; manual tiering leads to hot-tier bloat and cost overruns; retrieval fees from cold and archive tiers can be substantial, so model the total cost of ownership including retrieval patterns)
- [ ] **[Recommended]** How does storage integrate with the backup and disaster recovery strategy? (storage-level snapshots provide rapid point-in-time recovery within the same platform; backup tools like Veeam, Commvault, or Rubrik require agent or agentless access to storage volumes; backup targets should be on separate storage infrastructure or in a separate failure domain; immutable backup copies protect against ransomware — ensure backup integration is validated during storage platform selection, not after deployment)
- [ ] **[Recommended]** What storage is required for container workloads? (Kubernetes persistent volumes require a CSI driver compatible with the storage platform; ReadWriteOnce for single-pod database workloads; ReadWriteMany for shared file access across pods; ephemeral volumes for scratch space and caching; storage class definitions determine performance tier, reclaim policy, and provisioning mode — dynamic provisioning is preferred over static to reduce operational burden; test CSI driver compatibility with the target Kubernetes distribution before committing to a storage platform)
- [ ] **[Recommended]** What is the shared storage vs. local storage trade-off for each workload? (shared storage simplifies live migration, high availability, and backup but introduces network dependency and potential contention; local storage — NVMe, local SSD — provides lowest latency and highest IOPS but ties workloads to specific hosts and complicates HA; distributed storage systems like Ceph or vSAN aggregate local disks into shared pools — hybrid approaches using local storage for performance-critical workloads and shared storage for general workloads are common)
- [ ] **[Recommended]** What vendor lock-in risks exist with the selected storage platform? (proprietary storage formats and APIs create migration barriers; S3-compatible APIs provide a de facto standard for object storage portability; block storage formats vary by platform and rarely transfer directly; on-premises storage arrays with proprietary deduplication or compression require vendor-specific tools for data extraction — evaluate exit cost and data portability as part of platform selection, especially for multi-petabyte environments where migration timelines are measured in weeks)
- [ ] **[Recommended]** How are storage performance and capacity monitored? (IOPS, throughput, latency, queue depth, and capacity utilization must be tracked per volume and per tier; set alerting thresholds at 80% capacity and at latency degradation from baseline; integrate storage metrics into the centralized observability stack; capacity trend reporting enables proactive procurement for on-premises and cost forecasting for cloud — storage performance problems often manifest as application latency, so correlate storage metrics with application performance data)
- [ ] **[Optional]** Is deduplication or compression appropriate for any storage tier? (inline deduplication and compression reduce effective capacity consumption by 2-5x for virtualization and backup workloads; they add CPU overhead on the storage controller and may increase latency for write-intensive workloads; post-process deduplication runs during off-peak hours to reduce performance impact; VDI and backup workloads benefit most; database workloads with already-compressed data or random write patterns benefit least)
- [ ] **[Optional]** Are there specific multipath or high-availability requirements for storage connectivity? (multipath I/O across redundant HBAs and switches eliminates single points of failure in the storage network; active-active multipathing provides load balancing and failover; active-passive provides failover only — configure multipath policy to match the storage array vendor recommendations; misconfigured multipath is a leading cause of storage outages and data corruption in on-premises environments)
- [ ] **[Optional]** Is thin provisioning appropriate, and what are the overcommitment limits? (thin provisioning allocates storage on demand rather than at creation time, improving utilization; safe overcommitment ratios depend on workload growth patterns — 150-200% for stable workloads, more conservative for unpredictable growth; monitor actual consumption and set alerts well before physical capacity is exhausted — thin provisioning without monitoring leads to out-of-space conditions that crash applications and corrupt data)

## Why This Matters

Storage decisions are among the most persistent in any architecture. Migrating data between storage platforms — especially at scale — is time-consuming, risky, and often requires application downtime. A 100 TB dataset migrating at 1 Gbps sustained takes over 9 days of continuous transfer, assuming no errors or retransmissions. Choosing the wrong storage tier, protocol, or platform at design time creates a technical debt that compounds as data volume grows, eventually forcing a disruptive migration under pressure.

Performance mismatches between storage and compute are the most common root cause of application latency that teams struggle to diagnose. A database running on storage that delivers 1,000 IOPS when it needs 10,000 will exhibit query timeouts, connection pool exhaustion, and cascading failures — symptoms that appear to be application problems rather than infrastructure problems. Measuring and specifying storage performance requirements during architecture design, rather than discovering them during load testing, prevents months of troubleshooting.

Storage costs are frequently underestimated because capacity is only one dimension. Snapshot retention, replication overhead, retrieval fees from cold tiers, and data transfer charges between storage and compute can double the effective cost of stored data. Organizations that plan storage costs based on raw capacity alone consistently exceed their budgets. Lifecycle tiering policies that automatically move aging data to cheaper tiers are the most effective cost control mechanism, but they must be designed at architecture time — retrofitting tiering onto a flat storage model requires data reorganization and application changes.

## Common Decisions (ADR Triggers)

### ADR: Storage Tier Selection

**Context:** The architecture must store data with varying access patterns, performance requirements, and cost sensitivities.

**Options:**

| Criterion | Block Storage | Object Storage | File Storage (NAS) | Archive Storage |
|---|---|---|---|---|
| Access pattern | Random read/write, single-host attach | HTTP/API-based, write-once-read-many | Shared read/write across multiple hosts | Write-once, read-rarely |
| Latency | Sub-millisecond (NVMe/SSD), low-ms (HDD) | Milliseconds to seconds | Low to mid milliseconds | Hours (retrieval request required) |
| Throughput | High, dedicated per volume | Very high aggregate, variable per request | Moderate, shared across clients | N/A (batch retrieval) |
| Scalability | Terabytes per volume | Petabytes per bucket, unlimited objects | Terabytes to low petabytes | Petabytes |
| Cost | Highest per GB (especially SSD tier) | Low per GB, pay for retrieval and API calls | Moderate per GB | Lowest per GB |
| Best fit | Databases, transactional apps, boot volumes | Backups, media, logs, data lake, static content | Shared home directories, CMS, legacy apps | Compliance archives, cold backups, audit logs |

**Decision drivers:** Access pattern (random vs. sequential, read vs. write ratio), latency requirements, number of concurrent consumers, data volume and growth trajectory, and compliance requirements for immutability or retention.

### ADR: Storage Protocol Selection

**Context:** The architecture must connect compute workloads to storage with appropriate performance, compatibility, and network requirements.

**Options:**

| Criterion | NFS | iSCSI | Fibre Channel | S3-Compatible API | SMB/CIFS |
|---|---|---|---|---|---|
| Transport | TCP/IP (Ethernet) | TCP/IP (Ethernet) | Dedicated FC fabric (or FCoE) | HTTP/HTTPS (Ethernet) | TCP/IP (Ethernet) |
| Access model | File-level, multi-host | Block-level, typically single-host | Block-level, typically single-host | Object-level, multi-client | File-level, multi-host |
| Performance | Good for general workloads; jumbo frames improve throughput | Near-FC performance on dedicated VLANs | Lowest latency, highest reliability | Depends on network; higher latency per request | Good for general workloads |
| Infrastructure cost | Uses existing Ethernet | Uses existing Ethernet; may need dedicated VLANs | Requires FC HBAs, switches, and cabling | Uses existing Ethernet | Uses existing Ethernet |
| Best fit | VMware datastores, Linux shared mounts, Kubernetes RWX | Hypervisor datastores, databases on Ethernet-only networks | Mission-critical databases, high-transaction systems | Cloud-native apps, backup targets, hybrid cloud | Windows file shares, Active Directory environments |

**Decision drivers:** Existing network infrastructure (Ethernet-only vs. FC fabric), workload latency sensitivity, multi-host access requirements, team expertise with storage networking, and budget for dedicated storage networking.

### ADR: Shared Storage vs. Local Storage

**Context:** The architecture must balance storage performance against operational flexibility for high availability and workload mobility.

**Options:**
- **Centralized shared storage (SAN/NAS):** All compute nodes access a shared storage pool. Enables live migration, simplified backup, and centralized management. Introduces a network dependency and potential single point of contention. Higher cost for enterprise arrays with redundant controllers. Best for: virtualized environments, workloads requiring live migration, and centralized data management.
- **Local storage (DAS/NVMe):** Each compute node uses directly attached disks. Lowest latency, highest IOPS, no network dependency. Workloads are tied to specific hosts; HA requires application-level replication or distributed storage. Lower upfront cost per IOPS. Best for: distributed databases (Cassandra, MongoDB), high-performance caching, Kubernetes local persistent volumes for latency-sensitive pods.
- **Distributed software-defined storage (Ceph, vSAN, MinIO):** Aggregates local disks across nodes into a shared, replicated pool. Combines local-disk performance with shared-storage flexibility. Adds CPU and network overhead on compute nodes. Requires minimum node counts (typically 3+) and careful network design. Best for: hyperconverged infrastructure, private cloud, and environments seeking shared storage without dedicated array hardware.

**Decision drivers:** Workload latency requirements, HA and live migration needs, infrastructure budget, team operational expertise with storage platforms, and whether the environment is hyperconverged or uses dedicated storage hardware.

### ADR: Data Lifecycle and Tiering Strategy

**Context:** Stored data ages over time, and retaining all data on the highest-performance tier wastes budget without improving application performance.

**Options:**
- **Manual lifecycle management:** Administrators periodically review and migrate data between tiers. Low automation investment. Requires ongoing operational effort and discipline; commonly neglected, resulting in hot-tier bloat and overspend.
- **Policy-based automatic tiering:** Storage platform or cloud service moves data between tiers based on rules (last access time, creation date, size). Examples: S3 Lifecycle Rules, Azure Blob Lifecycle Management, NetApp FabricPool. Low operational effort once configured. Requires careful policy design to avoid prematurely tiering frequently accessed data.
- **Application-driven tiering:** Application code writes to the appropriate tier based on data type at creation time (e.g., thumbnails to object storage, metadata to database, raw media to archive). Most efficient but requires application awareness and developer cooperation. Best for greenfield applications designed around multi-tier storage.
- **No tiering (single tier):** All data remains on one performance tier. Simplest operationally. Cost-effective only when total data volume is small (under 1 TB) or access patterns are uniformly hot. Becomes prohibitively expensive as data grows.

**Decision drivers:** Total data volume and growth rate, percentage of data that is active vs. dormant, retrieval latency tolerance for aged data, regulatory retention requirements, and operational capacity for lifecycle policy management.

## See Also

- `providers/aws/storage.md` — AWS S3, EBS, EFS, and FSx configuration
- `providers/azure/storage.md` — Azure Blob, Disk, Files, and NetApp Files
- `providers/gcp/storage.md` — GCP Cloud Storage, Persistent Disk, and Filestore
- `providers/ceph/storage.md` — Ceph distributed storage architecture
- `providers/vmware/storage.md` — VMware vSAN and datastore configuration
- `providers/nutanix/storage.md` — Nutanix storage services and policies
- `providers/kubernetes/storage.md` — Kubernetes persistent volumes and CSI drivers
- `general/enterprise-backup.md` — Backup tools and strategies that depend on storage tier decisions
- `general/data.md` — Database engine selection and data management (storage underlies all database workloads)
- `general/disaster-recovery.md` — DR strategies that depend on storage replication and backup integration
