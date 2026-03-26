# Dell VxRail HCI

## Scope

Dell VxRail hyperconverged infrastructure: cluster design and node selection (E-series entry, P-series performance, S-series storage-dense, V-series GPU-enabled, D-series dynamic), VMware VCF/vSAN integration, lifecycle management (VxRail Manager/HCI System Software), network design, cluster expansion, external storage integration, and deployment patterns for enterprise, edge, and stretched cluster use cases.

## Checklist

- [ ] [Critical] Is the correct VxRail node model selected for the workload? (E-series for ROBO/edge, P-series for general enterprise, S-series for storage-heavy workloads, V-series for GPU/VDI/AI, D-series for flexible compute/storage ratio with NVMe)
- [ ] [Critical] Is the cluster sized with a minimum of 3 nodes for standard vSAN and are compute, memory, and storage capacity validated against workload requirements with appropriate headroom (25% minimum for vSAN rebuild and HA admission control)?
- [ ] [Critical] Is the vSAN storage policy configured correctly? (FTT=1 RAID-1 mirroring for 3-4 node clusters, FTT=1 RAID-5 erasure coding for 4+ nodes for space efficiency, FTT=2 for mission-critical requiring dual-failure tolerance with 6+ nodes)
- [ ] [Critical] Is the VxRail network design validated with the correct number of VLANs? (minimum: management, vMotion, vSAN, VM traffic -- each on dedicated VLAN, 2x 25GbE or higher uplinks recommended, MTU 9000 for vSAN and vMotion)
- [ ] [Critical] Is VxRail Manager configured and operational for lifecycle management? (VxRail Manager automates firmware, driver, ESXi, vCenter, and vSAN updates as a validated bundle -- never update components individually)
- [ ] [Critical] Is vCenter Server deployed on the VxRail cluster or externally, and is the decision documented? (internal vCenter is simpler but creates a chicken-and-egg dependency; external vCenter is recommended for multi-cluster and VCF deployments)
- [ ] [Recommended] Is VxRail deployed as part of VMware Cloud Foundation (VCF) for enterprise workloads requiring SDDC Manager, NSX, and full VMware stack lifecycle management?
- [ ] [Recommended] Is the cluster configured with a witness node or stretched cluster topology if deploying across two sites for metro high availability? (stretched clusters require <5ms RTT latency between sites and a witness at a third site)
- [ ] [Recommended] Are vSAN disk groups or storage pools configured correctly? (hybrid: 1 cache SSD + capacity HDDs per disk group, all-flash: cache tier + capacity tier NVMe/SSD, all-NVMe single tier is preferred for new deployments)
- [ ] [Recommended] Is Dell CloudIQ for VxRail enabled for proactive health scoring, capacity forecasting, and anomaly detection across the HCI fleet?
- [ ] [Recommended] Is external storage (PowerStore, PowerScale) integrated via vSphere datastores if workloads require capacity or performance beyond what vSAN provides? (iSCSI/NFS for PowerStore, NFS for PowerScale)
- [ ] [Recommended] Is the VxRail cluster connected to Dell Secure Connect Gateway (formerly SRS) for automated support case creation and log collection?
- [ ] [Recommended] Are vSphere HA and DRS configured appropriately? (HA admission control reserving capacity for at least 1 node failure, DRS in fully automated mode for load balancing, VM-host affinity rules for licensing compliance)
- [ ] [Optional] Is VxRail deployed at the edge using 2-node configurations with an external witness for remote office/branch office use cases?
- [ ] [Optional] Is vSAN Data-at-Rest Encryption (D@RE) or Data-in-Transit Encryption enabled for compliance requirements? (D@RE requires KMS server, imposes ~5-10% CPU overhead)
- [ ] [Optional] Is HCI Mesh configured to share vSAN storage capacity between VxRail clusters, avoiding siloed storage while maintaining separate compute domains?
- [ ] [Optional] Is vSAN File Services enabled to provide native NFS/SMB file shares directly from the vSAN datastore without requiring a separate NAS appliance?

## Why This Matters

VxRail is the only jointly engineered HCI platform between Dell and VMware (Broadcom), meaning lifecycle management is tightly integrated -- VxRail Manager updates the entire stack (firmware, drivers, ESXi, vSAN, vCenter) as a single validated bundle. This eliminates the compatibility matrix pain of standalone vSAN on generic hardware, but it requires strict adherence to VxRail Manager for all updates. The most common failure pattern is manually updating a component (e.g., ESXi patch, firmware) outside VxRail Manager, which breaks the validated state and voids support. Network misconfiguration (wrong MTU, missing VLANs, insufficient bandwidth) causes vSAN performance degradation and intermittent disconnects that are difficult to diagnose. The FTT and RAID policy decision has a massive impact on usable capacity -- RAID-1 FTT=1 uses 2x raw capacity while RAID-5 FTT=1 uses only 1.33x, but RAID-5 requires minimum 4 nodes and has higher write amplification.

## Common Decisions (ADR Triggers)

- **Node model selection** -- E/P/S/V/D series based on workload profile (compute-heavy, storage-heavy, GPU, balanced)
- **VCF vs standalone** -- VMware Cloud Foundation (enterprise SDDC with NSX, SDDC Manager) vs standalone VxRail (simpler, vSphere + vSAN only) based on scale and requirements
- **vSAN storage policy** -- RAID-1 mirroring (simple, 2x overhead) vs RAID-5 erasure coding (efficient, 1.33x overhead) vs RAID-6 (2-failure tolerance, 1.5x overhead)
- **vCenter placement** -- Internal (on-cluster, simpler) vs external (management cluster or physical, recommended for multi-cluster) -- impacts VCF compatibility
- **Network architecture** -- 2x 25GbE (minimum for modern workloads) vs 2x 100GbE (large clusters, high bandwidth) vs 4x 25GbE (dedicated storage + compute networks)
- **Cluster topology** -- Single-site cluster vs stretched cluster (metro HA) vs 2-node edge -- each has different network and witness requirements
- **External storage integration** -- VxRail-only vSAN (simpler) vs VxRail + PowerStore (additional block/file capacity) vs VxRail + PowerScale (scale-out NAS) based on capacity and performance needs
- **Encryption strategy** -- vSAN D@RE with external KMS vs self-encrypting drives (SED) vs no encryption -- compliance requirements drive this decision

## Reference Links

- [Dell VxRail Documentation](https://www.dell.com/support/home/en-us/product-support/product/dell-vxrail/docs) -- official VxRail administration and deployment guides
- [VxRail Planning Guide](https://infohub.delltechnologies.com/en-us/t/vxrail/) -- Dell InfoHub with sizing, networking, and deployment best practices
- [VxRail Network Guide](https://www.dell.com/support/kbdoc/en-us/000065


/vxrail-network-guide) -- network design and VLAN configuration for VxRail
- [VCF on VxRail Guide](https://docs.vmware.com/en/VMware-Cloud-Foundation/index.html) -- VMware Cloud Foundation deployment on VxRail
- [VxRail Sizing Tool](https://vxrailsizing.dell.com/) -- Dell VxRail interactive sizing and configuration tool
- [VxRail Support Matrix](https://www.dell.com/support/kbdoc/en-us/000021


/vxrail-support-matrix) -- validated software and hardware compatibility matrix

## See Also

- `providers/dell/poweredge.md` -- underlying Dell PowerEdge server hardware
- `providers/dell/powerstore.md` -- external storage integration with VxRail
- `providers/vmware/infrastructure.md` -- VMware vSphere architecture
- `providers/vmware/vcf-sddc-manager.md` -- VCF lifecycle management
- `providers/vmware/storage.md` -- vSAN storage policies and configuration
- `general/hardware-sizing.md` -- hardware sizing methodology
