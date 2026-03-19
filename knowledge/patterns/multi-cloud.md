# Multi-Cloud Architecture

## Scope

Covers architectures using two or more public cloud providers simultaneously, including cross-cloud networking, identity federation, unified observability, cost management, and workload placement. Distinct from hybrid cloud (public + on-premises). Applicable when regulatory requirements, M&A, best-of-breed services, or negotiation leverage justify multi-provider complexity.

## Overview

Multi-cloud architecture uses two or more public cloud providers simultaneously to deliver services. This is distinct from hybrid cloud (public + on-premises). Motivations include avoiding vendor lock-in, leveraging best-of-breed services, meeting data sovereignty requirements, and negotiating leverage. Multi-cloud adds significant operational complexity and should be adopted deliberately rather than accidentally.

## Checklist

- [ ] **[Critical]** What is the business justification for multi-cloud? (regulatory requirement, M&A inheritance, best-of-breed services, negotiation leverage — not just "avoiding lock-in")
- [ ] **[Critical]** What abstraction layer is used for infrastructure? (Terraform, Pulumi, Crossplane — avoid provider-specific IaC like CloudFormation or ARM in multi-cloud)
- [ ] **[Recommended]** Is Kubernetes the workload portability layer? (EKS, GKE, AKS, or self-managed — standardized deployment across providers)
- [ ] **[Critical]** How is identity federated across providers? (centralized IdP, cross-cloud role assumption, workload identity federation)
- [ ] **[Critical]** How is networking connected between clouds? (dedicated interconnects, VPN, DNS delegation, overlapping CIDR avoidance)
- [ ] **[Critical]** Where does data reside and why? (data sovereignty, data gravity, egress cost implications, replication strategy)
- [ ] **[Critical]** What data residency and sovereignty requirements apply per region? (GDPR for EU personal data, China data localization laws, India data residency rules, Russia data localization — each may restrict which provider and region can store or process data, and may require in-country data processing, not just storage)
- [ ] **[Recommended]** Which services are provider-native vs abstracted? (databases, AI/ML, managed services — accept lock-in for high-value differentiators)
- [ ] **[Recommended]** How is observability unified? (Datadog, Grafana Cloud, or provider-native tools with aggregation — single pane of glass)
- [ ] **[Critical]** How is security policy enforced consistently? (OPA/Gatekeeper, cloud-agnostic policy engine, unified SIEM)
- [ ] **[Recommended]** What is the cost comparison methodology? (normalized pricing, reserved/committed use, egress costs, support tiers)
- [ ] **[Recommended]** How are shared services deployed? (CI/CD, secrets management, container registry — centralized vs per-provider)
- [ ] **[Critical]** What is the disaster recovery strategy across providers? (active-active, active-passive, provider failover)
- [ ] **[Recommended]** How is DNS managed across providers? (Route 53, Cloud DNS, external DNS like Cloudflare — health-check-based routing)

## Why This Matters

Multi-cloud is often pursued for "vendor lock-in avoidance" but the operational overhead frequently exceeds the lock-in risk. Teams need expertise across multiple platforms, tooling must work everywhere, and the lowest common denominator problem limits the use of provider-specific innovations. However, legitimate multi-cloud use cases exist: regulatory requirements for data residency, M&A combining different cloud estates, or genuinely using best-of-breed services (e.g., GCP for ML, AWS for breadth). The key is intentional adoption with clear boundaries, not accidental sprawl. Egress costs between providers are a major hidden expense that can invalidate cost projections.

## Cost Benchmarks

> **Disclaimer:** Prices are rough estimates as of early 2025. Multi-cloud costs are inherently harder to estimate due to variability across providers. Actual costs vary by region, commitments, and usage patterns. Prices change over time — always verify with each provider's pricing calculator.

### Additional Costs of Multi-Cloud vs Single-Cloud

Multi-cloud architectures incur costs beyond the sum of individual provider bills. These overhead costs are often underestimated.

#### Management and Tooling Overhead

| Category | Single-Cloud | Multi-Cloud | Delta |
|----------|-------------|-------------|-------|
| IaC tooling | CloudFormation (free) | Terraform Cloud ($70/user/mo for teams) | +$700/mo (10 users) |
| Observability | CloudWatch ($) | Datadog/Grafana Cloud ($$) for unified view | +$1,000-5,000/mo |
| Security/policy | AWS-native tools | OPA/Gatekeeper + cross-cloud SIEM | +$500-2,000/mo |
| Identity federation | IAM | External IdP + cross-cloud federation | +$200-1,000/mo |
| Container management | EKS ($74/mo) | Multi-cluster Kubernetes (EKS + GKE + AKS) | +$220/mo (control planes) |
| CI/CD | CodePipeline | Multi-cloud CI/CD (GitHub Actions, GitLab) | +$100-500/mo |
| Team training | 1 platform | 2-3 platforms (certifications, upskilling) | +$5,000-15,000/yr |

#### Cross-Cloud Data Transfer Costs

| Transfer Path | Cost per GB | 1 TB/mo | 10 TB/mo |
|--------------|------------|---------|----------|
| AWS to Internet (then to GCP/Azure) | $0.09 | $90 | $900 |
| AWS via Direct Connect to on-prem | $0.02 | $20 | $200 |
| GCP to Internet | $0.12 | $120 | $1,200 |
| Azure to Internet | $0.087 | $87 | $870 |
| Cloud Interconnect (AWS-GCP/Azure dedicated) | $0.02-0.05 + port fees | $20-50 + $200-500 | $200-500 + $200-500 |

**Key takeaway:** Moving 10 TB/mo between clouds costs $900-1,200/mo via internet, or $400-1,000/mo via dedicated interconnects (plus port fees).

#### Duplicate Services

Running equivalent services on multiple providers creates cost overlap:

| Service Category | AWS | GCP | Azure | Multi-Cloud Annual Overhead |
|-----------------|-----|-----|-------|-----------------------------|
| Kubernetes control plane | EKS ($74/mo) | GKE ($74/mo) | AKS (free) | +$1,776/yr |
| Managed database | RDS | Cloud SQL | Azure SQL | 2-3x licensing (no cross-provider reserved pricing) |
| Object storage | S3 | GCS | Blob Storage | Minimal (pay per use) |
| CDN | CloudFront | Cloud CDN | Front Door | 2-3x committed use discounts lost |

### Total Cost of Multi-Cloud Overhead

| Deployment Size | Single-Cloud Baseline | Multi-Cloud Overhead | Overhead % |
|-----------------|----------------------|---------------------|------------|
| Small (< $5K/mo cloud spend) | $5,000/mo | +$2,000-4,000/mo | 40-80% |
| Medium ($20-50K/mo cloud spend) | $35,000/mo | +$5,000-10,000/mo | 15-30% |
| Large ($200K+/mo cloud spend) | $200,000/mo | +$15,000-40,000/mo | 8-20% |

### Biggest Cost Drivers

1. **Cross-cloud data transfer** — egress charges between providers are the single largest hidden cost. Data gravity makes moving data expensive.
2. **Duplicate tooling and expertise** — teams must learn, operate, and maintain tooling for multiple platforms. Engineering time is the most expensive resource.
3. **Lost volume discounts** — splitting spend across providers means less committed use/reserved instance coverage per provider.
4. **Unified observability** — commercial tools (Datadog, Splunk) charge per host/service across all providers.

### Optimization Tips

- **Minimize cross-cloud data transfer** — keep data processing close to where data is stored (data gravity principle).
- Use **dedicated cloud interconnects** instead of internet egress for regular cross-cloud communication.
- Negotiate **enterprise discount programs** (AWS EDP, Azure MACC, GCP CUDs) per provider despite split spend.
- Adopt **open-source tooling** (Prometheus, Grafana, ArgoCD) instead of commercial per-provider tools.
- Clearly define which workloads run where — avoid the "same workload on multiple clouds" anti-pattern unless required for DR.
- Consider whether the multi-cloud overhead justifies the benefit — for many organizations, **single-cloud with good architecture is more cost-effective** than multi-cloud.

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

## See Also

- `patterns/hybrid-cloud.md` — Hybrid cloud architecture spanning on-premises and public cloud
- `general/iac-planning.md` — Infrastructure as Code planning for cross-provider consistency
- `general/identity.md` — Identity federation across multiple environments
- `general/cost.md` — Cloud cost management including cross-provider FinOps
