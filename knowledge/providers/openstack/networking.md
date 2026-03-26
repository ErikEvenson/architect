# OpenStack Networking (Neutron)

## Scope

Covers Neutron networking configuration: ML2 mechanism drivers (OVN, OVS, Linux Bridge), provider and self-service networks, DVR, L3 HA, floating IPs, security groups, Octavia load balancing, Designate DNS integration, network QoS, BGP dynamic routing, trunk ports, and MTU configuration.

## Checklist

- [ ] **[Critical]** Is the ML2 mechanism driver selected? (OVN recommended for all new deployments; OVS deprecated since 2023.1 with removal planned for the release cycle following 2025.2 Flamingo -- migrate to OVN; Linux Bridge for simplicity in small environments, maintenance-only)
- [ ] **[Critical]** Are provider networks configured for external/public connectivity using VLAN or flat type drivers, with correct `physical_network` mappings in `ml2_conf.ini` and bridge mappings on compute/network nodes?
- [ ] **[Critical]** Are security groups configured with default-deny ingress and default-allow egress, port security enabled (`port_security_enabled = True`), and are stateful vs stateless security groups chosen per workload type?
- [ ] **[Critical]** Is the MTU chain validated end-to-end? (physical network MTU minus overlay overhead -- VXLAN adds 50 bytes, Geneve adds 38+ bytes; `global_physnet_mtu`, `path_mtu`, and `advertised` settings must be consistent)
- [ ] **[Recommended]** Are tenant self-service networks configured with VXLAN or Geneve overlay type drivers, with appropriate `vni_ranges` and `local_ip` (VTEP endpoint) settings on each node?
- [ ] **[Recommended]** Is Distributed Virtual Router (DVR) evaluated? (Not applicable for OVN which is natively distributed; for legacy OVS deployments: reduces east-west traffic hairpinning but adds complexity)
- [ ] **[Recommended]** Is L3 HA (VRRP-based router failover) enabled for centralized routers? (`l3_ha = True`, `max_l3_agents_per_router`, `l3_ha_net_cidr` for HA network) -- note: L3 HA and DVR can be combined; not needed with OVN
- [ ] **[Recommended]** Are floating IP pools sized appropriately and allocated from provider network subnets, with per-project quotas set to prevent pool exhaustion?
- [ ] **[Recommended]** Is Octavia load balancing deployed? (OVN provider for lightweight L4 LB recommended; amphora driver for full-featured L7 LB when needed; health monitors, TLS termination, connection limits)
- [ ] **[Recommended]** Are network QoS policies defined? (bandwidth limiting with `max_kbps`/`max_burst_kbps` for ingress/egress, DSCP marking for traffic classification, minimum bandwidth guarantees with placement integration)
- [ ] **[Recommended]** Are network namespaces and metadata proxies correctly functioning? (verify `dhcp-agent`, `l3-agent`, and metadata-agent connectivity -- a common failure mode where instances cannot reach 169.254.169.254)
- [ ] **[Optional]** Is DNS integration configured via Designate? (`dns_domain` in Neutron, `extension_drivers = dns_domain_ports` in ML2, automatic PTR record creation for floating IPs)
- [ ] **[Optional]** Is BGP dynamic routing considered for external connectivity? (`neutron-dynamic-routing` with `bgp_speaker` and `bgp_peer` for advertising tenant networks or floating IP ranges to physical routers)
- [ ] **[Optional]** Are allowed address pairs or trunk ports configured where needed? (trunk ports for NFV/VNF workloads requiring sub-interfaces, allowed address pairs for VRRP/keepalived within tenant networks)

## Why This Matters

Neutron architecture is the single most impactful design decision in OpenStack -- it determines east-west and north-south traffic performance, tenant isolation guarantees, and operational complexity. The ML2 mechanism driver choice (OVS vs OVN) affects every aspect of networking from DHCP to L3 routing to load balancing. OVN eliminates the need for separate L3, DHCP, and metadata agents but requires OVN-specific operational knowledge. DVR eliminates the network node bottleneck for east-west traffic but creates a distributed state problem that complicates troubleshooting. MTU misconfiguration causes mysterious packet drops and path MTU discovery failures that are notoriously difficult to diagnose in overlay networks. Security group misconfiguration is the most common cause of connectivity issues reported by tenants.

## Common Decisions (ADR Triggers)

- **ML2 mechanism driver** -- OVN (recommended default since 2023.1, distributed control plane, native L3/DHCP/LB) vs OVS (deprecated since 2023.1, removal planned after 2025.2) vs Linux Bridge (maintenance-only, no OpenFlow knowledge needed) -- affects operational model, feature set, and scaling characteristics
- **Network topology** -- provider networks only (operator-managed, simpler, VLAN-based) vs self-service overlay networks (tenant-managed, VXLAN/Geneve) vs hybrid (provider for external, self-service for internal) -- trades operator control for tenant flexibility
- **Routing model** -- centralized L3 (simpler, network node is bottleneck) vs DVR (distributed east-west, SNAT still centralized) vs OVN distributed routing (fully distributed, requires OVN adoption) -- performance vs complexity trade-off
- **Load balancer approach** -- Octavia OVN provider (lightweight L4 only, no dedicated VMs, recommended) vs Octavia amphora (feature-rich L4/L7, VM-based, resource overhead) vs external load balancer integration (F5, HAProxy external) -- capability vs resource cost
- **IP address management** -- Neutron-managed DHCP (standard) vs external IPAM integration (Infoblox, BlueCat) via IPAM driver -- depends on enterprise IPAM requirements
- **VPN strategy** -- Neutron VPNaaS (IPsec site-to-site via StrongSwan/Libreswan) vs external VPN concentrators vs WireGuard in tenant VMs -- supportability vs flexibility
- **Network segmentation** -- VLAN (limited to 4094 segments, hardware-integrated) vs VXLAN (16M segments, requires underlay multicast or unicast) vs Geneve (extensible, OVN default) -- scale and feature requirements drive choice

## Version Notes

| Feature | Pike (16) Oct 2017 | Queens (17) Feb 2018 | Rocky (18) Aug 2018 | Stein (19) Apr 2019 | Train (20) Oct 2019 | Ussuri (21) May 2020 | Victoria (22) Oct 2020 | Wallaby (23) Apr 2021 | Xena (24) Oct 2021 | Yoga (25) Mar 2022 | Zed (26) Oct 2022 | 2023.1 Antelope (27) | 2023.2 Bobcat (28) | 2024.1 Caracal (29) | 2024.2 Dalmatian (30) | 2025.1 Epoxy (31) | 2025.2 Flamingo (32) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ML2/OVS | Default | Default | Default | Default | Default | Default | Default | Default | Default | Supported (default) | Supported | Supported (deprecation notice) | Deprecation notice | Deprecated (migration recommended) | Deprecated | Deprecated (removal timeline published) | Deprecated (removal planned next cycle) |
| ML2/OVN | Not available | Not available | Tech Preview | Tech Preview | GA | GA | GA (improved) | GA | GA | GA (recommended for new) | GA (recommended) | GA (default for new) | GA (default) | GA (default) | GA (default) | GA (default, OVN 24.03+) | GA (default, OVN 24.09+ required) |
| Linux Bridge | Supported | Supported | Supported | Supported | Supported | Supported | Supported | Supported | Supported | Supported | Supported | Maintenance only | Maintenance only | Maintenance only | Maintenance only | Maintenance only | Maintenance only |
| Trunk ports | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Network segments | GA | Improved (segment ranges) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Port forwarding | Not available | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| DVR (distributed routing) | GA | GA (improved) | GA | GA | GA | GA (L3 HA + DVR) | GA | GA | GA | GA | GA | GA | GA | GA | N/A (OVN is default) | N/A (OVN is default) | N/A (OVN is default) |
| Neutron LBaaS v2 | Supported (deprecated) | Deprecated | Removed | Removed | Removed | Removed | Removed | Removed | Removed | Removed | Removed | Removed | Removed | Removed | Removed | Removed | Removed |
| Octavia (standalone LB) | Incubated | GA | GA | GA (flavors, TLS) | GA (amphora HA) | GA | GA (improved L7) | GA (provider framework) | GA | GA | GA | GA | GA | GA (amphora maintenance mode) | GA | GA | GA |
| Octavia OVN provider | Not available | Not available | Not available | Not available | Not available | Tech Preview | Tech Preview | GA (L4 only) | GA (L4) | GA (L4) | GA (L4) | GA (L4, health monitors) | GA | GA (L4, recommended) | GA | GA (improved health monitors) | GA |
| Stateless security groups | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Not available | Tech Preview | Tech Preview | GA | GA | GA | GA | GA | GA | GA |
| BGP dynamic routing | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA (improved VPN) | GA | GA | GA |
| Network QoS (bandwidth) | GA | GA | GA | GA (minimum bandwidth) | GA | GA (placement integration) | GA | GA | GA | GA (placement) | GA | GA | GA | GA (improved enforcement) | GA | GA (OVN QoS improvements) | GA |
| Network segment ranges | Not available | Introduced | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Neutron metadata via OVN | N/A | N/A | N/A | Tech Preview | GA | GA | GA | GA | GA | GA | GA | GA (improved reliability) | GA | GA | GA | GA | GA |
| DPDK support (OVS) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA (OVN also DPDK) | GA | GA (OVN DPDK improvements) | GA |
| OVN interconnection (multi-site) | N/A | N/A | N/A | N/A | N/A | N/A | Not available | Tech Preview | Tech Preview | Tech Preview | GA | GA | GA | GA (improved) | GA | GA (improved routing) | GA |

**Key changes across releases:**
- **Trunk ports (Pike+):** Trunk ports were introduced in Pike, enabling NFV/VNF workloads to use sub-interfaces (VLAN-tagged sub-ports) on a single Neutron port. This is essential for virtual network functions that require multiple network segments on a single NIC.
- **Network segment ranges (Queens+):** Queens introduced configurable network segment ranges, allowing operators to manage VLAN/VXLAN/GRE segment ID allocation ranges through the API rather than configuration files.
- **Port forwarding (Rocky+):** Rocky introduced port forwarding (floating IP port forwarding), allowing multiple services on different internal IPs to share a single floating IP by mapping specific ports. This reduces floating IP consumption.
- **Neutron LBaaS to Octavia migration:** Neutron LBaaS v2 was deprecated in Pike and removed in Rocky. Octavia became the standalone load balancing project, initially using amphora (VM-based) drivers. Octavia added TLS termination and flavor support in Stein, and amphora active-standby HA in Train.
- **OVS to OVN migration timeline:** OVN was introduced as a tech preview in Rocky, reached GA in Train, became recommended for new deployments in Yoga, became the default for new installs in 2023.1 (Antelope), and ML2/OVS received formal deprecation notice in 2023.1. In 2025.1 (Epoxy), a removal timeline was published for ML2/OVS. In 2025.2 (Flamingo), OVN 24.09+ is required and ML2/OVS removal is planned for the next release cycle. Organizations running ML2/OVS must migrate to OVN using the `neutron-ovn-migration-mech` tool.
- **DVR evolution:** DVR matured through Pike-Ussuri with improvements to L3 HA + DVR combined mode (Ussuri). With OVN becoming the default, DVR configuration is not applicable -- OVN is natively distributed. Legacy DVR on OVS remains functional but is deprecated along with ML2/OVS.
- **Octavia amphora vs OVN provider:** Amphora-based load balancers provide full L4/L7 functionality including TLS termination and L7 policy rules. The OVN provider (GA in Wallaby) is lightweight (no dedicated VMs) but limited to L4. Amphora entered maintenance mode in 2024.1 as the project focuses on the OVN provider. OVN provider health monitor improvements in 2025.1 (Epoxy).
- **Migration considerations:** Migrating from ML2/OVS to ML2/OVN requires careful planning. OVN uses Geneve encapsulation (not VXLAN), so MTU calculations change. DVR behavior differs -- OVN is natively distributed. Security group implementation changes from iptables to OVN ACLs. The migration tool handles most conversions but downtime is required for the control plane switchover.
- **Epoxy (2025.1) networking changes:** ML2/OVS removal timeline published -- organizations must begin migration planning. OVN QoS improvements for bandwidth enforcement. OVN DPDK performance improvements. OVN interconnection routing improvements for multi-site deployments.
- **Flamingo (2025.2) networking changes:** OVN 24.09+ required as minimum version. ML2/OVS removal planned for the next release cycle. Continued OVN provider improvements for Octavia health monitors.

## Reference Links

- [Neutron documentation](https://docs.openstack.org/neutron/latest/) -- Neutron networking architecture, plugins, and configuration
- [Neutron networking guide](https://docs.openstack.org/neutron/latest/admin/index.html) -- provider networks, self-service networks, routers, and ML2 plugin configuration
- [OVN integration with Neutron](https://docs.openstack.org/neutron/latest/admin/ovn/index.html) -- OVN-based networking for OpenStack deployment

## See Also

- `general/networking.md` -- general networking architecture patterns
- `providers/openstack/infrastructure.md` -- OpenStack infrastructure overview
- `providers/openstack/security.md` -- security groups and network access controls
- `providers/openstack/compute.md` -- Nova instance networking integration
