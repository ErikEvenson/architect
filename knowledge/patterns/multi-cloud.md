# Multi-Cloud Architecture

## Overview

Multi-cloud architecture uses two or more public cloud providers simultaneously to deliver services. This is distinct from hybrid cloud (public + on-premises). Motivations include avoiding vendor lock-in, leveraging best-of-breed services, meeting data sovereignty requirements, and negotiating leverage. Multi-cloud adds significant operational complexity and should be adopted deliberately rather than accidentally.

## Checklist

- [ ] What is the business justification for multi-cloud? (regulatory requirement, M&A inheritance, best-of-breed services, negotiation leverage — not just "avoiding lock-in")
- [ ] What abstraction layer is used for infrastructure? (Terraform, Pulumi, Crossplane — avoid provider-specific IaC like CloudFormation or ARM in multi-cloud)
- [ ] Is Kubernetes the workload portability layer? (EKS, GKE, AKS, or self-managed — standardized deployment across providers)
- [ ] How is identity federated across providers? (centralized IdP, cross-cloud role assumption, workload identity federation)
- [ ] How is networking connected between clouds? (dedicated interconnects, VPN, DNS delegation, overlapping CIDR avoidance)
- [ ] Where does data reside and why? (data sovereignty, data gravity, egress cost implications, replication strategy)
- [ ] Which services are provider-native vs abstracted? (databases, AI/ML, managed services — accept lock-in for high-value differentiators)
- [ ] How is observability unified? (Datadog, Grafana Cloud, or provider-native tools with aggregation — single pane of glass)
- [ ] How is security policy enforced consistently? (OPA/Gatekeeper, cloud-agnostic policy engine, unified SIEM)
- [ ] What is the cost comparison methodology? (normalized pricing, reserved/committed use, egress costs, support tiers)
- [ ] How are shared services deployed? (CI/CD, secrets management, container registry — centralized vs per-provider)
- [ ] What is the disaster recovery strategy across providers? (active-active, active-passive, provider failover)
- [ ] How is DNS managed across providers? (Route 53, Cloud DNS, external DNS like Cloudflare — health-check-based routing)

## Why This Matters

Multi-cloud is often pursued for "vendor lock-in avoidance" but the operational overhead frequently exceeds the lock-in risk. Teams need expertise across multiple platforms, tooling must work everywhere, and the lowest common denominator problem limits the use of provider-specific innovations. However, legitimate multi-cloud use cases exist: regulatory requirements for data residency, M&A combining different cloud estates, or genuinely using best-of-breed services (e.g., GCP for ML, AWS for breadth). The key is intentional adoption with clear boundaries, not accidental sprawl. Egress costs between providers are a major hidden expense that can invalidate cost projections.

## Common Decisions (ADR Triggers)

- **Multi-cloud justification** — documenting why multi-cloud is necessary vs simpler single-cloud or hybrid approaches
- **Abstraction layer depth** — full portability (Kubernetes + Terraform) vs selective portability (some workloads portable, some provider-native)
- **Provider allocation** — which workloads run where and why (data gravity, compliance, service availability, cost)
- **Networking topology** — interconnect architecture, DNS strategy, traffic flow between providers
- **Identity federation model** — centralized IdP choice, cross-cloud trust relationships, service account management
- **Data residency policy** — which data stays in which provider/region, replication rules, sovereignty compliance
- **Native vs portable services** — which managed services justify lock-in (e.g., BigQuery, DynamoDB) vs abstracted alternatives
- **Cost governance** — unified cost tracking, cross-provider FinOps tooling, committed use discount strategy
- **Operational model** — single team managing all clouds vs specialized teams per provider, on-call rotation
