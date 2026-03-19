# Enterprise Backup Tools and Strategies

## Scope

This file covers **enterprise backup architecture and tool selection** including product comparison (Commvault, Veeam, Veritas, Dell), immutable storage, ransomware resilience, storage tiering, and backup sizing. It does not cover disaster recovery site design or failover orchestration; for those, see `general/disaster-recovery.md`.

## Checklist

- [ ] **[Critical]** Define RPO and RTO targets for each application tier before selecting backup architecture
- [ ] **[Critical]** Implement the 3-2-1-1-0 rule: 3 copies, 2 media types, 1 offsite, 1 immutable, 0 errors verified
- [ ] **[Critical]** Deploy immutable backup storage (object lock, hardened Linux repo, or air-gapped media) for ransomware protection
- [ ] **[Critical]** Establish automated backup verification — run test restores on a schedule, not just during DR exercises
- [ ] **[Critical]** Size backup storage accounting for source data, daily change rate, deduplication ratio, and full retention period
- [ ] **[Recommended]** Classify workloads into tiers (Tier 1/2/3) with distinct RPO, retention, and restore priority
- [ ] **[Recommended]** Separate backup network traffic onto a dedicated VLAN or physical NIC to avoid production impact
- [ ] **[Recommended]** Configure cloud tiering for long-term retention (S3 Glacier, Azure Cool/Archive, GCS Nearline) to reduce on-prem storage costs
- [ ] **[Recommended]** Enable deduplication at the target (appliance or software) and evaluate source-side dedup for WAN-limited sites
- [ ] **[Recommended]** Monitor backup job success rates, duration trends, and storage consumption with alerting on failures
- [ ] **[Recommended]** Document and test the full restore procedure for each application tier at least quarterly
- [ ] **[Optional]** Implement application-aware backup (Exchange, SQL, Oracle) with log truncation and granular recovery
- [ ] **[Optional]** Evaluate per-workload licensing (Veeam VUL) vs. capacity-based licensing (Commvault, Veritas) against projected growth
- [ ] **[Optional]** Deploy a secondary backup product for critical workloads to avoid single-vendor dependency

## Why This Matters

Backup infrastructure is the last line of defense against data loss from hardware failure, human error, and ransomware. A poorly designed backup environment creates a false sense of security — organizations discover gaps only during an actual recovery event, when it is too late to fix them. Choosing the right tool, architecture, and retention policy directly determines whether the business can recover within its tolerance for downtime (RTO) and data loss (RPO).

Modern ransomware specifically targets backup infrastructure: it encrypts backup catalogs, deletes shadow copies, and compromises backup admin credentials. An enterprise backup design must assume the production environment and its backup server can both be compromised, which is why immutable copies, air-gapped storage, and verified restores are non-negotiable.

The difference between a well-designed and poorly-designed backup strategy is often measured in days of downtime and millions of dollars in lost revenue during an incident.

## Common Decisions (ADR Triggers)

### ADR: Backup Product Selection

**Context:** The organization needs to protect VMware, physical, and cloud workloads with a single backup platform.

**Options:**

| Criterion | Commvault | Veeam | Veritas NetBackup | Dell Avamar/NetWorker |
|---|---|---|---|---|
| VMware Integration | VADP, IntelliSnap for array snapshots | VADP, CBT, instant VM recovery | VADP, CBT | VADP, Data Domain target |
| Deduplication | Target-side, block-level | Per-job inline, SOBR offload | MSDP (media server dedup pool) | Variable-length source-side |
| Cloud Tiering | S3, Azure Blob, GCS native | SOBR capacity tier (S3, Azure, GCS) | CloudCatalyst to S3/Azure | Cloud Tier to Dell cloud |
| Ransomware Protection | Air-gap support, anomaly detection | Immutable hardened Linux repo, SureBackup verification | Isolated Recovery Environment (IRE) | Data Domain Retention Lock |
| Licensing | Per-VM or capacity-based | Per-workload (VUL), per-socket (legacy) | Flex capacity (TB managed) | Per-TB or per-client |
| Complexity | High — full feature set requires planning | Moderate — fast deployment, intuitive UI | High — enterprise-scale, steep learning curve | High — tightly coupled to Dell/EMC ecosystem |
| Best Fit | Large enterprise, multi-platform, strict compliance | VMware-heavy mid-to-large, fast time-to-value | Very large enterprise, mainframe, legacy OS | Dell/EMC storage shops |

**Decision drivers:** Existing storage vendor relationship, number of workload types, team skill set, budget model preference (CapEx appliance vs. OpEx subscription), and whether the organization requires mainframe or legacy OS support.

### ADR: Immutable Backup Storage Approach

**Context:** The organization must protect backup data from ransomware encryption and insider deletion.

**Options:**
- **Hardened Linux repository (Veeam):** Dedicated Linux server with single-use SSH credentials; Veeam sets immutability flags at the filesystem level. Low cost, no special hardware. Requires Linux administration skills.
- **Object lock on S3-compatible storage:** AWS S3 Object Lock (compliance or governance mode), MinIO, or Wasabi with WORM. Cloud-native, no on-prem hardware. Ongoing egress and API costs for restores.
- **Purpose-built appliance (Data Domain Retention Lock, ExaGrid):** Hardware-enforced immutability. High reliability, vendor-supported. Highest cost, vendor lock-in.
- **Air-gapped tape:** Physically removed from network after backup completes. Strongest isolation. Slowest restore, requires tape library and media management.

**Recommendation:** Use hardened Linux repo or object lock for daily immutable copies (fast restore), supplemented by air-gapped tape or isolated vault for monthly/quarterly copies (maximum isolation).

### ADR: Backup Storage Tiering Strategy

**Context:** Retaining 7 years of backup data on primary storage is cost-prohibitive.

**Options:**
- **Performance tier only:** All backups on fast storage (SAN/NAS). Fastest restores, highest cost. Only viable for short retention.
- **Performance + capacity tier:** Recent backups (30-90 days) on fast storage, older data tiered to S3 Glacier, Azure Cool, or GCS Nearline. Balances cost and restore speed.
- **Performance + capacity + archive tier:** Add a third tier for compliance archives (7+ years) on S3 Glacier Deep Archive or tape. Lowest cost for long retention, slowest restore (hours to retrieve from deep archive).

**Decision drivers:** Retention requirements (regulatory vs. operational), total data volume, acceptable restore time for aged data, and cloud egress budget.

### ADR: Backup Network Architecture

**Context:** Backup traffic (multi-TB nightly) competes with production traffic on the same network.

**Options:**
- **Shared production network:** No additional infrastructure. Backup jobs cause congestion during business hours; schedule jobs overnight only.
- **Dedicated backup VLAN:** Logical separation on existing switches. Allows QoS and traffic shaping. Low cost, moderate isolation.
- **Dedicated physical backup network:** Separate NICs, switches, and cabling. Full bandwidth isolation. Higher infrastructure cost, best performance.

## Reference Architectures

### Architecture 1: Mid-Size VMware Environment (Veeam)

**Scenario:** 200 VMs, 50 TB source data, 5% daily change rate, 30-day on-prem retention, 1-year cloud retention.

```
+-----------------------+         +------------------------+
|   vCenter / ESXi      |         |  Veeam Backup &        |
|   200 VMs (50 TB)     |-------->|  Replication Server     |
|   VADP + CBT          |  LAN    |  (Windows, 8 vCPU,     |
+-----------------------+         |   32 GB RAM)            |
                                  +----------+-------------+
                                             |
                          +------------------+------------------+
                          |                                     |
              +-----------v-----------+          +--------------v-----------+
              |  Primary Repository   |          |  Hardened Linux Repo     |
              |  (Performance Tier)   |          |  (Immutable Copy)        |
              |  Windows/ReFS or      |          |  Ubuntu 22.04, XFS       |
              |  Linux/XFS            |          |  Single-use SSH creds    |
              |  30 TB usable         |          |  Immutability: 14 days   |
              |  (3:1 dedup ratio)    |          |  15 TB usable            |
              +-----------+-----------+          +--------------------------+
                          |
              +-----------v-----------+
              |  SOBR Capacity Tier   |
              |  AWS S3 (Standard-IA) |
              |  Retention: 1 year    |
              |  Offload after 30d    |
              +-----------------------+
```

**Sizing calculation:**
- Source: 50 TB, 5% daily change = 2.5 TB/day incremental
- Dedup ratio 3:1: ~17 TB for 1 full + 30 incrementals on performance tier
- Hardened repo: 14-day immutable window, ~12 TB after dedup
- SOBR capacity tier: offloaded restore points older than 30 days, retained 1 year

**Key design decisions:**
- SureBackup runs weekly against 10 critical VMs to verify recoverability
- Veeam ONE monitors job success, repository capacity, and RPO compliance
- Backup proxy deployed 1 per 4 ESXi hosts (hot-add transport mode)
- Backup window: full synthetic weekly (Sunday), incremental nightly

### Architecture 2: Large Enterprise Multi-Site (Commvault)

**Scenario:** 3 data centers, 2,000 VMs, 500 TB source data, regulatory retention 7 years, DR site for replicated copies.

```
  Data Center 1 (Primary)            Data Center 2 (Secondary)
+---------------------------+      +---------------------------+
|  CommServe (HA pair)      |      |  MediaAgent + Proxy       |
|  Command Center Web UI    |      |  800 VMs                  |
|  MediaAgent (2x)          |      |  Local dedup storage      |
|  1,200 VMs                |      |  100 TB usable            |
|  Dedup storage: 200 TB    |      +-------------+-------------+
+-------------+-------------+                    |
              |                                   |
              +-----------------------------------+
              |          WAN (deduplicated)
              |
+-------------v-------------+
|  DR Site (Data Center 3)  |
|  MediaAgent (replica)     |
|  Dedup storage: 150 TB    |
|  Air-gapped tape library  |
|  (monthly full copies)    |
+---------------------------+
              |
+-------------v-------------+
|  Cloud Tier (Archive)     |
|  AWS S3 Glacier Deep      |
|  Retention: 7 years       |
|  Compliance lock enabled  |
+---------------------------+
```

**RPO/Retention by tier:**

| Tier | Examples | RPO | On-Prem Retention | Cloud Archive Retention |
|---|---|---|---|---|
| Tier 1 — Mission Critical | ERP, core DB, email | 1 hour | 30 days | 7 years |
| Tier 2 — Business Important | File servers, departmental apps | 4 hours | 14 days | 3 years |
| Tier 3 — Non-Critical | Dev/test, training VMs | 24 hours | 7 days | 1 year |

**Key design decisions:**
- IntelliSnap leverages storage array snapshots for Tier 1 RPO (1-hour snap schedule)
- CommServe HA pair with SQL Always On for catalog resilience
- WAN-optimized replication between sites using source-side dedup
- Monthly tape copies rotated to off-site vault (Iron Mountain) for air-gap
- Command Center dashboards for SLA compliance reporting to management

### Architecture 3: Ransomware-Resilient Design

**Scenario:** Organization prioritizes ransomware recovery after a previous incident. Must guarantee clean recovery within 4 hours for Tier 1 workloads.

```
Production Network                    Isolated Backup Network
+------------------+                 +---------------------------+
|  Production VMs  |----firewall---->|  Backup Server            |
|  (compromised    |  one-way allow  |  (separate AD domain,     |
|   assumed)       |  backup traffic |   unique credentials,     |
+------------------+  only           |   MFA for console)        |
                                     +----------+----------------+
                                                |
                      +-------------------------+-------------------------+
                      |                         |                         |
          +-----------v-----------+ +-----------v-----------+ +-----------v-----------+
          |  Copy 1: Fast Repo   | |  Copy 2: Immutable    | |  Copy 3: Air-Gap      |
          |  NVMe/SSD NAS        | |  Object Lock (MinIO)  | |  Tape or isolated     |
          |  7-day retention     | |  S3-compatible         | |  network vault        |
          |  Fastest restore     | |  30-day lock period   | |  Monthly copies       |
          +-----------------------+ +-----------------------+ +-----------------------+
                      |
          +-----------v-----------+
          |  Isolated Recovery    |
          |  Environment (IRE)   |
          |  Clean network        |
          |  Pre-staged ESXi host |
          |  Restore & scan       |
          |  before production    |
          +-----------------------+
```

**Ransomware-specific controls:**
- Backup server on a separate Active Directory domain (or no domain — local accounts only)
- MFA required for all backup console access; no shared admin accounts
- Network micro-segmentation: production can send backup data to backup network, but backup network initiates no connections to production
- Immutable copies use S3 Object Lock in compliance mode (cannot be deleted even by root)
- Isolated Recovery Environment: dedicated ESXi host on a quarantined network for restoring and scanning VMs before reconnecting to production
- Weekly SureBackup / automated restore tests verify backup integrity (the "0 errors" in 3-2-1-1-0)
- Backup anomaly detection alerts on unusual backup size changes (potential encryption indicator)

### Backup Sizing Quick Reference

| Parameter | How to Estimate |
|---|---|
| Full backup size | Source data size / dedup ratio (typically 2:1 to 5:1 depending on data type) |
| Daily incremental size | Source data size x daily change rate (typically 2-10%) |
| Repository capacity needed | (1 full + (N incrementals x change rate)) x retention period / dedup ratio |
| Network throughput needed | Total backup data / backup window hours; add 20% overhead |
| Cloud tiering cost | Monthly storage cost + API request cost + egress cost for restores |

**Example:** 50 TB source, 5% daily change, 3:1 dedup, 30-day retention:
- Effective full: 50 / 3 = ~17 TB
- Daily incremental: (50 x 0.05) / 3 = ~0.83 TB
- 30-day repository: 17 + (30 x 0.83) = ~42 TB usable capacity needed
- Add 20% headroom: ~50 TB usable repository

## Reference Links

- [Veeam](https://www.veeam.com/)
- [Commvault](https://www.commvault.com/)
- [Rubrik](https://www.rubrik.com/)
- [HYCU](https://www.hycu.com/)
- [Cohesity](https://www.cohesity.com/)
- [Veritas NetBackup](https://www.veritas.com/protection/netbackup)

## See Also

- [disaster-recovery.md](disaster-recovery.md) -- DR site design, failover orchestration, and RTO/RPO planning
- [data.md](data.md) -- database design and data retention policies that drive backup requirements
- [security.md](security.md) -- security controls including ransomware protection and data encryption
- [ransomware-resilience.md](ransomware-resilience.md) -- ransomware-specific resilience architecture, backup isolation, and recovery playbooks
