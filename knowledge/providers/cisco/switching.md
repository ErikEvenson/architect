# Cisco Switching

## Scope

This file covers Cisco campus and data center switching architecture including Catalyst 9000 series (9200, 9300, 9400, 9500, 9600) for campus access/distribution/core, Nexus platform (9000, 7000, 5000, 3000) for data center switching, ACI (Application Centric Infrastructure) fabric design with APIC controllers and leaf-spine topology, vPC (virtual PortChannel) for dual-homed server connectivity, spanning tree protocol design (RPVST+, MST) and loop prevention, EVPN-VXLAN fabric for modern campus and DC overlay networks, StackWise and StackWise Virtual for switch stacking and redundancy, and SD-Access integration with DNA Center (Catalyst Center).

## Checklist

- [ ] **[Critical]** Is the switching platform selected appropriately for each tier -- Catalyst 9300/9200 for campus access, Catalyst 9500/9600 for campus core/distribution, Nexus 9000 for data center leaf/spine -- with sufficient port density, uplink bandwidth, and forwarding capacity for projected growth?
- [ ] **[Critical]** Is the spanning tree design defined -- RPVST+ (per-VLAN spanning tree, simpler but higher control plane overhead with many VLANs) vs MST (Multiple Spanning Tree, maps many VLANs to few instances, better for 100+ VLANs) -- with root bridge placement on distribution/core switches and root guard, BPDU guard, and loop guard enabled on appropriate ports?
- [ ] **[Critical]** For data center Nexus deployments, is vPC (virtual PortChannel) configured correctly between peer switches with a dedicated vPC peer-link (minimum 2x 10GbE or 2x 40GbE), vPC peer-keepalive on a separate management VRF, and orphan port design documented for single-attached devices?
- [ ] **[Critical]** For ACI fabric deployments, is the APIC cluster sized correctly (minimum 3 APICs for production, 5 for large-scale), are leaf and spine roles properly assigned, and is the ACI policy model (tenant, VRF, bridge domain, EPG, contract) designed to match the application segmentation requirements?
- [ ] **[Critical]** Is the VLAN design documented with a VLAN allocation plan, including separation of management, user data, voice, IoT/OT, and infrastructure VLANs, with no use of VLAN 1 for production traffic and native VLAN explicitly configured on all trunks?
- [ ] **[Recommended]** For EVPN-VXLAN deployments, is the underlay routing protocol (IS-IS or OSPF) configured with proper area design, are VTEP (VXLAN Tunnel Endpoints) loopback addresses planned, and is the BGP EVPN control plane designed with route reflectors at spine switches (or dedicated RR nodes for large fabrics)?
- [ ] **[Recommended]** Are first-hop redundancy protocols configured -- HSRP (Hot Standby Router Protocol) or VRRP for traditional L2/L3 boundaries, or anycast gateway for EVPN-VXLAN fabrics -- with appropriate preemption, priority, and timers to ensure sub-second failover?
- [ ] **[Recommended]** Is StackWise Virtual (Catalyst 9500/9600) or StackWise (Catalyst 9300) evaluated for switch redundancy, with awareness that SVL reduces two physical switches to one logical switch (simplifying management but creating a larger failure domain) and that dual-supervisor chassis (Catalyst 9400/9600) provide in-chassis SSO redundancy?
- [ ] **[Recommended]** Are port security features enabled -- 802.1X for user authentication, MAB (MAC Authentication Bypass) for devices that cannot do 802.1X, DHCP snooping, dynamic ARP inspection (DAI), and IP source guard -- to prevent unauthorized access and layer 2 attacks?
- [ ] **[Recommended]** Is the QoS policy defined for campus switches -- trust boundaries at access ports, DSCP/CoS marking for voice (EF/DSCP 46), video (AF41/DSCP 34), and signaling (CS3/DSCP 24) traffic, with queuing policies (WRR or CBWFQ) on uplinks to prevent voice quality degradation during congestion?
- [ ] **[Recommended]** For ACI, are multi-site and multi-pod topologies evaluated when the fabric spans multiple data centers or requires IPN (Inter-Pod Network) connectivity, with ACI Multi-Site Orchestrator (MSO/NDO) for policy consistency across sites?
- [ ] **[Optional]** Is SD-Access evaluated for campus fabric -- LISP control plane, VXLAN data plane, and CTS (Cisco TrustSec) policy plane managed through Catalyst Center (formerly DNA Center) -- providing macro and micro-segmentation without VLAN sprawl?
- [ ] **[Optional]** Is MACsec (802.1AE) encryption enabled on switch-to-switch links (downlink MACsec for access to distribution, uplink MACsec for distribution to core) for environments requiring layer 2 encryption in transit?
- [ ] **[Optional]** Is NetFlow/IPFIX or Flexible NetFlow configured on key switch interfaces for traffic visibility, capacity planning, and anomaly detection, with export to a collector (e.g., Cisco Secure Network Analytics / StealthWatch)?

## Why This Matters

Switching infrastructure forms the foundation of every enterprise network -- a misconfigured spanning tree can take down an entire campus in seconds, and a vPC design flaw can cause split-brain scenarios that corrupt data traffic. Catalyst and Nexus platforms dominate enterprise campus and data center environments respectively, but they have fundamentally different operating models (IOS-XE vs NX-OS), different redundancy mechanisms (StackWise vs vPC), and different management paradigms (CLI/Catalyst Center vs CLI/ACI APIC). Choosing the wrong spanning tree mode, failing to properly configure root bridge election, or neglecting BPDU guard on access ports are among the most common causes of network outages in enterprise environments. ACI introduces a declarative policy model that is powerful but has a steep learning curve -- misconfigured contracts can silently block traffic, and the APIC dependency means controller failure modes must be well understood (fabric continues forwarding with cached policy, but no changes can be made). EVPN-VXLAN is increasingly replacing traditional L2/L3 designs in both campus and data center, but requires BGP expertise and careful underlay design that many organizations underestimate.

## Common Decisions (ADR Triggers)

- **Traditional L2/L3 vs EVPN-VXLAN fabric** -- Traditional designs with spanning tree and HSRP are well-understood and simpler to troubleshoot but limit mobility and scale. EVPN-VXLAN provides stretched L2 domains without spanning tree, anycast gateway for optimal traffic paths, and host mobility, but requires BGP expertise and adds encapsulation overhead. Choose EVPN-VXLAN for greenfield data center and large campus; traditional for small campus or brownfield with no fabric budget.
- **ACI vs standalone Nexus** -- ACI provides centralized policy management, microsegmentation, and multi-tenancy through APIC but requires minimum 3-node APIC cluster, has a unique policy model with a learning curve, and locks you into ACI-mode Nexus 9000 switches. Standalone NX-OS Nexus is simpler, uses standard CLI/automation, and avoids APIC dependency. Choose ACI for multi-tenant data centers, service provider environments, or when application-level policy is required; standalone Nexus for simpler DC fabrics.
- **StackWise Virtual vs chassis redundancy** -- StackWise Virtual (SVL) combines two Catalyst 9500/9600 switches into one logical switch, simplifying management and eliminating spanning tree on downlinks but creating a larger blast radius. Dual-supervisor chassis (Catalyst 9400/9600) provides in-chassis redundancy with SSO/NSF. Choose SVL for distribution/core where simplified topology is valued; chassis for access aggregation where supervisor redundancy is sufficient.
- **RPVST+ vs MST** -- RPVST+ provides per-VLAN spanning tree instances (optimal path per VLAN) but does not scale well beyond 100-200 VLANs due to BPDU overhead. MST maps multiple VLANs to fewer instances (typically 2-4), scaling to thousands of VLANs. Choose RPVST+ for environments with fewer than 100 VLANs; MST for large campus or data center with hundreds of VLANs.
- **SD-Access vs traditional campus** -- SD-Access (via Catalyst Center) provides automated segmentation, policy-based access, and fabric-wide VN (Virtual Network) isolation without VLAN sprawl, but requires Catalyst Center licensing, supported hardware, and ISE integration. Traditional campus design with VLANs and ACLs is simpler and works with any hardware. Choose SD-Access for large enterprise campuses needing segmentation at scale; traditional for smaller sites or budget-constrained environments.

## Reference Links

- [Cisco Catalyst 9000 switching architecture](https://www.cisco.com/c/en/us/products/switches/catalyst-9000.html) -- Catalyst 9200/9300/9400/9500/9600 platform overview, data sheets, and deployment guides
- [Cisco Nexus 9000 series](https://www.cisco.com/c/en/us/products/switches/nexus-9000-series-switches/index.html) -- Nexus 9000 platform for data center leaf-spine and ACI fabric deployments
- [ACI design guide](https://www.cisco.com/c/en/us/solutions/collateral/data-center-virtualization/application-centric-infrastructure/white-paper-c11-737909.html) -- ACI fabric design, policy model, and multi-site architecture
- [EVPN-VXLAN campus fabric design](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9500/software/evpn-vxlan/evpn-vxlan-book.html) -- EVPN-VXLAN configuration on Catalyst 9000 series
- [vPC design and configuration guide](https://www.cisco.com/c/en/us/td/docs/dcn/nx-os/nexus9000/104x/configuration/vpc/cisco-nexus-9000-series-nx-os-vpc-configuration-guide-104x.html) -- Nexus vPC best practices and configuration
- [SD-Access design guide](https://www.cisco.com/c/en/us/td/docs/solutions/CVD/Campus/cisco-sda-design-guide.html) -- SD-Access fabric design with Catalyst Center and ISE

## See Also

- `general/networking.md` -- general networking architecture patterns
- `providers/cisco/routing.md` -- Cisco routing platforms and protocols
- `providers/cisco/wireless.md` -- Cisco wireless LAN architecture
- `providers/cisco/meraki.md` -- Cisco Meraki cloud-managed switching
