# Hybrid Cloud Architecture

## Scope

Covers architectures spanning on-premises infrastructure and one or more public cloud providers, including connectivity, identity federation, workload placement, data synchronization, and unified operations. Applicable when workloads must be distributed across on-prem and cloud due to data residency, latency, compliance, cost, or migration phasing.

## Overview

Hybrid cloud spans on-premises infrastructure and one or more public cloud providers. Workloads are distributed based on requirements for data residency, latency, compliance, or cost.

## Checklist

- [ ] **[Critical]** What workloads stay on-premises vs move to cloud? What is the decision criteria?
- [ ] **[Critical]** How are on-premises and cloud networks connected? (VPN, dedicated connection, SD-WAN)
- [ ] **[Recommended]** What is the bandwidth and latency between on-premises and cloud?
- [ ] **[Critical]** Is there a single identity provider across both environments? (AD federation, SAML, OIDC)
- [ ] **[Recommended]** How is DNS managed across both environments? (split-horizon DNS)
- [ ] **[Critical]** Are there data residency or sovereignty requirements keeping data on-premises?
- [ ] **[Recommended]** How are workloads deployed consistently across both environments? (same CI/CD, IaC)
- [ ] **[Recommended]** Is there a container orchestration platform spanning both? (Kubernetes — Tanzu, Karbon, EKS Anywhere)
- [ ] **[Recommended]** How is monitoring unified across both environments? (single pane of glass)
- [ ] **[Critical]** How are secrets managed across both environments?
- [ ] **[Critical]** What is the DR strategy? (cloud as DR for on-prem, or vice versa)
- [ ] **[Recommended]** How is data synchronized between on-premises and cloud?
- [ ] **[Recommended]** Are there licensing considerations for on-premises software in the cloud? (BYOL vs cloud-native)
- [ ] **[Optional]** What is the migration path for workloads that may move to cloud later?

## Why This Matters

Hybrid cloud is a transitional or permanent state for most enterprises, not a temporary inconvenience. Treating cloud as "another data center" misses cloud-native benefits. Unreliable connectivity between environments causes cascading failures. Different security postures on-prem vs cloud create compliance gaps. Without unified monitoring, blind spots in one environment hide issues until they become outages. Tight coupling between on-prem and cloud workloads introduces latency-sensitive cross-environment calls that fail under load. Inconsistent identity management across environments creates security gaps and operational burden.

## Common Decisions (ADR Triggers)

- **Connectivity model** — VPN vs dedicated connection (Direct Connect, ExpressRoute), redundancy requirements, bandwidth planning
- **Workload placement** — criteria for on-prem vs cloud placement, data gravity, latency requirements, compliance constraints
- **Identity federation** — single IdP across both environments, directory sync approach, service account strategy
- **Monitoring unification** — single pane of glass tool selection, metric aggregation, alert routing across environments
- **Data synchronization** — replication strategy, consistency model, bandwidth budget for cross-environment data transfer
- **Kubernetes strategy** — single cluster spanning both vs separate clusters with federation, platform selection (Tanzu, Karbon, EKS Anywhere)
- **DR model** — cloud as DR target for on-prem, or on-prem as fallback, RPO/RTO alignment across environments
- **Migration path** — how workloads transition from on-prem to cloud over time, hybrid duration planning

## Cost Benchmarks

> **Disclaimer:** Prices are rough estimates based on AWS us-east-1 pricing as of early 2025. Actual costs vary by region, reserved instance commitments, and usage patterns. Prices change over time — always verify with the provider's pricing calculator.

### Connectivity Costs

| Connection Type | Monthly Cost | Bandwidth | Notes |
|----------------|-------------|-----------|-------|
| Site-to-Site VPN (2 tunnels) | $75 | Up to 1.25 Gbps per tunnel | Cheapest option; internet-dependent latency |
| AWS Direct Connect (1 Gbps, dedicated) | $220 port fee + partner circuit ($500-2,000) | 1 Gbps dedicated | Consistent latency; hosted connections provision in hours-days, dedicated connections take weeks-months depending on location |
| AWS Direct Connect (10 Gbps, dedicated) | $1,575 port fee + partner circuit ($2,000-8,000) | 10 Gbps dedicated | High throughput; required for large data volumes |
| Direct Connect hosted connection (500 Mbps) | $100 port fee + partner fees ($300-800) | 500 Mbps shared | Lower cost entry to dedicated connectivity |
| Redundant Direct Connect (2x 1 Gbps) | ~$1,440 + 2x partner circuits | 2 Gbps total | Required for production HA |

### Data Transfer Costs

| Transfer Type | Cost per GB | Notes |
|--------------|------------|-------|
| Inbound to AWS (from on-prem) | Free | Ingress is free |
| Outbound from AWS (to on-prem) via internet | $0.09 | First 10 TB/mo; decreases with volume |
| Outbound from AWS via Direct Connect | $0.02 | Significant savings over internet egress |
| Cross-region transfer within AWS | $0.02 | Between AWS regions |
| VPN data transfer out | $0.09 | Same as internet egress |

### Example: Split Infrastructure Deployment

#### Small Hybrid (dev/test in cloud, production on-prem)

| Component | Monthly Estimate |
|-----------|-----------------|
| VPN connectivity (2 tunnels) | $75 |
| Data transfer (100 GB/mo outbound) | $9 |
| Transit Gateway (for VPN attachment) | $40 |
| Cloud workloads (3x t3.medium dev/test) | $90 |
| Route 53 (hybrid DNS) | $5 |
| **Total cloud cost** | **~$220/mo** |

#### Medium Hybrid (burst to cloud, data on-prem)

| Component | Monthly Estimate |
|-----------|-----------------|
| Direct Connect (1 Gbps) + partner circuit | $1,200 |
| Data transfer (1 TB/mo via DX) | $20 |
| Cloud compute (burst: 10x m6i.large, avg 50% utilization) | $1,400 |
| Transit Gateway + attachments | $110 |
| CloudWatch + monitoring | $50 |
| **Total cloud cost** | **~$2,780/mo** |

#### Large Hybrid (multi-site, cloud-primary)

| Component | Monthly Estimate |
|-----------|-----------------|
| Redundant Direct Connect (2x 10 Gbps) + circuits | $12,000 |
| Data transfer (10 TB/mo via DX) | $200 |
| Cloud compute (production workloads) | $15,000 |
| Transit Gateway (multi-VPC, multi-site) | $500 |
| AWS Outposts (on-prem, 1 rack) | $7,000 |
| Hybrid monitoring (CloudWatch + on-prem agents) | $300 |
| **Total cloud cost** | **~$35,000/mo** |

### Biggest Cost Drivers

1. **Dedicated connectivity** — Direct Connect port fees plus partner/colocation circuit costs are the baseline. Redundant connections double the cost.
2. **Data transfer (egress)** — cloud-to-on-prem transfer at $0.02-$0.09/GB. High-volume workloads must use Direct Connect for the $0.02 rate.
3. **Duplicate infrastructure** — running the same workload both on-prem and in cloud during migration or for DR doubles costs temporarily.

### Optimization Tips

- Use **Direct Connect** instead of VPN for any data transfer exceeding 500 GB/mo — the $0.02/GB vs $0.09/GB rate pays for the circuit quickly.
- Process data **where it lives** — avoid round-tripping large datasets between on-prem and cloud.
- Use **AWS Storage Gateway** or **DataSync** for efficient on-prem-to-cloud data movement.
- Consider **AWS Outposts** when cloud services are needed on-prem (consistent APIs, avoids data movement).
- Plan migrations to **minimize the hybrid period** — dual-running environments are the most expensive phase.
- Use **Reserved Instances** for stable cloud workloads in hybrid deployments.

## Key Patterns

- **Cloud Bursting**: overflow to cloud during peak demand
- **Tiered Hybrid**: different tiers in different environments (e.g., app in cloud, data on-prem)
- **DR to Cloud**: on-prem primary, cloud standby for disaster recovery
- **Edge + Cloud**: edge processing on-prem, aggregation and analytics in cloud
- **Lift and Shift → Refactor**: migrate first, optimize later

## Vendor-Anchored Variants

When the on-prem side is anchored on a specific vendor's infrastructure, the generic hybrid pattern composes with vendor-specific integration points (control planes, SD-WAN backbones, identity bridges, workload-mobility tooling, observability layers). Per-vendor hybrid pattern files cover that connecting layer:

- `patterns/hpe-hybrid-cloud.md` -- HPE-anchored hybrid: GreenLake Central, Aruba EdgeConnect SD-WAN, Azure Arc / AWS Outposts / Anthos integration, Zerto / Morpheus / OpsRamp
- `patterns/dell-hybrid-cloud.md` -- Dell-anchored hybrid: APEX Console, Dell-Microsoft alliance (APEX Cloud Platform for Microsoft Azure), PowerProtect Data Manager + Cyber Recovery, CloudIQ
- `patterns/cisco-hybrid-cloud.md` -- Cisco-anchored hybrid (compute and network led): Intersight, Catalyst SD-WAN with cloud onramps, UCS X-Series, ThousandEyes + AppDynamics, ISE / Duo
- `patterns/lenovo-hybrid-cloud.md` -- Lenovo-anchored hybrid (Microsoft-aligned): TruScale, ThinkAgile MX (Azure Stack HCI on Lenovo), XClarity One, Veeam partnership
- `patterns/pure-hybrid-cloud.md` -- Pure-Storage-anchored hybrid (storage-led; composes with a compute-anchored pattern): Cloud Block Store, ActiveCluster, CloudSnap, Portworx, Pure1

## See Also

- `patterns/multi-cloud.md` — Multi-cloud architecture using multiple public cloud providers
- `general/networking.md` — Network architecture including VPN, dedicated connectivity, and DNS
- `general/disaster-recovery.md` — DR planning including cloud-as-DR-target for on-premises
- `patterns/migration-cutover.md` — Cutover procedures for migrating workloads between environments
