# CrowdStrike

## Scope

This file covers **CrowdStrike Falcon platform architecture and design** including Falcon Prevent (NGAV), Falcon Insight (EDR/XDR), Falcon LogScale (formerly Humio) for log management, Falcon Cloud Security (CWPP/CSPM), Falcon Identity (identity threat protection), Falcon Exposure Management, kernel-level sensor deployment strategy, Falcon Fusion SOAR workflows, Falcon Data Protection (DLP), Real Time Response (RTR) for remote remediation, and licensing models (Falcon Go, Falcon Pro, Falcon Enterprise, Falcon Elite, Falcon Flex). It does not cover general endpoint hardening or security architecture; for that, see `general/security.md`.

## Checklist

- [ ] **[Critical]** Plan kernel-level sensor deployment carefully — the Falcon sensor operates as a kernel-mode driver on Windows and a kernel module on Linux; test on representative OS builds and kernel versions before mass deployment to avoid stability issues (ref: July 2024 content update incident)
- [ ] **[Critical]** Configure sensor update policies with staged rollout rings (N-1 or N-2 sensor versions) — never deploy the latest sensor version to the entire fleet simultaneously; use canary groups, then pilot, then broad deployment
- [ ] **[Critical]** Establish a content update policy that delays rapid response content (Channel Files) by at least one ring — separate sensor updates from content updates in the rollout strategy
- [ ] **[Critical]** Ensure network connectivity from sensors to the CrowdStrike cloud (ts01-b.cloudsink.net on port 443) — the sensor requires persistent outbound TLS connectivity for detection, prevention, and policy updates; proxy or firewall rules must allow this
- [ ] **[Critical]** Design Falcon LogScale (Humio) ingestion architecture to handle expected log volume — LogScale is licensed per daily ingest volume (GB/day); overages are expensive and retroactive
- [ ] **[Critical]** Define prevention policy vs. detect-only policy per OS group — deploying aggressive prevention policies without baselining causes false-positive blocks on legitimate business applications
- [ ] **[Recommended]** Enable Falcon Identity Threat Protection for Active Directory environments — detects lateral movement, credential theft, and identity-based attacks that endpoint-only EDR misses
- [ ] **[Recommended]** Configure Real Time Response (RTR) access controls with role-based permissions — RTR provides full remote shell access to endpoints; restrict to trained responders and audit all sessions
- [ ] **[Recommended]** Integrate Falcon with SIEM/SOAR via the Falcon SIEM Connector or Streaming API — the Falcon console is not a SIEM replacement; forward detections to the central security operations platform
- [ ] **[Recommended]** Deploy Falcon Cloud Security agents on cloud workloads (EC2, Azure VMs, GCE, containers) — the same sensor covers server workloads but cloud-specific policies must be configured separately
- [ ] **[Recommended]** Size LogScale cluster for retention requirements — default Falcon telemetry retention is 7 days in the Falcon console; LogScale extends this to 30-365+ days but requires capacity planning for storage and compute
- [ ] **[Recommended]** Configure Falcon Fusion SOAR workflows for automated containment — network-contain compromised hosts automatically when high-confidence detections fire, reducing mean time to respond
- [ ] **[Recommended]** Plan for sensor exclusions carefully and document every exclusion with business justification — security teams are pressured to add exclusions for performance; each exclusion is a detection blind spot
- [ ] **[Optional]** Evaluate Falcon Data Protection (DLP) for endpoint data loss prevention — monitors and controls sensitive data movement on endpoints, integrating with the same sensor
- [ ] **[Optional]** Deploy Falcon for Mobile to extend EDR coverage to iOS and Android devices in BYOD environments
- [ ] **[Optional]** Evaluate Charlotte AI for natural-language threat investigation — generative AI assistant within the Falcon console that accelerates alert triage and threat hunting
- [ ] **[Optional]** Evaluate Falcon Exposure Management for attack surface visibility — discovers unmanaged assets, evaluates vulnerability context, and prioritizes remediation based on adversary intelligence

## Why This Matters

CrowdStrike Falcon is the dominant cloud-native endpoint protection platform in enterprise environments. Its kernel-level sensor architecture provides deep visibility but introduces operational risk if update and deployment processes are not carefully managed. The July 2024 channel file incident demonstrated that even well-tested platforms can cause widespread outages when content updates bypass staged rollout controls. Organizations must treat sensor deployment and update policies with the same rigor as operating system patching.

The platform's value extends well beyond basic endpoint protection. Falcon Insight XDR correlates telemetry across endpoints, cloud workloads, and identities, but only if all sensor types are deployed and integrated. Organizations that deploy only the endpoint sensor miss lateral movement detection (Identity), cloud-specific threats (Cloud Security), and long-term threat hunting capability (LogScale). LogScale licensing is volume-based and requires accurate forecasting; unexpected log volume spikes cause budget overruns that are difficult to address mid-contract.

Prevention policy design is a critical operational decision. Aggressive prevention blocks threats but generates false positives that disrupt business operations and erode trust in the platform. Most successful deployments start in detect-only mode, baseline normal application behavior for 2-4 weeks, create targeted exclusions, then gradually enable prevention policies per workload group.

## Common Decisions (ADR Triggers)

### ADR: Falcon Module Selection

**Context:** CrowdStrike offers modular licensing; organizations must select which Falcon modules to deploy.

**Options:**

| Criterion | Falcon Pro (NGAV+EDR) | Falcon Enterprise (+Hunting) | Falcon Elite (+Identity+LogScale) | Falcon Flex (Credits) |
|---|---|---|---|---|
| Coverage | Endpoint prevention + detection | + Overwatch managed hunting | + Identity + LogScale + Cloud | All modules, credit-based |
| Cost | Base tier | ~30% premium | ~60% premium | Variable by consumption |
| Use case | SMB, cost-constrained | Mid-market with SOC | Enterprise full coverage | Large orgs wanting flexibility |
| Staffing need | SOC required | Reduced (Overwatch augments) | Reduced | Varies |

### ADR: Sensor Update Strategy

**Context:** After the July 2024 incident, organizations must decide on sensor and content update rollout policies.

**Decision factors:** Risk tolerance for zero-day protection gaps vs. stability, number of rollout rings (recommended minimum 3), delay between rings (recommended 24-72 hours), automated vs. manual ring promotion, separate policies for servers vs. workstations, and whether to pin server sensors at N-2.

### ADR: LogScale vs. External SIEM for Falcon Telemetry

**Context:** Falcon telemetry can be stored in LogScale (native) or forwarded to an external SIEM (Splunk, Sentinel, etc.).

**Decision factors:** Existing SIEM investment, log volume cost comparison (LogScale GB/day pricing vs. SIEM ingest pricing), retention requirements, correlation with non-CrowdStrike data sources, and whether the SOC team wants a single pane of glass or best-of-breed tools.

### ADR: Prevention Policy Aggressiveness

**Context:** Falcon prevention policies range from detect-only to aggressive blocking with machine-learning sensitivity levels.

**Decision factors:** Application environment complexity, tolerance for false positives, ability to baseline before enabling prevention, workload type (developer machines need more exclusions than locked-down kiosks), and regulatory requirements for active blocking.

## AI and GenAI Capabilities

**Charlotte AI** -- Generative AI assistant embedded in the Falcon console. Capabilities: natural-language threat investigation ("Show me all lateral movement in the last 24 hours"), automated alert triage and summarization, threat hunting query generation from plain-language descriptions, and incident report drafting. Reduces analyst investigation time by correlating Falcon telemetry with CrowdStrike threat intelligence.

**Charlotte AI Agentic Workflows** -- Autonomous investigation agents that perform multi-step triage: collect endpoint context, correlate with threat intelligence, assess blast radius, and recommend containment actions. Analysts review and approve rather than manually performing each step.

**Falcon Foundry** -- Low-code application platform that allows security teams to build custom Falcon applications using CrowdStrike's data, threat intelligence, and AI models. Enables organization-specific automation without writing traditional code.

## See Also

- `general/security.md` -- Security architecture, hardening, compliance frameworks
- `patterns/zero-trust.md` -- Zero-trust architecture principles and implementation
- `providers/paloalto/firewall.md` -- Network-layer security (complementary to endpoint)
- `providers/splunk/observability.md` -- SIEM integration for Falcon telemetry forwarding

## Reference Links

- [CrowdStrike Falcon Technical Documentation](https://falcon.crowdstrike.com/documentation/) -- sensor deployment, policy configuration, API reference
- [Falcon Sensor Deployment Guide](https://falcon.crowdstrike.com/documentation/22/falcon-sensor-for-windows) -- Windows, Linux, and macOS sensor installation and troubleshooting
- [CrowdStrike LogScale Documentation](https://library.humio.com/) -- log ingestion, query language, retention configuration, and cluster sizing
- [Falcon Data Replicator (FDR) and Streaming API](https://falcon.crowdstrike.com/documentation/9/falcon-data-replicator) -- raw telemetry export for external SIEM integration
- [CrowdStrike Content Update Review (2024)](https://www.crowdstrike.com/falcon-content-update-remediation-and-guidance-hub/) -- root cause analysis and remediation guidance for the July 2024 incident
