# Palo Alto Networks

## Scope

This file covers **Palo Alto Networks firewall architecture and design** including PAN-OS configuration, zone-based security policy design, App-ID application identification, Panorama centralized management, GlobalProtect VPN, VM-Series virtual firewalls, CN-Series container firewalls, Prisma Cloud integration, Expedition migration tool for policy conversion from legacy vendors, and licensing models (subscription bundles, VM-Series sizing). It does not cover general security architecture; for that, see `general/security.md`.

## Checklist

- [ ] **[Critical]** Design zone architecture reflecting trust boundaries — do not flatten all internal traffic into a single zone; segment by function (servers, users, DMZ, management)
- [ ] **[Critical]** Build security policies using App-ID and User-ID instead of port-based rules — port-based rules undermine the primary value of the platform
- [ ] **[Critical]** Deploy Panorama for centralized management when operating more than one firewall — template stacks and device groups enforce consistency and prevent configuration drift
- [ ] **[Critical]** Size the firewall model (PA-series) or VM-Series instance based on throughput with Threat Prevention enabled, not just raw firewall throughput — enabling all subscriptions reduces throughput by 40-60%
- [ ] **[Recommended]** Configure log forwarding to a SIEM or Panorama log collector — local firewall storage fills quickly and logs are lost during high-volume events
- [ ] **[Recommended]** Implement SSL/TLS decryption for outbound traffic inspection with a proper certificate infrastructure — without decryption, Threat Prevention cannot inspect encrypted traffic
- [ ] **[Recommended]** Deploy GlobalProtect with HIP (Host Information Profile) checks to enforce endpoint compliance before granting VPN access
- [ ] **[Recommended]** Use Expedition migration tool when converting policies from legacy vendors (Cisco ASA, Check Point, Fortinet) — validate converted rules and remove shadowed or redundant entries post-migration
- [ ] **[Recommended]** Enable DNS Security and URL Filtering subscriptions to block command-and-control traffic and known malicious domains at the firewall layer
- [ ] **[Optional]** Deploy VM-Series in cloud environments (AWS, Azure, GCP) with bootstrap configuration for automated provisioning in infrastructure-as-code workflows
- [ ] **[Optional]** Evaluate CN-Series for Kubernetes environments where east-west container traffic requires Layer 7 inspection and policy enforcement
- [ ] **[Optional]** Configure HA (active/passive or active/active) with session synchronization and verify failover behavior under load before production deployment
- [ ] **[Optional]** Integrate with Prisma Cloud for unified visibility across on-premises firewalls, cloud workloads, and container environments
- [ ] **[Recommended]** Is Cortex XSIAM evaluated as the SOC platform — AI-driven security operations combining SIEM, SOAR, ASM, and XDR with autonomous investigation and response, replacing traditional SIEM+SOAR stacks?
- [ ] **[Recommended]** Is Cortex Copilot evaluated for security operations — natural language security queries, threat investigation, configuration guidance, and remediation actions initiated with plain language requests?
- [ ] **[Optional]** Is AgentiX evaluated for custom security automation — build, deploy, and govern custom security agents trained on 1.2 billion real-world playbook executions for organization-specific security workflows?

## Why This Matters

Palo Alto Networks firewalls are deployed as the primary perimeter and segmentation enforcement point in many enterprise environments. The platform's core differentiator — App-ID-based policy — only delivers value when security policies are written against applications rather than ports. Organizations that migrate from legacy firewalls and carry over port-based rules run expensive next-generation firewalls as if they were stateful packet filters, paying a premium for capabilities they never use.

Sizing is a common failure point. Vendors quote maximum firewall throughput under ideal conditions, but enabling Threat Prevention, WildFire, SSL decryption, and URL Filtering dramatically reduces actual throughput. A firewall sized on paper throughput will become a bottleneck in production. Panorama is essential at scale — managing individual firewalls through local console access creates configuration inconsistency, audit gaps, and delayed policy changes that increase security risk.

## Common Decisions (ADR Triggers)

### ADR: Firewall Platform Selection

**Context:** The organization needs next-generation firewall capabilities for perimeter and internal segmentation.

**Options:**

| Criterion | PA-Series (Hardware) | VM-Series (Virtual) | CN-Series (Container) |
|---|---|---|---|
| Deployment | Physical data center | Hypervisor or cloud | Kubernetes cluster |
| Throughput | Highest (custom ASIC) | Medium (CPU-based) | Low-medium (container) |
| Use case | Perimeter, data center core | Cloud, virtualized DC | Microservices segmentation |
| Licensing | Hardware + subscriptions | VM capacity + subscriptions | Per-node + subscriptions |

### ADR: Panorama Deployment Model

**Context:** Panorama can be deployed as a dedicated hardware appliance, virtual appliance, or in Panorama Cloud mode.

**Decision factors:** Number of managed firewalls, log storage requirements (local vs. log collectors vs. Cortex Data Lake), geographic distribution, high availability requirements, and whether Panorama will also manage VM-Series and CN-Series deployments.

### ADR: SSL/TLS Decryption Strategy

**Context:** Inspecting encrypted traffic requires deploying a decryption policy with an enterprise CA certificate on endpoints.

**Decision factors:** Compliance requirements for encrypted traffic inspection, endpoint certificate distribution method (GPO, MDM), privacy policy considerations, exemption list for financial and healthcare sites, and throughput impact on selected firewall model.

### ADR: Cortex XSIAM vs Traditional SIEM+SOAR

**Context:** Cortex XSIAM consolidates SIEM, SOAR, XDR, and ASM into a single AI-driven platform, replacing traditional multi-tool SOC stacks.

**Decision factors:** XSIAM consolidates multiple tools with AI-driven automation vs maintaining separate Splunk/QRadar SIEM + Demisto/Phantom SOAR; significant licensing investment but reduces SOC headcount requirements.

### ADR: Migration from Legacy Firewall Vendor

**Context:** Replacing an existing firewall vendor (Cisco ASA, Check Point, Fortinet) requires policy conversion and validation.

**Decision factors:** Number of existing rules, use of legacy features (NAT, VPN), Expedition tool compatibility, parallel-run duration, cutover strategy (big-bang vs. phased), and staff training timeline.

## AI and GenAI Capabilities

**Cortex XSIAM** — AI-driven SecOps platform that consolidates SIEM, SOAR, XDR, and attack surface management. Uses ML for alert correlation, automated investigation, and response. Surpassed $1B cumulative bookings in FY25 Q2. XSIAM 3.0 (April 2025) added proactive exposure management and advanced email security. Customers report 257% ROI and 73% cost savings vs traditional SIEM+SOAR (Forrester TEI study).

**Cortex Copilot** — Natural language interface for security operations within XSIAM. Capabilities: answer product knowledge questions, explore and visualize app/user/threat activity, answer targeted environment questions, guide configuration, search for IOCs, assess threat impact, and perform remediation actions — all initiated with natural language requests.

**AgentiX** — Agentic AI framework embedded in XSIAM (October 2025). Allows building custom security agents that plan, reason, and execute complex security tasks. Trained on 1.2 billion real-world playbook executions. Agents operate autonomously with human oversight for sensitive actions.

**PAN-OS AI** — ML-powered threat detection built into the firewall platform: Advanced URL Filtering (real-time ML classification), Advanced WildFire (ML-based malware analysis), DNS Security (ML-powered DGA detection), and Inline ML for zero-day threat prevention.

## See Also

- `general/security.md` — Security architecture, hardening, compliance frameworks
- `patterns/network-segmentation.md` — Segmentation design patterns and trust zone models
- `patterns/zero-trust.md` — Zero-trust architecture principles and implementation

## Reference Links

- [PAN-OS Technical Documentation](https://docs.paloaltonetworks.com/pan-os) -- security policy, App-ID, zone configuration, and GlobalProtect VPN
- [Panorama Administration](https://docs.paloaltonetworks.com/panorama) -- centralized management, device groups, templates, and log collection
- [Palo Alto Networks Reference Architectures](https://www.paloaltonetworks.com/resources/reference-architectures) -- deployment designs for data center, campus, and cloud environments
