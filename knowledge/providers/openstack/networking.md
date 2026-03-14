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
