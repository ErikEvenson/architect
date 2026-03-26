# VMware Storage

## Scope

This document covers VMware storage architecture decisions including vSAN (OSA and ESA), VMFS-on-SAN, NFS, vVols, storage policies (SPBM), encryption, Storage DRS, and capacity planning.

## Checklist

- [ ] **[Critical]** Is the storage architecture decision (vSAN vs VMFS-on-SAN vs NFS vs vVols) documented with rationale considering performance requirements, operational complexity, and existing storage investments? Note: vVols are deprecated in VCF 9.0 and should not be selected for new deployments.
- [ ] **[Critical]** Are vSAN disk groups configured correctly -- hybrid (SSD cache + HDD capacity) or all-flash (SSD cache + SSD capacity) -- with a minimum of 2 disk groups per host for resilience and performance?
- [ ] **[Critical]** Is the vSAN storage policy set with the appropriate Failures to Tolerate (FTT) and RAID level (FTT=1 RAID-1 for performance-sensitive, FTT=1 RAID-5 for capacity-efficient, FTT=2 RAID-6 for critical data) matching the number of available fault domains?
- [ ] **[Recommended]** Is vSAN stretched cluster configured with a witness host in a third site for metro-cluster deployments, with site affinity rules ensuring VMs prefer local data access and proper inter-site latency (<5ms RTT)?
- [ ] **[Recommended]** Is Storage DRS enabled on VMFS/NFS datastores with appropriate thresholds for space utilization (default 80%) and I/O latency (default 15ms), and is it set to manual recommendations for datastores with VMs that should not be migrated?
- [ ] **[Recommended]** Is VAAI (vStorage APIs for Array Integration) offloading confirmed as functional for block storage arrays (hardware-accelerated locking, full copy, block zeroing, thin provisioning reclaim) to reduce ESXi host CPU overhead?
- [ ] **[Recommended]** Is storage I/O control (SIOC) enabled to prevent individual VMs from monopolizing shared datastore IOPS, with latency thresholds set appropriately for the storage tier (10ms for flash, 30ms for hybrid)?
- [ ] **[Recommended]** Is thin provisioning used as the default with monitoring for overcommitment, and thick provisioning (eager-zeroed) reserved only for workloads requiring guaranteed allocation (e.g., FT-protected VMs, high-performance databases)?
- [ ] **[Recommended]** Is vSAN data-at-rest encryption enabled with a KMS (KMIP-compliant such as Thales CipherTrust, Entrust, or vSphere Native Key Provider) for environments requiring encryption, with an understanding of the performance overhead (5-10% for all-flash)?
- [ ] **[Optional]** Are vVols (Virtual Volumes) evaluated for environments with supported arrays (Pure Storage, NetApp, Dell, HPE)? **Note: vVols are deprecated in VCF 9.0 / vSphere 9. Do not select for new deployments; plan migration to vSAN or VMFS for existing vVols environments.**
- [ ] **[Critical]** Is vSAN capacity planning accounting for the slack space requirement (25-30% free for vSAN operations, resyncs, and component rebuilds) and the impact of deduplication and compression ratios on effective capacity?
- [ ] **[Recommended]** Is the vSAN OSA (Original Storage Architecture) vs ESA (Express Storage Architecture) decision evaluated for new deployments, considering ESA's single-tier storage pool, improved compression, and snapshot performance on vSAN 8+?
- [ ] **[Recommended]** Are datastore alarm thresholds configured to alert well before capacity exhaustion (warning at 75%, critical at 85%) with automated actions or runbooks for capacity remediation?

## Why This Matters

Storage is the most common bottleneck and the most consequential failure domain in VMware environments. vSAN policy misconfiguration (e.g., setting FTT=1 in a 3-node cluster with RAID-5, which actually requires 4 nodes) results in non-compliant objects that are vulnerable to data loss. Thin provisioning without capacity monitoring leads to datastore overcommitment and VM pauses when space runs out. Storage DRS misconfiguration can cause unnecessary Storage vMotion storms or, conversely, leave hot datastores unbalanced. VAAI offload failures silently degrade performance by forcing the ESXi host to handle operations that should be delegated to the array. vSAN stretched cluster misconfiguration can cause split-brain scenarios or force VMs to read across the WAN link, adding latency. The vSAN ESA architecture fundamentally changes capacity planning assumptions by eliminating the cache/capacity tier distinction.

## Common Decisions (ADR Triggers)

- **vSAN vs external SAN/NAS** -- hyperconverged simplicity and co-located compute/storage scaling vs independent scaling of compute and storage, existing array investments (NetApp, Pure, Dell PowerStore), and specialized storage features (synchronous replication, deduplication ratios)
- **vSAN RAID policy** -- RAID-1 mirroring (best write performance, 2x capacity overhead per FTT level) vs RAID-5/6 erasure coding (capacity-efficient, higher write amplification, requires 4+ hosts for RAID-5, 6+ for RAID-6)
- **vSAN OSA vs ESA** -- OSA for existing deployments and mixed-drive configurations vs ESA for new all-NVMe deployments benefiting from single storage pool, native snapshots, and improved compression
- **Thin vs thick provisioning** -- thin for capacity efficiency and general workloads vs eager-zeroed thick for FT, high-performance databases, and workloads intolerant of first-write latency
- **vVols vs traditional datastores** -- vVols for per-VM policy management and array-integrated snapshots vs VMFS/NFS for broad compatibility and operational familiarity. **Note: vVols are deprecated in VCF 9.0 -- do not select for new deployments.**
- **vSAN encryption vs array-level encryption** -- vSAN data-at-rest encryption (host-level, requires KMS) vs array-native encryption (SED drives, controller-based), with implications for key management, performance, and compliance scope
- **Storage DRS automation** -- fully automated for dynamic balancing vs manual recommendations for change-controlled environments; consideration of VM anti-affinity rules for datastores
- **vSAN stretched cluster vs VCF Live Site Recovery** -- stretched cluster for active-active metro availability (requires <5ms RTT) vs VCF Live Site Recovery (formerly SRM) for asynchronous disaster recovery across longer distances

## Version Notes

| Feature | vSphere 7 (7.0 U3) | vSphere 8 (8.0 U2+) | vSphere 9 / VCF 9.0 |
|---|---|---|---|
| vSAN architecture | OSA only | OSA and ESA | OSA and ESA (ESA preferred) |
| vSAN ESA (Express Storage Architecture) | Not available | GA (single-tier NVMe pool) | GA (enhanced, default for new deployments) |
| vSAN Max (disaggregated storage) | Not available | GA (8.0 U2+) | GA (continued) |
| vSAN OSA disk groups | Cache + Capacity tiers | Cache + Capacity tiers (unchanged) | Cache + Capacity tiers (unchanged) |
| ESA storage pool model | N/A | Single-tier (no cache/capacity split) | Single-tier (improved) |
| ESA compression | N/A | Improved (always-on, higher ratios) | Enhanced (higher efficiency) |
| ESA snapshots | N/A | Native, memory-efficient (no performance penalty) | Native (improved) |
| vSAN native file services | GA | GA (improved NFS 4.1 support) | GA |
| Storage policy-based management (SPBM) | GA | GA (simplified ESA policies) | GA |
| vSAN data-at-rest encryption | GA (KMS required) | GA (Native Key Provider or KMS) | GA (Native Key Provider or KMS) |
| vSAN HCI Mesh | GA (compute-only + storage-only) | GA (improved cross-cluster mount) | GA |
| vVols | GA | GA (improved provider scalability) | **Deprecated** (not recommended for new deployments) |
| vSAN stretched cluster | GA (<5ms RTT) | GA (<5ms RTT, ESA supported) | GA (<5ms RTT) |

**Key changes in vSphere 9 / VCF 9.0 storage:**
- **vVols deprecation:** VCF 9.0 deprecates Virtual Volumes (vVols). Organizations using vVols should plan migration to vSAN or VMFS. Do not select vVols for new deployments on VCF 9.0.
- **Version number jump:** VCF jumped from version 5.x directly to 9.0 to align all component version numbers (vSphere 9, ESXi 9, vSAN 9, NSX 9). There is no VCF 6.x, 7.x, or 8.x.
- **vSAN ESA preferred:** ESA is the preferred storage architecture for new VCF 9.0 deployments with all-NVMe hardware. OSA remains supported for existing environments.

**Key differences between vSphere 7 and 8 storage:**
- **vSAN OSA vs ESA:** vSphere 8 introduced ESA, a fundamentally redesigned storage architecture for all-NVMe clusters. ESA eliminates the cache/capacity tier distinction, using a single storage pool. This simplifies capacity planning (no cache-to-capacity ratio decisions), improves compression efficiency, and eliminates snapshot performance penalties. OSA remains supported in vSphere 8 for existing and mixed-drive deployments.
- **vSAN Max:** Introduced in vSphere 8.0 U2, vSAN Max enables disaggregated storage -- dedicated storage-only nodes that provide vSAN storage to compute-only hosts, allowing independent scaling of compute and storage. This addresses a longstanding HCI limitation.
- **Storage policy changes:** ESA simplifies storage policies by removing cache-tier-specific settings. RAID-5/6 erasure coding on ESA performs significantly better than on OSA due to the single-tier architecture. FTT and RAID policy selection remains the same conceptually but with better write performance on ESA.
- **Snapshot improvements:** vSAN OSA snapshots are known for performance degradation with deep snapshot chains. ESA uses a new native snapshot implementation that avoids the I/O penalty, making snapshots practical for backup and cloning workflows.
- **Native Key Provider:** vSphere 8 introduced the vSphere Native Key Provider, allowing vSAN encryption without an external KMS. This simplifies deployment for environments that do not have an existing KMIP-compliant key manager.

## Reference Links

- [vSAN documentation](https://docs.vmware.com/en/VMware-vSAN/index.html) -- vSAN OSA and ESA deployment, storage policies, and capacity planning
- [vSphere storage guide](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-storage/GUID-8AE88758-20C1-4873-99C7-181EF9ACFA70.html) -- VMFS, NFS, vVols, SPBM, and Storage DRS configuration
- [vSAN design guide](https://techdocs.broadcom.com/us/en/vmware-cis/vsan/vsan/8-0/vsan-planning-and-deployment-guide-80/planning-and-designing-a-vsan-cluster.html) -- cluster sizing, disk group design, and fault domain configuration

## See Also

- `general/data.md` -- general data architecture patterns
- `providers/vmware/compute.md` -- VM storage policies and encryption
- `providers/vmware/infrastructure.md` -- vSAN cluster configuration
- `providers/vmware/data-protection.md` -- storage replication and backup
