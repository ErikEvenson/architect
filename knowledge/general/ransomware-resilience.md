# Ransomware Resilience Architecture

## Scope

This file covers **ransomware-specific resilience controls** including immutable backup architecture, backup isolation, detection patterns, recovery playbooks, network segmentation for lateral movement containment, identity hardening, and incident response sequencing. It focuses on the architectural decisions that determine whether an organization can survive and recover from a ransomware attack. For general backup product selection and sizing, see `general/enterprise-backup.md`. For broader security controls (IAM, encryption, compliance), see `general/security.md`. For DR site design and failover orchestration, see `general/disaster-recovery.md`.

## Checklist

- [ ] **[Critical]** Implement immutable backup storage using WORM-capable targets (S3 Object Lock in compliance mode, Azure immutable blob with time-based retention, hardened Linux repository, or air-gapped tape) — compliance mode prevents deletion even by root or account administrators, which is essential because attackers with admin credentials will attempt to delete backups before encrypting production
- [ ] **[Critical]** Follow the 3-2-1-1-0 backup rule: maintain 3 copies of data on 2 different media types with 1 copy offsite, 1 copy immutable or air-gapped, and 0 errors verified through automated restore testing — each element addresses a specific failure mode, and skipping any one creates a gap ransomware operators will exploit
- [ ] **[Critical]** Isolate backup infrastructure from the production domain: deploy backup servers on a separate Active Directory domain or with local-only accounts, use unique credentials not shared with any production system, and enforce MFA on all backup console access — ransomware operators specifically harvest backup admin credentials from compromised domain controllers
- [ ] **[Critical]** Establish network segmentation to limit lateral movement: enforce default-deny firewall rules between zones, restrict RDP/SMB/WinRM to management VLANs only, segment IT/OT networks, and micro-segment high-value assets — most ransomware spreads via SMB and RDP, so blocking these protocols between workstation subnets eliminates the primary propagation path
- [ ] **[Critical]** Design and document a prioritized recovery playbook: define recovery order by business criticality (identity infrastructure first, then DNS/DHCP, then Tier 1 applications), establish clean-room recovery procedures on isolated network segments, and set time-to-recover benchmarks per tier — without a documented recovery order, teams waste hours in the chaos of an incident debating what to restore first
- [ ] **[Critical]** Harden identity infrastructure against ransomware operators: enforce MFA on all administrative access, deploy privileged access workstations (PAWs) for domain admin tasks, implement a tiered admin model (Tier 0 for identity, Tier 1 for servers, Tier 2 for workstations), and eliminate standing admin privileges using just-in-time (JIT) access — compromised domain admin credentials are the single most common enabler of enterprise-wide ransomware deployment
- [ ] **[Recommended]** Deploy ransomware detection patterns: monitor for anomalous encryption activity (entropy analysis on file writes), mass file modification or renaming in short time windows, canary files placed in common directories that trigger alerts when accessed, and honeypot shares that appear as high-value targets — early detection during the encryption phase can limit blast radius if automated containment triggers are in place
- [ ] **[Recommended]** Implement backup account and network isolation across cloud boundaries: use separate AWS accounts, Azure subscriptions, or GCP projects for backup infrastructure, with no IAM trust relationships to production accounts, and enforce network isolation so backup vaults are unreachable from production workloads — a compromised production account must not have any path to delete or modify backup data
- [ ] **[Recommended]** Configure cloud-native immutable backup services: AWS Backup Vault Lock (compliance mode with minimum retention), Azure Backup with immutable vault and soft delete enabled, GCP Backup with retention policies and organization policy constraints — these managed services enforce immutability at the platform level, removing the risk of misconfigured self-managed storage
- [ ] **[Recommended]** Conduct ransomware-specific DR exercises: test recovery from a simulated encrypted state at least annually, measure actual time-to-recover against target benchmarks, validate that backups are free of dormant malware before restoring to production (scan restored images in an isolated recovery environment), and document gaps discovered during each exercise
- [ ] **[Recommended]** Deploy vendor-specific hardened backup repositories: Veeam Hardened Repository on dedicated Linux servers with immutability flags, Cohesity DataLock with WORM-protected snapshots and quorum-based deletion, Rubrik SLA Domains with retention lock that prevents policy modification without multi-person approval — purpose-built hardened repositories provide defense-in-depth beyond generic storage immutability
- [ ] **[Optional]** Implement automated containment responses: integrate detection signals with SOAR platforms to automatically isolate infected hosts (disable switch ports, quarantine VMs, revoke session tokens), disable compromised accounts, and trigger backup verification jobs — automation reduces the window between detection and containment from hours to seconds, but requires careful tuning to avoid false-positive disruptions
- [ ] **[Optional]** Deploy deception technology beyond basic canary files: create realistic decoy servers, credentials, and file shares that mimic high-value targets (domain controllers, file servers, backup servers), with full telemetry on any interaction — deception technology provides high-fidelity alerts with near-zero false positives because legitimate users and processes have no reason to access decoy resources

## Why This Matters

Ransomware is the most financially destructive cyber threat facing organizations today. The average ransomware payment exceeds $1.5 million, but the total cost of an incident — including downtime, recovery, legal fees, regulatory fines, and reputational damage — routinely reaches tens of millions of dollars. Attacks that destroy backup infrastructure alongside production systems cause the most severe outcomes because they eliminate the organization's ability to recover without paying the ransom.

Modern ransomware operators are not opportunistic script runners. They are organized groups that conduct weeks or months of reconnaissance inside a compromised network before deploying encryption. During this dwell time, they systematically identify and compromise backup infrastructure, exfiltrate sensitive data for double-extortion leverage, and position encryption payloads across every reachable system. The encryption event itself is the final step in a carefully planned operation.

This means that ransomware resilience is not a backup problem alone — it is an architecture problem that spans identity management, network segmentation, detection capabilities, backup isolation, and recovery procedures. An organization with excellent backups but flat network segmentation and shared admin credentials will still suffer a catastrophic breach because the attacker will reach and destroy the backups. Conversely, strong network segmentation with poor backup immutability leaves the organization unable to recover even if the attack is contained. Every layer must be addressed, and they must be designed together as an integrated defense.

The organizations that recover quickly from ransomware attacks share common traits: immutable backups that the attacker could not reach, documented recovery playbooks that were tested before the incident, isolated recovery environments ready to receive restored workloads, and identity infrastructure that could be rebuilt independently from compromised domain controllers.

## Common Decisions (ADR Triggers)

### ADR: Immutable Backup Storage Strategy

**Context:** The organization must protect backup data from deletion or encryption by ransomware operators who have obtained administrative credentials.

**Options:**

| Approach | Immutability Enforcement | Restore Speed | Cost | Operational Complexity |
|---|---|---|---|---|
| S3 Object Lock (compliance mode) | Platform-enforced, irrevocable for retention period | Fast (network-speed restore from object storage) | Moderate (storage + API + egress costs) | Low (managed service) |
| Hardened Linux repository (Veeam) | OS-level immutability flags, single-use SSH credentials | Fast (local or LAN restore) | Low (commodity Linux server) | Moderate (requires Linux hardening expertise) |
| Air-gapped tape vault | Physical isolation (tapes removed from network) | Slow (hours to retrieve and mount media) | Low (tape media is inexpensive) | High (tape rotation logistics, media management) |
| Purpose-built appliance (Data Domain Retention Lock, ExaGrid) | Hardware/firmware-enforced WORM | Fast (local appliance) | High (proprietary hardware) | Low (vendor-managed firmware) |
| Cloud-native vault (AWS Backup Vault Lock, Azure immutable vault) | Platform-enforced, policy-driven | Moderate (cloud restore speeds) | Moderate (managed service pricing) | Low (managed service) |

**Recommendation:** Layer at least two approaches — a fast-restore immutable copy (hardened repository or object lock) for operational recovery, plus an air-gapped or physically isolated copy for maximum resilience against sophisticated attackers who may find ways to compromise cloud management planes.

### ADR: Backup Infrastructure Isolation Model

**Context:** Backup infrastructure must be isolated from production to prevent a compromised production environment from reaching backup data.

**Options:**
- **Separate network segment with firewall rules:** Backup servers on a dedicated VLAN with strict firewall rules allowing only backup traffic (one-way from production to backup). Low cost, moderate isolation. Risk: firewall misconfiguration, rules accumulate exceptions over time.
- **Separate Active Directory domain (or no domain):** Backup servers joined to a dedicated forest with no trust relationships to production AD, or using local accounts only. Eliminates credential reuse attack path. Requires managing a separate identity infrastructure.
- **Separate cloud account/subscription:** Backup vaults in a dedicated AWS account, Azure subscription, or GCP project with no IAM cross-account roles to production. Strongest cloud isolation. Requires cross-account backup configuration and separate billing.
- **Physical air gap:** Backup copies written to media that is physically disconnected from any network after the backup window completes. Maximum isolation. Slowest restore, operationally intensive.

**Decision drivers:** Threat model sophistication (nation-state vs. commodity ransomware), acceptable recovery time (air-gapped copies are slower to restore), operational capacity to manage separate infrastructure, and compliance requirements for backup segregation.

### ADR: Ransomware Detection and Response Approach

**Context:** The organization needs to detect ransomware activity during the encryption phase (or earlier, during reconnaissance and lateral movement) and respond fast enough to limit damage.

**Options:**
- **Endpoint Detection and Response (EDR):** Agents on every endpoint detect encryption behavior, process injection, and known ransomware indicators. Fastest detection on endpoints. Requires agent deployment coverage and SOC monitoring. Products: CrowdStrike Falcon, Microsoft Defender for Endpoint, SentinelOne.
- **Network Detection and Response (NDR):** Passive network monitoring detects lateral movement, C2 communication, and anomalous SMB/RDP traffic. Detects agentless threats and IoT/OT devices. Does not see encrypted internal traffic without TLS inspection. Products: Darktrace, ExtraHop, Vectra.
- **Canary files and honeypots:** Decoy files and shares that generate alerts on any access. Zero false positives (legitimate users never access decoys). Only detects attackers who interact with decoys — not comprehensive. Low cost, simple to deploy.
- **Backup anomaly detection:** Backup software monitors for unusual changes in backup job size, deduplication ratio, or file entropy between backup runs. Detects encryption after it starts. Built into Veeam, Rubrik, Cohesity. Late detection — encryption is already in progress.
- **SIEM correlation with automated response:** Aggregates signals from EDR, NDR, backup anomaly, and canary alerts into a SIEM with SOAR playbooks for automated containment. Most comprehensive, highest operational complexity.

**Decision drivers:** Existing security tooling investments, SOC maturity and staffing, network encryption posture (TLS inspection feasibility), acceptable false-positive rate for automated containment, and budget for managed detection and response (MDR) services.

### ADR: Recovery Environment Architecture

**Context:** After a ransomware incident, restored workloads must be validated as clean before reconnecting to production networks. The organization needs a pre-staged environment for this purpose.

**Options:**
- **Dedicated isolated recovery environment (IRE):** Pre-staged compute (physical or virtual) on a quarantined network segment with no connectivity to production. Restored VMs boot in the IRE, undergo malware scanning and validation, then are migrated to rebuilt production infrastructure. Fastest recovery, highest infrastructure cost.
- **Cloud-based clean room:** Spin up a temporary isolated VPC/VNet in the cloud for recovery validation. Restored backups are mounted in the cloud environment, scanned, and either migrated to production cloud or exported back to on-premises. Elastic cost (pay only during recovery), requires cloud backup replication.
- **Parallel restore on production hardware after wipe:** Rebuild production infrastructure from scratch (reimage servers, rebuild AD), then restore backups directly. No dedicated recovery infrastructure cost. Slower — rebuild and restore are sequential. Risk: incomplete eradication if any compromised system is missed during rebuild.

**Decision drivers:** Target recovery time (IRE enables parallel restore while production is rebuilt), budget for standing recovery infrastructure, cloud readiness of backup data, and whether the organization has tested each approach in a DR exercise.

## Reference Links

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CISA Ransomware Guide](https://www.cisa.gov/stopransomware)
- [Veeam Hardened Repository](https://www.veeam.com/blog/hardened-repository.html)
- [Cohesity DataLock](https://www.cohesity.com/)
- [Rubrik](https://www.rubrik.com/)
- [AWS Backup Vault Lock](https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html)
- [Azure Immutable Blob Storage](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)
- [MITRE ATT&CK — Ransomware Techniques](https://attack.mitre.org/)
- [CrowdStrike Falcon](https://www.crowdstrike.com/)
- [SentinelOne](https://www.sentinelone.com/)

## See Also

- [enterprise-backup.md](enterprise-backup.md) — backup product selection, sizing, storage tiering, and the 3-2-1-1-0 rule in detail
- [disaster-recovery.md](disaster-recovery.md) — DR site design, failover orchestration, and RTO/RPO planning
- [security.md](security.md) — IAM strategy, secrets management, encryption, network security, and incident response planning
- [networking.md](networking.md) — network segmentation, firewall design, and VLAN architecture that supports lateral movement containment
- [observability.md](observability.md) — logging, monitoring, and alerting infrastructure for detection signal aggregation
