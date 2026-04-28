# Zerto (Disaster Recovery and Migration)

## Scope

Zerto (now HPE Zerto) is a hypervisor-level, journal-based continuous replication platform for disaster recovery, migration, and workload mobility. Covers Virtual Replication Appliance (VRA) architecture, Virtual Protection Groups (VPGs), journal-based recovery, cross-platform DR and migration between VMware vSphere, Microsoft Hyper-V, AWS, Azure, and GCP. Does not cover backup or long-term retention — Zerto is a replication platform, not a backup solution. For vendor-neutral agent-based migration, see `providers/hystax/migration.md`. For Nutanix-native migration, see `providers/nutanix/migration-tools.md`. For general DR architecture, see `general/disaster-recovery.md`.

## Checklist

### Architecture and Deployment

- [ ] **[Critical]** Is the Zerto Virtual Manager (ZVM) deployed at both the protection (source) and recovery (target) sites? (ZVM is a Linux appliance since v10 — the Windows ZVM is fully deprecated. The ZVM manages replication orchestration, VPG configuration, and failover/failback operations. One ZVM per site, paired with the remote site's ZVM for bidirectional replication.)
- [ ] **[Critical]** Is a Virtual Replication Appliance (VRA) deployed on every ESXi or Hyper-V host that has protected VMs? (VRAs intercept writes at the hypervisor level and replicate them to the recovery site. One VRA per host. VRA sizing: 1 vCPU minimum, RAM determines I/O buffer size — 2 GB minimum, 4-8 GB recommended for hosts with high write workloads. Each VRA supports up to 1,500 volumes.)
- [ ] **[Critical]** For cloud targets (AWS, Azure), is a Zerto Cloud Appliance (ZCA) deployed in the target cloud environment? (The ZCA functions as a combined ZVM + VRA for cloud sites. Deployed as an EC2 instance or Azure VM. Requires appropriate IAM/RBAC permissions to provision recovery instances, volumes, and networking.)
- [ ] **[Recommended]** Is the ZVM appliance sized appropriately? (Minimum 4 vCPUs and 8 GB RAM for up to 500 VMs. Scale to 8+ vCPUs and 16+ GB RAM for 500-2,000 VMs. ZVM requires persistent connectivity to vCenter/SCVMM and all VRAs.)

### Virtual Protection Groups (VPGs)

- [ ] **[Critical]** Are Virtual Protection Groups (VPGs) configured to group application tiers that must fail over together? (A VPG defines a set of VMs that share a common RPO, journal history, and failover/failback behavior. Group web + app + database VMs of an application into a single VPG so they recover as a unit with write-order fidelity across all VMs in the group.)
- [ ] **[Critical]** Is journal history configured per VPG based on RPO requirements? (Journal stores all writes for a configurable retention period — 1 hour to 30 days. Longer journal history requires more storage at the recovery site. Sizing: estimate daily change rate × journal retention days × 1.5 overhead. Every few seconds, all journals receive a checkpoint timestamp ensuring crash-consistent recovery to any point in time.)
- [ ] **[Critical]** Is journal storage provisioned on shared storage accessible by all recovery hosts? (Journal volumes must be on a datastore accessible to all hosts in the recovery cluster, not local storage. Journal volumes auto-expand based on write rate and retention, then auto-shrink when capacity is no longer needed. Monitor journal storage utilization to avoid datastore exhaustion.)
- [ ] **[Recommended]** Are VPG boot order and startup scripts configured for multi-tier applications? (Zerto supports boot ordering within a VPG — start database VM first, wait for port availability, then start application VM, then web VM. Post-failover scripts can reconfigure IP addresses, update DNS, or start application services.)

### Replication and RPO

- [ ] **[Critical]** Is network bandwidth sufficient for continuous replication between sites? (Zerto replicates every write asynchronously — typical RPO is 5-15 seconds. Bandwidth requirement: `Daily Change Rate (GB) / 86,400 seconds × 8 bits × 1.3 overhead = required Mbps`. Zerto compresses replication traffic but does not deduplicate. WAN optimization appliances can complement Zerto for bandwidth-constrained links.)
- [ ] **[Recommended]** Is WAN throttling configured to prevent replication from saturating production links? (Zerto supports bandwidth throttling per VPG or per site. Set maximum bandwidth during business hours and allow full utilization during off-hours. If replication consistently exceeds available bandwidth, RPO degrades — monitor RPO metrics in the ZVM dashboard.)
- [ ] **[Recommended]** Are RPO alerts configured with appropriate thresholds? (Zerto reports real-time RPO per VPG. Configure alerts when RPO exceeds the target — e.g., alert at 30 seconds, critical at 60 seconds. Sustained RPO breaches indicate insufficient bandwidth, storage I/O bottlenecks, or VRA resource constraints.)

### Failover and Recovery

- [ ] **[Critical]** Are failover tests scheduled regularly using Zerto's non-disruptive test failover? (Zerto supports test failover that creates recovery VMs in an isolated network bubble without disrupting production replication. Test failover validates that VMs boot, applications start, and data is consistent. Run test failovers at least quarterly — monthly for critical applications. Clean up test VMs after validation.)
- [ ] **[Recommended]** Is the failover type understood for each scenario? (Zerto provides three failover modes: **Test** — non-disruptive, isolated network, replication continues; **Live failover** — production failover, source VMs are shut down, recovery VMs start on target site, replication reverses for failback; **Move** — planned migration, graceful shutdown of source, final sync, start on target, no data loss.)
- [ ] **[Recommended]** Is failback planned and tested? (After a live failover, Zerto supports reverse replication and failback to the original site or a new site. Failback requires re-pairing sites, reverse-protecting VPGs, and performing a planned move back. Test the full failover-failback cycle, not just failover.)

### Platform Compatibility

- [ ] **[Recommended]** Are source and target platforms confirmed as supported for the deployed Zerto version? (Supported hypervisors: VMware vSphere 7.0/8.0+, Microsoft Hyper-V 2016/2019/2022. Supported clouds: AWS, Azure, GCP, IBM Cloud, Oracle Cloud. VMware Cloud targets: VMC on AWS, AVS, GCVE. VCF 9.0 supported as of Zerto 10.8. Check the Zerto Interoperability Matrix for exact version combinations.)

## Why This Matters

Zerto's architecture is fundamentally different from snapshot-based replication tools. By intercepting writes at the hypervisor I/O level (not at the storage layer), Zerto achieves near-synchronous replication with RPOs of 5-15 seconds without the performance impact of storage snapshots. The journal-based recovery model stores every write with a timestamp, enabling recovery to any point in time within the journal retention window — not just the last snapshot. This is critical for ransomware recovery: if encryption begins at 2:47 PM, Zerto can recover to 2:46:55 PM, before the encryption started.

The VPG concept ensures write-order fidelity across multiple VMs in an application group. When a three-tier application fails over, the database VM's recovery point is consistent with the application and web VMs' recovery points — they all recover to the same checkpoint. Without this, cross-VM consistency requires application-level coordination that most organizations cannot implement.

Zerto's primary limitation is its hypervisor-level architecture: it requires VRAs on every host, which means it only works with supported hypervisors (VMware, Hyper-V) and cloud platforms. It cannot protect physical servers, KVM hosts, or OpenStack environments — for those, agent-based tools like Hystax are needed. Zerto's per-VM licensing (starting at approximately $745/VM/year, with minimums and volume discounts) makes it cost-effective for critical workloads requiring sub-minute RPO but expensive for protecting large VM estates where longer RPOs are acceptable.

Since HPE's acquisition of Zerto in 2021, the product has been integrated into HPE GreenLake and positioned alongside HPE storage for hybrid cloud DR. The v10 line transitioned the ZVM from Windows to Linux, and recent releases (10.7, 10.8) added VCF 9.0 support, cloud encryption, and Azure Stack HCI compatibility.

## Common Decisions (ADR Triggers)

- **Zerto vs storage-level replication** — Zerto (hypervisor-level, application-aware VPGs, any-to-any recovery, 5-15s RPO) vs storage array replication (NetApp SnapMirror, Pure ActiveCluster, Dell RecoverPoint — storage-level, requires matching arrays or supported targets, synchronous or async). Zerto is storage-agnostic and provides application grouping. Storage replication is simpler when source and target use the same array vendor and application-level grouping is not needed.
- **Zerto vs Hystax** — Zerto (hypervisor-level, agentless on VMware/Hyper-V, journal-based point-in-time recovery, 5-15s RPO, mature VMware-to-cloud DR) vs Hystax (agent-based, any-to-any including physical/KVM/OpenStack, block-level replication, primarily migration-focused with DR capabilities). Use Zerto for VMware/Hyper-V environments requiring production-grade DR with sub-minute RPO. Use Hystax for migrations to OpenStack/KVM or when source platforms are outside Zerto's support matrix.
- **Zerto vs cloud-native DR** — Zerto (cross-platform, journal-based, consistent VPG failover, vendor-neutral) vs AWS Elastic Disaster Recovery (agent-based, AWS-target only, free service + compute during DR) vs Azure Site Recovery (agent-based, Azure-target, integrated with Azure Backup). Cloud-native DR is cheaper and simpler when the target is a single cloud. Zerto is preferred for multi-cloud DR, VMware-to-VMware DR, or when journal-based granular recovery is required.
- **Zerto vs SRM/Live Site Recovery** — Zerto (storage-agnostic, journal-based, cross-platform including cloud targets) vs VMware SRM/VCF Live Site Recovery (vSphere-native, requires vSphere Replication or array-based replication, VMware-to-VMware only). Zerto provides cloud targets and granular point-in-time recovery. SRM/Live Site Recovery is included with VCF licensing and integrates natively with vSphere but cannot replicate to cloud targets without VMC/AVS/GCVE.
- **Journal retention sizing** — short journal (1-24 hours, minimal storage, sufficient for hardware failure DR) vs long journal (7-30 days, significant storage, required for ransomware recovery where the encryption event may not be detected for days). Journal storage cost: `daily change rate × retention days × 1.5 = journal storage`. Organizations with ransomware recovery requirements should configure 7+ day journals for critical workloads.
- **VPG granularity** — per-application VPGs (each application group in its own VPG with tailored RPO, journal, and boot order — most flexible, most management overhead) vs per-tier VPGs (all databases in one VPG, all web servers in another — simpler but loses cross-tier consistency) vs large VPGs (many applications in one VPG — simplest but coarse recovery granularity). Per-application VPGs are recommended for production DR.

## Reference Links

- [Zerto Platform Components](https://www.zerto.com/zerto-platform/how-zerto-works/components-of-the-platform/) — architecture overview of ZVM, VRA, ZCA, and journal
- [Zerto Interoperability Matrix](https://www.zerto.com/myzerto/support/interoperability-matrix/) — supported hypervisor, OS, and cloud platform versions
- [Zerto Journal Sizing Best Practices](https://help.zerto.com/bundle/BP.Journal.Sizing.HTML/page/Journal_Overview_Sizing_and_Best_Practice.htm) — journal capacity planning and storage recommendations
- [Zerto Scale and Benchmarking Guidelines](https://help.zerto.com/bundle/Scale.Bench.Guide.HTML/page/VRA_Considerations.htm) — VRA sizing, VPG limits, and performance guidelines
- [HPE Zerto Software](https://www.hpe.com/us/en/zerto-software.html) — HPE product page with licensing and GreenLake integration
- [Zerto on Azure VMware Solution](https://learn.microsoft.com/en-us/azure/azure-vmware/deploy-zerto-disaster-recovery) — deployment guide for Zerto with AVS
- [Zerto Architecture Guide (PDF)](https://www.zerto.com/myzerto/wp-content/uploads/2021/03/Zerto-Platform-Architecture-Guide.pdf) — detailed architecture whitepaper

## See Also

- `general/disaster-recovery.md` — cloud-agnostic DR architecture patterns, RPO/RTO tiers, and DR testing
- `providers/hystax/migration.md` — Hystax Acura for any-to-any migration and DR (agent-based, covers KVM/OpenStack)
- `providers/nutanix/migration-tools.md` — Nutanix Move and Zerto usage for AHV migrations
- `providers/vmware/data-protection.md` — VMware SRM/Live Site Recovery and vSphere Replication
- `providers/aws/disaster-recovery.md` — AWS Elastic Disaster Recovery and cross-region DR patterns
- `providers/azure/disaster-recovery.md` — Azure Site Recovery and AVS DR patterns
- `patterns/disaster-recovery-implementations.md` — pilot light, warm standby, hot standby, and active-active patterns
- `patterns/hpe-hybrid-cloud.md` — HPE-anchored hybrid pattern positioning Zerto for cross-environment DR (HPE acquired Zerto and bundles it for hybrid use cases)
- `general/ransomware-resilience.md` — ransomware recovery patterns where Zerto journal-based recovery is a key capability
