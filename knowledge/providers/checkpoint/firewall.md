# Check Point

## Scope

This file covers **Check Point firewall architecture and design** including SmartConsole management, Security Management Server (SmartCenter) architecture, security policy layers and ordered/inline layers, CloudGuard for cloud-native protection, Maestro hyperscale orchestration, VSX virtual firewall contexts, R81.x platform features, policy conversion from legacy rulesets, and licensing models (per-gateway with software blade subscriptions). It does not cover general security architecture; for that, see `general/security.md`.

## Checklist

- [ ] **[Critical]** Size the Security Gateway model based on throughput with Threat Prevention blades enabled (IPS, Anti-Bot, SandBlast) — vendor datasheets list maximum firewall throughput, which is substantially higher than inspected throughput
- [ ] **[Critical]** Deploy a dedicated Security Management Server (SMS) and do not co-locate the management plane on the gateway — co-located management limits scalability and complicates DR
- [ ] **[Critical]** Design security policy using ordered layers and inline layers to create a maintainable rule structure — flat monolithic rulesets with thousands of rules become unauditable and error-prone
- [ ] **[Critical]** Plan Management Server high availability with a secondary SMS or Multi-Domain Management Server (MDS) to ensure policy management continuity during outages
- [ ] **[Recommended]** Implement HTTPS inspection with a proper PKI infrastructure — without decryption, Threat Prevention blades cannot inspect the majority of modern encrypted traffic
- [ ] **[Recommended]** Use SmartConsole policy packages and policy layers to separate network, application, and threat prevention rules into manageable, delegatable sections
- [ ] **[Recommended]** Configure centralized logging to a dedicated Log Server or SmartEvent correlation server — gateway local logging is limited and insufficient for compliance or forensic investigation
- [ ] **[Recommended]** Deploy ClusterXL in HA mode (active/standby or active/active with Load Sharing) and validate failover behavior, session synchronization, and VPN tunnel persistence under load
- [ ] **[Recommended]** Plan R81.x upgrade path carefully — validate blade compatibility, SmartConsole version requirements, and test policy installation on a lab gateway before production rollout
- [ ] **[Optional]** Deploy Maestro orchestrator for hyperscale environments where a single gateway cannot meet throughput requirements — Maestro distributes traffic across multiple gateway appliances as a single logical firewall
- [ ] **[Optional]** Use VSX (Virtual System Extension) to create multiple virtual firewall contexts on a single physical gateway for multi-tenant or segmented environments
- [ ] **[Optional]** Deploy CloudGuard Network Security for cloud environments (AWS, Azure, GCP) with automated provisioning using CloudGuard Controller integration
- [ ] **[Optional]** Leverage SmartMove or migration tools when converting policies from competitor platforms or consolidating multiple Check Point management domains

## Why This Matters

Check Point is one of the longest-established enterprise firewall vendors, and many large organizations have deeply embedded Check Point infrastructure with complex, long-lived rulesets. The primary architectural challenge is often not deploying new Check Point firewalls but managing the accumulated complexity of existing environments — rulesets with thousands of rules, outdated objects, shadowed rules, and policies that no one fully understands.

Policy layers (introduced in R80+) provide the structural tools to decompose monolithic rulesets into manageable sections, but migration from legacy flat policies requires deliberate planning. The Security Management Server is the central brain of the Check Point environment; its loss means the inability to modify or install policies on any gateway. Organizations that treat SMS availability as an afterthought discover during incidents that they can see traffic flowing but cannot respond with policy changes. Maestro and VSX extend the platform's scalability but add operational complexity that must be justified by genuine throughput or multi-tenancy requirements.

## Common Decisions (ADR Triggers)

### ADR: Management Architecture

**Context:** Check Point management can be deployed as a standalone SMS, HA SMS pair, or Multi-Domain Management Server (MDS).

**Options:**

| Criterion | Standalone SMS | SMS with HA Secondary | Multi-Domain (MDS) |
|---|---|---|---|
| Gateway count | Small (1-5) | Medium (5-50) | Large (50+) or multi-tenant |
| Management continuity | Single point of failure | Automatic failover | Per-domain failover |
| Multi-tenancy | No | No | Yes (domain-level isolation) |
| Operational complexity | Low | Medium | High |
| Licensing | Included with gateways | Additional SMS license | MDS license |

### ADR: Policy Layer Design

**Context:** Security policy layers control rule evaluation order and enable delegation of policy sections to different teams.

**Decision factors:** Number of rule sections (network, application, compliance, threat prevention), teams responsible for each section, whether inline layers are needed for exception handling, and whether ordered layers should use "first match" or "all layers" evaluation.

### ADR: Scalability — Maestro vs. VSX vs. Separate Gateways

**Context:** When a single gateway cannot meet throughput or segmentation requirements, the organization must choose a scale-out or virtualization strategy.

**Options:**

| Criterion | Maestro Hyperscale | VSX Virtual Contexts | Separate Physical Gateways |
|---|---|---|---|
| Throughput scaling | Linear (add appliances) | Shared (single appliance) | Independent per gateway |
| Management complexity | Medium (orchestrator) | High (virtual routing) | Low (per-gateway) |
| Use case | High-throughput perimeter | Multi-tenant / segmentation | Distinct security domains |
| Cost | High (orchestrator + appliances) | Medium (single appliance) | High (multiple appliances) |

### ADR: Cloud Security — CloudGuard vs. Third-Party

**Context:** Extending Check Point policy to cloud environments requires evaluating CloudGuard against cloud-native or alternative solutions.

**Decision factors:** Existing Check Point investment and staff expertise, cloud platform (AWS/Azure/GCP), need for unified policy management across on-premises and cloud, CloudGuard licensing cost, and whether cloud-native security groups and WAF meet requirements without additional gateway deployment.

## See Also

- `general/security.md` — Security architecture, hardening, compliance frameworks
- `patterns/network-segmentation.md` — Segmentation design patterns and trust zone models

## Reference Links

- [Check Point Security Management](https://sc1.checkpoint.com/documents/latest/APIs/) -- SmartConsole, policy layers, and Security Management Server administration
- [Check Point CloudGuard](https://sc1.checkpoint.com/documents/CloudGuard_Dome9/Default.htm) -- cloud-native security, posture management, and workload protection
- [Check Point R81.x Administration Guide](https://sc1.checkpoint.com/documents/R81.20/WebAdminGuide/Default.htm) -- gateway configuration, VSX, Maestro, and ClusterXL HA
