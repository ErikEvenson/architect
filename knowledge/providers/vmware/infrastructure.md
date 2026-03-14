# VMware Infrastructure

## Checklist

- [ ] Is vCenter Server deployed as the centralized management plane, with an appropriately sized VCSA (vCenter Server Appliance) for the inventory scale?
- [ ] Are ESXi hosts configured with redundant NICs, proper NTP, syslog forwarding, and lockdown mode enabled for security?
- [ ] Is vSphere DRS (Distributed Resource Scheduler) enabled with appropriate automation level (fully automated for production, partially for sensitive workloads) and VM-host affinity rules?
- [ ] Is vSphere HA (High Availability) configured with admission control reserving capacity for host failures, and with VM restart priority and response to isolation set correctly?
- [ ] Is vSAN configured with the appropriate storage policy? (FTT=1 RAID-1 for standard, FTT=2 RAID-6 for production, deduplication and compression for all-flash)
- [ ] Is vSAN stretched cluster or HCI Mesh evaluated for multi-site resilience or capacity disaggregation?
- [ ] Is NSX deployed for network virtualization, providing distributed firewall, microsegmentation, load balancing, and VPN without physical network changes?
- [ ] Are NSX security policies configured with a zero-trust microsegmentation model using VM tags, groups, and context-aware rules?
- [ ] Is vSphere Lifecycle Manager (vLCM) used for ESXi host image management with desired state configuration and firmware baselines?
- [ ] Is VMware Tanzu (TKG/TKGS) deployed for Kubernetes workloads with vSphere namespaces, VM classes, and storage policies?
- [ ] Is HCX evaluated for workload migration (bulk, vMotion, replication-assisted) between on-premises and cloud (VMware Cloud on AWS, Azure VMware Solution)?
- [ ] Are VM templates and content libraries used for standardized VM provisioning with OVF properties and customization specs?
- [ ] Is vSphere distributed switch (VDS) used instead of standard switches for centralized network configuration, NIOC, and port mirroring?
- [ ] Are resource pools and VM resource limits/reservations configured to prevent noisy neighbor issues without over-committing?
- [ ] Is vRealize Operations (Aria Operations) or equivalent deployed for capacity planning, cost analysis, and performance optimization?

## Why This Matters

VMware remains the most widely deployed virtualization platform in enterprise datacenters. vSphere HA and DRS configuration directly determines availability during host failures. vSAN storage policy misconfiguration can result in data loss during simultaneous failures. NSX transforms physical network dependency into software-defined policies but adds operational complexity. Tanzu bridges traditional VM workloads and modern Kubernetes, but requires careful resource planning. Licensing changes (Broadcom acquisition) significantly impact cost planning.

## Common Decisions (ADR Triggers)

- **vSAN vs external storage** -- hyperconverged simplicity vs dedicated SAN/NAS (Pure, NetApp, Dell), performance and capacity independence
- **NSX vs physical firewalls** -- software-defined microsegmentation vs traditional perimeter firewalls, operational skills
- **Tanzu variant** -- TKG (standalone Kubernetes) vs TKGS (vSphere-integrated supervisor) vs upstream Kubernetes
- **DRS automation level** -- fully automated vs manual recommendations, DRS groups and rules for compliance
- **HA admission control** -- percentage-based vs slot-based vs dedicated failover hosts
- **Licensing model** -- VMware Cloud Foundation (VCF) bundle vs a la carte vSphere + vSAN + NSX, Broadcom subscription changes
- **Migration strategy** -- HCX for cloud mobility vs traditional P2V/V2V, VMware Cloud on AWS vs Azure VMware Solution
- **Storage policy** -- RAID-1 mirroring (performance, 2x capacity) vs RAID-5/6 erasure coding (efficiency, lower write performance)

## Reference Architectures

- [VMware Validated Solutions](https://core.vmware.com/vmware-validated-solutions) -- tested and validated architectures for VCF, private cloud, and edge deployments
- [VMware Cloud Foundation Architecture Guide](https://core.vmware.com/resource/vmware-cloud-foundation-architecture-guide) -- reference architecture for the full SDDC stack including vSphere, vSAN, NSX, and Aria
- [VMware vSAN Design Guide](https://core.vmware.com/resource/vmware-vsan-design-guide) -- validated design for hyper-converged storage including sizing, fault domains, and stretched clusters
- [VMware NSX Reference Design Guide](https://communities.vmware.com/t5/VMware-NSX/ct-p/3200) -- reference architecture for microsegmentation, distributed firewall, and multi-site networking
- [VMware Tanzu Reference Architecture](https://docs.vmware.com/en/VMware-Tanzu/services/tanzu-reference-architecture/GUID-reference-designs-index.html) -- validated designs for Kubernetes on vSphere with Tanzu namespaces and VM classes
