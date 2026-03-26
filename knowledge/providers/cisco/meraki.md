# Cisco Meraki

## Scope

This file covers Cisco Meraki cloud-managed networking including MX security appliances (SD-WAN, firewall, VPN), MS switches (access, aggregation), MR wireless access points, MV smart cameras, MT sensors, dashboard management and API, licensing models (per-device, co-termination legacy), Meraki SD-WAN with AutoVPN, integration with Catalyst SD-WAN and Cisco Secure, and operational considerations for cloud-managed infrastructure.

## Checklist

- [ ] **[Critical]** Is the Meraki licensing model understood and budgeted -- per-device licensing (mandatory, network ceases to function when licenses expire), with appropriate tier selected (ENT for enterprise features, ADV/SD-WAN for advanced security and SD-WAN analytics) and license duration (1/3/5/7/10 year terms, longer terms reduce annual cost)?
- [ ] **[Critical]** Is the cloud management dependency acceptable -- all Meraki configuration, monitoring, and firmware management requires internet connectivity to the Meraki dashboard (dashboard.meraki.com); local devices continue forwarding traffic if dashboard is unreachable, but no configuration changes or monitoring are possible until connectivity is restored?
- [ ] **[Critical]** Is the MX security appliance sized correctly for the site -- throughput rating accounts for all enabled features (firewall + IDS/IPS + AMP + content filtering significantly reduces throughput vs firewall-only), VPN tunnel capacity supports the site-to-site mesh or hub-and-spoke topology, and HA (warm spare) is configured for sites requiring sub-minute failover?
- [ ] **[Critical]** Is the SD-WAN / AutoVPN topology designed -- hub-and-spoke (branch MX to data center MX), full-mesh (direct branch-to-branch tunnels via AutoVPN), or hybrid -- with VPN concentrator MX appliances at hubs sized for aggregate tunnel throughput and concurrent VPN sessions?
- [ ] **[Recommended]** Is the Meraki dashboard organization structure designed -- single organization vs multiple organizations (for MSP/multi-tenant), network naming conventions, administrator roles (full, read-only, per-network), SAML/SSO integration for dashboard authentication, and API key management for automation?
- [ ] **[Recommended]** Is the MS switch stack design appropriate -- switch stacking for simplified management (up to 8 switches in a stack), uplink redundancy to distribution/core, L3 routing capability (MS390, MS410, MS425, MS450 support static and OSPF routing), and QoS policies for voice/video traffic prioritization?
- [ ] **[Recommended]** Are traffic shaping and SD-WAN policies configured on MX appliances -- application-aware traffic shaping by category (VoIP, video, SaaS), per-client bandwidth limits, WAN uplink preferences per application (direct internet vs VPN), and flow preferences for active-active WAN with performance-based failover?
- [ ] **[Recommended]** Is the Meraki wireless design planned -- MR access point model selection (Wi-Fi 6/6E for high-density, indoor vs outdoor), RF profile tuning (channel width, minimum bitrate, band steering to 5GHz/6GHz), SSID count (limit to 3-4 per AP to minimize beacon overhead), and guest network isolation (NAT mode or bridge mode with VLAN)?
- [ ] **[Recommended]** Is the firmware upgrade strategy defined -- Meraki controls firmware releases via dashboard (scheduled maintenance windows configurable), but organizations cannot pin specific firmware versions long-term or skip updates indefinitely; test firmware on a pilot network before broader rollout, and understand that Meraki may push critical security patches outside maintenance windows?
- [ ] **[Recommended]** Is the integration with on-premises/non-Meraki networks designed -- site-to-site VPN from MX to non-Meraki VPN peers (IKEv2 IPSec, requires static IPs or DDNS), VLAN/routing integration with existing campus infrastructure, and RADIUS/LDAP integration for 802.1X authentication?
- [ ] **[Optional]** Is the Meraki API and webhook integration planned for automation -- REST API for configuration management, webhook alerts for real-time event-driven automation (e.g., device online/offline, rogue AP detection), and integration with Cisco Catalyst Center or SIEM for cross-platform visibility?
- [ ] **[Optional]** Is Meraki Insight (VPN performance monitoring, web application health) enabled for SD-WAN deployments to provide per-application latency, loss, and jitter metrics across WAN links and VPN tunnels?
- [ ] **[Optional]** Is the Meraki-to-Catalyst SD-WAN integration evaluated for organizations with both cloud-managed (Meraki) branches and controller-managed (Catalyst SD-WAN) hubs, using the Meraki-Catalyst SD-WAN interconnect for unified WAN policy?

## Why This Matters

Meraki's cloud-managed model fundamentally changes network operations -- the simplicity of dashboard management and zero-touch provisioning makes it ideal for distributed enterprises with limited on-site IT, but the cloud dependency means organizations must accept that Cisco controls firmware release timing, the dashboard is a single management plane for the entire infrastructure, and no local CLI access exists for troubleshooting beyond basic packet capture. License expiration is the most critical operational risk: unlike traditional Cisco gear that continues functioning without active support contracts, Meraki devices stop passing traffic when licenses expire, making license lifecycle management a business-critical process. AutoVPN dramatically simplifies site-to-site VPN (one-click mesh or hub-and-spoke) but the underlying routing is abstracted -- organizations accustomed to granular BGP/OSPF policy control on WAN links will find Meraki's simplified model limiting for complex routing scenarios. MX security appliance throughput ratings are particularly misleading because enabling Advanced Security (IDS/IPS, AMP, content filtering) can reduce effective throughput by 50-70% compared to firewall-only mode, making proper sizing essential.

## Common Decisions (ADR Triggers)

- **Meraki vs Catalyst (traditional Cisco)** -- Meraki provides simplicity, zero-touch provisioning, and unified cloud dashboard but limits advanced configuration (no CLI, simplified routing, cloud dependency). Catalyst/ISR provides full CLI control, advanced routing (BGP, OSPF, PBR), and offline management but requires more skilled staff and per-device configuration. Choose Meraki for distributed retail/branch with standardized configurations; Catalyst for data center, WAN edge with complex routing, or environments requiring offline management.
- **Meraki SD-WAN vs Catalyst SD-WAN** -- Meraki SD-WAN (AutoVPN with performance-based routing) is simpler to deploy and manage via dashboard, best for 50-5000 branch sites with standardized WAN. Catalyst SD-WAN (formerly Viptela) provides granular policy, application-aware routing with SLA metrics, and scales to 10,000+ sites with complex topologies. Choose Meraki SD-WAN for simplicity-first branches; Catalyst SD-WAN for performance-critical or policy-complex WANs.
- **Single organization vs multi-organization** -- Single organization simplifies administration, cross-network visibility, and licensing management. Multiple organizations provide strict administrative isolation (different admin teams, separate billing, no cross-visibility) required for MSPs or business units with separate IT governance. Choose single organization for unified enterprises; multiple organizations only when administrative isolation is a hard requirement.
- **MX HA (warm spare) vs single MX** -- Warm spare provides automatic failover (VRRP-based, typically 5-15 second failover) with a second MX at each site but doubles hardware and licensing cost. Single MX with dual WAN uplinks provides WAN redundancy without device redundancy. Choose warm spare for sites where device failure cannot tolerate truck-roll repair time; single MX with dual WAN for sites where WAN redundancy is sufficient.
- **Per-device licensing vs co-termination** -- Per-device licensing (current model) provides flexibility to add devices at any time with independent expiration dates. Co-termination (legacy, no longer available for new orgs) shared a single expiration date across all devices. All new deployments use per-device licensing; manage expiration dates carefully to avoid staggered renewals creating operational complexity.

## Reference Links

- [Meraki documentation](https://documentation.meraki.com/) -- Dashboard configuration, MX/MS/MR deployment guides, and API reference
- [Meraki MX sizing guide](https://documentation.meraki.com/MX/MX_Overview_and_Specifications) -- MX appliance throughput ratings with and without advanced security features
- [Meraki SD-WAN and AutoVPN](https://documentation.meraki.com/MX/Site-to-site_VPN/Meraki_Auto_VPN_-_Configuration_and_Troubleshooting) -- AutoVPN configuration, hub-and-spoke design, and non-Meraki VPN peering
- [Meraki API documentation](https://developer.cisco.com/meraki/api/) -- REST API reference for dashboard automation, webhook configuration, and integration
- [Meraki licensing overview](https://documentation.meraki.com/General_Administration/Licensing/Meraki_Licensing_FAQs) -- Per-device licensing model, tier comparison, and renewal management
- [Meraki and Catalyst SD-WAN integration](https://www.cisco.com/c/en/us/solutions/enterprise-networks/sd-wan/meraki-sd-wan.html) -- Integration between Meraki and Catalyst SD-WAN platforms

## See Also

- `general/networking.md` -- general networking architecture patterns
- `providers/cisco/routing.md` -- Cisco Catalyst SD-WAN and traditional WAN routing
- `providers/cisco/switching.md` -- Cisco Catalyst switching (non-Meraki campus)
- `providers/cisco/wireless.md` -- Cisco Catalyst wireless (non-Meraki enterprise wireless)
