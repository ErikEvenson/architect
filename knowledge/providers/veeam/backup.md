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

## See Also

- `general/enterprise-backup.md` — Backup strategy, 3-2-1-1-0 rule, product comparison
- `general/disaster-recovery.md` — DR site design, failover orchestration
- `providers/nutanix/data-protection.md` — Nutanix-native backup and replication
