# Hypervisor-to-Hypervisor Migration Pattern

## Scope

This file covers **hypervisor-to-hypervisor migration**: moving virtual machine workloads from one hypervisor platform to another (e.g., VMware ESXi to Nutanix AHV, VMware to Hyper-V, VMware to KVM/Proxmox). It addresses source assessment, target selection, migration tooling, driver conversion, network mapping, management plane transition, and guest OS compatibility. For cloud migration (on-prem to IaaS/PaaS), see `general/workload-migration.md`. For cutover execution, see `patterns/migration-cutover.md`.

## Checklist

- [ ] **[Critical]** Complete VM inventory with OS versions, virtual hardware versions, disk formats, and resource consumption
- [ ] **[Critical]** Identify VMs with hardware dependencies that block automated migration (GPU passthrough, PCIe devices, USB passthrough, RDM/physical-mode disks, independent/persistent disks)
- [ ] **[Critical]** Verify guest OS compatibility with target hypervisor — check vendor support matrices for every OS version in the estate
- [ ] **[Critical]** Plan and test driver injection strategy (VirtIO for KVM/AHV, Hyper-V Integration Services for Hyper-V) before production migration
- [ ] **[Critical]** Map source network constructs (vDS port groups, VLANs, security policies, traffic shaping) to target equivalents — document every VLAN and port group mapping
- [ ] **[Critical]** Validate licensing — confirm target hypervisor licensing covers all hosts and that guest OS licenses (especially Windows Server) are valid under the new hypervisor
- [ ] **[Critical]** Define rollback procedure: can source VMs be restarted if migration fails? Are snapshots preserved?
- [ ] **[Recommended]** Capture performance baselines on source hypervisor (CPU, memory, IOPS, network throughput per VM) for post-migration comparison
- [ ] **[Recommended]** Run a pilot wave of 3-5 non-critical VMs through the full migration process before committing to production waves
- [ ] **[Recommended]** Identify and plan for management tool replacement: vCenter alternatives (Prism, SCVMM, Proxmox web UI), monitoring agents, backup agents
- [ ] **[Recommended]** Audit VMware-specific features in use (DRS, HA, vMotion, Storage DRS, fault tolerance) and map to target equivalents or alternatives
- [ ] **[Recommended]** Plan vCenter decommission timeline — do not decommission until all VMs are migrated, validated, and rollback window has closed
- [ ] **[Recommended]** Test backup and restore workflows on target hypervisor before migrating production workloads
- [ ] **[Optional]** Evaluate Broadcom/VMware contract renewal timeline to establish migration deadline and negotiate short-term bridge licensing if needed
- [ ] **[Optional]** Assess VMware NSX dependencies — micro-segmentation rules, distributed firewall policies, load balancers that must be replicated on the target platform
- [ ] **[Optional]** Plan physical host re-purposing or replacement if target hypervisor has different hardware requirements or certification lists

## Why This Matters

Hypervisor migration is fundamentally different from cloud migration. Both source and target are on-premises infrastructure under your control, but the VM format, driver model, network abstraction, and management plane all change simultaneously. A VM that runs perfectly on ESXi may fail to boot on KVM because it lacks VirtIO drivers, or it may boot but lose network connectivity because the virtual NIC type changed.

The Broadcom acquisition of VMware (completed November 2023) has made hypervisor migration an urgent reality for many organizations. Broadcom eliminated perpetual licensing in favor of subscription-only bundles (VMware Cloud Foundation or VMware vSphere Foundation), shifted to per-core pricing with a 72-core minimum per CPU (effective April 2025), and terminated the VMware Cloud Service Provider (VCSP) program in favor of an invite-only model (January 2026). Many organizations have seen 3-5x cost increases, with some smaller deployments experiencing even higher multipliers. This has driven a wave of migrations to Nutanix AHV, Microsoft Hyper-V, Proxmox VE, and KVM-based platforms.

The most common hypervisor migration failures are: VMs that fail to boot because drivers were not injected before conversion, network connectivity loss because VLAN mappings were incomplete, performance degradation because storage I/O paths changed without tuning, and management gaps because teams decommissioned vCenter before establishing equivalent monitoring and automation on the target platform. All of these are preventable with proper assessment and pilot testing.

## Common Decisions (ADR Triggers)

### ADR: Target Hypervisor Selection
**Context:** Organization needs to migrate off VMware ESXi. Must select a replacement hypervisor platform.
**Options:**
- **Nutanix AHV** — Included with Nutanix HCI licensing (no separate hypervisor cost). Tightly integrated with Nutanix Prism management. Supports live migration, HA, and ADS (Acropolis Dynamic Scheduling, equivalent to DRS). Migration tooling (Nutanix Move) purpose-built for VMware-to-AHV. Requires Nutanix hardware or certified OEM hardware.
- **Microsoft Hyper-V / Azure Stack HCI** — Included with Windows Server Datacenter licensing. Familiar to Windows-centric shops. SCVMM for management. Strong integration with Azure Arc and Azure hybrid services. Weaker Linux guest support historically, though improved significantly.
- **Proxmox VE** — Open-source (AGPL), no licensing cost. KVM-based with LXC container support. Web UI included. Community and enterprise support subscriptions available. Strong fit for SMBs and cost-sensitive environments. Lacks enterprise features like distributed switching and centralized multi-cluster management at scale.
- **Red Hat OpenShift Virtualization (KubeVirt)** — Runs VMs as Kubernetes pods alongside containers. Strategic for organizations already committed to OpenShift. Higher operational complexity. Not a drop-in hypervisor replacement.
- **Oracle Linux Virtualization Manager (oVirt)** — Open-source KVM management. Free but smaller ecosystem. Suitable for Oracle-heavy environments.

**Decision criteria:** If already running Nutanix HCI or willing to adopt it, AHV is the lowest-friction path with purpose-built migration tooling. If Windows-centric with existing Microsoft EA, Hyper-V/Azure Stack HCI leverages existing licenses. If cost is the primary driver and the team is Linux-capable, Proxmox VE eliminates hypervisor licensing entirely. If the strategic direction is containers and Kubernetes, OpenShift Virtualization consolidates VMs and containers on one platform but is not a like-for-like hypervisor swap.

### ADR: Migration Tooling Strategy
**Context:** Need to convert and migrate VMs from source hypervisor to target hypervisor format.
**Options:**
- **Vendor-native tools** — Nutanix Move (VMware to AHV), Microsoft MVMC/Azure Migrate (VMware to Hyper-V), SCVMM (import VMware VMs). Purpose-built, supported, handle driver injection automatically. Limited to vendor-specific target.
- **virt-v2v (Red Hat/open-source)** — Converts VMs from VMware, Xen, or Hyper-V to KVM. Handles driver injection (VirtIO) for both Linux and Windows guests. Supports output to libvirt, oVirt, OpenStack, and local disk. Industry standard for KVM targets.
- **Veeam / NAKIVO / Zerto** — Backup-based migration: back up from source hypervisor, restore to target. Works across hypervisors. Adds a tested backup/restore path as a side benefit. Slower than streaming replication tools.
- **Manual conversion** — Export OVA/VMDK from source, convert disk format (qemu-img convert), import to target, manually install drivers. Full control but labor-intensive and error-prone at scale.

**Decision criteria:** Always prefer vendor-native tools when migrating to their platform — they handle driver injection, hardware abstraction, and network mapping automatically. Use virt-v2v for KVM/Proxmox targets. Consider backup-based migration for small estates (< 50 VMs) or when you want the migration to also validate your backup/restore pipeline. Manual conversion is a last resort for VMs that automated tools cannot handle (e.g., unusual OS, non-standard disk configurations).

### ADR: Network Architecture Transition
**Context:** VMware vDS (Distributed Switch) provides centralized network management, port mirroring, LACP, traffic shaping, and network I/O control. Target hypervisor uses a different networking model.
**Options:**
- **Pre-migration to vSS** — Migrate VMware VMs from vDS to vSS (Standard Switch) before hypervisor migration. Simplifies the hypervisor migration by removing vDS dependency. Extra step but reduces variables during conversion.
- **Direct vDS-to-target mapping** — Map vDS port groups directly to target network constructs (AHV managed networks, Hyper-V virtual switches, OVS bridges). Requires complete port group inventory and VLAN mapping documentation.
- **Network redesign** — Use the hypervisor migration as an opportunity to simplify or redesign the network architecture. Higher risk, higher reward. Only appropriate if the current network architecture has known deficiencies.

**Decision criteria:** Direct mapping is safest for most migrations — preserve existing VLAN assignments and security zones. Pre-migration to vSS is warranted if the vDS configuration is complex (LACP, NetFlow, port mirroring) and those features are not needed on the target. Network redesign should be a separate project, not combined with hypervisor migration.

### ADR: Management Plane Transition Strategy
**Context:** vCenter provides VM lifecycle management, monitoring, alerting, RBAC, automation (vRealize/Aria), and third-party integrations. Decommissioning vCenter requires replacing all of these functions.
**Options:**
- **Parallel management** — Run both vCenter and target management (Prism, SCVMM, Proxmox UI) during migration. Decommission vCenter only after all VMs are migrated and validated. Safest but requires maintaining vCenter licensing during transition.
- **Immediate vCenter decommission** — Decommission vCenter as soon as VMs are migrated off ESXi hosts. Fastest license cost reduction. Risk: lose visibility into any remaining VMware infrastructure.
- **Phased feature migration** — Migrate management functions in phases: VM lifecycle first, then monitoring, then automation, then RBAC. Ensures no management gaps.

**Decision criteria:** Always use parallel management during migration. Decommission vCenter only after the last VMware VM is migrated, validated, and the rollback window has closed. Budget for short-term vCenter licensing overlap — the cost of maintaining vCenter for 3-6 months during migration is far less than the cost of a management gap during a production incident.

## Source Assessment

### VM Inventory and Classification

Catalog every VM in the VMware environment with the following attributes:

| Attribute | Why It Matters |
|-----------|---------------|
| Guest OS and version | Target hypervisor may not support EOL operating systems (Windows Server 2008, RHEL 5, etc.) |
| Virtual hardware version | Newer hardware versions may use features not available on the target hypervisor |
| Disk type and format | RDM (Raw Device Mapping), independent disks, eager/lazy thick provisioning affect conversion |
| Disk size | Some migration tools have maximum disk size limits per migration task |
| CPU/memory allocation | Right-sizing opportunity during migration |
| Network adapters and port groups | Must map to target network constructs |
| VMware Tools version | Must be replaced with target guest agents (Nutanix Guest Tools, Hyper-V Integration Services) |
| Snapshots | Must be consolidated before migration — do not migrate VMs with active snapshot chains |
| GPU/PCIe passthrough | Cannot be automatically migrated — requires manual reconfiguration on target |
| Affinity/anti-affinity rules | Must be recreated on target management plane |
| Custom attributes and tags | Used for automation and organization — must be replicated or mapped |

### Workloads That Require Special Handling

- **VMs with RDM (Raw Device Mapping)** — Convert to VMDK before migration, or re-attach raw storage on target
- **VMs with independent/persistent disks** — Nutanix Move and most automated tools do not support these; migrate data separately
- **VMs with PCIe passthrough (GPU, NIC SR-IOV)** — Requires manual passthrough reconfiguration on target hypervisor
- **VMs with active snapshot trees** — Consolidate all snapshots before migration
- **VMs running unsupported guest OS** — May need to retain on VMware or perform P2V-style conversion
- **VMs with VMware-specific drivers or agents** — NSX agents, vRealize agents, third-party agents tied to VMware APIs

## Target Selection Considerations

### Feature Parity Matrix

| VMware Feature | Nutanix AHV | Hyper-V / Azure Stack HCI | Proxmox VE (KVM) |
|---------------|-------------|---------------------------|-------------------|
| Live migration (vMotion) | AHV live migration | Live Migration | QEMU live migration |
| HA (auto-restart on failure) | AHV HA | Failover Clustering | HA (Corosync/QEMU) |
| DRS (dynamic load balancing) | ADS (Acropolis Dynamic Scheduling) | SCVMM dynamic optimization | Manual / third-party |
| Distributed switching (vDS) | AHV managed networking (OVS-based) | Logical switch (SCVMM) | OVS bridges / Linux bridges |
| Storage vMotion | AHV storage live migration | Storage Migration | Storage live migration |
| Fault tolerance | Not available (use HA + application-level clustering) | Not available (use HA) | Not available |
| NSX micro-segmentation | Flow Network Security (Nutanix Flow) | Azure Network Security Groups / Windows Firewall | OVN / firewall rules |
| vRealize / Aria automation | Nutanix Calm / Prism Pro | Azure Arc / SCVMM / WAC | Ansible / Terraform |
| Content library (templates) | Image service | SCVMM library | Template system |

### Hardware Compatibility

- **Nutanix AHV** — Runs on Nutanix-branded hardware or certified OEM nodes (Dell, Lenovo, HPE, Fujitsu). Cannot run on arbitrary servers.
- **Hyper-V** — Runs on any x86-64 server meeting Windows Server hardware requirements. Broad compatibility.
- **Proxmox VE** — Runs on any x86-64 server with VT-x/VT-d support. Widest hardware compatibility. No vendor lock-in.
- **General** — Verify CPU, NIC, and storage controller compatibility with the target hypervisor's HCL (Hardware Compatibility List) before purchasing or repurposing hardware.

## Migration Tooling

### Nutanix Move

Nutanix Move is a purpose-built cross-hypervisor migration tool for migrating VMs to AHV.

**Capabilities:**
- Agentless migration from VMware ESXi (connects to vCenter)
- Seeding (initial full copy) followed by incremental replication of changed blocks
- Automatic driver injection (VirtIO drivers for AHV)
- Network mapping (source port groups to AHV managed networks)
- Automated VMware Tools uninstall and Nutanix Guest Tools (NGT) install
- Supports both Linux and Windows guests
- Bulk migration with configurable bandwidth throttling
- Cutover scheduling with minimal downtime (final delta sync + VM power-on)

**Limitations:**
- Does not support VMs with independent/persistent disks — must detach before migration
- Does not support VMs with PCIe passthrough devices — must remove before migration
- Does not support VMs with active snapshot chains — consolidate first
- Does not support physical-mode RDMs — convert to virtual-mode or VMDK first
- Does not migrate VMware-level constructs (resource pools, DRS rules, custom attributes)
- Does not handle program management (wave scheduling, stakeholder communication, executive reporting)
- UEFI-to-UEFI migration support depends on Move version and guest OS — verify against release notes

### virt-v2v (KVM/Proxmox Target)

Red Hat's open-source VM conversion tool, the industry standard for converting VMs to KVM.

**Capabilities:**
- Converts VMs from VMware (via vCenter or direct ESXi), Hyper-V, and Xen to KVM
- Injects VirtIO drivers (block, network, balloon) for both Linux and Windows guests
- Windows VirtIO driver injection requires the virtio-win package installed on the conversion host
- Outputs to libvirt, oVirt, OpenStack, or local QCOW2/raw disk files
- Handles boot loader reconfiguration (GRUB updates for Linux guests)
- Companion tool virt-p2v for physical-to-virtual conversion

**Limitations:**
- Offline conversion only — VM must be shut down during conversion
- Windows driver injection requires virtio-win ISO/drivers to be available on the conversion host
- Complex VMware configurations (vApps, multi-NIC with specific port group mappings) require manual post-conversion configuration
- No incremental replication — each conversion is a full copy

### Microsoft MVMC / SCVMM (Hyper-V Target)

**Capabilities:**
- Converts VMware VMs to Hyper-V (VHD/VHDX format)
- Installs Hyper-V Integration Services during conversion
- SCVMM can import VMware VMs directly by connecting to vCenter

**Limitations:**
- MVMC has been deprecated — SCVMM or Azure Migrate is the current supported path
- Some Linux guest OS versions may require manual installation of Hyper-V Integration Services

## Driver Injection and Conversion

### The Driver Problem

Every hypervisor presents different virtual hardware to guest operating systems. VMware guests use PVSCSI (storage) and VMXNET3 (network) paravirtual drivers. KVM/AHV guests use VirtIO drivers. Hyper-V guests use Hyper-V Integration Services (VSC drivers). If the target drivers are not present when the VM boots on the new hypervisor, the VM either fails to boot (cannot find boot disk) or boots without network connectivity.

### Driver Injection Strategies

| Strategy | When to Use | Risk |
|----------|-------------|------|
| **Automated tool injection** | Migration tool handles it (Nutanix Move, virt-v2v) — always prefer this | Low — tool is tested against supported OS matrix |
| **Pre-install drivers on source** | Install target drivers (VirtIO, Integration Services) on the VM while it still runs on VMware | Low — drivers coexist, activate when hardware is detected |
| **Offline injection** | Mount VM disk on conversion host, inject drivers into offline OS | Medium — requires knowledge of OS driver store and boot configuration |
| **Recovery mode injection** | Boot VM on target hypervisor with IDE/emulated devices, install drivers, switch to paravirtual | Medium — requires guest OS recovery/safe mode boot |

### Windows Guest Driver Injection

1. **Preferred:** Use migration tool's automated injection (Nutanix Move, virt-v2v with virtio-win)
2. **Fallback — pre-install on source:** Install VirtIO drivers (Red Hat signed) or NGT on the Windows VM while it runs on VMware. Drivers register but remain inactive until matching hardware is detected.
3. **Emergency — offline injection:** Mount the VMDK/QCOW2 on a Linux host, use `virt-customize` or manual registry edits to inject drivers into the Windows driver store
4. **Last resort:** Boot VM on target with IDE emulation (slow but functional), install paravirtual drivers, shut down, reconfigure to paravirtual, restart

### Linux Guest Driver Injection

Linux kernels 2.6.25+ include VirtIO drivers in-tree. Most modern Linux distributions (RHEL 6+, Ubuntu 12.04+, SLES 11+, Debian 7+) have VirtIO modules compiled into the kernel or initramfs. Driver injection is rarely needed for Linux guests — the kernel detects the new virtual hardware and loads appropriate modules automatically. Verify that the initramfs/initrd includes VirtIO modules (`lsinitrd` on RHEL, `lsinitramfs` on Debian/Ubuntu).

## Network Mapping

### VMware vDS to Target Hypervisor Networking

VMware Distributed Switch (vDS) provides centralized network configuration across an ESXi cluster. When migrating to a different hypervisor, every vDS port group must be mapped to an equivalent construct on the target.

### Network Mapping Checklist

1. **Export vDS configuration** — Document every port group, VLAN ID, security policy (promiscuous mode, MAC changes, forged transmits), traffic shaping policy, and LACP/LAG configuration
2. **Map VLANs** — VLANs are hypervisor-independent; the same VLAN IDs work on any hypervisor. Map each vDS port group to a target virtual switch port with the same VLAN tag
3. **Recreate security policies** — Promiscuous mode, MAC spoofing settings must be configured on target virtual switches
4. **LACP/LAG** — If using LACP on vDS, configure equivalent bonding on target (OVS bond on AHV/Proxmox, NIC teaming on Hyper-V)
5. **Traffic shaping** — If using vDS traffic shaping or Network I/O Control, configure QoS on target (OVS QoS, Hyper-V bandwidth management)
6. **Port mirroring** — If using vDS port mirroring (SPAN), configure equivalent on target (OVS mirror ports, Hyper-V port mirroring)

### Target Networking Equivalents

| VMware vDS Feature | Nutanix AHV (OVS) | Hyper-V | Proxmox VE (OVS/Linux Bridge) |
|-------------------|--------------------|---------|----|
| Port group with VLAN | AHV managed network with VLAN | Virtual switch with VLAN ID | OVS port with VLAN tag |
| LACP / LAG | OVS bond (LACP mode) | NIC teaming (LACP) | OVS bond (LACP mode) |
| Promiscuous mode | OVS port mirror or promisc flag | Hyper-V port mirroring | OVS or bridge promisc |
| Traffic shaping | OVS QoS (ingress policing, egress shaping) | Hyper-V bandwidth management | OVS QoS / tc |
| Private VLAN | Nutanix Flow micro-segmentation | Hyper-V isolation mode | OVS ACL rules |
| NetFlow/IPFIX | OVS sFlow/IPFIX | Not native (third-party) | OVS sFlow/IPFIX |

## VM Hardware Compatibility

### Virtual Hardware Differences

| Component | VMware ESXi | KVM/AHV | Hyper-V |
|-----------|-------------|---------|---------|
| Storage controller (paravirtual) | PVSCSI | VirtIO-blk / VirtIO-SCSI | StorVSC |
| Network adapter (paravirtual) | VMXNET3 | VirtIO-net | NetVSC |
| Display adapter | SVGA | QXL / VirtIO-GPU | Synthetic video |
| Memory ballooning | VMware balloon driver | VirtIO-balloon | Dynamic Memory |
| Guest agent | VMware Tools | QEMU Guest Agent / NGT | Hyper-V Integration Services |
| Disk format | VMDK | QCOW2 (KVM) / raw (AHV) | VHD / VHDX |
| UEFI firmware | VMware EFI | OVMF (TianoCore) | Hyper-V Gen 2 |
| TPM | vTPM | swtpm | vTPM (Gen 2) |
| Secure Boot | Supported (HW v13+) | Supported (OVMF + signed shim) | Supported (Gen 2) |

### Conversion Considerations

- **BIOS vs UEFI** — Ensure the target hypervisor supports the same firmware type. BIOS VMs on VMware should remain BIOS on the target. Converting BIOS to UEFI (or vice versa) during migration adds unnecessary risk.
- **SCSI controller type** — Migration tools typically handle this, but verify that the boot disk is attached to a paravirtual controller on the target (VirtIO-SCSI for KVM/AHV, not IDE emulation which is significantly slower).
- **vCPU topology** — VMware sockets/cores-per-socket settings should be mapped to equivalent topology on the target, especially for applications with socket-based licensing (SQL Server, Oracle).
- **Memory reservation** — VMware memory reservations do not exist on most target hypervisors. Evaluate whether the application requires guaranteed memory or can use overcommitted memory with ballooning.

## Guest OS Compatibility

### Support Matrix Considerations

Each hypervisor vendor publishes a supported guest OS list. VMs running unsupported guest operating systems may work but will not receive vendor support if issues arise.

| Guest OS | Nutanix AHV | Hyper-V (WS 2022) | Proxmox VE / KVM |
|----------|-------------|--------------------|----|
| Windows Server 2022 | Supported | Supported | Supported |
| Windows Server 2019 | Supported | Supported | Supported |
| Windows Server 2016 | Supported | Supported | Supported |
| Windows Server 2012 R2 | Supported (check EOL) | Supported | Supported |
| Windows 10/11 | Supported | Supported | Supported |
| RHEL 8.x / 9.x | Supported | Supported | Supported |
| Ubuntu 20.04 / 22.04 / 24.04 | Supported | Supported | Supported |
| SLES 12 / 15 | Supported | Supported | Supported |
| Debian 11 / 12 | Community (check AHV matrix) | Supported | Supported |
| CentOS 7 (EOL June 2024) | Supported (may drop) | Supported | Supported |
| Windows Server 2008 R2 (EOL) | Not supported | Legacy support | Works (unsupported) |
| RHEL 5/6 (EOL) | Not supported | Not supported | Works (unsupported) |

### EOL Operating Systems

VMs running end-of-life operating systems are the highest-risk workloads in a hypervisor migration:

- **Option 1: Upgrade OS before migration** — Safest. Upgrade to a supported OS version, then migrate. Two changes, but each is well-understood.
- **Option 2: Migrate as-is, accept risk** — The VM may work on the target hypervisor even if not officially supported. No vendor support if issues arise.
- **Option 3: Retain on VMware** — Keep the EOL VM on a minimal VMware cluster until the application is decommissioned. Requires maintaining VMware licensing for that cluster.
- **Option 4: P2V to target** — If the EOL OS cannot be migrated by automated tools, use physical-to-virtual techniques (disk-level clone and conversion).

## Management Plane Transition

### vCenter Replacement Checklist

vCenter is not just a VM manager — it is the integration point for monitoring, backup, automation, compliance, and operations tooling. Decommissioning vCenter requires replacing every integration.

| vCenter Function | Replacement Required |
|-----------------|---------------------|
| VM lifecycle (create, clone, delete, snapshot) | Target management plane (Prism, SCVMM, Proxmox UI) |
| Performance monitoring | Target monitoring + external tools (Prometheus, Grafana, Datadog) |
| Alerting | Target alerting + external tools |
| RBAC and permissions | Target RBAC (Prism roles, AD integration on all platforms) |
| Automation (vRealize/Aria) | Nutanix Calm, Ansible, Terraform, Rundeck |
| Backup integration (Veeam, Commvault) | Reconfigure backup agents/proxies for target hypervisor |
| Compliance scanning (vRealize SaltStack, Tanzu) | Target-compatible compliance tools |
| API consumers (custom scripts, CMDB sync) | Rewrite against target API (Nutanix Prism v3 API, Hyper-V WMI/PowerShell, Proxmox API) |
| Log forwarding (syslog from ESXi/vCenter) | Configure syslog on target hypervisor hosts |

### vCenter Decommission Timeline

```
Migration start:     vCenter remains fully operational
                     Target management plane deployed in parallel
                     All new VMs created on target platform

Migration waves:     VMs migrate wave by wave
                     vCenter visibility decreases as VMs leave
                     Maintain vCenter for rollback capability

Last VM migrated:    Begin rollback timer (typically 2-4 weeks)
                     vCenter still running for emergency rollback

Rollback window      Decommission vCenter, ESXi hosts
closed:              Reclaim VMware licenses
                     Archive vCenter database for historical reference
```

## Migration Wave Planning

### Wave Sequencing for Hypervisor Migration

1. **Wave 0 — Infrastructure preparation:** Deploy target hypervisor, configure networking (VLANs, bonds, virtual switches), configure storage, deploy management plane, validate backup integration
2. **Wave 1 — Pilot (3-5 VMs):** Non-critical VMs, mix of Linux and Windows, test full migration lifecycle including rollback
3. **Wave 2 — Development/test environments:** Lower-risk workloads, larger batch, validate automation and wave process
4. **Wave 3-N — Production waves:** Group by application dependency clusters. Migrate tightly coupled VMs together. Schedule during maintenance windows.
5. **Final wave — Stragglers and special cases:** VMs requiring manual conversion, EOL OS workloads, GPU passthrough VMs

### VMs Per Wave Sizing

- **Pilot:** 3-5 VMs (manual, high-touch)
- **Early waves:** 10-20 VMs (building confidence)
- **Steady state:** 20-50 VMs per wave (depends on network bandwidth for replication and team capacity for validation)
- **Constraint:** Total migration bandwidth — each VM's disk must be fully replicated. A 500 GB VM over a 1 Gbps link takes ~70 minutes for initial seed. Plan wave sizes against available bandwidth and cutover window duration.

## See Also

- `general/workload-migration.md` — Cloud migration strategy and the 6 Rs framework
- `patterns/migration-cutover.md` — Cutover runbook pattern, rollback procedures, communication templates
- `general/disaster-recovery.md` — DR planning for migrated workloads
- `general/networking.md` — Network architecture patterns
