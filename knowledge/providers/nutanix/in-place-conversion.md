# Nutanix In-Place AHV Conversion (ESXi Cluster Re-Imaging)

## Scope

This file covers **in-place conversion of Nutanix clusters from ESXi to AHV** -- the process of re-imaging Nutanix hardware nodes that currently run VMware ESXi as the hypervisor to run Nutanix AHV natively. This is distinct from VM-by-VM migration (covered in `providers/nutanix/migration-tools.md`) and applies only when the underlying hardware is already Nutanix (NX, Dell XC, Lenovo HX, HPE DX series). For VM-level migration between hypervisors, see `providers/nutanix/migration-tools.md`. For general hypervisor migration patterns, see `patterns/hypervisor-migration.md`.

## Checklist

### Assessment and Prerequisites

- [ ] **[Critical]** Are all cluster nodes confirmed as Nutanix-manufactured or Nutanix-certified hardware? In-place conversion only works on Nutanix HCI nodes -- not on third-party servers running Nutanix software.
- [ ] **[Critical]** Is the Nutanix AOS version compatible with AHV conversion? Verify the current AOS version supports AHV and check the Nutanix compatibility matrix for the target AHV version.
- [ ] **[Critical]** Are VMs using VMware Distributed vSwitches (vDS)? VMs must be migrated to vSphere Standard Switches (vSS) before conversion -- vDS configurations cannot be preserved during hypervisor change.
- [ ] **[Critical]** Is VMware NSX in use on any cluster nodes? NSX-dependent network policies, microsegmentation rules, and overlay networks must be re-implemented on Nutanix Flow or removed before conversion.
- [ ] **[Critical]** Are there VMs with physical RDMs, PCIe passthrough devices, or USB passthrough? These are incompatible with AHV and must be addressed before conversion (migrate to virtual disks, remove passthrough).
- [ ] **[Critical]** Is the cluster running Nutanix CVM (Controller VM) on each node? The CVM is required for the conversion process -- verify CVMs are healthy and communicating with Prism.
- [ ] **[Critical]** Has a pre-conversion cluster health check been run via Nutanix Cluster Check (NCC)? All health checks must pass before initiating conversion -- especially storage health, CVM health, and metadata consistency.
- [ ] **[Recommended]** Are VM hardware versions documented? VMs with very old hardware versions (< v8) may need upgrading before conversion.
- [ ] **[Recommended]** Is the cluster minimum node count maintained during conversion? The process takes nodes offline one at a time -- a 3-node cluster will temporarily run on 2 nodes, which may violate RF2 data protection if a second node fails.
- [ ] **[Recommended]** Are VMs with encrypted disks (vSphere VM Encryption) identified? These must be decrypted before conversion.
- [ ] **[Optional]** Are vSphere DRS rules, affinity/anti-affinity policies, and resource pools documented? These must be manually recreated in AHV post-conversion.

### Conversion Planning

- [ ] **[Critical]** Is a maintenance window sized for the full cluster conversion? The rolling process takes approximately 30-60 minutes per node (including data rebalancing), so a 4-node cluster requires 2-4 hours, an 8-node cluster 4-8 hours.
- [ ] **[Critical]** Is the conversion sequence planned node-by-node? Only one node is converted at a time -- the process evacuates VMs, re-images the hypervisor, reboots, and rebalances data before proceeding to the next node.
- [ ] **[Critical]** Is there sufficient cluster capacity to run all VMs on N-1 nodes during each node conversion? If the cluster is at high utilization, VMs may not be able to evacuate successfully.
- [ ] **[Critical]** Has Nutanix Support been engaged? In-place conversion typically requires Nutanix Support involvement or a qualified Nutanix partner to execute.
- [ ] **[Recommended]** Is a rollback plan documented? Rolling back a partially converted cluster (some nodes AHV, some ESXi) is complex and may require Nutanix Support -- it is preferable to complete the conversion forward.
- [ ] **[Recommended]** Is the vCenter server decommission plan prepared? After conversion, vCenter is no longer needed for this cluster -- plan for license reclamation, DNS cleanup, and monitoring updates.
- [ ] **[Optional]** Is a pilot conversion planned on a non-production or smaller cluster first to validate the process before converting large production clusters?

### Conversion Execution

- [ ] **[Critical]** Is VM evacuation (vMotion) confirmed working between all nodes in the cluster before starting? If vMotion is broken, VMs cannot be live-migrated off nodes during conversion.
- [ ] **[Critical]** Are Nutanix VirtIO drivers pre-installed in Windows VMs before conversion? Linux VMs typically include VirtIO drivers in-kernel, but Windows VMs need the Nutanix VirtIO driver package installed while still running on ESXi to ensure they boot on AHV.
- [ ] **[Critical]** Is VM network mapping prepared? ESXi port groups must be mapped to AHV virtual networks -- the conversion process needs this mapping to reconnect VM NICs post-conversion.
- [ ] **[Recommended]** Are application owners notified of the maintenance window? While VMs continue running (they vMotion between nodes), there may be brief network blips during VM migration.
- [ ] **[Recommended]** Is storage rebalancing monitored after each node conversion? The cluster redistributes data to the newly converted node -- wait for rebalancing to complete before converting the next node.

### Post-Conversion Validation

- [ ] **[Critical]** Are all VMs running and accessible after the final node conversion? Validate network connectivity, application functionality, and storage access.
- [ ] **[Critical]** Is Nutanix Guest Tools (NGT) installed on all VMs for VSS-consistent snapshots and self-service capabilities?
- [ ] **[Critical]** Are backup jobs updated to use AHV-compatible backup methods (Veeam for AHV, HYCU, or Nutanix Leap)?
- [ ] **[Recommended]** Are monitoring tools updated to reflect the new AHV hypervisor? vCenter-based monitoring will no longer function -- transition to Prism-based or agent-based monitoring.
- [ ] **[Recommended]** Are VMware Tools uninstalled from all VMs? Residual VMware Tools can cause issues with AHV guest agents.
- [ ] **[Optional]** Is the vCenter server decommissioned and VMware licenses reclaimed?

## Why This Matters

In-place conversion is dramatically faster and less risky than VM-by-VM migration when the hardware is already Nutanix. A VM-by-VM migration of 1,000 VMs using Nutanix Move might take 4-8 weeks (seeding, cutover scheduling, validation). In-place conversion of the same cluster can complete in a single maintenance window (hours, not weeks) because VMs are never actually moved -- the hypervisor underneath them changes while data stays on the same Nutanix distributed storage.

The most common mistake is not realizing the option exists. Many organizations treat ESXi-on-Nutanix the same as ESXi-on-VxRail and plan VM-by-VM migration for both. The cluster naming convention is the key signal -- clusters named with NUNX, NTNX, or NUDX patterns but showing ESX hypervisor are in-place conversion candidates. Hardware discovery tools like HPE OneView report the hypervisor (ESX vs AHV) but not the underlying hardware platform, so cluster naming analysis is essential.

The second most common mistake is attempting conversion on a cluster with vDS-connected VMs. The conversion process cannot preserve vDS configurations -- VMs must be on Standard Switches first. This is a pre-requisite that can take days to complete on large clusters with complex networking, so it should be identified early in planning.

## Decision Framework: In-Place Conversion vs. VM-by-VM Migration

| Factor | In-Place Conversion | VM-by-VM Migration |
|--------|--------------------|--------------------|
| **Hardware** | Must be Nutanix HCI | Any source hardware |
| **Speed** | Hours per cluster | Weeks per cluster |
| **Downtime** | Brief VM vMotion blips | Per-VM cutover windows |
| **Data movement** | None (data stays on Nutanix storage) | Full data copy to target |
| **Network change** | Minimal (same cluster IPs) | May require IP changes |
| **Complexity** | Lower (automated process) | Higher (per-VM planning) |
| **Risk** | Cluster-level (all VMs affected) | VM-level (one VM at a time) |
| **Rollback** | Difficult mid-conversion | Easy (keep source running) |
| **Prerequisites** | No vDS, no NSX, VirtIO pre-installed | Fewer prerequisites |
| **vCenter required** | Yes (for VM evacuation during conversion) | Yes (as Move source) |

**Choose in-place conversion when:**
- Underlying hardware is Nutanix
- Cluster is not using vDS or NSX
- A maintenance window is available for the full cluster
- Speed is prioritized over granular VM-level control

**Choose VM-by-VM migration when:**
- Source hardware is not Nutanix (VxRail, HPE, Dell standalone)
- VMs need to move to a different cluster or site
- Per-VM cutover scheduling is required (different maintenance windows per application)
- vDS/NSX removal is not feasible

## Common Decisions (ADR Triggers)

- **Conversion vs. migration decision per cluster** -- which Nutanix clusters running ESXi should be converted in-place vs. having VMs migrated to other clusters; criteria include cluster age, hardware generation, and capacity
- **vDS remediation approach** -- migrate VMs to vSS before conversion (adds time) vs. recreate networking on AHV after conversion (adds risk); hybrid approaches for clusters with mixed vSS/vDS VMs
- **Conversion sequence** -- which clusters convert first; typically start with smallest/least critical cluster as pilot, then proceed by business criticality
- **VirtIO driver pre-installation method** -- deploy via SCCM/Intune/Ansible before conversion vs. rely on the conversion process to inject drivers; pre-installation is strongly recommended for Windows VMs
- **vCenter decommission timing** -- decommission vCenter immediately after last cluster conversion vs. maintain for a grace period; license cost vs. rollback safety

## See Also

- `providers/nutanix/migration-tools.md` -- VM-by-VM migration using Nutanix Move, Veeam, Zerto
- `patterns/hypervisor-migration.md` -- General hypervisor-to-hypervisor migration patterns
- `providers/nutanix/infrastructure.md` -- Nutanix cluster architecture, AOS, Prism
- `providers/vmware/licensing.md` -- VMware/Broadcom licensing changes driving migrations
