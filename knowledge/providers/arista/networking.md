# Arista Networks

## Scope

This file covers **Arista Networks switching, routing, and network management** including Arista EOS (Extensible Operating System), CloudVision as-a-service (CVaaS) and on-premises (CVP) management platform, EVPN-VXLAN data center fabric design, leaf-spine architecture, campus networking with Arista CCS (Cognitive Campus Solution), DANZ Monitoring Fabric (DMF) for network visibility, Arista Multi-Domain Segmentation Service (MSS), Wi-Fi 6/6E/7 with Arista WLAN, routing platforms (7500R/7800R series), and licensing models (subscription EOS, CloudVision, and perpetual). It does not cover general networking architecture; for that, see `general/networking.md`.

## Checklist

- [ ] **[Critical]** Select the appropriate Arista switch platform based on deployment role — 7050X/7060X (leaf/ToR), 7260X/7300X (spine), 7500R/7800R (core/DCI/peering), 720XP (campus access) — each uses different ASICs (Memory, Memory-2, Sand, Memory-3) with distinct table sizes, buffer depth, and feature support
- [ ] **[Critical]** Design EVPN-VXLAN fabric with explicit underlay (eBGP or OSPF/ISIS) and overlay (eBGP EVPN) separation — Arista best practice uses eBGP for both underlay and overlay with distinct ASNs per leaf (ASN-per-rack model) for simplified troubleshooting
- [ ] **[Critical]** Deploy CloudVision (CVaaS or CVP) for network-wide configuration management, telemetry, compliance, and change control — CloudVision uses a network data lake (NetDB) that stores every state change for forensic analysis and compliance auditing
- [ ] **[Critical]** Plan EOS software upgrade strategy using CloudVision's image management and staged rollout capabilities — EOS uses a single binary image per platform with no intermediate upgrade requirements, but ISSU (In-Service Software Upgrade) support varies by platform and feature set
- [ ] **[Critical]** Validate hardware TCAM (Ternary Content-Addressable Memory) capacity for the required number of MAC addresses, ARP entries, routes, ACL entries, and VXLAN tunnels — different Arista ASICs have different TCAM profiles, and profile selection determines resource allocation tradeoffs
- [ ] **[Critical]** Configure MLAG (Multi-Chassis Link Aggregation) pairs at the leaf tier for dual-homed server connectivity — MLAG is the primary multi-chassis redundancy mechanism in Arista deployments, using a peer-link and keepalive link between two switches with shared LACP system ID
- [ ] **[Recommended]** Implement Arista AVA (Autonomous Virtual Assist) and CloudVision AI-powered analytics for proactive network health monitoring, anomaly detection, and predictive failure analysis
- [ ] **[Recommended]** Use CloudVision Studios for declarative, intent-based network configuration — Studios provides workspace-based change control with pre-validation, approval workflows, and automated rollback, replacing manual CLI-based provisioning
- [ ] **[Recommended]** Design BGP-based leaf-spine underlay with BFD (Bidirectional Forwarding Detection) on all BGP sessions for sub-second failure detection — Arista supports BFD with 300ms detection timers as default and can tune down to 50ms on hardware-offloaded platforms
- [ ] **[Recommended]** Configure Terminattr (TerminAttr agent) on all EOS devices for streaming telemetry to CloudVision — Terminattr uses gNMI and provides real-time state synchronization with CloudVision's NetDB
- [ ] **[Recommended]** Evaluate DANZ Monitoring Fabric (DMF) for network-wide packet capture, TAP aggregation, and tool-chain load balancing — DMF provides a dedicated monitoring network separate from the production fabric for security, compliance, and troubleshooting visibility
- [ ] **[Recommended]** Implement Arista Macro-Segmentation Service (MSS) for firewall integration in EVPN-VXLAN fabrics — MSS-FW redirects traffic to firewalls using policy-based routing within the EVPN overlay without requiring complex service chaining
- [ ] **[Recommended]** Deploy Arista Network Detection and Response (NDR) for encrypted traffic analysis and threat detection — NDR uses AI/ML models on mirrored traffic (via DANZ) to detect lateral movement, C2 communications, and data exfiltration without decryption
- [ ] **[Recommended]** Validate ECMP (Equal-Cost Multi-Path) hash distribution across the fabric — Arista supports resilient hashing, adaptive load balancing, and dynamic flow prioritization (Flowspec) to prevent hash polarization in multi-tier fabrics
- [ ] **[Optional]** Evaluate Arista 720XP and CCS (Cognitive Campus Solution) for campus access layer deployments — 720XP switches support PoE++, 802.1X with CloudVision identity, and Mist-like AI-driven operations through CloudVision and AVA
- [ ] **[Optional]** Configure FlexRoute on 7500R/7800R platforms for internet routing table scale — FlexRoute provides a multi-million route FIB using algorithmic TCAM with support for full internet tables plus VPN routes on platforms with Memory or Memory-2 forwarding ASICs
- [ ] **[Optional]** Implement EOS eAPI (JSON-RPC over HTTPS) or gNMI/gNOI for programmatic device management — EOS exposes the full CLI and state as structured JSON, making automation straightforward without requiring specialized libraries
- [ ] **[Optional]** Deploy Arista WLAN (formerly Mojo Networks / Arista Cognitive Wi-Fi) for enterprise wireless with CloudVision integration — provides cloud-managed Wi-Fi 6/6E/7 access points with unified wired-wireless policy enforcement
- [ ] **[Optional]** Plan for Arista Network as a Service (NaaS) subscription licensing — Arista A-Care and CloudVision subscriptions bundle software updates, TAC support, and CloudVision entitlements differently from perpetual EOS licensing

## Why This Matters

Arista dominates hyperscale and large enterprise data center networking due to EOS's architectural advantages: a single-image binary, Linux-based userspace with direct shell access, an in-memory state database (Sysdb) that provides transactional consistency across all agents, and a robust automation-first design with eAPI and gNMI. Organizations selecting Arista typically prioritize programmability, operational stability, and scale over feature breadth in areas like integrated security (where Palo Alto or Fortinet may complement).

The EVPN-VXLAN fabric design with CloudVision management is Arista's strategic architecture for data centers. CloudVision's network data lake approach is unique in the industry — it stores every state change on every device, enabling forensic troubleshooting ("what changed and when") that is impossible with traditional SNMP-based management. However, CloudVision is a significant additional investment (subscription-based per switch), and organizations that deploy Arista without CloudVision lose much of the operational advantage.

MLAG is a mature and widely deployed technology in Arista environments, but it introduces tight coupling between paired switches. For new large-scale deployments, Arista also supports EVPN multihoming (ESI-LAG) as an alternative that eliminates the MLAG peer-link, though MLAG remains the more commonly deployed option due to its operational simplicity and mature tooling. DANZ Monitoring Fabric and NDR represent Arista's push into network security, providing visibility and threat detection capabilities that compete with dedicated security vendors.

## Common Decisions (ADR Triggers)

### ADR: CloudVision Deployment Model

**Context:** CloudVision is available as a cloud service (CVaaS) or on-premises appliance cluster (CVP).

**Options:**

| Criterion | CVaaS (Cloud) | CVP (On-Premises) |
|---|---|---|
| Infrastructure | Arista-hosted SaaS | Customer-managed cluster (3+ nodes) |
| Connectivity | Requires HTTPS outbound from switches | Air-gapped capable |
| Updates | Automatic, Arista-managed | Customer-managed upgrades |
| Data Sovereignty | Data in Arista cloud | Data remains on-premises |
| Scale | Multi-region support | Scales with cluster size |
| Cost | Subscription per device | Subscription per device + infrastructure |
| Best For | Cloud-connected enterprises | Regulated, air-gapped, government |

### ADR: Underlay Routing Protocol

**Context:** EVPN-VXLAN fabrics require an underlay routing protocol for VTEP reachability.

**Decision factors:** eBGP (Arista recommended, simpler ASN-per-rack, no separate IGP), OSPF (familiar to many teams, but area design adds complexity at scale), IS-IS (common in service provider environments), number of leaf-spine tiers, and operational team BGP experience level.

### ADR: MLAG vs. EVPN Multihoming

**Context:** Both MLAG and EVPN ESI-LAG provide active-active server dual-homing in leaf-spine fabrics.

**Options:**

| Criterion | MLAG | EVPN Multihoming (ESI-LAG) |
|---|---|---|
| Peer Link Required | Yes (dedicated link) | No |
| Switch Pairing | Fixed pairs | Any combination |
| Failure Domain | Paired switches | Per-device |
| Maturity on Arista | Very mature, widely deployed | Supported, less common |
| Configuration Complexity | Lower | Higher |
| CloudVision Support | Full | Full |
| Best For | Most deployments | Very large fabrics, no peer-link budget |

### ADR: DANZ Monitoring Fabric Deployment

**Context:** Network visibility for security, compliance, and troubleshooting requires packet-level access.

**Decision factors:** Number of TAP and SPAN sources, monitoring tool chain (IDS, NPM, APM, forensics), required filtering and packet manipulation (header stripping, deduplication, truncation), whether inline or out-of-band monitoring is needed, dedicated monitoring switches vs. integrated SPAN on production fabric, and budget for dedicated DMF switching infrastructure.

### ADR: Campus Networking Platform

**Context:** Arista competes for campus access deployments with Cisco, Juniper/Mist, and HPE/Aruba.

**Decision factors:** Existing data center Arista investment (unified CloudVision management), PoE requirements (720XP supports 802.3bt), WLAN integration needs (Arista Wi-Fi vs. third-party), 802.1X/NAC integration strategy, campus fabric requirements (Arista MSS-G for campus segmentation), and operational team familiarity with EOS.

## AI and GenAI Capabilities

**Arista AVA (Autonomous Virtual Assist)** -- AI-powered assistant integrated into CloudVision that provides natural language network queries, automated troubleshooting, and configuration recommendations. AVA uses machine learning models trained on network telemetry data to detect anomalies and suggest remediation.

**CloudVision AI Analytics** -- ML-driven analytics within CloudVision for predictive failure detection, capacity planning, and network health scoring. Analyzes telemetry streams from Terminattr to identify trends, outliers, and correlations across the entire network fabric.

**Arista NDR (Network Detection and Response)** -- AI/ML-based threat detection using encrypted traffic analysis, behavioral modeling, and entity analytics. NDR builds network entity models from traffic metadata to detect threats without packet decryption, integrating with SIEM/SOAR platforms for automated response.

## See Also

- `general/networking.md` -- General networking architecture, VLAN design, routing protocols
- `general/networking-physical.md` -- Physical network design, cabling, and topology
- `patterns/network-segmentation.md` -- Segmentation design patterns and trust zone models
- `providers/juniper/networking.md` -- Juniper Junos, QFX, and Apstra for data center networking

## Reference Links

- [Arista EOS Documentation](https://www.arista.com/en/support/product-documentation) -- EOS configuration guides, command reference, and release notes
- [CloudVision Documentation](https://www.arista.com/en/support/product-documentation/cloudvision) -- CVaaS and CVP deployment, Studios, and telemetry
- [Arista Design Guides](https://www.arista.com/en/solutions/design-guides) -- validated reference architectures for data center, campus, and WAN
- [EVPN Deployment Guide](https://www.arista.com/en/solutions/design-guides/evpn-design-guide) -- EVPN-VXLAN fabric design with leaf-spine architecture
- [DANZ Monitoring Fabric](https://www.arista.com/en/products/danz-monitoring-fabric) -- network visibility, TAP aggregation, and packet broker design
- [Arista NDR Documentation](https://www.arista.com/en/products/network-detection-and-response) -- AI-driven threat detection and encrypted traffic analysis
