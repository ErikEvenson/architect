# Nutanix Compute (AHV and VM Management)

## Scope

Nutanix AHV compute configuration: vCPU/pCPU ratios, CPU pinning and NUMA alignment, VM affinity and anti-affinity rules, VM HA and live migration, AHV host networking bond modes, CVM resource allocation, VM image management via Prism Central, and Nutanix Guest Tools (NGT).


## Checklist

- [ ] **[Critical]** Is the vCPU to pCPU ratio appropriate for the workload? (1:1 to 4:1 for general workloads, 1:1 for latency-sensitive applications like databases, up to 8:1 for VDI with careful monitoring)
- [ ] **[Critical]** Are VM CPU and memory reservations configured for critical workloads to prevent resource contention during cluster degradation (N+1 or N+2 scenarios)?
- [ ] **[Recommended]** Is AHV CPU scheduling set correctly, using CPU pinning for latency-sensitive VMs and NUMA alignment for memory-intensive applications (SQL Server, SAP HANA)?
- [ ] **[Critical]** Are VM affinity rules configured to co-locate dependent VMs on the same host (e.g., app + local cache), and anti-affinity rules to separate redundant VMs (e.g., HA pairs, domain controllers)?
- [ ] **[Optional]** Is GPU passthrough configured using AHV's vGPU support (NVIDIA GRID/vGPU profiles) for VDI, AI/ML, or rendering workloads, with appropriate GPU driver management?
- [ ] **[Critical]** Is VM High Availability (HA) enabled at the cluster level with host reservation capacity guaranteeing that all VMs can restart on surviving hosts after node failure?
- [ ] **[Recommended]** Are live migrations tested and confirmed working for all production VMs, with VM compatibility checks ensuring no host-specific CPU feature dependencies?
- [ ] **[Critical]** Is the AHV host networking configured with appropriate bond modes -- active-backup for management traffic, balance-slb or LACP (802.3ad) for VM traffic -- on OVS bridges?
- [ ] **[Recommended]** Are VM images managed through Prism Central image service (not uploaded per-cluster), with image placement policies controlling which clusters cache which images?
- [ ] **[Critical]** Is CVM (Controller VM) resource allocation adequate -- minimum 12 vCPUs and 32 GB RAM for general workloads, increased to 16+ vCPUs and 48+ GB for heavy storage I/O or dedup/compression workloads?
- [ ] **[Recommended]** Are VM boot configurations using UEFI with Secure Boot for Windows Server 2016+ and modern Linux distributions, with vTPM enabled where required?
- [ ] **[Critical]** Is the AHV scheduler host capacity reservation (HA reservation) configured to tolerate the loss of at least one host without VM resource starvation?
- [ ] **[Recommended]** Are VM hardware clocks set to the correct timezone and NTP sources, with Nutanix Guest Tools (NGT) installed for VSS-consistent snapshots and cross-hypervisor migration support?

## Why This Matters

AHV is a KVM-based hypervisor tightly integrated with the Nutanix Distributed Storage Fabric, meaning compute and storage performance are deeply coupled. CVM resource starvation directly degrades storage I/O for the entire host. Overcommitting vCPUs beyond safe ratios causes CPU ready times to spike, which manifests as application latency rather than obvious failures. NUMA misalignment for large VMs forces remote memory access with 2-3x latency penalty. Without affinity rules, HA restart can land redundant VMs on the same host, creating a single point of failure. Bond mode selection on OVS bridges directly impacts throughput and failover behavior -- balance-slb provides basic load balancing without switch configuration, while LACP requires switch support but provides true link aggregation. GPU passthrough requires careful host-level planning since vGPU profiles consume fixed GPU memory and cannot be overcommitted.

## Common Decisions (ADR Triggers)

- **CPU overcommit ratio** -- Conservative (2:1) vs aggressive (6:1+), depends on workload burstiness and acceptable CPU ready percentages
- **NUMA alignment strategy** -- Automatic NUMA balancing vs explicit NUMA pinning for large VMs, cross-socket vs single-socket placement
- **Bond mode for VM traffic** -- active-backup (simple, no switch config) vs balance-slb (OVS-native load balancing) vs LACP (requires switch support, highest throughput)
- **GPU virtualization** -- Full GPU passthrough (1 VM per GPU) vs vGPU profiles (multiple VMs per GPU), NVIDIA GRID licensing model
- **VM HA reservation** -- Reserve capacity for 1 host failure (N+1) vs 2 host failures (N+2), impacts usable cluster capacity by 25-40%
- **Image management** -- Per-cluster image upload vs Prism Central centralized image management with placement policies
- **Guest tools** -- NGT (Nutanix-native, VSS integration, self-service restore) vs VMware Tools compatibility layer, impact on snapshot consistency

## Sizing Methodology

### vCPU:pCPU Ratios

| Workload Type | Recommended Ratio | Notes |
|---|---|---|
| General purpose (web, app servers) | 4:1 | Standard starting point; monitor CPU ready time <5% |
| Latency-sensitive (databases, real-time) | 2:1 | SQL Server, Oracle, Redis, message queues |
| Dedicated/licensed (per-core licensing) | 1:1 | Required for Oracle per-core licensing compliance, SAP HANA |
| VDI (task workers) | 6:1 to 8:1 | Monitor closely; bursty but short-duration CPU usage |
| VDI (knowledge workers) | 4:1 | More sustained CPU, Office apps, browser tabs |
| Batch/HPC | 1:1 to 2:1 | Sustained 100% CPU usage, overcommit causes queuing |

**CPU ready time** is the primary metric for detecting overcommit issues. A VM waiting for a physical CPU shows CPU ready >5%. Above 10% causes user-noticeable latency. Monitor via Prism Element > VM > Performance > CPU Ready.

### Memory Sizing

- **No memory overcommit for production workloads.** Nutanix AHV does not use memory ballooning by default, and memory overcommit leads to VM stalling or OOM conditions. Allocate physical RAM = sum of all VM RAM + CVM reservation + AHV hypervisor overhead.
- **CVM (Controller VM) reservation**: Minimum 32 GB RAM and 8 vCPUs per node for general workloads. Increase to 48-64 GB RAM and 12-16 vCPUs for heavy storage I/O, deduplication, compression, or erasure coding workloads. CVM memory directly impacts storage cache (Unified Cache) performance.
- **AHV hypervisor overhead**: ~1-2 GB RAM per host (minimal compared to other hypervisors).
- **Usable RAM per node** = Total Physical RAM - CVM RAM - AHV overhead. Example: 512 GB physical - 32 GB CVM - 2 GB AHV = 478 GB available for VMs.

### Storage Sizing

**Usable storage formula:**

```
Usable Capacity = (Raw Capacity / Replication Factor) x Data Efficiency Ratio

Where:
  Raw Capacity     = Sum of all drive capacities across cluster
  Replication Factor = RF2 (2 copies) or RF3 (3 copies)
  Data Efficiency  = Compression x Deduplication savings
                     (conservative estimate: 1.5x for compression alone)
                     (do not assume dedup unless workload is known to dedup well, e.g., VDI)
```

**Example:** 12-node cluster, each node has 2x 1.92 TB NVMe (cache/tier) + 4x 3.84 TB SSD (capacity)

```
Raw capacity tier  = 12 nodes x 4 drives x 3.84 TB = 184.32 TB raw
Usable (RF2)       = 184.32 / 2 = 92.16 TB
With 1.5x compression = 92.16 x 1.5 = 138.24 TB effective
CVM storage overhead = ~30-50 GB per node (negligible at scale)
```

**Important considerations:**
- Always size based on the capacity tier (HDD or SSD), not the cache/performance tier (NVMe/SSD)
- Account for CVM storage: each CVM uses ~30-50 GB for its own OS and logs
- Leave 10-15% free space headroom for Nutanix Curator garbage collection, snapshots, and cluster operations
- RF2 provides tolerance for 1 simultaneous component failure; RF3 for 2 (required for critical/compliance workloads)

### N+1 (and N+2) Node Planning

The cluster must have sufficient capacity to absorb the failure of at least one node (N+1 for RF2) or two nodes (N+2 for RF3) and continue running all VMs.

```
Usable compute (N+1) = (Total Nodes - 1) x Per-Node Usable Resources
Usable compute (N+2) = (Total Nodes - 2) x Per-Node Usable Resources

Example (4-node cluster, each node: 40 vCPU usable, 478 GB RAM usable):
  N+1: (4-1) x 40 = 120 vCPUs, (4-1) x 478 = 1,434 GB RAM
  Total VMs must fit within 120 vCPUs and 1,434 GB RAM

Example (5-node cluster):
  N+1: (5-1) x 40 = 160 vCPUs, (5-1) x 478 = 1,912 GB RAM
  The 5th node provides 33% more usable capacity than 4-node (vs 25% raw increase)
```

**Recommendation:** Minimum 4 nodes for production RF2 clusters (3 nodes works but N+1 leaves only 2 nodes carrying full load -- 50% utilization ceiling). For RF3, minimum 5 nodes.

### Example Sizing: Three-Tier Web Application

**Workload requirements:**
- Web tier: 4 VMs x (4 vCPU, 8 GB RAM, 100 GB disk)
- App tier: 4 VMs x (8 vCPU, 32 GB RAM, 200 GB disk)
- Database tier: 2 VMs x (16 vCPU, 128 GB RAM, 500 GB disk)
- Total: 10 VMs, 80 vCPU, 416 GB RAM, 2.2 TB disk

**Compute sizing (4:1 ratio for web/app, 2:1 for DB):**
- Web: 4 x 4 vCPU / 4 ratio = 4 pCPU needed
- App: 4 x 8 vCPU / 4 ratio = 8 pCPU needed
- DB: 2 x 16 vCPU / 2 ratio = 16 pCPU needed
- Total pCPU needed: 28 cores

**Memory sizing (no overcommit):**
- Total VM RAM: 416 GB
- CVM reservation: 32 GB per node
- AHV overhead: 2 GB per node

**Storage sizing (RF2, 1.5x compression):**
- Raw disk needed: 2.2 TB / 1.5 compression x 2 (RF2) = 2.93 TB raw

**Node selection (example: NX-3170-G8 with 2x Intel Xeon 8470, 52 cores/socket):**
- 3-node cluster: 3 x 104 cores = 312 cores total, 28 cores needed + N+1 = easily fits
- Memory per node: (416 GB / 2 nodes for N+1) + 34 GB overhead = ~242 GB minimum per node, so 256 GB per node works
- Storage: 3 nodes x 4 x 1.92 TB SSD = 23 TB raw, far exceeds 2.93 TB needed
- **Result: 3 nodes with 256 GB RAM each.** However, consider 4 nodes for better N+1 headroom and growth.

### Nutanix Sizer Tool

For production sizing, always validate with the **Nutanix Sizer** tool ([sizer.nutanix.com](https://sizer.nutanix.com/)), which accounts for:
- Specific hardware platform capabilities (NX, Dell XC, Lenovo HX, HPE DX)
- Workload-specific profiles (VDI, SQL Server, SAP, Splunk, general server)
- Storage efficiency estimates based on workload type
- CVM overhead and AHV reservation
- N+1/N+2 calculations with anti-affinity considerations
- Power and cooling estimates

Sizer outputs a Bill of Materials (BOM) with specific SKUs and provides a shareable sizing report for procurement and architecture review.

## See Also

- `general/compute.md` -- general compute architecture patterns
- `providers/nutanix/infrastructure.md` -- Nutanix cluster sizing and hypervisor selection
- `providers/nutanix/storage.md` -- Distributed Storage Fabric and CVM sizing
- `providers/nutanix/networking.md` -- AHV networking and Flow microsegmentation
