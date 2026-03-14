# OpenStack Networking (Neutron)

## Checklist

- [ ] Is the ML2 mechanism driver selected? (OVS for mature deployments with established tooling, OVN for modern deployments needing distributed control plane and native L3/DHCP without agents, Linux Bridge for simplicity in small environments)
- [ ] Are provider networks configured for external/public connectivity using VLAN or flat type drivers, with correct `physical_network` mappings in `ml2_conf.ini` and bridge mappings on compute/network nodes?
- [ ] Are tenant self-service networks configured with VXLAN or Geneve overlay type drivers, with appropriate `vni_ranges` and `local_ip` (VTEP endpoint) settings on each node?
- [ ] Is Distributed Virtual Router (DVR) evaluated? (reduces east-west traffic hairpinning through network nodes but adds complexity -- each compute node runs L3 agent, SNAT still centralized for non-floating-IP traffic)
- [ ] Is L3 HA (VRRP-based router failover) enabled for centralized routers? (`l3_ha = True`, `max_l3_agents_per_router`, `l3_ha_net_cidr` for HA network) -- note: L3 HA and DVR can be combined in recent releases
- [ ] Are floating IP pools sized appropriately and allocated from provider network subnets, with per-project quotas set to prevent pool exhaustion?
- [ ] Are security groups configured with default-deny ingress and default-allow egress, port security enabled (`port_security_enabled = True`), and are stateful vs stateless security groups chosen per workload type?
- [ ] Is Octavia load balancing deployed? (amphora driver for full-featured L7 LB, OVN provider for lightweight L4 LB without amphora VMs, health monitors, TLS termination, connection limits)
- [ ] Is DNS integration configured via Designate? (`dns_domain` in Neutron, `extension_drivers = dns_domain_ports` in ML2, automatic PTR record creation for floating IPs)
- [ ] Are network QoS policies defined? (bandwidth limiting with `max_kbps`/`max_burst_kbps` for ingress/egress, DSCP marking for traffic classification, minimum bandwidth guarantees with placement integration)
- [ ] Are network namespaces and metadata proxies correctly functioning? (verify `dhcp-agent`, `l3-agent`, and metadata-agent connectivity -- a common failure mode where instances cannot reach 169.254.169.254)
- [ ] Is BGP dynamic routing considered for external connectivity? (`neutron-dynamic-routing` with `bgp_speaker` and `bgp_peer` for advertising tenant networks or floating IP ranges to physical routers)
- [ ] Is the MTU chain validated end-to-end? (physical network MTU minus overlay overhead -- VXLAN adds 50 bytes, Geneve adds 38+ bytes; `global_physnet_mtu`, `path_mtu`, and `advertised` settings must be consistent)
- [ ] Are allowed address pairs or trunk ports configured where needed? (trunk ports for NFV/VNF workloads requiring sub-interfaces, allowed address pairs for VRRP/keepalived within tenant networks)

## Why This Matters

Neutron architecture is the single most impactful design decision in OpenStack -- it determines east-west and north-south traffic performance, tenant isolation guarantees, and operational complexity. The ML2 mechanism driver choice (OVS vs OVN) affects every aspect of networking from DHCP to L3 routing to load balancing. OVN eliminates the need for separate L3, DHCP, and metadata agents but requires OVN-specific operational knowledge. DVR eliminates the network node bottleneck for east-west traffic but creates a distributed state problem that complicates troubleshooting. MTU misconfiguration causes mysterious packet drops and path MTU discovery failures that are notoriously difficult to diagnose in overlay networks. Security group misconfiguration is the most common cause of connectivity issues reported by tenants.

## Common Decisions (ADR Triggers)

- **ML2 mechanism driver** -- OVS (mature, well-documented, large ecosystem) vs OVN (modern, distributed control plane, native L3/DHCP/LB) vs Linux Bridge (simple, no OpenFlow knowledge needed) -- affects operational model, feature set, and scaling characteristics
- **Network topology** -- provider networks only (operator-managed, simpler, VLAN-based) vs self-service overlay networks (tenant-managed, VXLAN/Geneve) vs hybrid (provider for external, self-service for internal) -- trades operator control for tenant flexibility
- **Routing model** -- centralized L3 (simpler, network node is bottleneck) vs DVR (distributed east-west, SNAT still centralized) vs OVN distributed routing (fully distributed, requires OVN adoption) -- performance vs complexity trade-off
- **Load balancer approach** -- Octavia amphora (feature-rich L4/L7, VM-based, resource overhead) vs Octavia OVN provider (lightweight L4 only, no dedicated VMs) vs external load balancer integration (F5, HAProxy external) -- capability vs resource cost
- **IP address management** -- Neutron-managed DHCP (standard) vs external IPAM integration (Infoblox, BlueCat) via IPAM driver -- depends on enterprise IPAM requirements
- **VPN strategy** -- Neutron VPNaaS (IPsec site-to-site via StrongSwan/Libreswan) vs external VPN concentrators vs WireGuard in tenant VMs -- supportability vs flexibility
- **Network segmentation** -- VLAN (limited to 4094 segments, hardware-integrated) vs VXLAN (16M segments, requires underlay multicast or unicast) vs Geneve (extensible, OVN default) -- scale and feature requirements drive choice

## Version Notes

| Feature | Yoga (April 2022) | Zed (Oct 2022) | 2023.1 (Antelope) | 2024.1 (Caracal) |
|---|---|---|---|---|
| ML2/OVS | Supported (default) | Supported | Supported (deprecation notice) | Deprecated (migration recommended) |
| ML2/OVN | GA (recommended for new) | GA (recommended) | GA (default for new deployments) | GA (default) |
| OVN as default ML2 driver | No | No | Yes (new installs) | Yes |
| Linux Bridge | Supported | Supported | Supported (maintenance only) | Maintenance only |
| Octavia amphora driver | GA | GA | GA | GA (maintenance mode) |
| Octavia OVN provider | GA (L4 only) | GA (L4 only) | GA (L4, improved health monitors) | GA (L4, recommended for OVN deployments) |
| DVR with OVN | N/A (OVN is natively distributed) | N/A | N/A | N/A |
| Stateless security groups | Tech Preview | GA | GA | GA |
| BGP dynamic routing | GA | GA | GA | GA (improved VPN integration) |
| Network QoS minimum bandwidth | GA (placement integration) | GA | GA | GA (improved enforcement) |
| Neutron metadata via OVN | GA | GA | GA (improved reliability) | GA |
| DPDK support (OVS) | GA | GA | GA | GA (OVN also supports DPDK) |
| OVN interconnection (multi-site) | Tech Preview | GA | GA | GA (improved) |

**Key changes across releases:**
- **OVN becoming default:** OVN (Open Virtual Network) has been the recommended ML2 mechanism driver since Yoga for new deployments. Starting with 2023.1 (Antelope), OVN is the default for new installations. OVN provides distributed L3 routing, DHCP, and metadata services without separate agents, reducing operational complexity. ML2/OVS remains functional but receives only critical fixes.
- **ML2/OVS deprecation timeline:** ML2/OVS received a formal deprecation notice in 2023.1 (Antelope). It is expected to enter maintenance-only mode and eventually be removed in a future release (estimated 2025.x or 2026.x). Organizations running ML2/OVS should plan migration to OVN. The `neutron-ovn-migration-mech` tool assists with in-place migration from ML2/OVS to ML2/OVN.
- **Octavia amphora vs OVN provider:** Amphora-based load balancers deploy dedicated VMs (amphorae) for each load balancer, providing full L4/L7 functionality including TLS termination, HTTP cookie persistence, and L7 policy rules. The OVN provider is lightweight (no dedicated VMs) but limited to L4 load balancing. For OVN-based deployments, the OVN provider is simpler and lower overhead for L4 use cases. Amphora remains necessary for L7 features. Amphora entered maintenance mode in 2024.1 as the project focuses on the OVN provider.
- **Migration considerations:** Migrating from ML2/OVS to ML2/OVN requires careful planning. OVN uses Geneve encapsulation (not VXLAN), so MTU calculations change. DVR behavior differs -- OVN is natively distributed, so DVR configuration is not applicable. Security group implementation changes from iptables to OVN ACLs. The migration tool handles most conversions but downtime is required for the control plane switchover.
