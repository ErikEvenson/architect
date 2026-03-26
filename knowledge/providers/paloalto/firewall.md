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

### ADR: Migration from Legacy Firewall Vendor

**Context:** Replacing an existing firewall vendor (Cisco ASA, Check Point, Fortinet) requires policy conversion and validation.

**Decision factors:** Number of existing rules, use of legacy features (NAT, VPN), Expedition tool compatibility, parallel-run duration, cutover strategy (big-bang vs. phased), and staff training timeline.

## See Also

- `general/security.md` — Security architecture, hardening, compliance frameworks
- `patterns/network-segmentation.md` — Segmentation design patterns and trust zone models
- `patterns/zero-trust.md` — Zero-trust architecture principles and implementation
