# On-Premises Cost Modeling and TCO Analysis

## Checklist

- [ ] **[Critical]** Is the hardware depreciation schedule defined (3-year for performance-sensitive/fast-evolving hardware, 5-year for general compute), and is the monthly equivalent cost calculated for CapEx-to-OpEx comparison (monthly = purchase price / depreciation months)?
- [ ] **[Critical]** Are all software licensing costs captured including hypervisor (per-socket or per-core), management tools (per-node), backup (per-VM or per-TB), monitoring, and OS licenses -- with support/maintenance renewal costs for years 2-5?
- [ ] **[Critical]** Is power and cooling cost calculated per node using measured wattage (300-800W typical per 2U server), PUE multiplier (1.4-1.8 for enterprise DC), and local electricity rate ($/kWh), projected across the depreciation period?
- [ ] **[Recommended]** Are data center space costs included -- per-rack-unit monthly rates for colocation ($50-$200/U/mo depending on market), or allocated building/facilities cost for owned datacenters?
- [ ] **[Recommended]** Are network circuit costs included -- WAN/MPLS ($500-$5,000/mo per site), internet ($100-$2,000/mo per circuit), cross-connects ($100-$500/mo per cross-connect), and bandwidth overage charges?
- [ ] **[Recommended]** Is staffing overhead allocated -- what fraction of FTE time is dedicated to infrastructure management (server, storage, network, backup), and is this costed at fully-burdened rate ($120K-$200K/yr per FTE in US)?
- [ ] **[Recommended]** Is the TCO framework capturing all cost categories: CapEx (hardware, initial licensing), OpEx (power, cooling, space, circuits, support renewals), and staffing (allocated FTE time)?
- [ ] **[Recommended]** Is a cloud comparison analysis prepared using equivalent cloud configurations (instance types, storage tiers, networking) at 1-year, 3-year, and 5-year horizons including reserved/committed pricing?
- [ ] **[Optional]** Is hardware residual value estimated at end of depreciation period (typically 5-15% of original cost for 3-year-old servers, near zero for 5-year-old)?
- [ ] **[Optional]** Is opportunity cost considered -- what projects or innovations are deferred because team is spending time on infrastructure maintenance versus application development?
- [ ] **[Optional]** Are refresh cycle costs modeled -- when hardware reaches end-of-depreciation, what is the cost of the replacement cycle including migration labor, parallel running costs, and disposal/recycling?
- [ ] **[Recommended]** Are growth projections included -- is the cost model accounting for 20-30% annual capacity growth (industry average) and the "lumpiness" of on-prem scaling (must buy full nodes/racks vs. cloud's per-VM granularity)?
- [ ] **[Optional]** Is a financial model built that shows monthly burn rate to enable direct comparison with cloud's monthly billing model?

## Why This Matters

On-prem vs. cloud cost comparisons are the most frequently debated and most frequently wrong analysis in enterprise IT. On-prem advocates often undercount costs by including only hardware purchase price and ignoring power, cooling, space, staffing, and opportunity cost -- this makes on-prem appear 50-70% cheaper than cloud when the real difference may be 10-20% or even favoring cloud. Cloud advocates often compare list-price on-demand instances against fully depreciated on-prem hardware -- ignoring reserved instances, committed use discounts (40-60% off on-demand), and the fact that cloud costs scale linearly with consumption while on-prem costs are largely fixed after purchase. A rigorous TCO analysis is an ADR-worthy decision that should be revisited every 2-3 years as both cloud pricing and on-prem technology evolve. The analysis must also consider non-financial factors: speed of provisioning (minutes in cloud vs. weeks/months for on-prem procurement), data sovereignty requirements, and team skill sets.

## Common Decisions (ADR Triggers)

- **3-year vs 5-year depreciation** -- 3-year aligns with warranty periods and technology refresh cycles (newer hardware is ~20-30% more power efficient), creates higher monthly costs but avoids running out-of-warranty hardware. 5-year reduces monthly cost by ~40% but risks running hardware past peak reliability (failure rates increase significantly in years 4-5). Most enterprises use 3-year for compute, 5-year for network switches and power infrastructure.
- **CapEx vs OpEx (purchase vs lease/subscription)** -- Purchasing hardware is CapEx (balance sheet asset, depreciated over time, favorable for companies with available capital and tax depreciation benefits). Leasing or hardware-as-a-service (Dell APEX, HPE GreenLake, Nutanix NX-as-a-Service) converts to OpEx (monthly expense, no asset on books, easier budget approval in OpEx-oriented organizations). Subscription models typically cost 15-25% more over the hardware lifetime but provide flexibility and refresh guarantees.
- **Colocation vs owned datacenter** -- Colocation ($500-$2,500/mo per rack including power and cooling) provides professional DC facilities without building/managing them, scales from 1 rack to cages/suites, and allows geographic distribution. Owned DC provides full control and lower per-rack cost at scale (>50 racks) but requires significant CapEx, facilities team, and 18-24 month build timeline. Most enterprises below Fortune 500 use colocation.
- **Cloud repatriation threshold** -- Workloads that are stable (predictable resource consumption), long-running (24/7 not burst), and do not need cloud-native services (managed databases, serverless, AI/ML APIs) are candidates for on-prem at the 3-5 year horizon. The break-even point is typically 60-70% sustained utilization -- below that, cloud reserved instances are often cheaper. Each workload should be evaluated individually.
- **Software licensing: per-node vs per-core vs subscription** -- Per-node licensing (e.g., Nutanix, some backup products) favors dense nodes with many cores. Per-core licensing (e.g., SQL Server, Oracle, Red Hat) penalizes dense nodes -- consider deploying fewer cores per node or using Standard vs Enterprise editions. Subscription licensing (annual) provides current version access and support but creates recurring OpEx; perpetual licensing (one-time) is cheaper long-term but requires separate support contracts and may fall behind on versions.

## Cost Calculation Framework

### Per-Node Monthly Cost

```
Hardware (monthly)    = Purchase Price / (Depreciation Years x 12)
                      Example: $25,000 / (5 x 12) = $416.67/mo

Power (monthly)       = Node Watts x PUE x Hours/Month x $/kWh
                      Example: 500W x 1.5 x 730h x $0.10 = $54.75/mo

Cooling               = Included in PUE multiplier (above)

Space (colo, monthly) = Rack Units x $/RU/mo
                      Example: 2U x $75/U = $150/mo
                      (Or: $1,500/mo per rack / nodes per rack)
                      Example: $1,500 / 10 nodes = $150/mo

Software (monthly)    = Annual License & Support / 12
                      Example: $12,000/yr / 12 = $1,000/mo per node

Network (allocated)   = Circuit Costs / Nodes Served
                      Example: $3,000/mo circuits / 40 nodes = $75/mo

Staffing (allocated)  = (FTEs x Fully-Burdened Salary) / Nodes Managed
                      Example: (2 FTE x $180,000/yr) / 40 nodes / 12 = $750/mo

─────────────────────────────────────────────────────
TOTAL PER-NODE/MO   = $416.67 + $54.75 + $150 + $1,000 + $75 + $750
                    = $2,446.42/mo per node
```

### TCO Summary Template

| Cost Category | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 | Total |
|---|---|---|---|---|---|---|
| Hardware (CapEx) | $X | $0 | $0 | $0 | $0 | $X |
| Software licenses | $X | $X | $X | $X | $X | $5X |
| Support/maintenance | $X | $X | $X | $X | $X | $5X |
| Power & cooling | $X | $X | $X | $X | $X | $5X |
| DC space (colo) | $X | $X | $X | $X | $X | $5X |
| Network circuits | $X | $X | $X | $X | $X | $5X |
| Staffing (allocated) | $X | $X | $X | $X | $X | $5X |
| **Total** | | | | | | **$TCO** |
| Residual value | | | | | -$R | -$R |
| **Net TCO** | | | | | | **$TCO - $R** |

### Cloud Comparison Template

| Metric | On-Prem (5yr) | Cloud On-Demand (5yr) | Cloud Reserved (5yr) |
|---|---|---|---|
| Compute | $X | $Y (list price) | $Z (1yr RI/CUD) |
| Storage | $X | $Y | $Z |
| Networking | $X | $Y (egress!) | $Z |
| Licensing | $X | Included or BYOL | Included or BYOL |
| Staffing | $X | $X (reduced ~30%) | $X (reduced ~30%) |
| **Total** | **$A** | **$B** | **$C** |
| Break-even utilization | N/A | >X% sustained | >Y% sustained |

**Key cloud cost traps:**
- Data egress charges ($0.08-$0.12/GB) can dominate costs for data-heavy workloads
- Cloud storage (EBS, managed disks) is 5-10x more expensive per TB than local NVMe
- Cloud networking (load balancers, NAT gateways, VPN connections) adds $200-$1,000+/mo in hidden costs
- Licensing in cloud: SQL Server on AWS/Azure can be 2-4x more expensive than on-prem with Software Assurance

## Common Software Licensing Models

| Vendor/Product | Model | Approximate Cost | Notes |
|---|---|---|---|
| Nutanix (NCI) | Per-node, subscription | $5,000-$15,000/node/yr | Starter/Pro/Ultimate tiers |
| VMware vSphere | Per-core, subscription | $200-$500/core/yr | Changed from per-socket to per-core in 2024 |
| Red Hat Enterprise Linux | Per-socket-pair | $800-$1,500/yr | Standard/Premium support tiers |
| Microsoft Windows Server | Per-core (min 16/server) | $800-$6,000/server | Standard (2 VMs) vs Datacenter (unlimited VMs) |
| SQL Server | Per-core (min 4) | $3,700-$15,000/core | Standard vs Enterprise, SA adds ~25%/yr |
| Veeam Backup | Per-VM or per-workload | $50-$200/VM/yr | Universal License model |
| Commvault | Per-TB front-end | Varies widely | Complex licensing, get quote |

## Reference Architectures

- **Gartner TCO Model**: Gartner publishes comprehensive TCO methodologies for infrastructure comparison -- available to Gartner subscribers, frequently cited in enterprise decision-making
- **AWS TCO Calculator**: [calculator.aws](https://calculator.aws/) -- useful for generating cloud-side costs for comparison, but note it is designed to favor cloud (does not include all on-prem cost reductions)
- **Nutanix TCO Calculator**: Available through Nutanix sales -- models HCI-specific TCO against traditional three-tier and cloud, includes power/cooling/space
- **Uptime Institute PUE**: [uptimeinstitute.com](https://uptimeinstitute.com/) -- industry benchmarks for Power Usage Effectiveness; global average is ~1.58, best-in-class hyperscalers achieve 1.1-1.2
- **IDC CloudTrack**: IDC research on cloud vs on-prem cost comparison across enterprise segments -- useful for benchmarking your analysis against industry data
- **FinOps Foundation**: [finops.org](https://www.finops.org/) -- practices for cloud financial management; applicable to on-prem cost discipline as well
