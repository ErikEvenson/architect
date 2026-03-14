# Nutanix Storage (Distributed Storage Fabric)

## Checklist

- [ ] Is the replication factor chosen based on fault tolerance requirements -- RF2 (tolerates 1 component failure, 2x raw storage) for non-critical workloads, RF3 (tolerates 2 failures, 3x raw storage) for production databases and mission-critical systems?
- [ ] Are storage containers configured with appropriate compression policy -- inline compression (LZ4, always recommended) enabled by default, with delay set to 0 for inline or 60 minutes for post-process on write-heavy workloads?
- [ ] Is deduplication configured only for appropriate workloads (VDI, full clones, test/dev with similar VMs) and disabled for workloads with unique data (databases, media files) to avoid metadata overhead?
- [ ] Is erasure coding (EC-X) enabled for cold data containers to reduce storage overhead from RF3's 3x to approximately 1.5x, understanding that EC-X trades CPU and rebuild time for space efficiency?
- [ ] Is data locality being maintained by ensuring VMs access data primarily through their local CVM, avoiding remote CVM reads which add network latency and cross-node traffic?
- [ ] Is the storage tier composition appropriate -- all-NVMe for high IOPS (databases, OLTP), hybrid SSD+HDD for general workloads with automatic tiering (hot data on SSD, cold on HDD)?
- [ ] Are volume groups configured for workloads requiring shared block storage (iSCSI) -- clustered databases (Oracle RAC, SQL FCI), or external bare-metal servers needing Nutanix storage?
- [ ] Is storage QoS (IOPS throttling) configured on noisy-neighbor workloads to prevent a single VM from saturating the storage controller and degrading performance for other tenants?
- [ ] Are CVM storage controller resources (vCPUs and RAM) scaled up for heavy I/O workloads -- 20+ vCPUs and 64+ GB RAM for all-flash clusters running databases with high IOPS requirements?
- [ ] Is the cluster runway (capacity forecasting) monitored in Prism Central, with alerts set at 70% and 85% capacity thresholds to allow time for node expansion?
- [ ] Are storage container advertised capacity limits set to prevent any single container from consuming all cluster storage, enforcing multi-tenant fair use?
- [ ] Is the oplog (write buffer) sized appropriately -- default 6 GB per CVM on SSD tier, increased for write-burst workloads to absorb random writes before sequential drain to the extent store?
- [ ] Are snapshots and clones using redirect-on-write (ROW) rather than copy-on-write, and is snapshot retention monitored to prevent excessive metadata growth and storage bloat?
- [ ] Is the rebuild time after a disk or node failure understood and acceptable -- RF2 rebuild distributes data across remaining nodes but increases I/O load, larger clusters rebuild faster due to more parallel contributors?

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
