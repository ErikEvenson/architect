# Hystax Acura (Live Migration and Disaster Recovery)

## Scope

Hystax Acura is a vendor-neutral, any-to-any live migration and disaster recovery platform. Covers agent-based block-level replication, migration orchestration, DR with continuous replication, and cost optimization (OptScale). Applicable when migrating workloads between heterogeneous platforms — VMware to OpenStack/KVM, cloud to cloud, physical to virtual, or any combination. For Nutanix-native migration tooling, see `providers/nutanix/migration-tools.md`. For AWS-native migration services, see `providers/aws/migration-services.md`. For general migration planning, see `general/workload-migration.md`.

## Checklist

### Platform and Architecture

- [ ] **[Critical]** Is the Hystax Acura controller deployed on the target platform with adequate resources? (The controller manages replication, orchestration, and the web UI. Deploy on the target cloud/hypervisor — OpenStack, AWS, Azure, GCP, or KVM. Requires a dedicated VM with connectivity to both source agents and target infrastructure.)
- [ ] **[Critical]** Is network connectivity established between source replication agents and the Acura controller? (Agents connect to the controller on TCP 443 for control and send logs on UDP 12201. Replication data flows through the controller's receiver service or, in newer versions, directly via Receiver Mesh for improved scalability.)
- [ ] **[Critical]** Are replication agents deployed on all source workloads? (Agent-based: install the Hystax replication agent on each source VM or physical server. Supports Windows and Linux. Agents perform block-level replication of all attached disks. For agentless VMware sources, Hystax supports snapshot-based replication via vCenter API as an alternative.)
- [ ] **[Recommended]** Is Receiver Mesh enabled for large-scale migrations? (Receiver Mesh, introduced in Acura 4.4+, removes the controller from the critical replication data path. Replication data flows directly from agents to cloud storage, improving scalability and eliminating the controller as a throughput bottleneck. Recommended for environments with 50+ concurrent replications.)

### Source and Target Compatibility

- [ ] **[Critical]** Are source and target platforms confirmed as supported? (Sources: VMware ESXi, Hyper-V, KVM, OpenStack, AWS, Azure, GCP, Oracle Cloud, Alibaba Cloud, bare metal physical servers. Targets: OpenStack/KVM, AWS, Azure, GCP, Alibaba Cloud. Not all source-target combinations may be supported in every release — verify against the current compatibility matrix.)
- [ ] **[Critical]** Are source workload operating systems supported? (Windows Server 2012 R2+, Windows 10/11, RHEL/CentOS 7+, Ubuntu 16.04+, Debian 9+, SLES 12+, Oracle Linux 7+. Custom or hardened kernels may require agent compatibility verification. Check the Hystax OS compatibility matrix for the deployed version.)
- [ ] **[Recommended]** Are workloads with unsupported configurations identified? (Physical servers with hardware RAID controllers may require driver injection at the target. VMs with GPU passthrough, SR-IOV, or proprietary virtual hardware may not replicate cleanly. Identify these early and plan alternative migration paths.)

### Replication and Cutover

- [ ] **[Critical]** Is bandwidth estimated for initial seeding and ongoing replication? (Block-level replication transfers all used blocks during initial seed, then replicates changed blocks continuously. Estimate: `Used Disk (TB) / Available Bandwidth (Gbps) × 1.2 overhead = Seed Duration`. Hystax supports network compression and deduplication to reduce transfer volume by 30-50%.)
- [ ] **[Recommended]** Are migration plans organized into waves with application dependency grouping? (Use Hystax orchestration to define migration plans that launch dependent VMs in sequence — database first, then application, then web tier. Hystax supports boot order sequencing and post-launch scripts within migration plans.)
- [ ] **[Recommended]** Are test migrations performed before production cutover? (Hystax supports unlimited test migrations — launch a full replica of the workload on the target without disrupting the source or stopping replication. Use test migrations to validate network connectivity, application functionality, and performance before committing to cutover.)
- [ ] **[Recommended]** Is the cutover window sized based on final delta sync duration? (Continuous replication keeps the target close to the source. At cutover, the source is shut down, a final delta sync completes, and the target is launched. Delta sync duration depends on the change rate since the last sync — typically seconds to minutes for most workloads.)

### Disaster Recovery

- [ ] **[Recommended]** Is Hystax DR evaluated alongside migration for workloads requiring ongoing protection? (Hystax Acura provides continuous replication for DR with configurable RPO. After migration, the same replication agents can be repurposed for DR protection to a secondary site or cloud. DR failover and failback are orchestrated through the same Acura controller.)
- [ ] **[Optional]** Are DR runbooks defined in Hystax with automated failover sequencing? (Hystax DR plans support boot ordering, network reconfiguration, and post-launch scripts. Define recovery plans per application group with documented RTO targets. Test DR failover regularly — Hystax supports non-disruptive DR testing.)

## Why This Matters

Hystax Acura occupies a unique position in the migration tooling landscape: it is one of the few platforms that supports genuinely heterogeneous, any-to-any live migration with continuous block-level replication. Most migration tools are either vendor-specific (Nutanix Move for VMware-to-AHV, AWS Application Migration Service for anything-to-AWS) or limited to specific source-target pairs. Hystax's vendor neutrality makes it particularly valuable for VMware-to-OpenStack and VMware-to-KVM migrations — scenarios that have become increasingly common since the Broadcom acquisition drove organizations to evaluate VMware alternatives.

The platform's agent-based architecture means it works at the block level regardless of the source hypervisor, cloud provider, or physical hardware. This eliminates the need for different tools for different source platforms within the same migration program. For organizations migrating from multiple source environments (e.g., VMware + Hyper-V + physical servers) to a single target (e.g., OpenStack), Hystax provides a single replication and orchestration layer.

The combined migration and DR capability is also significant. Many migration programs discover mid-project that they need DR for workloads that have already migrated to the new platform. With Hystax, the same agents and controller used for migration can be reconfigured for ongoing DR replication, avoiding a second tool deployment. However, Hystax is not a backup solution — it provides replication for mobility and DR, not point-in-time recovery or long-term retention.

Pricing is per-replication (per-workload) and is typically negotiated based on scale. For large migration programs (hundreds or thousands of VMs), the per-VM cost is competitive with vendor-specific tools, but for small migrations (under 20 VMs), the controller deployment overhead may not be justified.

## Common Decisions (ADR Triggers)

- **Hystax vs vendor-native migration tools** — Hystax (vendor-neutral, any-to-any, single tool for heterogeneous sources) vs Nutanix Move (free, tightly integrated with AHV, VMware/Hyper-V sources only) vs AWS Application Migration Service (free, AWS-target only) vs Azure Migrate (free, Azure-target only). Use Hystax when migrating to OpenStack/KVM, migrating from multiple source types simultaneously, or when the target is not a hyperscaler. Use vendor-native tools when migrating to a single vendor's platform and the source is supported.
- **Hystax vs Zerto for DR** — Hystax Acura (any-to-any DR, agent-based, combined migration + DR) vs Zerto (hypervisor-level replication, near-synchronous RPO, journal-based recovery, VMware/Hyper-V focus). Zerto is more mature for VMware-to-VMware DR with sub-minute RPO. Hystax is more flexible for cross-platform DR (e.g., VMware-to-OpenStack DR, cloud-to-on-prem DR).
- **Agent-based vs agentless replication** — Hystax agent-based (block-level, works on any platform including physical, requires agent installation on each VM) vs agentless via vCenter API (snapshot-based, no agent installation, VMware sources only, higher source-side impact during snapshots). Agent-based is preferred for production workloads where snapshot stun is unacceptable. Agentless is simpler for VMware environments where agent installation is restricted.
- **Receiver Mesh vs controller-routed replication** — Receiver Mesh (direct agent-to-storage replication, scales horizontally, requires Acura 4.4+) vs controller-routed (all data flows through controller, simpler architecture, controller becomes throughput bottleneck at scale). Use Receiver Mesh for 50+ concurrent replications or when controller bandwidth is constrained.
- **Migration-only vs migration + DR** — deploy Hystax for migration only (decommission after migration completes) vs retain Hystax for ongoing DR protection post-migration. Retaining for DR avoids deploying a second DR tool but adds ongoing licensing and controller operational overhead. Evaluate whether the target platform has native DR capabilities (e.g., OpenStack Masakari, cloud-native DR) that could replace Hystax post-migration.

## Reference Links

- [Hystax Acura Cloud Migration](https://hystax.com/cloud-migration/) — product overview, supported platforms, and feature summary
- [Hystax Acura Documentation (Migration)](https://hystax.com/documentation/live-cloud-migration/index.html) — deployment guides, agent installation, migration plan configuration
- [Hystax Acura Documentation (DR)](https://hystax.com/documentation/disaster-recovery-and-cloud-backup/) — DR configuration, failover procedures, runbook setup
- [Hystax Platform Compatibility Matrix](https://hystax.com/hystax-acura-platform-compatibility-matrix/) — supported source/target platforms and OS versions
- [Hystax Acura Full Product Specification](https://hystax.com/hystax-acura-full-product-specification/) — detailed technical specification including architecture, networking, and API
- [Hystax Acura Network Scheme](https://hystax.com/hystax-acura-network-scheme/) — network architecture, port requirements, and connectivity diagrams
- [Hystax VMware to OpenStack Migration](https://hystax.com/hystax-acura-migration-from-vmware-to-openstack/) — VMware-to-OpenStack specific migration guide
- [Hystax OptScale (Cost Optimization)](https://hystax.com/optscale/) — companion product for cloud cost optimization and FinOps

## See Also

- `general/workload-migration.md` — cloud-agnostic migration planning, wave methodology, and cutover procedures
- `general/data-migration-tools.md` — migration tool landscape including database and storage migration
- `providers/nutanix/migration-tools.md` — Nutanix Move, Veeam, and Zerto for AHV migrations
- `providers/aws/migration-services.md` — AWS Application Migration Service, DMS, and Transfer Family
- `patterns/migration-cutover.md` — cutover execution mechanics applicable to each migration wave
- `patterns/hypervisor-migration.md` — hypervisor change patterns (VMware to KVM/AHV/Hyper-V)
- `general/disaster-recovery.md` — DR architecture patterns including replication-based DR
