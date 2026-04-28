# Dell PowerEdge Servers

## Scope

Dell PowerEdge rack, tower, and blade server platforms: model selection (R-series rack, T-series tower, MX modular), iDRAC integrated management, OpenManage Enterprise centralized management, firmware and BIOS lifecycle, hardware configuration (RAID, NIC teaming, power redundancy), and integration with VMware, Nutanix, and bare-metal Linux/Windows deployments.

## Checklist

- [ ] [Critical] Is the correct PowerEdge generation and form factor selected for the workload? (R-series rack for datacenter density, T-series tower for edge/remote, MX modular for blade consolidation, C-series for hyperscale/cloud, XE-series for GPU-accelerated AI/ML)
- [ ] [Critical] Is iDRAC Enterprise or Datacenter licensed and configured for out-of-band management, virtual console, virtual media, and remote firmware updates on every server?
- [ ] [Critical] Are RAID controllers configured with the correct RAID level for the workload? (RAID 1 for OS mirrors, RAID 5/6 for general storage, RAID 10 for database/high-IOPS, hardware RAID via PERC vs software RAID vs HBA pass-through for vSAN/S2D)
- [ ] [Critical] Is redundant power configured with dual PSUs connected to separate power feeds/PDUs, and is the power redundancy policy set correctly in iDRAC (redundant vs non-redundant)?
- [ ] [Critical] Is the firmware baseline defined and consistent across all servers? (BIOS, iDRAC, NIC, RAID controller, drive firmware all at the same Dell-validated baseline)
- [ ] [Critical] Is OpenManage Enterprise (OME) deployed for centralized server discovery, inventory, monitoring, alerting, firmware compliance, and configuration drift detection across the fleet?
- [ ] [Recommended] Is the iDRAC network on a dedicated out-of-band management VLAN, isolated from production traffic and protected by ACLs?
- [ ] [Recommended] Is Dell OpenManage Integration for VMware vCenter (OMIVV) or Microsoft SCVMM deployed if running those hypervisors, for hardware health visibility within the hypervisor management console?
- [ ] [Recommended] Are server profiles/templates created in OpenManage Enterprise for consistent BIOS settings, boot order, storage configuration, and network adapter settings across identical servers?
- [ ] [Recommended] Is the BIOS configured with the correct performance profile? (e.g., Performance mode for databases, Dense Configuration Optimized for VDI, Custom for specific workloads -- disable C-states and turbo boost limits for latency-sensitive workloads)
- [ ] [Recommended] Is Secure Boot enabled with UEFI boot mode to prevent unauthorized OS or bootloader modifications?
- [ ] [Recommended] Are NIC ports configured with proper teaming/bonding for redundancy? (LACP for switch-dependent, active-backup for switch-independent, consider RDMA/RoCE for storage traffic on 25GbE+ NICs)
- [ ] [Recommended] Is Dell SupportAssist Enterprise configured to enable automated case creation, parts dispatch, and proactive health monitoring with Dell support?
- [ ] [Recommended] Is the server warranty level (ProSupport, ProSupport Plus, ProSupport Mission Critical) aligned with the workload SLA, with 4-hour onsite response for production systems?
- [ ] [Optional] Is Dell OpenManage Ansible Modules or Redfish API automation used for server provisioning and configuration-as-code?
- [ ] [Optional] Is iDRAC Telemetry Streaming configured to export server health metrics to Prometheus, Splunk, or other monitoring platforms via Redfish SSE?
- [ ] [Optional] Is System Lockdown Mode enabled in iDRAC to prevent unauthorized configuration changes to BIOS, iDRAC, and storage controllers?
- [ ] [Optional] Are thermal and acoustic profiles configured appropriately for the deployment environment? (default for datacenter, minimum power/low noise for office/edge deployments)

## Why This Matters

PowerEdge servers are the most widely deployed x86 server platform globally. Configuration decisions at the BIOS and firmware level directly impact performance, reliability, and supportability. Inconsistent firmware versions across a cluster cause unpredictable behavior -- vSAN and Nutanix both require validated firmware baselines. iDRAC misconfiguration (e.g., shared LOM instead of dedicated management port) creates security exposure. RAID controller mode selection (RAID vs HBA) is a one-time decision that determines whether the server can run vSAN, S2D, or Nutanix -- getting it wrong means wiping drives and starting over. OpenManage Enterprise is essential for fleet management but is often skipped in small deployments, leading to firmware drift and missed hardware alerts.

## Common Decisions (ADR Triggers)

- **Server generation and model** -- PowerEdge R760 (2U general purpose) vs R660 (1U dense) vs R960 (4-socket mission critical) vs XE9680 (8-GPU AI/ML) based on workload requirements
- **RAID controller mode** -- PERC RAID (traditional) vs HBA pass-through (vSAN, Nutanix, Ceph, S2D require direct disk access)
- **Management architecture** -- iDRAC standalone vs OpenManage Enterprise (fleet >10 servers) vs OpenManage Integration for hypervisor consoles
- **Firmware update strategy** -- OpenManage Enterprise repository-based rolling updates vs Dell System Update (DSU) scripted vs manual iDRAC updates during maintenance windows
- **NIC configuration** -- 10GbE vs 25GbE vs 100GbE, integrated LOM vs add-in PCIe, Intel vs Broadcom vs Mellanox/NVIDIA ConnectX
- **Boot architecture** -- RAID 1 local SSD boot vs Boot from SAN (FC/iSCSI) vs Boot from NVMe-oF vs SD/USB embedded (deprecated in newer generations)
- **GPU strategy** -- NVIDIA A-series/H-series/L-series selection, PCIe vs SXM form factor, MIG partitioning vs full GPU passthrough for AI/ML workloads
- **Warranty and support** -- ProSupport (next business day) vs ProSupport Plus (predictive, 4-hour) vs Mission Critical (2-hour response, dedicated TAM)

## Reference Links

- [Dell PowerEdge Server Portfolio](https://www.dell.com/en-us/shop/dell-poweredge-servers/sc/servers) -- current PowerEdge models and configurations
- [iDRAC User Guide](https://www.dell.com/support/home/en-us/product-support/product/idrac9-lifecycle-controller-v7.x-series/docs) -- iDRAC9 documentation for configuration and management
- [OpenManage Enterprise User Guide](https://www.dell.com/support/kbdoc/en-us/000176472/dell-openmanage-enterprise-user-s-guide) -- centralized server management platform documentation
- [Dell PowerEdge RAID Controller (PERC) Guide](https://www.dell.com/support/kbdoc/en-us/000178016/dell-poweredge-understanding-raid-levels-and-perc-controllers) -- RAID configuration best practices
- [Dell OpenManage Ansible Modules](https://github.com/dell/dellemc-openmanage-ansible-modules) -- infrastructure-as-code automation for PowerEdge servers
- [Dell Support Matrix for VMware](https://www.dell.com/support/kbdoc/en-us/000203498/support-matrix-for-dell-emc-vmware-solutions) -- validated firmware and driver combinations for VMware deployments

## See Also

- `general/compute.md` -- general compute architecture patterns
- `general/hardware-sizing.md` -- hardware sizing methodology
- `general/hardware-vendor-partnerships.md` -- vendor partnership and support considerations
- `providers/dell/vxrail.md` -- Dell VxRail HCI (PowerEdge-based)
- `providers/vmware/infrastructure.md` -- VMware vSphere on PowerEdge servers
- `patterns/dell-hybrid-cloud.md` -- Dell-anchored hybrid cloud pattern (Azure Arc enrollment of PowerEdge, APEX integration)
