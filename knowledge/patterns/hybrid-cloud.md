# Hybrid Cloud Architecture

## Overview

Hybrid cloud spans on-premises infrastructure and one or more public cloud providers. Workloads are distributed based on requirements for data residency, latency, compliance, or cost.

## Checklist

- [ ] What workloads stay on-premises vs move to cloud? What is the decision criteria?
- [ ] How are on-premises and cloud networks connected? (VPN, dedicated connection, SD-WAN)
- [ ] What is the bandwidth and latency between on-premises and cloud?
- [ ] Is there a single identity provider across both environments? (AD federation, SAML, OIDC)
- [ ] How is DNS managed across both environments? (split-horizon DNS)
- [ ] Are there data residency or sovereignty requirements keeping data on-premises?
- [ ] How are workloads deployed consistently across both environments? (same CI/CD, IaC)
- [ ] Is there a container orchestration platform spanning both? (Kubernetes — Tanzu, Karbon, EKS Anywhere)
- [ ] How is monitoring unified across both environments? (single pane of glass)
- [ ] How are secrets managed across both environments?
- [ ] What is the DR strategy? (cloud as DR for on-prem, or vice versa)
- [ ] How is data synchronized between on-premises and cloud?
- [ ] Are there licensing considerations for on-premises software in the cloud? (BYOL vs cloud-native)
- [ ] What is the migration path for workloads that may move to cloud later?

## Common Mistakes

- Treating cloud as just "another data center" (missing cloud-native benefits)
- Unreliable connectivity between environments (no redundant connections)
- Different security postures on-prem vs cloud (inconsistent compliance)
- No unified monitoring (blind spots in one environment)
- Tight coupling between on-prem and cloud workloads (latency-sensitive cross-environment calls)
- No consistent identity management (separate credentials per environment)

## Key Patterns

- **Cloud Bursting**: overflow to cloud during peak demand
- **Tiered Hybrid**: different tiers in different environments (e.g., app in cloud, data on-prem)
- **DR to Cloud**: on-prem primary, cloud standby for disaster recovery
- **Edge + Cloud**: edge processing on-prem, aggregation and analytics in cloud
- **Lift and Shift → Refactor**: migrate first, optimize later
