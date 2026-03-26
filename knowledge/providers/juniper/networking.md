# Juniper Networks

## Scope

This file covers **Juniper Networks switching, routing, security, and fabric management** including Junos OS configuration and operations, EX-series access and aggregation switches, QFX-series data center switches, SRX-series firewalls and security appliances, MX-series edge and core routers, Apstra intent-based fabric management, Mist AI cloud-driven operations, EVPN-VXLAN fabric design, Virtual Chassis multi-switch clustering, Junos Space network management, and licensing models (perpetual, subscription, and Flex). It does not cover general networking architecture; for that, see `general/networking.md`.

## Checklist

- [ ] **[Critical]** Select Junos OS variant appropriate to the platform — Junos OS Evolved (EVO) runs on QFX5700/QFX5130/PTX and uses a Linux-based architecture; classic Junos runs on EX/SRX/MX and uses a FreeBSD-based architecture — mixing assumptions between variants causes operational confusion
- [ ] **[Critical]** Design EVPN-VXLAN fabric topology with clearly defined spine, leaf, and optional super-spine roles — Juniper supports both ERB (Edge-Routed Bridging) and CRB (Centrally-Routed Bridging) models, and the choice determines where L3 gateway and inter-VNI routing occur
- [ ] **[Critical]** Size QFX switch models based on required port density, line-rate throughput, and buffer depth — QFX5120 (campus/small DC), QFX5130 (high-density 25/100G), QFX5700 (400G spine) have significantly different ASIC capabilities and table sizes
- [ ] **[Critical]** Configure dual Routing Engines (RE) on MX and high-end QFX platforms with Graceful Routing Engine Switchover (GRES) and Nonstop Active Routing (NSR) to maintain forwarding during RE failover
- [ ] **[Critical]** Deploy Apstra for data center fabric management when operating EVPN-VXLAN at scale — Apstra provides intent-based networking with automated configuration, compliance validation, and root cause analysis across multi-vendor fabrics
- [ ] **[Critical]** Plan SRX firewall sizing based on inspected throughput with AppSecure (AppID, AppTrack, AppFW) and IDP/IPS enabled — marketing throughput numbers reflect stateless traffic, not real-world application-aware inspection
- [ ] **[Recommended]** Implement Mist AI for campus and branch network management — Mist provides AI-driven WLAN, wired (EX switches via Mist cloud), and WAN (SRX/SSR) operations with Marvis Virtual Network Assistant for automated troubleshooting
- [ ] **[Recommended]** Use Virtual Chassis to cluster up to 10 EX-series switches (EX4300/EX4400/EX4600) into a single logical device — reduces management overhead but introduces blast radius concerns; evaluate whether EVPN multihoming is more appropriate for data center deployments
- [ ] **[Recommended]** Enable commit-confirmed for all production configuration changes — Junos automatically rolls back if the commit is not confirmed within the specified timeframe, preventing lockouts from misconfigurations
- [ ] **[Recommended]** Design MX-series deployment for WAN edge, peering, and service provider roles — evaluate MPC (Modular Port Concentrator) line card selection based on required interface types, subscriber scale, and service chaining capabilities
- [ ] **[Recommended]** Configure Class of Service (CoS) with proper scheduler maps, rewrite rules, and BA (Behavior Aggregate) classifiers — Junos CoS uses a different model than Cisco QoS, with 8 forwarding classes per interface and strict-priority plus weighted scheduling
- [ ] **[Recommended]** Implement RPKI (Resource Public Key Infrastructure) origin validation on MX/PTX routers performing BGP peering — Junos supports RPKI with multiple validation cache servers for route origin authentication
- [ ] **[Recommended]** Deploy Junos Telemetry Interface (JTI) with gRPC/gNMI streaming for real-time operational data — OpenConfig models are supported alongside native Junos YANG models for multi-vendor telemetry pipelines
- [ ] **[Recommended]** Validate firmware upgrade paths using Juniper's JTAC recommended releases — Junos does not support skipping major versions, and intermediate upgrades may be required; Junos OS Evolved has a separate release train from classic Junos
- [ ] **[Optional]** Evaluate Juniper Session Smart Router (SSR, formerly 128 Technology) for SD-WAN deployments — SSR uses session-based routing with tunnel-free WAN optimization, distinct from traditional IPsec-based SD-WAN overlays
- [ ] **[Optional]** Configure Junos Automation with PyEZ (Python library), SLAX/XSLT commit scripts, and event policies for operational automation — Junos has native XML API support that predates NETCONF/YANG and remains widely used
- [ ] **[Optional]** Plan Virtual Chassis Fabric (VCF) for QFX-series data center deployments as an alternative to EVPN-VXLAN when simpler L2 fabrics are sufficient — VCF is being superseded by EVPN-VXLAN and Apstra for new deployments
- [ ] **[Optional]** Enable MACsec (802.1AE) on EX4400/QFX5120/QFX5130 for line-rate encryption on inter-switch links — requires compatible optics and key management via 802.1X or static connectivity associations
- [ ] **[Optional]** Evaluate Juniper Paragon Automation for WAN path computation, traffic engineering, and network planning across MX/PTX deployments — Paragon includes Pathfinder (PCE), Planner, and Active Assurance for service-level monitoring

## Why This Matters

Juniper's portfolio spans campus access (EX-series with Mist AI), data center fabric (QFX-series with Apstra), WAN edge and core routing (MX/PTX-series), and security (SRX-series). The platform's architectural strength lies in its consistent Junos OS CLI and configuration model across product families, making cross-domain operations more predictable than multi-vendor alternatives. However, the bifurcation between classic Junos (FreeBSD-based) and Junos OS Evolved (Linux-based) introduces operational differences that must be understood during platform selection and upgrade planning.

EVPN-VXLAN has become Juniper's strategic data center fabric architecture, with Apstra providing the management layer. Apstra is notable for its multi-vendor support (it can manage Cisco, Arista, and SONiC devices alongside Juniper), making it relevant even in heterogeneous environments. Organizations that deploy QFX switches without Apstra for large fabrics often struggle with configuration consistency, troubleshooting complexity, and Day 2 operations at scale.

Virtual Chassis remains popular for campus aggregation and small data center deployments, but it introduces a single management domain with shared control plane risk. For new data center designs, EVPN multihoming with Apstra is the recommended approach over Virtual Chassis Fabric. The SRX platform competes directly with Palo Alto and Fortinet for enterprise firewall roles, with particular strength in service provider and large-enterprise deployments where Junos routing integration provides advantages.

## Common Decisions (ADR Triggers)

### ADR: Data Center Fabric Architecture

**Context:** Juniper offers multiple approaches to data center switching fabric design.

**Options:**

| Criterion | EVPN-VXLAN with Apstra | Virtual Chassis Fabric | IP Fabric (L3 Only) |
|---|---|---|---|
| Scale | Hundreds of leaf switches | Up to 20 switches | Hundreds of switches |
| L2 Extension | Yes, across fabric | Yes, single domain | No |
| Multi-vendor | Yes (Apstra) | No, Juniper only | Yes (standard BGP) |
| Management Complexity | Medium (Apstra automates) | Low (single device) | Low (standard routing) |
| Failure Domain | Per-leaf or per-pod | Entire fabric | Per-device |
| Best For | Large DC, cloud-scale | Small DC, campus core | Pure L3 workloads |

### ADR: ERB vs. CRB for EVPN-VXLAN

**Context:** EVPN-VXLAN fabrics require a routing model for inter-subnet traffic.

**Decision factors:** Whether L3 gateway should be distributed (ERB, on every leaf) or centralized (CRB, on border/spine devices), number of VRFs and VNIs, traffic patterns (east-west vs. north-south), required convergence time, and whether service chaining or firewall insertion is needed at the L3 boundary.

### ADR: Mist AI vs. Junos Space for Network Management

**Context:** Juniper offers cloud-managed operations via Mist AI and on-premises management via Junos Space Network Director.

**Decision factors:** Cloud connectivity requirements (Mist requires outbound HTTPS to Juniper cloud), air-gapped or restricted environments (Junos Space is on-premises), AI/ML-driven troubleshooting needs (Mist Marvis), existing Junos Space investment, and whether wireless (Mist AP) management integration is required.

### ADR: SRX Firewall Deployment Model

**Context:** SRX firewalls can be deployed as standalone, in chassis cluster (HA), or as virtual SRX (vSRX) in cloud/virtualized environments.

**Decision factors:** Throughput requirements (hardware SRX vs. vSRX), HA requirements (chassis cluster active/passive or active/active), integration with Juniper Security Director for policy management, whether ATP (Advanced Threat Prevention) cloud or on-premises appliance is needed, and regulatory requirements for hardware-based security.

### ADR: Virtual Chassis vs. EVPN Multihoming

**Context:** Both Virtual Chassis and EVPN ESI-LAG provide multi-chassis link aggregation for server or switch redundancy.

**Decision factors:** Number of member switches (VC supports up to 10, EVPN is unlimited), whether single management IP is desired (VC advantage), failure domain tolerance, need for mixed-vendor downstream connections, and long-term fabric growth plans.

## AI and GenAI Capabilities

**Mist AI and Marvis Virtual Network Assistant** -- Cloud-based AI engine providing proactive anomaly detection, root cause analysis, and automated remediation across wired, wireless, and WAN domains. Marvis uses natural language processing for conversational troubleshooting and provides AI-driven actions (Marvis Actions) that automatically identify and resolve common network issues such as missing VLANs, authentication failures, and cable errors.

**Apstra Intent-Based Analytics** -- Apstra uses intent-based networking with continuous validation to detect configuration drift, anomalies, and compliance violations. Includes IBA (Intent-Based Analytics) probes that apply telemetry-driven analysis to detect issues before they impact services.

**Juniper AI-Native Networking Platform** -- Juniper's strategic direction toward an AI-native networking platform that integrates Mist AI across all domains (campus, data center, WAN, security) with unified AI-driven operations, AIOps, and predictive analytics.

## See Also

- `general/networking.md` -- General networking architecture, VLAN design, routing protocols
- `general/networking-physical.md` -- Physical network design, cabling, and topology
- `patterns/network-segmentation.md` -- Segmentation design patterns and trust zone models
- `providers/arista/networking.md` -- Arista EOS and CloudVision for data center networking

## Reference Links

- [Junos OS Documentation](https://www.juniper.net/documentation/product/us/en/junos-os/) -- CLI reference, configuration guides, and feature documentation
- [Apstra Documentation](https://www.juniper.net/documentation/product/us/en/apstra/) -- intent-based fabric management, reference designs, and API documentation
- [Mist AI Documentation](https://www.juniper.net/documentation/product/us/en/mist/) -- cloud-managed operations, Marvis, and AI-driven networking
- [EVPN-VXLAN Reference Architecture](https://www.juniper.net/documentation/us/en/software/junos/evpn-vxlan/index.html) -- data center fabric design with EVPN-VXLAN on QFX platforms
- [SRX Series Documentation](https://www.juniper.net/documentation/product/us/en/srx-series/) -- firewall policy, security zones, VPN, and ATP configuration
- [Juniper JTAC Recommended Releases](https://supportportal.juniper.net/s/article/Junos-Software-Versions-Suggested-Releases-to-Consider-and-Evaluate) -- recommended Junos versions by platform
