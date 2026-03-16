# VMware Networking

## Scope

This document covers VMware networking including vSphere Distributed Switch (VDS), NSX overlay and VLAN networking, Tier-0/Tier-1 gateways, edge nodes, NIOC, NIC teaming, NSX load balancing (NSX ALB), VPN, and physical network design considerations.

## Checklist

- [ ] **[Recommended]** Is vSphere Distributed Switch (VDS) deployed instead of vSphere Standard Switch (VSS) for centralized network configuration, network I/O control, port mirroring, NetFlow/IPFIX export, and LACP support?
- [ ] **[Critical]** Are VMkernel adapters properly separated with dedicated port groups for management, vMotion, vSAN, Fault Tolerance logging, and NFS storage traffic, each on isolated VLANs?
- [ ] **[Critical]** Is NSX deployed with transport zones (overlay and VLAN-backed) correctly mapped to the physical infrastructure, with TEP (Tunnel Endpoint) interfaces on a dedicated VLAN with MTU 1600+ for Geneve encapsulation?
- [ ] **[Critical]** Are NSX Tier-0 and Tier-1 gateways architected correctly -- T0 for north-south traffic with BGP/OSPF peering to physical routers, T1 per tenant/application for east-west routing and service insertion?
- [ ] **[Critical]** Are NSX edge nodes deployed as bare-metal (preferred for production) or as VMs with sufficient resources (8 vCPU, 32GB minimum for large form factor) in an edge cluster with active-standby or ECMP active-active configuration?
- [ ] **[Recommended]** Is Network I/O Control (NIOC) version 3 configured on VDS to guarantee bandwidth shares and reservations for traffic types (management, vMotion, vSAN, VM traffic, NFS) preventing any single traffic class from starving others during contention?
- [ ] **[Recommended]** Are NIC teaming policies set appropriately -- Route Based on Physical NIC Load (recommended for most workloads), Route Based on IP Hash (required for etherchannel/LACP), or Route Based on Originating Port (simplest) -- with explicit failover order for active/standby configurations?
- [ ] **[Recommended]** Is jumbo frames (MTU 9000) enabled end-to-end for vSAN, vMotion, NFS, and NSX TEP traffic, with confirmation that all intermediate physical switches support the MTU to avoid silent packet fragmentation?
- [ ] **[Recommended]** Are NSX segments (formerly logical switches) configured with appropriate transport zone scope, and are segment profiles (IP discovery, MAC discovery, SpoofGuard, segment security) applied to prevent ARP/MAC spoofing and IP address conflicts?
- [ ] **[Recommended]** Is NSX load balancing (NSX Advanced Load Balancer / Avi Networks) deployed for application load balancing with virtual services, pools, health monitors, and SSL termination, replacing legacy NSX-T LB which was removed in NSX 4.x?
- [ ] **[Optional]** Are VPN services (IPSec site-to-site, L2 VPN for stretched networks) configured on NSX T0 gateways with IKEv2, and is NAT (SNAT/DNAT) configured on T0 or T1 gateways as appropriate for the routing topology?
- [ ] **[Recommended]** Is the physical network designed with a spine-leaf topology to support NSX overlay networking, with sufficient uplink bandwidth (25GbE minimum per host, 100GbE recommended for vSAN and converged traffic)?
- [ ] **[Optional]** Are private VLANs (community, isolated, promiscuous) or NSX microsegmentation used for workload isolation within the same broadcast domain where required by compliance?

## Why This Matters

Networking misconfiguration is the leading cause of vSphere outages that affect multiple workloads simultaneously. VDS provides consistency and advanced features but a misconfiguration propagates across all hosts in the datacenter, making changes higher-risk than VSS. NSX overlay networking eliminates physical network change dependencies but adds an abstraction layer that complicates troubleshooting -- packet captures must account for Geneve encapsulation, and MTU mismatches on TEP interfaces cause intermittent, difficult-to-diagnose packet drops. NIOC prevents vMotion or vSAN resyncs from saturating links and impacting VM traffic, but only when reservations are properly sized. NSX edge node sizing directly determines north-south throughput -- undersized edge VMs become the bottleneck for all external traffic. NIC teaming policy mismatches between VDS and physical switches cause intermittent connectivity and are among the hardest network issues to diagnose.

## Common Decisions (ADR Triggers)

- **VDS vs VSS** -- VDS for centralized management, NIOC, LACP, and NetFlow vs VSS for simplicity in small environments or where VDS licensing is unavailable; VDS is required for NSX
- **NSX vs physical network segmentation** -- NSX for software-defined microsegmentation, multi-tenancy, and cloud-like networking vs VLANs and physical firewalls for environments without NSX skills or licensing
- **NSX edge deployment** -- bare-metal edge nodes for maximum throughput and consistent performance vs VM-based edges for flexibility and lower hardware cost; bare-metal edges cannot be vMotioned
- **T0 gateway routing mode** -- active-standby with stateful failover for NAT/firewall/VPN services vs ECMP active-active for maximum throughput without stateful services
- **NIC teaming policy** -- Route Based on Physical NIC Load (best general-purpose distribution) vs IP Hash (required for LACP but less granular) vs explicit failover (simplest, active/standby)
- **NSX ALB vs third-party load balancers** -- NSX ALB (Avi) for integrated VMware ecosystem, auto-discovery of pool members, and GSLB vs F5/Citrix for existing investment and advanced iRules/policies
- **Jumbo frames vs standard MTU** -- jumbo frames (9000) for vSAN, vMotion, and NFS performance gains (15-20% throughput improvement) vs standard MTU (1500) for simplicity and compatibility; partial jumbo frame deployment causes silent failures
- **Overlay vs VLAN-backed segments** -- overlay (Geneve) for scalability beyond 4094 VLANs and decoupling from physical network vs VLAN-backed for low-latency, no encapsulation overhead, and physical device integration

## Version Notes

| Feature | NSX-T 3.x (3.2) | NSX 4.x (4.1+) | NSX 9.x / VCF 9.0 |
|---|---|---|---|
| Product naming | NSX-T Data Center | NSX (rebranded, dropped "-T") | NSX 9.x (version aligned with VCF 9.0) |
| Manager mode (imperative API) | Supported | Deprecated (removal planned) | **Removed** (Policy mode only) |
| Policy mode (declarative API) | GA (recommended) | GA (required for new features) | GA (sole management interface) |
| Distributed Firewall (DFW) | GA | GA (improved rule processing, Malware Prevention) | GA (enhanced) |
| DFW Malware Prevention | Not available | GA (NSX 4.1+, distributed file inspection) | GA |
| Gateway Firewall | GA | GA (URL filtering, IDS/IPS improvements) | GA |
| NSX ALB (Avi Networks) | GA (separate deployment) | GA (tighter integration, NSX 4.x aware) | GA |
| Legacy NSX-T LB | Deprecated | Removed (use NSX ALB) | Removed |
| NSX Security Intelligence | NSX Intelligence (traffic flow analysis) | NSX Intelligence (improved recommendations) | **Renamed to Security Intelligence** |
| NSX Application Platform | GA | GA | **EOL May 2026** (plan migration) |
| Project-based multi-tenancy | Not available | GA (NSX 4.1+, delegated admin per project) | GA |
| VPC (Virtual Private Cloud) | Not available | GA (NSX 4.1+, self-service networking) | GA |
| Online Diagnostic System | Not available | GA (NSX 4.0+, built-in troubleshooting) | GA |
| Federation (multi-site) | GA | GA (improved cross-site policy sync) | GA |
| DPU-based acceleration | Not available | GA (NSX on DPU for SmartNIC offload) | GA (enhanced) |
| IPv6 overlay | Not available | GA (NSX 4.1+) | GA |

**Key changes in NSX 9.x / VCF 9.0:**
- **Version alignment:** NSX jumped from 4.x to 9.x to align with VCF 9.0 unified versioning. There is no NSX 5.x through 8.x.
- **NSX Intelligence renamed to Security Intelligence:** The traffic flow analysis and policy recommendation feature formerly known as NSX Intelligence is now called NSX Security Intelligence in NSX 9.x.
- **Manager mode removed:** Manager mode (the imperative API) is fully removed in NSX 9.x. Only Policy mode is supported. Organizations must complete migration from Manager mode before upgrading.
- **NSX Application Platform EOL:** The NSX Application Platform reaches end of life in May 2026. Features that depended on the Application Platform (NSX Security Intelligence, NSX Malware Prevention, NSX Network Detection and Response) are being re-architected. Plan accordingly for environments relying on these capabilities.

**Key differences between NSX-T 3.x and NSX 4.x:**
- **Policy vs Manager mode:** NSX 4.x strongly pushes Policy mode as the sole management interface. Manager mode (the imperative, object-based API from NSX-T 3.x) is deprecated. New features are only available in Policy mode. Organizations still using Manager mode must migrate before upgrading to future NSX releases. The migration coordinator tool assists with converting Manager objects to Policy objects.
- **Distributed Firewall improvements:** NSX 4.x adds distributed Malware Prevention, which inspects files at the hypervisor level without agents in the guest. DFW rule processing is more efficient with improved context-aware grouping and identity-based firewall rules.
- **NSX ALB integration:** The legacy NSX-T load balancer (Tier-1 LB) was deprecated in NSX-T 3.x and removed in NSX 4.x. NSX Advanced Load Balancer (Avi Networks) is now the only supported load balancing solution. NSX 4.x provides tighter integration between NSX ALB and NSX networking/security policies.
- **Project-based multi-tenancy and VPC:** NSX 4.1 introduced Projects and VPCs, enabling delegated network administration. Tenant administrators can manage their own network segments, security policies, and NAT rules within a Project without affecting other tenants. This is a significant improvement for service provider and large enterprise use cases.
- **DPU-based acceleration:** NSX 4.x supports offloading distributed firewall and overlay networking to DPUs (SmartNICs), reducing host CPU overhead for networking operations.
