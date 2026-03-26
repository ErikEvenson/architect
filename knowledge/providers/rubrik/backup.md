# Rubrik

## Scope

This file covers **Rubrik architecture and design** including CDM (Cloud Data Management) appliance architecture, SLA domain policy configuration, Live Mount for instant recovery, CloudOut for archival to public cloud, CloudOn for cloud-based recovery, Rubrik Security Cloud for ransomware detection and investigation, API-first automation, Polaris SaaS management platform, and ransomware recovery workflows. It does not cover general backup strategy; for that, see `general/enterprise-backup.md`.

## Checklist

- [ ] **[Critical]** Size the Rubrik cluster (number of nodes, storage capacity per node) based on total protected data, daily change rate, retention requirements, and anticipated ingest throughput
- [ ] **[Critical]** Define SLA domains aligned to application tiers — each SLA domain specifies snapshot frequency, local retention, archival target, and replication target
- [ ] **[Critical]** Configure at least one archival (CloudOut) location with immutable storage (S3 Object Lock, Azure Immutable Blob) to protect against ransomware
- [ ] **[Critical]** Validate network connectivity between Rubrik nodes and all protected hosts — Rubrik uses its own distributed file system and requires predictable low-latency links within the cluster
- [ ] **[Recommended]** Deploy Rubrik in a minimum 4-node cluster for production workloads to maintain data durability and availability during node failures
- [ ] **[Recommended]** Use Live Mount for rapid recovery validation — mount snapshots instantly as running VMs without full restore to verify backup integrity
- [ ] **[Recommended]** Connect the Rubrik cluster to Polaris SaaS for centralized multi-cluster management, compliance reporting, and Radar ransomware anomaly detection
- [ ] **[Recommended]** Configure RBAC (role-based access control) on the Rubrik cluster to enforce least-privilege access — separate backup admin, restore operator, and compliance auditor roles
- [ ] **[Recommended]** Plan cluster expansion capacity — Rubrik scales by adding nodes, so ensure rack space, power, and network ports are available for growth
- [ ] **[Optional]** Use CloudOn to spin up workloads directly in AWS or Azure from archived snapshots for DR testing or cloud migration validation
- [ ] **[Optional]** Leverage the Rubrik REST API and SDK for automating SLA assignment, on-demand snapshots, and integration with CI/CD or orchestration platforms
- [ ] **[Optional]** Enable Rubrik Radar (anomaly detection) and Sonar (sensitive data discovery) for environments with strict compliance or security monitoring requirements
- [ ] **[Optional]** Evaluate Rubrik NAS protection for large-scale file share environments — requires NAS proxy deployment and fileset configuration

## Why This Matters

Rubrik's appliance-based architecture simplifies backup infrastructure by converging compute, storage, and backup software into a single cluster that scales horizontally. This eliminates the need to separately manage backup servers, proxies, media servers, and storage targets. However, simplicity at the operational layer does not remove the need for careful architectural planning — an undersized cluster, poorly defined SLA domains, or missing archival configuration will result in an environment that cannot meet RPO/RTO targets or withstand a ransomware attack.

Rubrik's API-first design makes it highly automatable, but this also means that misconfigured API access or overly broad RBAC permissions can expose the entire backup environment to compromise. The Security Cloud features (Radar anomaly detection, threat hunting, data classification) represent a meaningful advantage for ransomware resilience, but only when connected to Polaris and actively monitored. An unmonitored Rubrik cluster with alerting disabled provides the same false confidence as any other unchecked backup system.

## Common Decisions (ADR Triggers)

### ADR: Rubrik Cluster Sizing

**Context:** Rubrik clusters must be sized for both current workloads and anticipated growth, as node additions require cluster rebalancing.

**Options:**

| Criterion | 4-Node Cluster | 6-Node Cluster | 8+ Node Cluster |
|---|---|---|---|
| Protected data (typical) | Up to 50 TB front-end | Up to 100 TB front-end | 100+ TB front-end |
| Concurrent streams | Moderate | High | Very high |
| Node failure tolerance | 1 node | 1-2 nodes | 2 nodes |
| Use case | SMB / single site | Mid-enterprise | Large enterprise / multi-workload |

### ADR: Data Archival Strategy

**Context:** CloudOut sends aged snapshots to cloud object storage for long-term retention and off-site protection.

**Options:**

| Criterion | AWS S3 | Azure Blob | GCS | NFS Archive |
|---|---|---|---|---|
| Immutability | Object Lock | Immutable Blob | Retention Lock | Not native |
| CloudOn support | Yes | Yes | Limited | No |
| Egress cost | Per-GB | Per-GB | Per-GB | None |
| Air-gap potential | Yes (separate account) | Yes (separate subscription) | Yes (separate project) | Physical only |

### ADR: Polaris SaaS vs. Local-Only Management

**Context:** Polaris provides centralized management and advanced security features but requires outbound internet connectivity from the Rubrik cluster.

**Decision factors:** Number of clusters, compliance requirements for SaaS connectivity, need for Radar/Sonar features, multi-site visibility requirements, and organizational policy on cloud management planes.

## See Also

- `general/enterprise-backup.md` — Backup strategy, 3-2-1-1-0 rule, product comparison
- `general/ransomware-resilience.md` — Ransomware defense, immutable storage, recovery workflows

## Reference Links

- [Rubrik Documentation](https://docs.rubrik.com/) -- CDM architecture, SLA domains, Live Mount, CloudOut, and API reference
- [Rubrik Build (API Documentation)](https://docs.rubrik.com/en-us/saas/saas/api_getting_started.html) -- REST API for automation and integration
- [Rubrik Security Cloud](https://docs.rubrik.com/en-us/saas/saas/introduction_rsc.html) -- ransomware detection, investigation, and recovery workflows
