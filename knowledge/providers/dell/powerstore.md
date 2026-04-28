# Dell PowerStore

## Scope

Dell PowerStore unified block and file storage arrays: model selection (PowerStore T-series all-flash, PowerStore X-series with AppsON), storage provisioning (volumes, vVols, file systems), data services (snapshots, replication, thin provisioning, deduplication, compression), NVMe and NVMe-oF connectivity, VMware integration, cluster scaling, and performance optimization for enterprise workloads.

## Checklist

- [ ] [Critical] Is the correct PowerStore model selected for the workload? (T-series for pure external storage, X-series for AppsON capability to run VMs directly on the appliance -- X-series uses embedded VMware ESXi)
- [ ] [Critical] Is the storage protocol selected and configured correctly? (FC for legacy SAN environments, iSCSI for IP-based connectivity, NVMe-oF/TCP or NVMe-oF/FC for lowest latency workloads -- NVMe-oF requires end-to-end NVMe support)
- [ ] [Critical] Are storage volumes sized with appropriate service level policies (performance vs capacity tier), and is thin provisioning enabled by default to avoid overallocation?
- [ ] [Critical] Is data protection configured with snapshot policies for local recovery and replication (synchronous metro for RPO=0, asynchronous for DR) to a secondary PowerStore or supported target?
- [ ] [Critical] Is the PowerStore cluster configured for high availability? (dual-controller active/active within an appliance, multi-appliance clusters for scale-out up to 4 appliances)
- [ ] [Critical] Are host connectivity best practices followed? (multipathing configured with Round Robin or Dell-recommended ALUA policy, correct HBA queue depths, jumbo frames for iSCSI)
- [ ] [Recommended] Is PowerStore Manager used for centralized management, and is it integrated with VMware vCenter via VASA provider for vVols-based provisioning?
- [ ] [Recommended] Are data reduction features (inline deduplication and compression) enabled and monitored? (always-on by default, but verify data reduction ratios against vendor estimates for capacity planning)
- [ ] [Recommended] Is the PowerStore network configured with dedicated storage VLANs and proper MTU settings? (9000 MTU for iSCSI/NVMe-oF/TCP, separate management network from data network)
- [ ] [Recommended] Is file integration configured correctly if using unified NAS? (NFS and SMB shares, AD/LDAP integration for SMB, export rules for NFS, file-level snapshots and replication)
- [ ] [Recommended] Is CloudIQ connected for proactive health monitoring, predictive analytics, capacity forecasting, and performance trending across the PowerStore fleet?
- [ ] [Recommended] Are performance policies assigned to volumes matching the workload? (high for databases/OLTP, medium for general purpose, low for archive/backup targets)
- [ ] [Recommended] Is the PowerStore firmware update process planned with non-disruptive upgrades (NDU) tested and scheduled during maintenance windows?
- [ ] [Optional] Is AppsON (X-series only) being used to run VMware VMs directly on the PowerStore appliance for workloads that benefit from data locality (e.g., database, analytics)?
- [ ] [Optional] Is PowerStore import functionality used to non-disruptively migrate data from legacy Dell EMC arrays (VNX, Unity, SC-series, PS-series)?
- [ ] [Optional] Is Ansible or Terraform automation configured for PowerStore provisioning using the Dell PowerStore Ansible Collection or Terraform provider?
- [ ] [Optional] Is metro replication configured for stretched storage across two sites with automatic failover for mission-critical workloads?

## Why This Matters

PowerStore is Dell's modern midrange storage platform, replacing VNX, Unity, and SC-series arrays. Its NVMe-native architecture delivers significantly better latency and IOPS than legacy arrays, but realizing these gains requires end-to-end NVMe configuration. The T-series vs X-series decision is fundamental -- X-series includes an embedded VMware hypervisor for AppsON, which adds cost and complexity but enables data-local compute. Incorrect multipathing configuration is the most common cause of storage performance issues; default ALUA settings on ESXi are wrong for PowerStore active/active and must be changed. Data reduction ratios vary dramatically by workload type -- assuming 3:1 for databases when actual ratios are 1.5:1 leads to premature capacity exhaustion.

## Common Decisions (ADR Triggers)

- **Model selection** -- PowerStore T-series (external storage only) vs X-series (storage + AppsON compute) based on workload locality requirements
- **Storage protocol** -- FC (mature, dedicated fabric) vs iSCSI (converged network, lower cost) vs NVMe-oF (lowest latency, newer ecosystem) based on existing infrastructure and performance needs
- **Provisioning model** -- Traditional LUNs/volumes vs VMware vVols (per-VM granularity, SPBM-driven) vs NFS datastores for file-based storage
- **Data protection strategy** -- Local snapshots (RPO minutes) vs async replication (RPO 5-60 min) vs metro sync replication (RPO=0) vs third-party backup (Veeam, Commvault, NDMP)
- **Cluster scaling** -- Single appliance (up to 96 NVMe drives) vs multi-appliance cluster (up to 4 appliances, federated management) vs federation across sites
- **Migration approach** -- PowerStore native import (non-disruptive from legacy EMC) vs storage vMotion vs host-based replication for migrating from non-Dell arrays
- **Encryption** -- Data at rest encryption (DAR) with internal key management vs external KMIP server (Thales, Vormetric, Gemalto) for compliance

## Reference Links

- [Dell PowerStore Documentation](https://www.dell.com/support/home/en-us/product-support/product/powerstore/docs) -- official product documentation and guides
- [PowerStore Best Practices Guide](https://infohub.delltechnologies.com/en-us/t/powerstore/) -- Dell InfoHub with best practices and white papers
- [PowerStore Host Configuration Guide](https://www.dell.com/support/kbdoc/en-us/000199067/dell-powerstore-host-configuration-guide) -- multipathing and host connectivity settings for ESXi, Linux, and Windows
- [PowerStore Networking Guide](https://infohub.delltechnologies.com/en-us/t/powerstore/) -- network configuration best practices for iSCSI and NVMe-oF
- [Dell PowerStore Ansible Collection](https://github.com/dell/ansible-powerstore) -- infrastructure-as-code automation for PowerStore provisioning
- [Dell CloudIQ](https://www.dell.com/en-us/dt/storage/cloudiq.htm) -- proactive monitoring and analytics for Dell storage

## See Also

- `general/storage.md` -- general storage architecture patterns
- `general/disaster-recovery.md` -- DR strategy and RPO/RTO planning
- `providers/dell/powerscale.md` -- Dell PowerScale for scale-out NAS workloads
- `providers/dell/vxrail.md` -- Dell VxRail HCI with PowerStore external storage integration
- `providers/vmware/storage.md` -- VMware storage integration (vVols, VMFS, NFS)
- `patterns/dell-hybrid-cloud.md` -- Dell-anchored hybrid cloud pattern (PowerProtect / Cyber Recovery, cross-environment data mobility)
