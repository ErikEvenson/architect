# VMware Compute

## Checklist

- [ ] Are vSphere clusters sized with N+1 (or N+2 for critical workloads) host capacity to accommodate DRS rebalancing and HA failover without performance degradation?
- [ ] Is DRS configured with the appropriate automation level (fully automated for general workloads, partially automated for latency-sensitive VMs) and migration threshold tuned to avoid excessive vMotion?
- [ ] Are VM-host affinity rules defined for licensing compliance (e.g., Oracle, SQL Server pinning to specific hosts) and anti-affinity rules separating redundant VMs across hosts?
- [ ] Is HA admission control configured with the correct policy (percentage-based for uniform clusters, slot-based for heterogeneous, dedicated failover host for deterministic failover) reserving sufficient capacity for the planned number of host failures?
- [ ] Are VMs right-sized with appropriate vCPU counts (avoiding over-provisioning past physical core count per host) and memory reservations set for critical workloads to prevent ballooning and swapping?
- [ ] Are resource pools structured to enforce shares, limits, and reservations at the business-unit or tier level, avoiding deeply nested resource pool hierarchies that cause unexpected resource allocation behavior?
- [ ] Is EVC (Enhanced vMotion Compatibility) mode set at the cluster level to the lowest common CPU generation, ensuring vMotion compatibility during rolling hardware refreshes?
- [ ] Are VM hardware versions intentionally managed (not auto-upgraded) to maintain compatibility with the oldest ESXi host in the cluster and to control feature exposure?
- [ ] Is VM encryption (vSphere Native Key Provider or external KMS like HyTrust, Thales) configured for workloads requiring encryption at rest, with an understanding that encrypted VMs cannot use some features (e.g., fault tolerance, suspend/resume)?
- [ ] Is vSphere Fault Tolerance (FT) reserved only for single-vCPU or dual-vCPU mission-critical VMs requiring zero-downtime failover, with HA used as the standard availability mechanism for all other workloads?
- [ ] Are content libraries configured for VM template distribution across vCenters, with subscriber libraries pulling from a publisher to ensure consistent golden images and OVF templates?
- [ ] Is NUMA topology respected in VM sizing (vCPUs and memory fitting within a single NUMA node) to avoid cross-NUMA memory access latency, especially for databases and latency-sensitive applications?
- [ ] Are vMotion network interfaces configured on dedicated VMkernel adapters with sufficient bandwidth (10GbE minimum, 25GbE recommended) and multi-NIC vMotion enabled for large-memory VM migrations?

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
