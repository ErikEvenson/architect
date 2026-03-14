# Nutanix Infrastructure

## Checklist

- [ ] Is the cluster sized correctly for the workload? (minimum 3 nodes for RF2, minimum 5 nodes recommended for RF3, consider compute-heavy vs storage-heavy node configurations)
- [ ] Is AHV selected as the hypervisor unless there is a specific requirement for ESXi or Hyper-V, to simplify licensing and management?
- [ ] Is Prism Central deployed for multi-cluster management, reporting, role-based access control, and advanced features (Flow, Calm, Leap)?
- [ ] Is the storage container configured with appropriate redundancy factor (RF2 for non-critical, RF3 for production), compression, deduplication, and erasure coding policies?
- [ ] Are data protection policies configured with protection domains or Leap for VM-level snapshots, replication, and disaster recovery to a secondary site?
- [ ] Is Flow Network Security (microsegmentation) configured to enforce application-tier isolation and zero-trust policies between VMs?
- [ ] Are categories (key-value tags) applied to VMs for use with Flow policies, Calm blueprints, and Prism Central reporting?
- [ ] Is Nutanix Karbon (NKE) evaluated for Kubernetes workloads, with node OS image updates and etcd backup configured?
- [ ] Is Nutanix Objects (S3-compatible object storage) deployed for backup targets, log aggregation, and unstructured data with WORM policies for compliance?
- [ ] Is Nutanix Files deployed for SMB/NFS file shares with File Analytics enabled for audit trails and ransomware detection?
- [ ] Is cluster expansion planned with mixed-node-size awareness, ensuring the CVM (Controller VM) memory and CPU reservations are adequate?
- [ ] Are lifecycle management (LCM) updates tested in a staging cluster before production, with one-click firmware and software upgrades?
- [ ] Is network segmentation configured using VLANs or Nutanix AHV virtual switches to separate management, VM, storage (iSCSI), and backup traffic?
- [ ] Is Prism Central configured with Active Directory or SAML integration for centralized authentication and role-based access?

## Why This Matters

Nutanix hyperconverged infrastructure collapses compute, storage, and networking into a single platform, but this simplicity masks important sizing and configuration decisions. Undersized clusters cause storage bottlenecks when nodes fail and data rebalances. RF2 tolerates only one node failure; RF3 tolerates two but uses 50% more storage. Flow microsegmentation is the only built-in way to enforce network policies without external firewalls. Prism Central is essential for any multi-cluster or enterprise deployment.

## Common Decisions (ADR Triggers)

- **Hypervisor selection** -- AHV (included, no license cost) vs ESXi (VMware ecosystem) vs Hyper-V (Windows ecosystem)
- **Redundancy factor** -- RF2 (can lose 1 node/drive) vs RF3 (can lose 2), storage overhead vs resilience
- **Storage optimization** -- inline compression + dedup (always-on) vs post-process, erasure coding for cold data
- **DR strategy** -- Nutanix Leap (orchestrated failover) vs third-party (Zerto, Veeam), synchronous vs async replication
- **Kubernetes platform** -- Nutanix Karbon (NKE) vs upstream Kubernetes on VMs vs Rancher/OpenShift
- **Microsegmentation** -- Flow (built-in, category-based) vs third-party firewall appliance (Palo Alto VM-Series)
- **Backup target** -- Nutanix Objects (on-cluster S3) vs external NAS vs cloud-tier to AWS S3/Azure Blob
