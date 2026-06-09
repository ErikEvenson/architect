# Veeam Backup and Replication

## Scope

This file covers **Veeam Backup & Replication architecture and design** including backup server sizing, proxy and repository deployment, supported platforms (VMware, Hyper-V, Nutanix AHV, physical servers, cloud workloads), backup job configuration, SureBackup automated verification, Veeam ONE monitoring, licensing models (per-workload VUL), Scale-Out Backup Repository (SOBR) with capacity and archive tiers, immutable backup strategies, Veeam for AHV integration, and V2V migration scenarios using Veeam. It does not cover general backup strategy or DR site design; for those, see `general/enterprise-backup.md` and `general/disaster-recovery.md`.

## Checklist

- [ ] **[Critical]** Size the Veeam backup server (CPU, RAM, SQL/PostgreSQL database) based on the number of concurrent jobs, protected VMs, and retention points
- [ ] **[Critical]** Deploy dedicated backup proxies close to source datastores — at least one proxy per transport mode (Virtual Appliance for VMware, Off-host for Hyper-V, AHV API for Nutanix)
- [ ] **[Critical]** Configure immutable backup repositories using hardened Linux repositories or S3 Object Lock to protect against ransomware
- [ ] **[Critical]** Enable SureBackup verification jobs to automatically validate backup recoverability on a defined schedule
- [ ] **[Critical]** Design SOBR with performance tier (fast local storage) and capacity tier (S3-compatible or Azure Blob) to balance cost and restore speed
- [ ] **[Recommended]** Separate Veeam management traffic, backup data traffic, and production traffic onto distinct network segments
- [ ] **[Recommended]** Deploy Veeam ONE for centralized monitoring, capacity planning, and SLA compliance reporting across all backup infrastructure
- [ ] **[Recommended]** Configure per-job encryption with AES-256 and manage encryption passwords in a secure vault — not stored solely in the Veeam configuration database
- [ ] **[Recommended]** Plan VUL (Veeam Universal License) allocation based on current workload count plus projected growth over the license term
- [ ] **[Recommended]** For Nutanix AHV environments, deploy Veeam Backup for AHV using the AHV API proxy and validate snapshot-based backup compatibility with storage containers
- [ ] **[Optional]** Configure archive tier (S3 Glacier, Azure Archive) within SOBR for long-term retention beyond 90 days to reduce capacity tier costs
- [ ] **[Optional]** Use Veeam for V2V migration by restoring backups to a different hypervisor target — validate NIC, disk controller, and boot compatibility post-migration
- [ ] **[Optional]** Implement Veeam CDP (Continuous Data Protection) for Tier-1 workloads requiring RPOs under 15 minutes
- [ ] **[Optional]** Is Veeam AI Assistant evaluated for backup operations — provides AI-powered troubleshooting, configuration guidance, and log analysis to accelerate backup issue resolution?

## Why This Matters

Veeam is one of the most widely deployed backup products in virtualized and hybrid cloud environments. Its architecture — backup server, proxies, and repositories — must be properly sized and distributed to avoid bottlenecks that cause backup windows to overrun or restore operations to fail under pressure. A misconfigured Veeam environment (undersized proxies, single repository, no verification jobs) creates the illusion of protection while leaving the organization vulnerable during an actual recovery event.

Veeam's SOBR and immutability features are powerful ransomware defenses, but only when configured correctly. A hardened Linux repository with immutability disabled, or an S3 target without Object Lock, provides no protection against an attacker who compromises the backup server. SureBackup verification is the only way to confirm that backups are actually restorable — without it, organizations discover corruption during the worst possible moment.

## Common Decisions (ADR Triggers)

### ADR: Veeam Repository Architecture

**Context:** The environment requires backup storage that balances performance, cost, and ransomware resilience.

**Options:**

| Criterion | Hardened Linux Repo | Windows Repo + SOBR | Dedicated Appliance (e.g., ExaGrid) |
|---|---|---|---|
| Immutability | Native (XFS flags) | Requires S3 Object Lock on capacity tier | Vendor-specific retention lock |
| Performance | High (local NVMe/SSD) | Medium (depends on tier) | High (landing zone + dedup) |
| Cost | Low (commodity hardware) | Medium | High (appliance licensing) |
| Complexity | Medium (Linux hardening) | Medium (SOBR config) | Low (turnkey) |

### ADR: Backup Transport Mode

**Context:** Backup proxies must be configured with the appropriate transport mode for each hypervisor platform.

**Options:**

| Criterion | Virtual Appliance (VMware) | Network (NBD) | AHV API (Nutanix) | Direct SAN |
|---|---|---|---|---|
| Performance | High (HotAdd) | Medium (network-bound) | High (snapshot-based) | Highest (SAN fabric) |
| Infrastructure requirement | Proxy VM on each host/cluster | Any proxy with network access | AHV proxy appliance | SAN zoning to proxy |
| Complexity | Low | Low | Medium | High |

### ADR: VUL Licensing Strategy

**Context:** Veeam Universal License is portable across workload types but must be allocated against protected instances.

**Decision factors:** Current VM count, physical server count, cloud workload count, projected growth rate, license term length (1/3/5 year), and whether perpetual sockets are already owned.

## AI and GenAI Capabilities

**Veeam AI Assistant** — AI-powered assistant for backup operations. Provides troubleshooting guidance for backup job failures, configuration recommendations based on environment analysis, and log analysis to identify root causes. Available through the Veeam support portal and integrated into Veeam ONE monitoring. Supplements but does not replace Veeam's knowledge base and support channels.

## Day-2 Operations: Source-Object Lifecycle

The architecture decisions above (proxy/repository design, SOBR, immutability) determine *how* data is protected. Implementing backup-lifecycle synchronization (`patterns/backup-lifecycle-synchronization.md`) requires the Veeam-specific mechanics for removing a machine's protection and reclaiming its restore points. Veeam distinguishes three distinct removal operations that map directly onto the pattern's soft and hard action paths -- and conflating them is the common mistake.

- **Remove from job (soft path).** Removing a machine from its backup job stops new restore points while **leaving existing restore points on the repository to age out under the job's retention (and GFS) policy**. This is soft reclamation: protection stops, data recedes as retention lapses. The machine's existing backup chain remains restorable until it ages off.
- **Remove from backup vs Remove from configuration vs Delete from disk (the critical distinction).** In *Backups → Disk*, three operations differ: **Remove from configuration** drops the machine from the Veeam database but **leaves the backup files on the repository** (recoverable by re-import); **Remove from backup** removes the machine from the chain going forward; **Delete from disk** **physically deletes the backup files** and is the hard-reclamation action -- irreversible. Lifecycle automation must select deliberately: soft path = stop the job + let retention age out; hard path (erasure/immediate cost) = Delete from disk, gated by the pattern's legal-hold and approval checks.
- **Retention aging (soft enforcement).** Job retention (restore points) plus GFS (weekly/monthly/yearly) governs automatic pruning. After a machine is removed from its job, its chain reclaims per retention. Confirm retention/GFS equals the intended reclamation deadline -- a multi-year GFS yearly means a removed machine's data persists for years.
- **Immutability is the legal-hold gate.** A **hardened Linux repository** (XFS immutable flag) or **S3 Object Lock** capacity tier blocks deletion until the immutability period expires -- by design. Delete-from-disk against an immutable restore point will not free it early; the reclamation loop must treat immutable-locked data as non-reclaimable until its lock lapses, which is exactly the compliance-lock gate the pattern requires.
- **Dynamic job scope (governs re-protection).** Jobs that target vSphere containers (folders, tags, resource pools) rather than explicit VMs will **auto-include a newly created -- or recreated -- VM** that lands in scope. A deleted-then-recreated VM matching a tag/folder is re-protected automatically. Key the reclamation loop on the VM's stable reference (instance UUID / MoRef), not the name, and be aware that some operations (restore to a new VM, certain migrations) change a VM's reference -- the loop must track the identifier Veeam actually uses so it does not mis-correlate.
- **Automation surface.** The Veeam PowerShell module and the Veeam REST API drive job membership, remove-from-backup, and delete-from-disk programmatically, so the reclamation loop integrates without UI steps. Scope its credentials so it can reclaim but cannot disable repository immutability.

## See Also

- `general/enterprise-backup.md` — Backup strategy, 3-2-1-1-0 rule, product comparison
- `general/disaster-recovery.md` — DR site design, failover orchestration
- `providers/nutanix/data-protection.md` — Nutanix-native backup and replication
- `patterns/backup-lifecycle-synchronization.md` — end-to-end source-deletion → backup-reclamation pattern these mechanics implement

## Reference Links

- [Veeam Help Center](https://helpcenter.veeam.com/docs/backup/vsphere/overview.html) -- Backup & Replication architecture, proxy/repository design, and job configuration
- [Veeam Best Practices](https://bp.veeam.com/) -- deployment sizing, SOBR configuration, and immutable backup design
- [Veeam Technical Documentation](https://helpcenter.veeam.com/) -- product documentation for all Veeam platform components
