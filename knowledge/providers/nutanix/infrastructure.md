# Nutanix Infrastructure

## Scope

Core Nutanix hyperconverged infrastructure: cluster sizing, hypervisor selection (AHV/ESXi/Hyper-V), storage containers, data protection, networking, and platform services integration. Covers initial deployment decisions, expansion planning, and lifecycle management.

## Checklist

- [ ] [Critical] Is the cluster sized correctly for the workload? (minimum 3 nodes for RF2, minimum 5 nodes recommended for RF3, consider compute-heavy vs storage-heavy node configurations)
- [ ] [Critical] Is AHV selected as the hypervisor unless there is a specific requirement for ESXi or Hyper-V, to simplify licensing and management?
- [ ] [Critical] Is Prism Central deployed for multi-cluster management, reporting, role-based access control, and advanced features (Flow, NCM Self-Service (formerly Calm), Leap)?
- [ ] [Critical] Is the storage container configured with appropriate redundancy factor (RF2 for non-critical, RF3 for production), compression, deduplication, and erasure coding policies?
- [ ] [Critical] Are data protection policies configured with protection domains or Leap for VM-level snapshots, replication, and disaster recovery to a secondary site?
- [ ] [Recommended] Is Flow Network Security (microsegmentation) configured to enforce application-tier isolation and zero-trust policies between VMs?
- [ ] [Recommended] Are categories (key-value tags) applied to VMs for use with Flow policies, NCM Self-Service (formerly Calm) blueprints, and Prism Central reporting?
- [ ] [Recommended] Is Nutanix Kubernetes Management (formerly NKE/Karbon) evaluated for Kubernetes workloads, with node OS image updates and etcd backup configured?
- [ ] [Recommended] Is Nutanix Objects (S3-compatible object storage) deployed for backup targets, log aggregation, and unstructured data with WORM policies for compliance?
- [ ] [Recommended] Is Nutanix Files deployed for SMB/NFS file shares with File Analytics enabled for audit trails and ransomware detection?
- [ ] [Recommended] Is cluster expansion planned with mixed-node-size awareness, ensuring the CVM (Controller VM) memory and CPU reservations are adequate?
- [ ] [Recommended] Are lifecycle management (LCM) updates tested in a staging cluster before production, with one-click firmware and software upgrades?
- [ ] [Optional] Is network segmentation configured using VLANs or Nutanix AHV virtual switches to separate management, VM, storage (iSCSI), and backup traffic?
- [ ] [Recommended] Is Prism Central configured with Active Directory or SAML integration for centralized authentication and role-based access?

## Why This Matters

Nutanix hyperconverged infrastructure collapses compute, storage, and networking into a single platform, but this simplicity masks important sizing and configuration decisions. Undersized clusters cause storage bottlenecks when nodes fail and data rebalances. RF2 tolerates only one node failure; RF3 tolerates two but uses 50% more storage. Flow microsegmentation is the only built-in way to enforce network policies without external firewalls. Prism Central is essential for any multi-cluster or enterprise deployment.

## Common Decisions (ADR Triggers)

- **Hypervisor selection** -- AHV (included, no license cost) vs ESXi (VMware ecosystem) vs Hyper-V (Windows ecosystem)
- **Redundancy factor** -- RF2 (can lose 1 node/drive) vs RF3 (can lose 2), storage overhead vs resilience
- **Storage optimization** -- inline compression + dedup (always-on) vs post-process, erasure coding for cold data
- **DR strategy** -- Nutanix Leap (orchestrated failover) vs third-party (Zerto, Veeam), synchronous vs async replication
- **Kubernetes platform** -- Nutanix Kubernetes Management (formerly NKE/Karbon) vs upstream Kubernetes on VMs vs Rancher/OpenShift
- **Microsegmentation** -- Flow (built-in, category-based) vs third-party firewall appliance (Palo Alto VM-Series)
- **Backup target** -- Nutanix Objects (on-cluster S3) vs external NAS vs cloud-tier to AWS S3/Azure Blob

## Reference Architectures

- [Nutanix Validated Designs](https://portal.nutanix.com/page/documents/solutions) -- vendor-validated reference architectures for enterprise applications including SAP, SQL Server, Oracle, and VDI
- [Nutanix Reference Architecture Library](https://portal.nutanix.com/page/documents/solutions) -- comprehensive library of tested architectures for databases, EUC, DevOps, and hybrid cloud
- [Nutanix Best Practice Guide for AHV](https://portal.nutanix.com/page/documents/solutions/details?targetId=BP-2071-AHV:BP-2071-AHV) -- official best practices for AHV hypervisor configuration, networking, and storage
- [Nutanix Cloud Platform Architecture](https://www.nutanixbible.com/) -- "The Nutanix Bible" covering distributed storage fabric, CVM architecture, and cluster design
- [Nutanix DR and Business Continuity reference architecture](https://portal.nutanix.com/page/documents/solutions) -- validated designs for Leap-based disaster recovery and metro availability
