# Capacity Planning

## Scope

This file covers **capacity planning and performance sizing** including load testing, growth projections, auto-scaling validation, database connection limits, and cost projection. For compute instance selection, see `general/compute.md`. For testing strategies including load testing tools, see `general/testing-strategy.md`.

## Checklist

- [ ] **[Recommended]** What sizing methodology is used? (bottleneck analysis, queuing theory, empirical load testing, historical trend extrapolation)
- [ ] **[Recommended]** Which load testing tool is used? (k6 for developer-friendly scripting, Locust for Python-based distributed tests, Gatling for JVM, JMeter for protocol breadth)
- [ ] **[Critical]** Are performance benchmarks established for current baseline? (request latency p50/p95/p99, throughput RPS, error rate, resource utilization under load)
- [ ] **[Recommended]** What are the growth projections? (user growth rate, data growth rate, traffic seasonality, planned marketing campaigns or launches)
- [ ] **[Recommended]** Is 20-30% headroom maintained above peak projected load? (buffer for unexpected spikes, degradation before scaling kicks in)
- [ ] **[Recommended]** How is burst capacity handled? (auto-scaling response time, pre-warming, reserved burst capacity, CDN absorption of traffic spikes)
- [ ] **[Recommended]** Is auto-scaling validated under realistic conditions? (scale-up speed vs traffic ramp rate, scale-down cooldown, oscillation prevention)
- [ ] **[Critical]** What are the database connection limits? (max connections per instance, connection pooling configuration — PgBouncer, RDS Proxy, ProxySQL)
- [ ] **[Recommended]** How is network bandwidth planned? (inter-AZ traffic, egress costs, VPN throughput limits, API gateway throttling)
- [ ] **[Recommended]** What is the storage growth forecast? (data retention policy impact, log volume, backup storage, archive tiering strategy)
- [ ] **[Optional]** How is the capacity plan translated to cost projection? (instance sizing to pricing, reserved instance coverage, cost per transaction/user)
- [ ] **[Critical]** Are there known bottlenecks or single points of saturation? (single database writer, NAT gateway throughput, load balancer limits, DNS query limits)
- [ ] **[Optional]** What is the load testing cadence? (pre-release, quarterly, before major events — automated performance regression testing in CI/CD)
- [ ] **[Optional]** How are capacity limits communicated to the business? (maximum supported users, degradation thresholds, cost per additional capacity tier)

## Why This Matters

Under-provisioning causes outages during peak traffic. Over-provisioning wastes money continuously. Without load testing, capacity is guesswork — teams discover limits during production incidents instead of planned tests. Auto-scaling is not instant; it takes 2-10 minutes to provision new instances, during which traffic must be absorbed by existing capacity (hence the headroom requirement). Database connection limits are the most common unplanned bottleneck — a 100-connection limit shared across 20 application instances means only 5 connections per instance. Storage growth is predictable but frequently ignored until disks fill up. Translating capacity plans into cost projections lets the business make informed decisions about growth investment vs architecture changes.

## Common Decisions (ADR Triggers)

- **Sizing approach** — empirical (load test and measure) vs analytical (model-based), frequency of re-validation
- **Load testing tool** — k6 vs Locust vs Gatling, distributed load generation setup, realistic traffic patterns vs synthetic
- **Headroom policy** — percentage buffer above peak (20-30% typical), cost justification, review cadence
- **Auto-scaling configuration** — scaling metric (CPU, memory, request count, custom), thresholds, cooldown periods, instance limits
- **Database connection strategy** — connection pooler selection (PgBouncer, RDS Proxy), pool sizing formula, read replica connection routing
- **Storage tiering** — hot/warm/cold storage lifecycle, data retention policy, archive strategy (Glacier, Archive Storage)
- **Burst capacity approach** — pre-provisioned reserve vs pure auto-scaling vs CDN/edge absorption vs queue-based load leveling
- **Performance budget** — latency targets per endpoint (p99 < 500ms), error rate thresholds, degradation graceful fallbacks
- **Cost modeling** — cost per user/transaction at scale, reserved vs on-demand ratio, break-even analysis for architectural changes

## See Also

- [compute.md](compute.md) -- compute instance selection and sizing
- [testing-strategy.md](testing-strategy.md) -- load testing tools and performance testing strategies
- [cost.md](cost.md) -- cloud cost optimization and reserved instance planning
- [hardware-sizing.md](hardware-sizing.md) -- physical server hardware selection for on-premises capacity
