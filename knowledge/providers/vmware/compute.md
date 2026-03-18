# VMware Compute

## Scope

This document covers VMware vSphere compute configuration including cluster sizing, DRS, HA, resource management, VM hardware versions, encryption, Fault Tolerance, content libraries, NUMA awareness, and lifecycle management.

## Checklist

- [ ] **[Critical]** Are vSphere clusters sized with N+1 (or N+2 for critical workloads) host capacity to accommodate DRS rebalancing and HA failover without performance degradation?
- [ ] **[Critical]** Is DRS configured with the appropriate automation level (fully automated for general workloads, partially automated for latency-sensitive VMs) and migration threshold tuned to avoid excessive vMotion?
- [ ] **[Recommended]** Are VM-host affinity rules defined for licensing compliance (e.g., Oracle, SQL Server pinning to specific hosts) and anti-affinity rules separating redundant VMs across hosts?
- [ ] **[Critical]** Is HA admission control configured with the correct policy (percentage-based for uniform clusters, slot-based for heterogeneous, dedicated failover host for deterministic failover) reserving sufficient capacity for the planned number of host failures?
- [ ] **[Critical]** Are VMs right-sized with appropriate vCPU counts (avoiding over-provisioning past physical core count per host) and memory reservations set for critical workloads to prevent ballooning and swapping?
- [ ] **[Recommended]** Are resource pools structured to enforce shares, limits, and reservations at the business-unit or tier level, avoiding deeply nested resource pool hierarchies that cause unexpected resource allocation behavior?
- [ ] **[Recommended]** Is EVC (Enhanced vMotion Compatibility) mode set at the cluster level to the lowest common CPU generation, ensuring vMotion compatibility during rolling hardware refreshes?
- [ ] **[Recommended]** Are VM hardware versions intentionally managed (not auto-upgraded) to maintain compatibility with the oldest ESXi host in the cluster and to control feature exposure?
- [ ] **[Recommended]** Is VM encryption (vSphere Native Key Provider or external KMS like Entrust, Thales CipherTrust) configured for workloads requiring encryption at rest, with an understanding that encrypted VMs cannot use some features (e.g., fault tolerance, suspend/resume)?
- [ ] **[Optional]** Is vSphere Fault Tolerance (FT) reserved only for single-vCPU or dual-vCPU mission-critical VMs requiring zero-downtime failover, with HA used as the standard availability mechanism for all other workloads?
- [ ] **[Recommended]** Are content libraries configured for VM template distribution across vCenters, with subscriber libraries pulling from a publisher to ensure consistent golden images and OVF templates?
- [ ] **[Recommended]** Is NUMA topology respected in VM sizing (vCPUs and memory fitting within a single NUMA node) to avoid cross-NUMA memory access latency, especially for databases and latency-sensitive applications?
- [ ] **[Recommended]** Are vMotion network interfaces configured on dedicated VMkernel adapters with sufficient bandwidth (10GbE minimum, 25GbE recommended) and multi-NIC vMotion enabled for large-memory VM migrations?

## Why This Matters

Compute configuration in vSphere directly determines application availability, performance, and cost efficiency. Over-provisioning vCPUs leads to CPU ready time and co-stop (where multi-vCPU VMs wait for all virtual processors to be scheduled simultaneously), degrading performance worse than under-provisioning. HA admission control misconfiguration can either waste capacity (over-reserving) or leave insufficient room for failover (under-reserving), resulting in VMs that fail to restart after a host outage. DRS affinity rules are frequently audit-critical for software licensing compliance -- Oracle, for example, requires licensing all cores on any host where its VMs could run, making unconstrained DRS a significant financial liability. EVC mode misconfiguration blocks vMotion during hardware refreshes, forcing maintenance windows. Resource pool misuse (particularly nested pools with default shares) is one of the most common vSphere misconfigurations, silently starving workloads during contention.

## Common Decisions (ADR Triggers)

- **HA admission control policy** -- percentage-based (flexible, works well for uniform clusters) vs slot-based (predictable but wasteful with heterogeneous VM sizes) vs dedicated failover hosts (deterministic but idle capacity); percentage should match N+X host failure tolerance
- **DRS automation level** -- fully automated (best for dynamic workloads, reduces manual intervention) vs partially automated (initial placement only, recommended for workloads sensitive to vMotion) vs manual (recommendations only, for regulated environments requiring change control)
- **Fault tolerance vs HA** -- FT provides zero-downtime failover with a secondary shadow VM but is limited to 8 vCPUs, doubles resource consumption, and blocks snapshots/Storage vMotion; HA restarts VMs after failure with brief downtime but works universally
- **Resource pools vs VM-level reservations** -- pool-level controls for multi-tenant isolation vs per-VM reservations for guaranteed resources; pools are frequently misused as organizational folders, causing unintended resource allocation
- **VM hardware version strategy** -- upgrade immediately for new features (virtual NVMe, Precision Clock, vPMem) vs hold at a specific version for cross-cluster compatibility and rollback flexibility
- **NUMA-aware sizing** -- fit within NUMA boundaries for performance-critical VMs vs allow wide VMs for workloads that need large vCPU counts regardless of NUMA topology
- **Content library architecture** -- single publisher with subscribers for multi-site template consistency vs local libraries per site for independence; published libraries require reliable WAN connectivity

## Version Notes

| Feature | vSphere 7 (7.0 U3) | vSphere 8 (8.0 U2+) | vSphere 9 / VCF 9.0 |
|---|---|---|---|
| Maximum VM hardware version | vmx-19 | vmx-21 | vmx-22 |
| DPU (Data Processing Unit) support | Not available | GA (offload networking/security to SmartNIC) | GA (enhanced) |
| DRS | GA (load balancing) | GA (improved workload placement, DRS scores) | GA |
| vSphere Lifecycle Manager (vLCM) | GA (image-based) | GA (enhanced firmware/driver management) | GA (sole lifecycle tool) |
| Update Manager (VUM) | Supported (baseline-based) | Deprecated (replaced by vLCM) | **Removed** |
| Host Profiles | GA | GA | **Deprecated** (use vSphere Configuration Profiles) |
| Auto Deploy | GA | GA | **Deprecated** |
| vSphere Configuration Profiles | Not available | GA (host config drift remediation) | GA (replaces Host Profiles) |
| DevOps Center | Not available | GA (VM Service for developer self-service) | GA |
| VM vGPU profiles | GA (NVIDIA GRID) | GA (improved MIG support, vGPU 16+) | GA (enhanced AI/ML) |
| vSphere Fault Tolerance | GA (up to 8 vCPU) | GA (up to 8 vCPU, unchanged) | GA |
| Content Library | GA | GA (improved OVF deployment, check-in/check-out) | GA |
| vSphere+ (SaaS management) | Not available | GA (cloud-connected vCenter management) | GA |
| AI/ML workload support | Basic GPU passthrough | Enhanced (vSphere AI integration, DPU offload) | Enhanced (VCF AI focus) |
| Assignable Hardware | Not available | GA (framework for DPU, GPU, other devices) | GA |

**Key changes in vSphere 9 / VCF 9.0 compute:**
- **VUM removed:** VMware Update Manager (VUM) is fully removed in vSphere 9. All host lifecycle management must use vSphere Lifecycle Manager (vLCM) with image-based desired state. Organizations still using VUM baselines must migrate to vLCM before upgrading.
- **Host Profiles deprecated:** Host Profiles are deprecated in vSphere 9 in favor of vSphere Configuration Profiles. Plan migration from Host Profiles to Configuration Profiles for host configuration management.
- **Auto Deploy deprecated:** vSphere Auto Deploy is deprecated in vSphere 9. Evaluate alternative stateless host provisioning approaches using vLCM image-based management.
- **Version number alignment:** VCF jumped from 5.x directly to 9.0 to align all component versions (vSphere 9, ESXi 9, vSAN 9, NSX 9). There is no VCF 6.x, 7.x, or 8.x.

**Key differences between vSphere 7 and 8 compute:**
- **DPU support:** vSphere 8 introduced support for Data Processing Units (SmartNICs such as NVIDIA BlueField, AMD Pensando). DPUs offload networking, security, and storage I/O processing from the host CPU, freeing compute resources for workloads. The ESXi control plane runs on the DPU in a "stateless" host model.
- **VM hardware versions:** vmx-21 (vSphere 8) adds support for new virtual device types and performance optimizations. Upgrading VM hardware version is one-way -- ensure all hosts in the cluster are at the target ESXi version before upgrading VMs.
- **DRS improvements:** vSphere 8 DRS uses a workload placement scoring model that provides better initial placement and more predictable migrations. DRS scores are visible in the UI, making it easier to understand why migrations occur.
- **Lifecycle Manager vs Update Manager:** vSphere 7 supported both vLCM (image-based, desired-state) and VUM (baseline-based, legacy). vSphere 8 deprecates VUM in favor of vLCM exclusively. vLCM manages ESXi images, firmware, and drivers as a single desired-state image per cluster. Organizations using VUM-based workflows must migrate to vLCM.
- **vSphere Configuration Profiles:** New in vSphere 8, these enable host configuration drift detection and remediation at the cluster level, ensuring all hosts maintain consistent settings for networking, storage, and security.
- **vSphere+:** Cloud-connected SaaS management layer that provides centralized vCenter visibility, subscription-based licensing, and lifecycle management across distributed vSphere environments.

## See Also

- `general/compute.md` -- general compute architecture patterns
- `providers/vmware/infrastructure.md` -- VMware cluster and host configuration
- `providers/vmware/storage.md` -- vSAN and storage for VM workloads
- `providers/vmware/networking.md` -- VDS and NSX networking for VMs
