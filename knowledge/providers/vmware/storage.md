# VMware Storage

## Checklist

- [ ] Is the storage architecture decision (vSAN vs VMFS-on-SAN vs NFS vs vVols) documented with rationale considering performance requirements, operational complexity, and existing storage investments?
- [ ] Are vSAN disk groups configured correctly -- hybrid (SSD cache + HDD capacity) or all-flash (SSD cache + SSD capacity) -- with a minimum of 2 disk groups per host for resilience and performance?
- [ ] Is the vSAN storage policy set with the appropriate Failures to Tolerate (FTT) and RAID level (FTT=1 RAID-1 for performance-sensitive, FTT=1 RAID-5 for capacity-efficient, FTT=2 RAID-6 for critical data) matching the number of available fault domains?
- [ ] Is vSAN stretched cluster configured with a witness host in a third site for metro-cluster deployments, with site affinity rules ensuring VMs prefer local data access and proper inter-site latency (<5ms RTT)?
- [ ] Is Storage DRS enabled on VMFS/NFS datastores with appropriate thresholds for space utilization (default 80%) and I/O latency (default 15ms), and is it set to manual recommendations for datastores with VMs that should not be migrated?
- [ ] Is VAAI (vStorage APIs for Array Integration) offloading confirmed as functional for block storage arrays (hardware-accelerated locking, full copy, block zeroing, thin provisioning reclaim) to reduce ESXi host CPU overhead?
- [ ] Is storage I/O control (SIOC) enabled to prevent individual VMs from monopolizing shared datastore IOPS, with latency thresholds set appropriately for the storage tier (10ms for flash, 30ms for hybrid)?
- [ ] Is thin provisioning used as the default with monitoring for overcommitment, and thick provisioning (eager-zeroed) reserved only for workloads requiring guaranteed allocation (e.g., FT-protected VMs, high-performance databases)?
- [ ] Is vSAN data-at-rest encryption enabled with a KMS (KMIP-compliant such as Thales, HyTrust, or vSphere Native Key Provider) for environments requiring encryption, with an understanding of the performance overhead (5-10% for all-flash)?
- [ ] Are vVols (Virtual Volumes) evaluated for environments with supported arrays (Pure Storage, NetApp, Dell, HPE) to enable per-VM storage policies, eliminating VMFS/NFS datastore management overhead?
- [ ] Is vSAN capacity planning accounting for the slack space requirement (25-30% free for vSAN operations, resyncs, and component rebuilds) and the impact of deduplication and compression ratios on effective capacity?
- [ ] Is the vSAN OSA (Original Storage Architecture) vs ESA (Express Storage Architecture) decision evaluated for new deployments, considering ESA's single-tier storage pool, improved compression, and snapshot performance on vSAN 8+?
- [ ] Are datastore alarm thresholds configured to alert well before capacity exhaustion (warning at 75%, critical at 85%) with automated actions or runbooks for capacity remediation?

## Why This Matters

Storage is the most common bottleneck and the most consequential failure domain in VMware environments. vSAN policy misconfiguration (e.g., setting FTT=1 in a 3-node cluster with RAID-5, which actually requires 4 nodes) results in non-compliant objects that are vulnerable to data loss. Thin provisioning without capacity monitoring leads to datastore overcommitment and VM pauses when space runs out. Storage DRS misconfiguration can cause unnecessary Storage vMotion storms or, conversely, leave hot datastores unbalanced. VAAI offload failures silently degrade performance by forcing the ESXi host to handle operations that should be delegated to the array. vSAN stretched cluster misconfiguration can cause split-brain scenarios or force VMs to read across the WAN link, adding latency. The vSAN ESA architecture fundamentally changes capacity planning assumptions by eliminating the cache/capacity tier distinction.

## Common Decisions (ADR Triggers)

- **vSAN vs external SAN/NAS** -- hyperconverged simplicity and co-located compute/storage scaling vs independent scaling of compute and storage, existing array investments (NetApp, Pure, Dell PowerStore), and specialized storage features (synchronous replication, deduplication ratios)
- **vSAN RAID policy** -- RAID-1 mirroring (best write performance, 2x capacity overhead per FTT level) vs RAID-5/6 erasure coding (capacity-efficient, higher write amplification, requires 4+ hosts for RAID-5, 6+ for RAID-6)
- **vSAN OSA vs ESA** -- OSA for existing deployments and mixed-drive configurations vs ESA for new all-NVMe deployments benefiting from single storage pool, native snapshots, and improved compression
- **Thin vs thick provisioning** -- thin for capacity efficiency and general workloads vs eager-zeroed thick for FT, high-performance databases, and workloads intolerant of first-write latency
- **vVols vs traditional datastores** -- vVols for per-VM policy management and array-integrated snapshots vs VMFS/NFS for broad compatibility and operational familiarity
- **vSAN encryption vs array-level encryption** -- vSAN data-at-rest encryption (host-level, requires KMS) vs array-native encryption (SED drives, controller-based), with implications for key management, performance, and compliance scope
- **Storage DRS automation** -- fully automated for dynamic balancing vs manual recommendations for change-controlled environments; consideration of VM anti-affinity rules for datastores
- **vSAN stretched cluster vs SRM** -- stretched cluster for active-active metro availability (requires <5ms RTT) vs SRM for asynchronous disaster recovery across longer distances
