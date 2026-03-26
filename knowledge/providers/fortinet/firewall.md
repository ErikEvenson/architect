# Fortinet FortiGate

## Scope

This file covers **Fortinet FortiGate firewall architecture and design** including FortiOS configuration, VDOM (Virtual Domain) multi-tenancy, FortiManager centralized management, FortiAnalyzer logging and analytics, SD-WAN integration, FortiGate VM for virtualized and cloud deployments, Security Fabric cross-product integration, ZTNA (Zero Trust Network Access), and licensing models (hardware appliance plus FortiGuard subscription bundles). It does not cover general security architecture; for that, see `general/security.md`.

## Checklist

- [ ] **[Critical]** Size the FortiGate model based on throughput with UTM/NGFW features enabled (IPS, AV, SSL inspection, application control) — not raw firewall throughput, which can be 5-10x higher than inspected throughput
- [ ] **[Critical]** Deploy FortiManager for centralized policy and configuration management when operating more than two FortiGates — manual per-device management causes drift and audit failures
- [ ] **[Critical]** Design VDOM architecture for multi-tenant or functional segmentation requirements — each VDOM operates as an independent firewall with separate routing tables, policies, and admin access
- [ ] **[Critical]** Configure FortiAnalyzer or equivalent centralized logging to retain firewall logs beyond the limited local storage capacity of FortiGate appliances
- [ ] **[Recommended]** Enable SSL/TLS deep inspection for outbound traffic using an enterprise CA certificate — without it, UTM features cannot inspect encrypted traffic that comprises the majority of modern web traffic
- [ ] **[Recommended]** Deploy FortiGate SD-WAN for branch office connectivity with application-aware routing, SLA-based path selection, and centralized orchestration through FortiManager
- [ ] **[Recommended]** Integrate FortiGate into the Fortinet Security Fabric for correlated threat intelligence across FortiGate, FortiSwitch, FortiAP, and FortiClient endpoints
- [ ] **[Recommended]** Configure FortiGuard subscription bundles (UTP or Enterprise) based on required security features — evaluate whether AI-based features (FortiGuard AI, inline sandbox) justify the Enterprise bundle cost
- [ ] **[Recommended]** Implement HA (active-passive or active-active with FGCP) and validate failover time, session synchronization, and VPN tunnel re-establishment under realistic traffic conditions
- [ ] **[Optional]** Evaluate ZTNA for replacing traditional VPN with identity-aware, per-application access proxied through FortiGate and enforced by FortiClient
- [ ] **[Optional]** Deploy FortiGate VM in cloud environments (AWS, Azure, GCP) using bootstrapping for automated provisioning within infrastructure-as-code pipelines
- [ ] **[Optional]** Configure automation stitches (event-triggered actions) to automatically quarantine compromised hosts, block threat sources, or escalate alerts without manual intervention
- [ ] **[Optional]** Plan FortiOS firmware upgrade strategy with staged rollouts — test upgrades on non-production VDOMs or lab devices before applying to production, and verify FortiManager/FortiAnalyzer compatibility
- [ ] **[Recommended]** Is FortiAI evaluated for SOC automation — AI-powered threat detection, automated investigation, and natural language security queries via the FortiAI Assistant?
- [ ] **[Optional]** Is FortiGuard AI-Powered Security Services evaluated — ML-driven threat intelligence across FortiGuard services including IPS, anti-malware, web filtering, and application control with real-time model updates?

## Why This Matters

FortiGate is widely deployed across enterprises of all sizes due to its competitive price-to-performance ratio and broad feature set. The platform's integrated SD-WAN, ZTNA, and Security Fabric capabilities can consolidate multiple point products, but this consolidation requires deliberate architectural planning. Organizations that deploy FortiGate as a simple stateful firewall without enabling UTM inspection, centralized management, or Security Fabric integration leave significant security value on the table.

VDOM design is a frequent source of architectural complexity. VDOMs enable multi-tenancy and functional isolation on a single appliance, but each VDOM consumes resources and adds management overhead. Poorly planned VDOM architectures — too many VDOMs with insufficient resources, or VDOMs created for organizational rather than security reasons — create operational burden without meaningful security benefit. FortiManager and FortiAnalyzer are essential for any deployment beyond a single site; without them, configuration consistency, compliance reporting, and forensic investigation capabilities are severely limited.

## Common Decisions (ADR Triggers)

### ADR: FortiGate Licensing Bundle

**Context:** FortiGuard subscriptions are sold in bundles that determine which security features are available.

**Options:**

| Criterion | ATP (Advanced Threat Protection) | UTP (Unified Threat Protection) | Enterprise |
|---|---|---|---|
| IPS, AV, Botnet | Yes | Yes | Yes |
| Web Filter, App Control | No | Yes | Yes |
| Anti-Spam, Video Filter | No | Yes | Yes |
| Sandbox (inline) | No | No | Yes |
| FortiGuard AI | No | No | Yes |
| Cost | Low | Medium | High |

### ADR: VDOM Architecture

**Context:** VDOMs provide logical firewall separation on a single physical or virtual appliance.

**Decision factors:** Number of tenants or security zones requiring full isolation, whether separate routing domains are needed, resource allocation per VDOM (session tables, interfaces), administrative delegation requirements, and whether inter-VDOM links are needed for shared services.

### ADR: SD-WAN vs. Traditional WAN

**Context:** FortiGate integrates SD-WAN directly into the firewall, eliminating the need for separate SD-WAN appliances.

**Decision factors:** Number of branch offices, existing MPLS contracts and termination timelines, internet circuit availability at branch sites, application SLA requirements, FortiManager availability for centralized SD-WAN orchestration, and whether dual-hub or full-mesh overlay topology is needed.

### ADR: FortiAI Adoption

**Context:** FortiAI provides AI-assisted security operations within the Fortinet ecosystem.

**Decision factors:** Enable AI-assisted security operations (faster investigation, reduced analyst workload) vs traditional manual workflows; evaluate whether FortiAI capabilities reduce the need for a separate SIEM/SOAR platform.

### ADR: VPN vs. ZTNA for Remote Access

**Context:** FortiGate supports both traditional SSL/IPsec VPN and ZTNA proxy-based per-application access.

**Decision factors:** Number of remote users, application access granularity requirements, endpoint agent deployment feasibility (FortiClient required for ZTNA), legacy application compatibility, and organizational readiness for zero-trust principles.

## AI and GenAI Capabilities

**FortiAI** — AI-powered security operations assistant. Provides natural language queries for policy configuration, threat investigation, and troubleshooting. Integrates with FortiAnalyzer and FortiManager for cross-fabric visibility. FortiAI Assistant can explain security events, suggest policy changes, and guide remediation.

**FortiGuard AI Services** — ML-driven threat intelligence powering all FortiGuard security services. Includes AI-based inline malware detection, AI-powered URL/web filtering, and behavioral analysis for unknown threats. Models are trained on FortiGuard Labs threat data and updated in real-time.

**Security Fabric AI** — Fortinet's Security Fabric uses AI/ML across the fabric for automated threat correlation and response across FortiGate, FortiAnalyzer, FortiManager, FortiSIEM, and FortiSOAR.

## See Also

- `general/security.md` — Security architecture, hardening, compliance frameworks
- `patterns/network-segmentation.md` — Segmentation design patterns and trust zone models

## Reference Links

- [FortiOS Documentation](https://docs.fortinet.com/product/fortigate) -- firewall policy, VDOM, SD-WAN, and ZTNA configuration
- [FortiManager Documentation](https://docs.fortinet.com/product/fortimanager) -- centralized management, ADOM, policy packages, and device provisioning
- [FortiAnalyzer Documentation](https://docs.fortinet.com/product/fortianalyzer) -- log management, analytics, SOC features, and reporting
