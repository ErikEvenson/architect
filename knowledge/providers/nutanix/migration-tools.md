# Nutanix Migration Tools (Move, Veeam, Zerto, Manual V2V)

## Scope

Migration tooling for workload mobility to Nutanix AHV from VMware ESXi, Microsoft Hyper-V, AWS EC2, and Azure. Covers Nutanix Move (native), Veeam Backup & Replication (backup/restore migration), Zerto (replication-based migration), and manual V2V conversion. Includes appliance deployment, bandwidth planning, cutover methodology, validation, and rollback.

## Checklist

### Nutanix Move — Appliance and Planning

- [ ] [Critical] Is the Nutanix Move appliance deployed with minimum 2 vCPUs (2 cores each), 8 GB RAM, and adequate disk? Scale to 4+ vCPUs and 16 GB RAM for large-scale concurrent migrations (50+ VMs).
- [ ] [Critical] Is the Move appliance placed on a network segment with low-latency, high-bandwidth connectivity to both source hypervisor hosts and target AHV cluster CVMs?
- [ ] [Critical] Are firewall rules configured for Move — TCP 443 and TCP 902 to ESXi hosts, TCP/UDP 2049 and 111 to AHV CVMs, TCP 443 to vCenter, and TCP 9440 to Prism Central/Element?
- [ ] [Critical] Has a source environment inventory been completed identifying total VM count, aggregate data volume, per-VM disk sizes, and daily change rates before creating migration plans?
- [ ] [Recommended] Is the Move appliance deployed on the target Nutanix cluster (not the source) for best performance during data seeding?
- [ ] [Recommended] Has the Move appliance been updated to the latest version (6.1.x as of early 2026) before beginning migrations?

### Nutanix Move — Source Compatibility

- [ ] [Critical] Have all VMs been audited for unsupported configurations — physical RDMs, independent-mode disks, VMs with PCIe passthrough devices, and shared VMDK disks — which Move cannot migrate?
- [ ] [Critical] Are all source VMs using supported guest operating systems? Verify against the Move compatibility matrix for the deployed version (Windows Server 2012 R2+, Windows 10/11, RHEL 7+, Ubuntu 16.04+, SLES 12+, CentOS 7+, Oracle Linux 7+).
- [ ] [Critical] Have encrypted VMs (vSphere VM Encryption or BitLocker with vTPM) been identified? Move cannot snapshot encrypted VM disks — these require decryption before migration or alternative migration paths.
- [ ] [Recommended] Have UEFI/Secure Boot VMs been identified? Move supports UEFI migration (ESXi-to-AHV) but Secure Boot VMs require VirtIO 1.1.7+ installed before cutover and must be validated post-migration.
- [ ] [Recommended] Are VMs with disks >10 TB identified and scheduled in separate migration waves with extended seeding windows?
- [ ] [Optional] Have VMs with IDE virtual disks been identified? These cannot be converted to Secure Boot on AHV and must remain BIOS-mode.

### Nutanix Move — Seeding and Cutover

- [ ] [Critical] Has bandwidth been estimated for the seeding phase using the formula: `Total Data (TB) / Available Bandwidth (Gbps) x overhead factor (1.2) = Seeding Duration`?
- [ ] [Critical] Is the cutover window sized based on the final delta sync — do not initiate cutover when replication lag exceeds 30 seconds, as this extends the outage window beyond acceptable RTO?
- [ ] [Critical] Is the migration plan organized into waves (batches of 10-20 VMs), with application dependencies grouped so that dependent VMs cut over together?
- [ ] [Recommended] Has bandwidth throttling been configured in Move to prevent seeding from saturating production network links during business hours?
- [ ] [Recommended] Are migration waves scheduled to allow seeding to run for 2-7 days before cutover, pre-staging data to minimize final delta size?
- [ ] [Recommended] Is CVM CPU utilization monitored during seeding — sustained >70-75% CPU on CVMs indicates storage fabric contention that may impact production workloads on the target cluster?
- [ ] [Optional] Are test cutovers performed on non-production VMs first to validate the full workflow (driver injection, network mapping, application startup)?

### Nutanix Move — Guest OS Preparation and Driver Injection

- [ ] [Critical] Will Move automatically uninstall VMware Tools and install Nutanix VirtIO drivers during migration? Confirm this is enabled in the migration plan settings.
- [ ] [Critical] For Windows VMs, are VirtIO drivers confirmed compatible with the guest OS version? Move injects drivers automatically, but verify the injected driver version is current.
- [ ] [Critical] For Linux VMs, confirm the kernel includes VirtIO block (virtio_blk) and network (virtio_net) drivers — all supported Linux distributions ship these in-kernel, but custom kernels may not.
- [ ] [Recommended] Is Nutanix Guest Tools (NGT) installation planned post-migration for VSS-consistent snapshots and self-service file restore capabilities?
- [ ] [Recommended] Are static IP configurations, DNS entries, and host-based firewall rules documented before migration so they can be validated post-cutover?
- [ ] [Optional] For VMs with third-party agents (monitoring, backup, antivirus), is a post-migration checklist prepared to verify agent connectivity after IP/network changes?

### Cross-Hypervisor Migration — ESXi to AHV

- [ ] [Critical] Is vCenter connectivity configured in Move with a service account that has at least read-only privileges on VMs, datastores, and hosts, plus permission to create/delete snapshots?
- [ ] [Critical] Are VM hardware versions compatible? Move supports VM hardware version 4 through 21 (vSphere 8.0 U3).
- [ ] [Recommended] Are VMware Distributed vSwitches and port group names mapped to AHV virtual networks in the Move migration plan?
- [ ] [Recommended] Are VM affinity/anti-affinity rules documented so they can be recreated in AHV post-migration?

### Cross-Hypervisor Migration — Hyper-V to AHV

- [ ] [Critical] Is WinRM (TCP 5985/5986) enabled on Hyper-V hosts with appropriate credentials configured in Move?
- [ ] [Critical] Are Generation 2 Hyper-V VMs (UEFI) identified? Move supports these but they require post-migration boot verification.
- [ ] [Recommended] Are Hyper-V Integration Services removed post-migration and replaced with Nutanix VirtIO drivers?

### Cloud Migration — AWS EC2 to AHV

- [ ] [Critical] Is an IAM user or role configured with EC2 read permissions plus snapshot/AMI creation permissions for Move to access source instances?
- [ ] [Critical] Has network connectivity been established between the on-premises Move appliance and AWS VPC (via VPN or Direct Connect) with sufficient bandwidth for data transfer?
- [ ] [Recommended] Are EBS volume types and sizes documented? GP3/IO2 volumes with provisioned IOPS will not retain performance characteristics after migration to AHV.
- [ ] [Recommended] Has data transfer cost from AWS been estimated? Egress charges apply to all data transferred out of AWS during seeding.

### Alternative Migration Paths

- [ ] [Recommended] For VMs that Move cannot handle (physical RDMs, encrypted disks, PCIe passthrough), has Veeam Backup & Replication been evaluated as a backup-then-restore migration path?
- [ ] [Recommended] For environments requiring near-zero RPO during migration, has Zerto been evaluated for continuous replication with journal-based recovery?
- [ ] [Optional] For small numbers of VMs (<10) or one-off migrations, has manual V2V conversion (export OVA, convert with qemu-img, import to AHV) been considered to avoid deploying additional tooling?

### Migration Validation and Testing

- [ ] [Critical] Is a post-migration validation checklist defined covering: VM boot, OS login, network connectivity, application health, storage I/O performance, and DNS resolution?
- [ ] [Critical] Are application-level health checks (database connectivity, web response codes, service cluster membership) verified within 30 minutes of cutover?
- [ ] [Critical] Is storage I/O latency monitored via Prism for 24-48 hours post-migration to confirm performance meets baseline (Stargate latency <5ms for SSD-backed workloads)?
- [ ] [Recommended] Are VMware Tools remnants cleaned up post-migration? Leftover VMware drivers can cause performance issues or BSODs on Windows VMs.
- [ ] [Recommended] Is a parallel-run period defined (1-5 business days) before decommissioning source VMs?
- [ ] [Optional] Are synthetic benchmarks (diskspd for Windows, fio for Linux) run post-migration to compare storage performance against pre-migration baselines?

### Rollback Procedures

- [ ] [Critical] Are source VMs retained (powered off, not deleted) for a defined rollback window (minimum 5 business days) after successful cutover?
- [ ] [Critical] Is a rollback procedure documented covering: power off AHV VM, update DNS/load balancer to point back to source, power on source VM, verify application health?
- [ ] [Recommended] For database VMs, is a data reconciliation procedure defined if rollback is needed after the application has been processing transactions on the AHV target?
- [ ] [Recommended] Are rollback communication and escalation procedures defined — who authorizes rollback, notification chain, and maximum decision time?

## Why This Matters

Migration is the highest-risk phase of any hypervisor transition. Nutanix Move simplifies V2V conversion but its limitations — no support for physical RDMs, independent disks, encrypted VMs, or PCIe passthrough devices — mean that a meaningful percentage of enterprise VMs (typically 5-15%) require alternative migration paths. Failing to inventory these VMs before migration planning leads to stalled waves and blown cutover windows. Bandwidth underestimation is the most common planning failure: a 50 TB migration over a 1 Gbps link takes approximately 5 days of continuous seeding at wire speed, but real-world throughput is typically 60-70% of theoretical maximum due to protocol overhead and production traffic sharing the link. The seeding-then-cutover model means data is continuously replicated while the source VM stays live, so cutover downtime is limited to the final delta sync (typically minutes), but only if seeding has been running long enough for the delta to converge. Driver injection failures — particularly VMware Tools remnants conflicting with VirtIO — cause post-migration BSODs that are difficult to troubleshoot under cutover time pressure. Retaining source VMs for rollback is non-negotiable: deleting source VMs immediately after cutover eliminates the safety net and converts a recoverable migration issue into a disaster recovery event.

## Common Decisions (ADR Triggers)

- **Primary migration tool** — Nutanix Move (free, native, purpose-built) vs Veeam (backup/restore, useful if already licensed) vs Zerto (continuous replication, near-zero RPO but additional licensing cost) vs manual V2V (no tooling needed, labor-intensive)
- **Migration wave sizing** — Small waves (5-10 VMs, lower risk, longer project timeline) vs large waves (20-50 VMs, faster completion, higher blast radius if issues arise)
- **Seeding network strategy** — Share production network with bandwidth throttling vs dedicated migration VLAN with full bandwidth allocation
- **Cutover timing** — Business hours with application team standby vs maintenance window (nights/weekends) with reduced support availability
- **Source VM retention period** — Short (3-5 days, saves storage) vs long (14-30 days, maximum safety) vs storage-constrained (keep only critical VMs, delete commodity)
- **Driver injection method** — Automatic via Move (standard) vs pre-install VirtIO before migration (higher confidence, requires source VM downtime) vs post-migration manual install (risky, VM may not boot)
- **Rollback granularity** — Per-VM rollback (surgical, complex) vs per-wave rollback (all-or-nothing, simpler coordination) vs per-application rollback (business-aligned, requires dependency mapping)
- **Alternative path for unsupported VMs** — Veeam backup/restore (requires Veeam license) vs manual V2V conversion (labor-intensive) vs application-level migration (rebuild on AHV, re-import data)

## Migration Tool Comparison Matrix

| Capability | Nutanix Move | Veeam Backup & Replication | Zerto | Manual V2V |
|---|---|---|---|---|
| **Cost** | Free with Nutanix | Requires Veeam license | Requires Zerto license | No tooling cost (labor only) |
| **ESXi to AHV** | Native support | Backup then restore to AHV | Continuous replication | Export OVA, convert, import |
| **Hyper-V to AHV** | Native support | Backup then restore to AHV | Continuous replication | Export VHD, convert, import |
| **AWS EC2 to AHV** | Native support | Not directly supported | Not supported | Snapshot, export, convert |
| **Azure to AHV** | Native support | Not directly supported | Not supported | Export VHD, convert, import |
| **Physical RDM VMs** | Not supported | Supported (agent-based backup) | Not supported | Convert RDM to VMDK first |
| **Encrypted VMs** | Not supported | Supported (with key access) | Not supported | Decrypt, then export |
| **Near-zero RPO** | Minutes (delta sync) | Hours (backup frequency) | Seconds (journal-based) | N/A (offline conversion) |
| **Concurrent VMs** | ~20 per appliance (resource-dependent) | Limited by repository I/O | Limited by replication bandwidth | 1 at a time (manual) |
| **Automatic driver swap** | Yes (VMware Tools removal, VirtIO install) | No (manual post-restore) | No (manual post-failover) | No (manual) |
| **Cutover model** | Seeding + final delta sync | Full restore from backup | Failover from journal | Offline conversion |
| **Typical downtime** | 5-30 minutes per VM | 30-120 minutes per VM | 1-5 minutes per VM | 1-4 hours per VM |
| **Complexity** | Low | Medium | High | High |
| **Best for** | Bulk migration, standard VMs | VMs Move cannot handle, existing Veeam customers | Mission-critical apps requiring minimal downtime | Small-scale, one-off conversions |

## Bandwidth and Duration Estimation

### Seeding Phase

```
Seeding Duration (hours) = Total VM Data (GB) / (Link Speed (Mbps) x 0.65 efficiency / 8) / 3600

Examples at 65% link utilization:
  1 Gbps link:  ~54 hours per 10 TB  (~2.3 days)
  10 Gbps link: ~5.4 hours per 10 TB (~0.2 days)

Concurrent migration factor:
  20 VMs seeding simultaneously share the available bandwidth
  Per-VM throughput = Total throughput / concurrent VMs
```

### Cutover Window

```
Cutover Duration per VM = (Delta Data since last sync / Replication Throughput)
                        + VM shutdown time (1-2 min)
                        + Final sync time
                        + VM boot on AHV (1-3 min)
                        + Validation time (2-5 min)

Best case:  5 minutes (small delta, fast storage)
Typical:    10-20 minutes (moderate change rate)
Worst case: 30-60 minutes (high change rate, slow convergence)

Rule: Do not initiate cutover if replication lag > 30 seconds
```

### Change Rate Impact

| Daily Change Rate | 10 TB VM Seeding (1 Gbps) | Cutover Delta (4h window) |
|---|---|---|
| 1% (100 GB/day) | ~2.5 days | ~5 GB |
| 5% (500 GB/day) | ~3 days (re-sync overhead) | ~25 GB |
| 10% (1 TB/day) | ~4+ days (convergence risk) | ~50 GB |

High change rate VMs (databases with heavy write I/O) should be scheduled in the final migration wave with the shortest possible gap between last sync and cutover.

## Move Appliance Sizing Guide

| Migration Scale | vCPUs | RAM | Disk | Concurrent VMs |
|---|---|---|---|---|
| Small (< 50 VMs total) | 4 cores | 8 GB | 100 GB | 10 |
| Medium (50-200 VMs total) | 8 cores | 16 GB | 200 GB | 20 |
| Large (200+ VMs total) | 8-12 cores | 16-32 GB | 200 GB | 20 (deploy multiple appliances) |

For large-scale migrations (500+ VMs), deploy multiple Move appliances with separate migration plans to parallelize seeding and avoid single-appliance bottlenecks.

## Port Requirements Summary

| Source | Destination | Port | Protocol | Purpose |
|---|---|---|---|---|
| Move appliance | vCenter | TCP 443 | HTTPS | VM inventory, snapshot management |
| Move appliance | ESXi hosts | TCP 443 | HTTPS | NFC data transfer |
| Move appliance | ESXi hosts | TCP 902 | VMware NFC | Disk data streaming |
| Move appliance | Hyper-V hosts | TCP 5985/5986 | WinRM | VM management |
| Move appliance | AHV CVMs | TCP 9440 | HTTPS | Prism API |
| Move appliance | AHV CVMs | TCP/UDP 2049 | NFS | Disk data transfer |
| Move appliance | AHV CVMs | TCP/UDP 111 | Portmapper | NFS service discovery |
| Move appliance | AWS API | TCP 443 | HTTPS | EC2/EBS API calls |
| Browser | Move appliance | TCP 8443 | HTTPS | Move web console |

## Reference Links

- [Nutanix Move Documentation](https://portal.nutanix.com/page/documents/details?targetId=Nutanix-Move-v5_0:Nutanix-Move-v5_0)
- [Nutanix VirtIO Drivers](https://portal.nutanix.com/page/downloads?product=virtio)
- [Nutanix Compatibility Matrix](https://portal.nutanix.com/page/documents/compatibility-interoperability-matrix/software)

## See Also

- `general/workload-migration.md` -- general workload migration patterns
- `providers/nutanix/in-place-conversion.md` -- ESXi-to-AHV cluster re-imaging
- `providers/nutanix/compute.md` -- target AHV compute configuration
- `providers/vmware/licensing.md` -- VMware licensing driving migration decisions
