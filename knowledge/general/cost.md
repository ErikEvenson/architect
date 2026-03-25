# Cost Management and FinOps Strategy

## Scope

This file covers **what** cost management decisions need to be made during architecture design: budgeting, right-sizing, commitment discounts, cost allocation, FinOps practices, and optimization strategies. Provider-specific pricing models, cost tools, and discount programs vary; consult individual provider documentation for implementation details.

## Checklist

- [ ] **[Critical]** Produce a cost estimate for the proposed architecture before deployment (use provider calculators — AWS Pricing Calculator, Azure Pricing Calculator, GCP Pricing Calculator — with realistic assumptions for compute, storage, network, and managed service usage; include a 15-25% buffer for unexpected costs; compare at least two deployment options)
- [ ] **[Critical]** Define commitment strategy for predictable workloads (Reserved Instances offer up to 72% savings with 1- or 3-year terms and capacity reservation; Savings Plans offer flexibility across instance families at slightly lower discounts; on-demand is appropriate for variable or short-lived workloads — never commit before establishing a 2-3 month usage baseline)
- [ ] **[Critical]** Implement cost allocation tagging strategy across all resources (tag by project, environment, team/owner, cost center, and application tier; enforce tagging via policy engines like AWS SCC, Azure Policy, or GCP Organization Policy; untagged resources are invisible to cost analysis and become orphaned spend)
- [ ] **[Critical]** Establish budget alerts with escalating notification thresholds (set alerts at 50%, 75%, 90%, and 100% of monthly budget; route alerts to both engineering and finance stakeholders; consider automated actions at threshold — e.g., block non-production deployments at 90%, but never auto-terminate production workloads)
- [ ] **[Recommended]** Conduct right-sizing analysis using utilization data, not initial estimates (collect 2-4 weeks of CPU, memory, disk, and network metrics before selecting instance types; target 60-70% average utilization for production and 40-50% for burst-capable workloads; re-evaluate quarterly as workload patterns change — over-provisioned instances are the single largest source of cloud waste)
- [ ] **[Recommended]** Design egress cost management into the network architecture from the start (cross-AZ data transfer costs $0.01-0.02/GB and accumulates at scale; cross-region transfer costs $0.02-0.09/GB; internet egress costs $0.05-0.12/GB; mitigate with VPC endpoints for AWS service traffic, CDN for content delivery, data compression, and regional data locality — monitor egress as a first-class metric)
- [ ] **[Recommended]** Configure storage tier lifecycle policies to move data automatically (hot storage for active access at highest cost; warm/infrequent-access for data accessed less than monthly at 40-60% savings; cold/archive for compliance retention at 80-90% savings — set lifecycle rules based on access frequency analysis, not guesswork; account for retrieval costs and latency when tiering)
- [ ] **[Recommended]** Evaluate license optimization across the estate (BYOL reduces cloud costs when existing licenses have Software Assurance or equivalent mobility rights; license-included instances simplify management but may cost more at scale; consider license-free alternatives like PostgreSQL over SQL Server, or Linux over Windows Server — the Azure Hybrid Benefit and AWS License Manager can track entitlements)
- [ ] **[Recommended]** Build a Total Cost of Ownership comparison when evaluating cloud migration or multi-cloud (include compute, storage, network, licensing, labor, training, migration effort, and opportunity cost; on-premises TCO must include power, cooling, floor space, hardware refresh cycles, and staffing — avoid comparing only list prices without factoring operational overhead)
- [ ] **[Recommended]** Implement cost anomaly detection to catch unexpected spend early (enable provider-native tools — AWS Cost Anomaly Detection, Azure Cost Management anomaly alerts, GCP billing anomaly notifications; set sensitivity to flag deviations above 20% from baseline; investigate anomalies within 24 hours — common causes include runaway auto-scaling, forgotten dev environments, and data transfer spikes)
- [ ] **[Recommended]** Define showback or chargeback model for multi-team environments (showback reports costs by team or project for visibility without financial accountability; chargeback allocates actual costs to business unit budgets and drives accountability; shared infrastructure costs like networking and security tools must be allocated fairly — per-resource usage, headcount-proportional, or even-split depending on organizational maturity)
- [ ] **[Optional]** Identify workloads suitable for spot or preemptible instances (batch processing, CI/CD pipelines, stateless workers, and dev/test environments tolerate interruption; savings of 60-90% over on-demand; implement graceful interruption handling with 2-minute warning hooks; use diversified instance pools and fallback to on-demand to maintain availability)
- [ ] **[Optional]** Establish a FinOps practice with defined roles, cadence, and tooling (assign cost ownership to engineering teams, not just finance; conduct monthly cost reviews comparing actual vs. forecast; use tools like Infracost for pre-deployment cost estimation in CI/CD pipelines; track unit economics — cost per transaction, cost per user, cost per GB stored — not just total spend)
- [ ] **[Optional]** Schedule regular cleanup of unused and orphaned resources (unattached EBS volumes, old snapshots, idle load balancers, unused Elastic IPs, stale DNS records, and non-production environments left running overnight and weekends; automate shutdown schedules for dev/test environments to save 65% on those resources; run cleanup scripts monthly at minimum)

## Why This Matters

Cloud cost overruns are among the most common and preventable problems in infrastructure management. Without deliberate cost controls, organizations routinely spend 30-50% more than necessary — the result of over-provisioned instances selected during initial deployment and never re-evaluated, forgotten development environments running 24/7, and data transfer patterns that were never analyzed. Unlike traditional IT procurement where costs are fixed at purchase time, cloud spending is continuous and elastic, which means waste compounds silently month after month.

Commitment discounts (Reserved Instances, Savings Plans) represent the single largest cost optimization lever, offering 30-72% savings for predictable workloads. However, committing too early or to the wrong instance families locks in waste. The right approach is to establish a usage baseline on on-demand pricing for 2-3 months, then commit to the predictable portion while keeping variable workloads on on-demand or spot. Organizations that skip this step either miss massive savings or commit to resources they do not actually need.

FinOps — the practice of bringing financial accountability to cloud spending — is not just a tooling problem. It requires cultural change: engineering teams must see cost as a first-class architecture concern alongside performance, security, and reliability. Without showback or chargeback, teams have no feedback loop connecting their design decisions to their cost impact. The organizations that manage cloud costs effectively treat cost optimization as a continuous practice with monthly reviews, not a one-time cleanup exercise.

## Common Decisions (ADR Triggers)

### ADR: Commitment Discount Strategy

**Context:** The organization has established workloads running on cloud infrastructure and wants to reduce costs below on-demand pricing.

**Options:**

| Criterion | Reserved Instances (RI) | Savings Plans (SP) | On-Demand | Spot/Preemptible |
|---|---|---|---|---|
| Discount Range | 40-72% (3-year, all upfront) | 30-66% (3-year, all upfront) | 0% (baseline) | 60-90% |
| Flexibility | Locked to instance type, region, OS | Flexible across instance families (compute SP) or any usage (EC2 SP) | Full flexibility | Full flexibility, but interruptible |
| Commitment | 1- or 3-year term | 1- or 3-year term, $/hour commitment | None | None |
| Capacity Reservation | Yes (zonal RIs) | No | No | No |
| Best Fit | Stable, well-understood workloads in fixed regions | Workloads that may change instance families or regions over time | Variable workloads, new projects, pre-baseline | Batch jobs, CI/CD, stateless workers |

**Decision drivers:** Workload stability and predictability, planning horizon, flexibility requirements, and upfront payment tolerance. Most organizations benefit from a blended approach: 60-70% committed coverage for baseline, on-demand for variable, spot for fault-tolerant batch.

### ADR: Cost Allocation and Accountability Model

**Context:** Multiple teams share cloud infrastructure and the organization needs visibility into who is spending what and why.

**Options:**
- **Showback (visibility only):** Finance reports costs by team or project monthly. Teams see their spend but are not financially accountable. Low friction to implement. Does not change behavior without management reinforcement.
- **Chargeback (financial accountability):** Actual cloud costs are allocated to business unit budgets. Strong incentive to optimize. Requires accurate tagging, fair allocation of shared costs, and finance system integration. Can create friction if shared infrastructure costs are allocated unfairly.
- **Hybrid (showback with guardrails):** Teams see costs and have budget thresholds with alerts, but are not directly billed. Balances visibility and accountability without full chargeback complexity. Most common starting point.

**Recommendation:** Start with showback and mandatory tagging. Graduate to chargeback only after tagging coverage exceeds 90% and teams have had 2-3 months to understand their cost profiles. Attempting chargeback with poor tagging creates inaccurate allocations that undermine trust.

### ADR: Right-Sizing and Auto-Scaling Strategy

**Context:** Initial instance types were selected based on estimates, and actual utilization data is now available.

**Options:**
- **Manual right-sizing (quarterly review):** Review utilization metrics, resize instances during maintenance windows. Low risk, full control. Labor-intensive, changes lag behind workload shifts.
- **Automated right-sizing recommendations (AWS Compute Optimizer, Azure Advisor, GCP Recommender):** Provider tools analyze utilization and suggest smaller or larger instances. Requires human approval before changes. Good balance of automation and control.
- **Auto-scaling with target tracking:** Automatically add or remove instances to maintain a target utilization (e.g., 70% CPU). Responds to demand in real-time. Requires stateless application design and proper health checks. Risk of runaway scaling without max-instance guardrails.

**Decision drivers:** Workload variability, application statefulness, team operational capacity, and risk tolerance for automated changes.

### ADR: Egress Cost Optimization

**Context:** Data transfer costs are a significant and growing portion of the cloud bill, especially in multi-region or hybrid architectures.

**Options:**
- **VPC endpoints and private connectivity:** Eliminate NAT gateway and internet egress charges for cloud service API traffic. AWS S3 gateway endpoints are free; interface endpoints cost $0.01/hour + data processing. Significant savings for S3-heavy workloads.
- **CDN for content delivery:** Cache and serve static content from edge locations. Reduces origin egress and improves latency. Most effective for read-heavy, cacheable content. CDN data transfer is typically cheaper than direct egress.
- **Data compression and protocol optimization:** Compress data in transit (gzip, zstd) to reduce transferred bytes by 60-80% for text-based payloads. Use efficient serialization formats (Protocol Buffers, MessagePack) instead of verbose JSON for high-volume internal APIs.
- **Regional data locality:** Keep compute and storage in the same region. Avoid cross-region data transfer by deploying read replicas and caches locally. Design event-driven architectures to process data where it is generated.

**Decision drivers:** Traffic volume and patterns, data compressibility, latency requirements, and whether traffic is internal (service-to-service) or external (user-facing).

## See Also

- `general/compute.md` — Instance type selection and compute architecture decisions
- `general/networking.md` — Network architecture including data transfer paths
- `general/observability.md` — Monitoring and observability including cost metric dashboards
- `general/finops.md` — FinOps practices, frameworks, tooling, and organizational cost management at scale
- `general/cost-onprem.md` — On-premises cost modeling, TCO analysis, hardware depreciation, and cloud comparison frameworks
