# VMware Networking

## Checklist

- [ ] Is vSphere Distributed Switch (VDS) deployed instead of vSphere Standard Switch (VSS) for centralized network configuration, network I/O control, port mirroring, NetFlow/IPFIX export, and LACP support?
- [ ] Are VMkernel adapters properly separated with dedicated port groups for management, vMotion, vSAN, Fault Tolerance logging, and NFS storage traffic, each on isolated VLANs?
- [ ] Is NSX-T (now NSX) deployed with transport zones (overlay and VLAN-backed) correctly mapped to the physical infrastructure, with TEP (Tunnel Endpoint) interfaces on a dedicated VLAN with MTU 1600+ for Geneve encapsulation?
- [ ] Are NSX Tier-0 and Tier-1 gateways architected correctly -- T0 for north-south traffic with BGP/OSPF peering to physical routers, T1 per tenant/application for east-west routing and service insertion?
- [ ] Are NSX edge nodes deployed as bare-metal (preferred for production) or as VMs with sufficient resources (8 vCPU, 32GB minimum for large form factor) in an edge cluster with active-standby or ECMP active-active configuration?
- [ ] Is Network I/O Control (NIOC) version 3 configured on VDS to guarantee bandwidth shares and reservations for traffic types (management, vMotion, vSAN, VM traffic, NFS) preventing any single traffic class from starving others during contention?
- [ ] Are NIC teaming policies set appropriately -- Route Based on Physical NIC Load (recommended for most workloads), Route Based on IP Hash (required for etherchannel/LACP), or Route Based on Originating Port (simplest) -- with explicit failover order for active/standby configurations?
- [ ] Is jumbo frames (MTU 9000) enabled end-to-end for vSAN, vMotion, NFS, and NSX TEP traffic, with confirmation that all intermediate physical switches support the MTU to avoid silent packet fragmentation?
- [ ] Are NSX segments (formerly logical switches) configured with appropriate transport zone scope, and are segment profiles (IP discovery, MAC discovery, SpoofGuard, segment security) applied to prevent ARP/MAC spoofing and IP address conflicts?
- [ ] Is NSX load balancing (NSX Advanced Load Balancer / Avi Networks) deployed for application load balancing with virtual services, pools, health monitors, and SSL termination, replacing legacy NSX-T LB which is deprecated?
- [ ] Are VPN services (IPSec site-to-site, L2 VPN for stretched networks) configured on NSX T0 gateways with IKEv2, and is NAT (SNAT/DNAT) configured on T0 or T1 gateways as appropriate for the routing topology?
- [ ] Is the physical network designed with a spine-leaf topology to support NSX overlay networking, with sufficient uplink bandwidth (25GbE minimum per host, 100GbE recommended for vSAN and converged traffic)?
- [ ] Are private VLANs (community, isolated, promiscuous) or NSX microsegmentation used for workload isolation within the same broadcast domain where required by compliance?

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
