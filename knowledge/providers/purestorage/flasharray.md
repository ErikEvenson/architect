# Pure Storage FlashArray

## Scope

Pure Storage FlashArray all-flash block storage: FlashArray//X (hybrid NVMe/SAS) and //XL (scale-out NVMe), Purity//FA operating environment, ActiveCluster synchronous replication, ActiveDR asynchronous replication, SafeMode snapshots, host connectivity (FC, iSCSI, NVMe-oF), Evergreen//Forever subscription model, REST API (Purity 2.x), and integration with VMware, Linux, Windows, and Kubernetes (Pure CSI).

## Checklist

- [ ] **[Critical]** Is the FlashArray model selected based on workload requirements? (//X for general-purpose block storage with mixed NVMe/SAS DirectFlash — //XL for high-performance workloads requiring NVMe end-to-end with dual-controller scale-out and up to 4.4M IOPS per array)
- [ ] **[Critical]** Is Purity//FA version compatible with all planned features? (ActiveCluster requires Purity 5.x+, ActiveDR requires 6.1+, SafeMode snapshots require 5.2.6+, NVMe-oF/RoCE requires 6.1+, file services require 6.3.4+ — verify release notes for feature dependencies)
- [ ] **[Critical]** Is ActiveCluster configured correctly for zero-RPO synchronous replication? (requires Purity 5.x+, a Mediator VM on a third site, maximum 10ms round-trip latency between arrays, synchronous replication of pods, automatic transparent failover — Mediator must be reachable from both arrays)
- [ ] **[Critical]** Are SafeMode snapshots enabled for ransomware protection? (immutable snapshots that cannot be deleted or modified even by array administrators — requires Pure Support PIN-based authorization to disable, set appropriate eradication timer of 1-30 days, applies to protection group snapshots)
- [ ] **[Critical]** Is host connectivity designed for redundancy? (minimum 2 paths per host with multipath I/O — FC: multi-initiator to multi-target zoning, iSCSI: multiple subnets with CHAP authentication, NVMe-oF: RDMA or TCP with ANA multipathing)
- [ ] **[Critical]** Are protection groups configured for all critical volumes? (group volumes by RPO/RTO requirements, configure snapshot schedules per group, set replication targets for off-array copies — snap-to-snap replication does not require additional licensing)
- [ ] **[Recommended]** Is the Evergreen subscription model evaluated? (Evergreen//Forever: non-disruptive controller upgrades every 3 years included, capacity-on-demand with right-size guarantee — Evergreen//Flex: consumption-based, pay-per-use with Pure as-a-Service SLA — Evergreen//One: unified subscription across block, file, and object)
- [ ] **[Recommended]** Is Pure1 Meta cloud management connected? (SaaS-based monitoring, predictive analytics with Pure1 Meta AI, capacity planning, performance trending, hardware lifecycle tracking — requires call-home connectivity via HTTPS port 443 to Pure1 cloud)
- [ ] **[Recommended]** Is ActiveDR configured for asynchronous disaster recovery? (continuous replication with near-zero RPO, one-click failover and failback, no Mediator required unlike ActiveCluster — minimum bandwidth: calculate based on daily change rate and available WAN bandwidth)
- [ ] **[Recommended]** Are host groups and volume groups organized for management at scale? (host groups for clustered hosts like VMware ESXi clusters, volume groups for application-consistent snapshot sets — avoid one-to-one host-to-volume mappings in large environments)
- [ ] **[Recommended]** Is data reduction ratio realistic for capacity planning? (FlashArray typically achieves 5:1 average data reduction with inline deduplication, compression, and thin provisioning — do not plan capacity based on best-case ratios, use Pure1 workload planner for estimates based on actual workload profiles)
- [ ] **[Recommended]** Is the Pure Storage CSI driver deployed for Kubernetes integration? (supports dynamic provisioning, snapshots, clones, volume expansion, topology-aware provisioning — use Pure Service Orchestrator (PSO) or the newer Pure CSI driver for cloud-native workflows)
- [ ] **[Optional]** Is NVMe-oF (NVMe over Fabrics) connectivity planned? (NVMe-oF/RoCE or NVMe-oF/TCP for lowest latency — requires compatible HBAs, switches with lossless Ethernet for RoCE, and Purity 6.1+ — delivers up to 50% lower latency than FC for latency-sensitive workloads)
- [ ] **[Optional]** Is vVol integration configured for VMware environments? (VASA provider for per-VM storage management, policy-based provisioning, VM-granular snapshots and replication without VMFS overhead — requires vSphere 6.5+ and Purity 5.x+)
- [ ] **[Optional]** Are REST API v2.x integrations planned for automation? (Purity REST API 2.x is the modern API — supports Ansible modules, Terraform provider, PowerShell SDK, Python SDK — API 1.x is deprecated, migrate automations to v2.x)
- [ ] **[Optional]** Is QoS (bandwidth/IOPS limiting) configured for noisy-neighbor prevention? (per-volume bandwidth and IOPS limits in Purity 6.0+ — use for multi-tenant or mixed-workload arrays to prevent a single volume from consuming all performance)

## Why This Matters

FlashArray is a tier-1 enterprise all-flash storage platform with a unique Evergreen ownership model that decouples hardware refresh from data migration. Design decisions around replication topology (ActiveCluster vs ActiveDR), host connectivity protocol, and protection group strategy directly impact RPO/RTO capabilities and cannot be easily changed post-deployment.

ActiveCluster's requirement for a Mediator VM on a third site is frequently overlooked — without it, automatic failover does not function and the cluster degrades to manual recovery. SafeMode snapshots are the primary defense against ransomware on FlashArray, but the eradication timer must be set before an attack occurs. Data reduction ratios vary dramatically by workload type (databases may see 2:1, VDI can exceed 10:1), and overestimating reduction leads to premature capacity exhaustion.

The Evergreen//Forever model means the array hardware is refreshed every 3 years non-disruptively, but this only applies if the subscription is maintained — lapsed subscriptions revert to traditional support without controller upgrades. Understanding the subscription model is essential for TCO analysis.

## Common Decisions (ADR Triggers)

- **FlashArray model selection** — //X (cost-effective, mixed NVMe/SAS, up to 3PB effective) vs //XL (performance-oriented, all-NVMe, dual-controller scale-out, up to 4.4M IOPS) vs //C (capacity-optimized QLC, for secondary/archive workloads) — workload IOPS and latency requirements determine model
- **Replication strategy** — ActiveCluster (synchronous, zero RPO, requires Mediator and <10ms RTT) vs ActiveDR (asynchronous, near-zero RPO, no Mediator, any distance) vs snapshot replication (scheduled, configurable RPO) — depends on RPO/RTO requirements and WAN characteristics
- **Host connectivity protocol** — Fibre Channel (established, mature multipathing, 16/32Gb) vs iSCSI (IP-based, lower cost, 10/25GbE) vs NVMe-oF (lowest latency, requires infrastructure investment) — existing infrastructure and latency requirements drive the choice
- **Subscription model** — Evergreen//Forever (CapEx with included upgrades) vs Evergreen//Flex (OpEx consumption-based) vs Evergreen//One (unified subscription across platforms) — financial model preference, cloud-like vs traditional procurement
- **VMware integration approach** — VMFS datastores (traditional, well-understood) vs vVols (per-VM granularity, policy-driven) — vVols offer better granularity but add VASA provider dependency
- **Snapshot immutability** — SafeMode enabled (ransomware protection, requires Pure Support to disable) vs standard snapshots (administrator-deletable) — compliance and security posture determine requirement
- **Kubernetes storage provisioner** — Pure CSI driver direct (simpler, single-array) vs Pure Fusion (multi-array abstraction, storage-as-code) — depends on scale and multi-array requirements

## Reference Links

- [Pure Storage FlashArray Documentation](https://support.purestorage.com/FlashArray) — official FlashArray administration and configuration guides
- [Purity//FA REST API Reference](https://support.purestorage.com/FlashArray/PurityFA/Purity_FA_REST_API) — REST API v2.x reference documentation
- [ActiveCluster Design Guide](https://support.purestorage.com/Solutions/Pure_Storage_ActiveCluster) — synchronous replication architecture and requirements
- [Pure Storage CSI Driver](https://github.com/purestorage/pso-csi) — Kubernetes CSI driver source and documentation
- [Pure1 Meta](https://pure1.purestorage.com/) — cloud-based monitoring and analytics portal
- [Pure Storage Ansible Collection](https://galaxy.ansible.com/purestorage/flasharray) — Ansible modules for FlashArray automation
- [Pure Storage Terraform Provider](https://registry.terraform.io/providers/PureStorage-OpenConnect/flash/latest) — Terraform provider for infrastructure-as-code
- [FlashArray Best Practices for VMware](https://support.purestorage.com/Solutions/VMware) — VMware vSphere integration guides

## See Also

- `general/storage.md` — general storage architecture patterns
- `general/disaster-recovery.md` — DR strategy and RPO/RTO planning
- `general/ransomware-resilience.md` — ransomware protection strategies including immutable snapshots
- `providers/purestorage/flashblade.md` — FlashBlade unstructured data and object storage
- `providers/purestorage/portworx.md` — Portworx Kubernetes-native storage
- `providers/vmware/storage.md` — VMware storage integration including vVols
- `providers/kubernetes/storage.md` — Kubernetes CSI and persistent storage
