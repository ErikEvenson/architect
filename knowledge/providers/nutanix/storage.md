# Nutanix Storage (Distributed Storage Fabric)

## Scope

Nutanix Distributed Storage Fabric (DSF) configuration: replication factors, storage containers, compression, deduplication, erasure coding, data locality, tiering, volume groups, QoS, CVM sizing, capacity planning, and snapshot management.

## Checklist

- [ ] [Critical] Is the replication factor chosen based on fault tolerance requirements -- RF2 (tolerates 1 component failure, 2x raw storage) for non-critical workloads, RF3 (tolerates 2 failures, 3x raw storage) for production databases and mission-critical systems?
- [ ] [Critical] Are storage containers configured with appropriate compression policy -- inline compression (LZ4, always recommended) enabled by default, with delay set to 0 for inline or 60 minutes for post-process on write-heavy workloads?
- [ ] [Recommended] Is deduplication configured only for appropriate workloads (VDI, full clones, test/dev with similar VMs) and disabled for workloads with unique data (databases, media files) to avoid metadata overhead?
- [ ] [Recommended] Is erasure coding (EC-X) enabled for cold data containers to reduce storage overhead from RF3's 3x to approximately 1.5x, understanding that EC-X trades CPU and rebuild time for space efficiency?
- [ ] [Recommended] Is data locality being maintained by ensuring VMs access data primarily through their local CVM, avoiding remote CVM reads which add network latency and cross-node traffic?
- [ ] [Critical] Is the storage tier composition appropriate -- all-NVMe for high IOPS (databases, OLTP), hybrid SSD+HDD for general workloads with automatic tiering (hot data on SSD, cold on HDD)?
- [ ] [Recommended] Are volume groups configured for workloads requiring shared block storage (iSCSI) -- clustered databases (Oracle RAC, SQL FCI), or external bare-metal servers needing Nutanix storage?
- [ ] [Recommended] Is storage QoS (IOPS throttling) configured on noisy-neighbor workloads to prevent a single VM from saturating the storage controller and degrading performance for other tenants?
- [ ] [Recommended] Are CVM storage controller resources (vCPUs and RAM) scaled up for heavy I/O workloads -- 20+ vCPUs and 64+ GB RAM for all-flash clusters running databases with high IOPS requirements?
- [ ] [Critical] Is the cluster runway (capacity forecasting) monitored in Prism Central, with alerts set at 70% and 85% capacity thresholds to allow time for node expansion?
- [ ] [Recommended] Are storage container advertised capacity limits set to prevent any single container from consuming all cluster storage, enforcing multi-tenant fair use?
- [ ] [Optional] Is the oplog (write buffer) sized appropriately -- default 6 GB per CVM on SSD tier, increased for write-burst workloads to absorb random writes before sequential drain to the extent store?
- [ ] [Recommended] Are snapshots and clones using redirect-on-write (ROW) rather than copy-on-write, and is snapshot retention monitored to prevent excessive metadata growth and storage bloat?
- [ ] [Optional] Is the rebuild time after a disk or node failure understood and acceptable -- RF2 rebuild distributes data across remaining nodes but increases I/O load, larger clusters rebuild faster due to more parallel contributors?

## Why This Matters

The Nutanix Distributed Storage Fabric (DSF) runs as a distributed system across CVMs on every node, presenting local storage as a shared pool. Every write goes through the local CVM, is written to the oplog (SSD write buffer), acknowledged to the guest, then replicated to RF-number of nodes and later drained to the extent store. This architecture means CVM health directly equals storage health -- a starved CVM degrades I/O for all VMs on that host. Data locality is a core performance optimization: when a VM's data is on its local node, reads bypass the network entirely. VM migrations break locality until a background process (ILM curator) moves data to follow the VM. Erasure coding dramatically reduces capacity consumption for cold data but increases rebuild times and CPU usage -- it should never be applied to performance-sensitive containers. Understanding the oplog, extent store, and curator background processes is essential for diagnosing storage performance issues.

## Common Decisions (ADR Triggers)

- **Replication factor** -- RF2 (1 failure tolerance, 2x overhead) vs RF3 (2 failure tolerance, 3x overhead), consider RF3 for clusters with fewer than 8 nodes where losing 1 of 3 nodes is 33% capacity loss
- **Compression vs deduplication** -- Inline compression (always recommended, LZ4 near-zero overhead) vs deduplication (only for clone-heavy workloads, significant metadata RAM cost on CVM)
- **Erasure coding** -- EC-X for cold/archive data (1.5x overhead vs 3x for RF3) vs maintaining full RF replication for hot data requiring fast rebuild
- **Storage tier composition** -- All-NVMe (maximum IOPS, highest cost) vs hybrid SSD/HDD (automatic tiering, cost-effective for mixed workloads) vs all-SSD (balanced)
- **Block storage access** -- vDisks on AHV (simplest) vs Volume Groups over iSCSI (shared storage for clusters, bare metal) vs Volume Groups over Fibre Channel (legacy SAN integration)
- **Capacity management** -- Aggressive thin provisioning (higher VM density) vs conservative allocation with storage container limits, runway planning horizon
- **Container design** -- Single container (simple) vs multiple containers segregated by workload type (DB, VDI, general) with different RF, compression, and QoS policies

## Version Notes

| Feature | AOS 6.x (6.5 LTS / 6.7) | AOS 7.x (7.0+) |
|---|---|---|
| Storage architecture | Distributed Storage Fabric | Distributed Storage Fabric (optimized) |
| Inline compression (LZ4) | GA | GA (improved efficiency) |
| Erasure coding (EC-X) | GA | GA (faster rebuild, reduced CPU overhead) |
| Oplog optimization | GA (6 GB default per CVM) | GA (dynamic oplog sizing) |
| Autonomous Extent Store (AES) | GA (metadata optimization) | GA (improved, mandatory for new containers) |
| NVMe storage tier support | GA | GA (enhanced NVMe-oF support) |
| Snapshot performance | GA (ROW snapshots) | GA (improved metadata handling, reduced overhead) |
| Storage QoS (IOPS throttling) | GA (per-VM) | GA (per-VM and per-container) |
| Data-at-rest encryption | GA (software, SED) | GA (software, SED, improved key management) |
| Volume Groups (iSCSI) | GA | GA (improved multi-path, performance) |
| vDisk blockmap optimization | GA | GA (reduced metadata footprint) |
| CVM auto-pathing | GA | GA (improved failover responsiveness) |
| Disaggregated storage (compute-only nodes) | Supported | GA (improved, flexible licensing) |
| Capacity runway forecasting | GA (Prism Central) | GA (improved ML-based forecasting) |

**Key differences between AOS 6.x and 7.x:**
- **Performance improvements:** AOS 7.x includes significant I/O path optimizations, reducing latency for random read/write workloads by 15-25% on all-NVMe clusters. The oplog now dynamically sizes based on workload patterns rather than using a fixed allocation, improving write burst absorption.
- **Erasure coding (EC-X):** AOS 7.x reduces the CPU overhead and rebuild time for EC-X encoded data, making erasure coding more practical for a broader range of workloads. Rebuild operations are more parallelized and less disruptive to foreground I/O.
- **Autonomous Extent Store (AES):** AES, which optimizes metadata management and reduces CVM memory consumption, becomes mandatory for new storage containers in AOS 7.x. Existing containers can be migrated from legacy extent store to AES.
- **Snapshot and clone efficiency:** AOS 7.x improves snapshot metadata handling, reducing the performance impact of deep snapshot chains and large numbers of concurrent clones. This benefits Nutanix Database Service (NDB, formerly Era) and backup integration workflows.
- **NVMe-oF support:** AOS 7.x adds enhanced NVMe over Fabrics support, enabling external hosts to access Nutanix storage with lower latency than traditional iSCSI.
- **Disaggregated storage:** While compute-only nodes were supported in AOS 6.x, AOS 7.x improves the experience with more flexible licensing and better performance for remote storage access patterns.
- **AOS 7.5 (December 2025):** Introduces VM Startup Policies for controlled boot sequencing after cluster or host restarts, and enhanced CVM security with improved integrity validation and hardened default configurations.

## Reference Links

- [Nutanix storage guide](https://portal.nutanix.com/page/documents/details?targetId=Web-Console-Guide-Prism-v6_9:wc-storage-management-wc-c.html) -- storage containers, replication factor, compression, and deduplication
- [Nutanix Files documentation](https://portal.nutanix.com/page/documents/details?targetId=Files-v5_0:Files-v5_0) -- file server deployment, shares, and multi-protocol access
- [Nutanix Objects documentation](https://portal.nutanix.com/page/documents/details?targetId=Objects-v4_3:Objects-v4_3) -- S3-compatible object storage deployment and bucket management

## See Also

- `general/data.md` -- general data architecture patterns
- `providers/nutanix/infrastructure.md` -- cluster sizing and CVM configuration
- `providers/nutanix/compute.md` -- VM storage I/O and CVM resource allocation
- `providers/ceph/storage.md` -- Ceph as alternative software-defined storage
