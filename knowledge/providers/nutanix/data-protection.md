# Nutanix Data Protection and Disaster Recovery

## Checklist

- [ ] Are protection domains (PDs) configured for legacy VM-centric snapshot and replication, or has the environment migrated to Prism Central-based protection policies using Leap for orchestrated DR?
- [ ] Are consistency groups used within protection domains to snapshot multiple related VMs simultaneously (e.g., app server + database), ensuring crash-consistent recovery points across dependent workloads?
- [ ] Are snapshot schedules configured with appropriate RPO -- hourly for general production, NearSync (1-minute RPO) for critical databases, synchronous replication (metro availability) for zero-RPO applications?
- [ ] Is Nutanix Leap configured with recovery plans that define VM boot order, network mappings (source-to-target VLAN mapping), IP re-addressing rules, and post-recovery scripts for automated failover?
- [ ] Is metro availability (synchronous replication) deployed only where network latency between sites is under 5ms RTT, with a witness VM at a third site to handle split-brain scenarios?
- [ ] Is NearSync replication configured for Tier-1 applications requiring 1-minute RPO, understanding that it requires AOS 5.17+ and consumes more network bandwidth and CVM resources than async replication?
- [ ] Are async replication schedules configured with bandwidth throttling to prevent DR replication from saturating the WAN link and impacting production traffic?
- [ ] Is third-party backup software (Veeam, HYCU, Commvault) integrated using Nutanix API v3 or Changed Block Tracking (CBT) for efficient incremental backups rather than full-image copies?
- [ ] Are backup targets configured on Nutanix Objects (S3-compatible, on-cluster or separate cluster) for cost-effective, air-gapped backup storage with WORM (Write Once Read Many) for ransomware protection?
- [ ] Are retention policies defined per workload tier -- 7-day local snapshots for fast restore, 30-day remote snapshots for DR, 90-day+ backup copies on Objects or external NAS for compliance?
- [ ] Is DR testing performed quarterly using Leap's test failover capability, which creates an isolated network bubble to validate recovery plans without impacting production?
- [ ] Are DR runbooks documented with clear RTO/RPO targets per application, failover procedures, DNS/IP switchover steps, and validated rollback procedures?
- [ ] Is the replication bandwidth between primary and DR sites sized for both steady-state change rate and initial seeding, with compression enabled on replication streams to reduce WAN consumption?
- [ ] Are Nutanix Guest Tools (NGT) installed on Windows VMs to enable application-consistent (VSS-quiesced) snapshots rather than crash-consistent snapshots?

## Why This Matters

Nutanix provides multiple data protection tiers, each with different RPO, complexity, and resource costs. Protection domains with async replication are the simplest approach but provide only crash-consistent snapshots at hourly or longer intervals. NearSync reduces RPO to 1 minute but requires lightweight snapshots and additional CVM resources. Metro availability provides synchronous replication with zero RPO but requires low-latency (<5ms) links and a witness VM -- without the witness, a network partition forces manual intervention to avoid split-brain. Leap adds orchestration on top of any replication method, automating the complex sequence of powering on VMs in order, remapping networks, and re-addressing IPs -- without Leap, DR failover is a manual, error-prone process under pressure. Backup is distinct from replication: replication protects against site failure, while backup with immutable targets (Objects with WORM) protects against ransomware and accidental deletion. Most organizations need both.

## Common Decisions (ADR Triggers)

- **Replication tier** -- Async (hourly+ RPO, lowest resource cost) vs NearSync (1-minute RPO, moderate overhead) vs metro availability (zero RPO, requires low-latency link and witness)
- **DR orchestration** -- Nutanix Leap (built-in, recovery plans, test failover) vs third-party DR orchestration (Zerto, VMware SRM with ESXi) vs manual runbooks
- **Backup solution** -- HYCU (Nutanix-native, API-integrated) vs Veeam (broad ecosystem, mature) vs Commvault (enterprise scale, complex) vs Rubrik (SaaS management)
- **Backup target** -- Nutanix Objects with WORM (on-cluster, immutable) vs external NAS (simple, familiar) vs cloud tier to AWS S3/Azure Blob (offsite, pay-per-use)
- **Snapshot consistency** -- Crash-consistent (default, no guest dependency) vs application-consistent (requires NGT/VSS on Windows, pre/post scripts on Linux)
- **Retention strategy** -- Short local + long remote (optimize local storage) vs long local + archive offsite (fastest restore) vs tiered with lifecycle policies
- **DR site architecture** -- Symmetric (identical cluster at DR site, bidirectional replication) vs asymmetric (smaller DR cluster, one-way replication, accept degraded performance during failover)
