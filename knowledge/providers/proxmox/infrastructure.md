# Proxmox VE

## Scope

This document covers Proxmox VE cluster architecture, including corosync quorum, pmxcfs (Proxmox Cluster File System), KVM/QEMU virtual machines, LXC containers, Ceph hyper-converged integration, ZFS storage, SDN (VXLAN/VLAN zones), HA manager, Proxmox Backup Server, VMware migration (OVA/VMDK import, V2V), web UI and REST API, the subscription model (Community/Enterprise/Premium), hardware compatibility considerations, enterprise support limitations, and comparison with VMware and Nutanix.

## Checklist

- [ ] **[Critical]** Is the Proxmox VE cluster quorum designed with an odd number of nodes (minimum 3) or a properly configured QDevice (corosync-qdevice) to prevent split-brain scenarios?
- [ ] **[Critical]** Is shared storage (Ceph, NFS, iSCSI, or GlusterFS) configured for VM live migration and HA failover, or is local storage used only for non-HA workloads?
- [ ] **[Critical]** Is the Ceph cluster (if HCI) sized with sufficient OSDs, correct replication factor (size=3, min_size=2 for production), and separate dedicated network for Ceph replication traffic?
- [ ] **[Critical]** Is the HA manager configured with appropriate fencing (IPMI, iLO, iDRAC, or hardware watchdog) to ensure failed nodes are reliably power-cycled before workloads restart elsewhere?
- [ ] **[Critical]** Is the network design properly segmented with dedicated interfaces or VLANs for management, VM traffic, Ceph replication (if applicable), and corosync cluster communication?
- [ ] **[Recommended]** Is ZFS configured on appropriate hardware (ECC RAM strongly recommended, sufficient ARC cache sizing, SLOG/L2ARC devices evaluated) with correct RAID level (mirror, RAIDZ1/Z2/Z3)?
- [ ] **[Recommended]** Is the SDN module (VXLAN zones, VLAN zones, simple zones) evaluated for software-defined networking, or is traditional Linux bridge/OVS configuration sufficient?
- [ ] **[Recommended]** Is Proxmox Backup Server deployed for VM and container backups with deduplication, encryption, and off-site replication, with tested restore procedures?
- [ ] **[Recommended]** Are LXC containers used where appropriate (lightweight services, infrastructure tooling) with proper AppArmor profiles and unprivileged mode for security?
- [ ] **[Recommended]** Is a V2V migration strategy documented for importing VMware workloads (OVA/VMDK conversion, qm importdisk, or third-party tools like virt-v2v) with driver replacement (virtio)?
- [ ] **[Optional]** Is the Proxmox subscription tier evaluated (Community repository for non-production, Enterprise/Premium for production with vendor support and stable updates)?
- [ ] **[Optional]** Is GPU passthrough (IOMMU/VFIO) configured for workloads requiring direct hardware access (VDI, AI/ML, media transcoding)?
- [ ] **[Recommended]** Are resource pools and VM/container resource limits (CPU shares, memory ballooning, I/O throttling) configured to prevent noisy neighbor issues?
- [ ] **[Optional]** Is the REST API or Terraform provider (bpg/proxmoxve) used for infrastructure-as-code provisioning rather than manual web UI configuration?

## Why This Matters

Proxmox VE is an increasingly popular open-source virtualization platform, particularly for organizations evaluating alternatives to VMware following the Broadcom acquisition and associated licensing changes. It provides enterprise-class features -- live migration, HA, Ceph HCI, software-defined networking -- at dramatically lower licensing cost. However, Proxmox lacks the deep ecosystem of VMware (no equivalent to vSAN ReadyNodes, limited HCL, smaller partner ecosystem) and enterprise support is more limited. Cluster quorum and fencing misconfiguration are the most common causes of catastrophic failure in Proxmox deployments -- split-brain scenarios or HA failover without proper fencing can cause data corruption.

For VMware migration projects, Proxmox supports importing OVA/VMDK disk images, but driver replacement (IDE/SCSI to virtio for disk and network) and guest agent installation must be planned. Organizations should evaluate whether the operational savings from open-source licensing offset the additional effort required for hardware validation, driver compatibility, and the smaller support ecosystem compared to commercial hypervisors.

## Common Decisions (ADR Triggers)

- **Ceph HCI vs external storage** -- integrated Ceph simplicity vs dedicated SAN/NAS for performance-sensitive workloads, capacity planning differences
- **ZFS vs Ceph vs LVM-thin** -- local ZFS for single-node or small clusters vs Ceph for distributed storage vs LVM-thin for simple provisioning
- **KVM vs LXC** -- full VM isolation vs lightweight container density, security boundary requirements
- **Subscription tier** -- Community (no-subscription) repository vs Enterprise/Premium for production support and stable update channel
- **SDN vs traditional networking** -- Proxmox SDN zones for multi-tenant isolation vs Linux bridges with VLAN trunking
- **Fencing strategy** -- IPMI/BMC-based fencing vs hardware watchdog vs no fencing (non-HA only)
- **Migration tooling** -- native qm importdisk vs virt-v2v vs commercial migration tools for VMware-to-Proxmox V2V
- **Backup infrastructure** -- Proxmox Backup Server vs third-party (Veeam with Proxmox support, Nakivo) vs script-based vzdump

## See Also

- `general/compute.md` -- general compute architecture patterns
- `providers/vmware/licensing.md` -- VMware licensing context for migration decisions
- `patterns/hypervisor-migration.md` -- hypervisor migration planning patterns
- `providers/ceph/storage.md` -- Ceph storage architecture deep dive

## Reference Links

- [Proxmox VE Administration Guide](https://pve.proxmox.com/wiki/Main_Page) -- cluster setup, KVM/LXC management, storage, SDN, and HA configuration
- [Proxmox VE API Reference](https://pve.proxmox.com/pve-docs/api-viewer/) -- REST API for automation, VM provisioning, and cluster management
- [Proxmox Backup Server](https://pbs.proxmox.com/wiki/index.php/Main_Page) -- backup architecture, deduplication, encryption, and restore procedures
