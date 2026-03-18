# AWS Well-Architected Framework

## Scope

Covers the six pillars of the AWS Well-Architected Framework (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability) with AWS-specific checklists and guidance for architecture reviews. Does not cover Azure (see `frameworks/azure-well-architected.md`) or GCP (see `frameworks/gcp-architecture-framework.md`) equivalents.

The AWS Well-Architected Framework helps cloud architects build secure, high-performing, resilient, and efficient infrastructure for their applications and workloads. It is organized into six pillars, each representing a foundational area of cloud architecture excellence.

---

## Pillar 1: Operational Excellence

Focuses on running and monitoring systems to deliver business value and continually improving supporting processes and procedures.

### Design Principles

- Perform operations as code
- Make frequent, small, reversible changes
- Refine operations procedures frequently
- Anticipate failure
- Learn from all operational failures

### Checklist

- [ ] **[Recommended]** Define operational priorities aligned with business outcomes
- [ ] **[Recommended]** Structure the organization to support workload ownership and accountability
- [ ] **[Recommended]** Establish an operational readiness review process before launching workloads
- [ ] **[Recommended]** Use infrastructure as code (CloudFormation, CDK, Terraform) for all environment provisioning
- [ ] **[Recommended]** Implement automated deployment pipelines with rollback capabilities
- [ ] **[Recommended]** Define and collect operational metrics and KPIs for all workloads
- [ ] **[Recommended]** Create runbooks and playbooks for routine and emergency operational procedures
- [ ] **[Recommended]** Establish event and alert management with appropriate escalation paths
- [ ] **[Critical]** Conduct post-incident analysis and feed learnings back into procedures
- [ ] **[Recommended]** Regularly review and evolve operational practices based on metrics and lessons learned
- [ ] **[Recommended]** Use feature flags and canary deployments to reduce blast radius of changes
- [ ] **[Recommended]** Ensure observability across all layers: application logs, traces, and metrics

### Why This Matters

Operational excellence ensures your workloads can be managed predictably over time. Without it, teams spend excessive time firefighting, changes carry high risk, and the organization cannot learn from failures. AWS services like CloudWatch, Systems Manager, and EventBridge support operational excellence, but the organizational practices matter more than the tools.

---

## Pillar 2: Security

Focuses on protecting information, systems, and assets while delivering business value through risk assessments and mitigation strategies.

### Design Principles

- Implement a strong identity foundation
- Enable traceability
- Apply security at all layers
- Automate security best practices
- Protect data in transit and at rest
- Keep people away from data
- Prepare for security events

### Checklist

- [ ] **[Critical]** Implement least-privilege access using IAM policies, roles, and permission boundaries
- [ ] **[Critical]** Enable multi-factor authentication (MFA) for all privileged accounts and root access
- [ ] **[Recommended]** Use AWS Organizations and SCPs to enforce governance guardrails across accounts
- [ ] **[Critical]** Enable CloudTrail in all regions and centralize logs for audit and detection
- [ ] **[Critical]** Configure GuardDuty, Security Hub, and Config Rules for continuous threat detection
- [ ] **[Critical]** Protect network boundaries with VPCs, security groups, NACLs, and WAF
- [ ] **[Critical]** Encrypt data at rest using KMS with customer-managed keys where appropriate
- [ ] **[Recommended]** Enforce TLS for all data in transit, including internal service-to-service communication
- [ ] **[Recommended]** Classify data and apply appropriate protection controls based on sensitivity
- [ ] **[Critical]** Develop and regularly test an incident response plan with defined roles and runbooks
- [ ] **[Critical]** Automate security controls using Config Rules, Lambda remediation, and pipeline checks
- [ ] **[Recommended]** Rotate credentials and secrets automatically using Secrets Manager or Parameter Store

### Why This Matters

Security is not optional or bolt-on; it must be foundational. A single misconfigured S3 bucket or overly permissive IAM role can expose an entire organization. The shared responsibility model means AWS secures the cloud, but you must secure what you build in it. Automated, layered security controls reduce human error and ensure consistent protection.

---

## Pillar 3: Reliability

Focuses on the ability of a workload to perform its intended function correctly and consistently when expected.

### Design Principles

- Automatically recover from failure
- Test recovery procedures
- Scale horizontally to increase aggregate workload availability
- Stop guessing capacity
- Manage change in automation

### Checklist

- [ ] **[Recommended]** Understand and manage service quotas and constraints across all AWS services used
- [ ] **[Critical]** Design network topology for high availability (multi-AZ, multi-Region where needed)
- [ ] **[Recommended]** Use loosely coupled, service-oriented architectures to isolate failure domains
- [ ] **[Critical]** Implement health checks, circuit breakers, and graceful degradation patterns
- [ ] **[Recommended]** Design idempotent operations to handle retries safely
- [ ] **[Recommended]** Use Auto Scaling to match capacity to demand automatically
- [ ] **[Recommended]** Automate change management through CI/CD pipelines with automated testing
- [ ] **[Recommended]** Back up data automatically and validate restoration procedures regularly
- [ ] **[Critical]** Design for and test failover to secondary regions or availability zones
- [ ] **[Recommended]** Conduct game days and chaos engineering exercises to validate resilience
- [ ] **[Recommended]** Implement distributed tracing to diagnose failures across microservices
- [ ] **[Recommended]** Define and track Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO)

### Why This Matters

Users expect systems to work. Reliability underpins all other pillars because an insecure but unavailable system, or a cost-optimized but unreliable one, delivers no value. AWS provides the building blocks (multi-AZ, Auto Scaling, Route 53 health checks), but reliability requires deliberate architectural decisions around failure isolation, testing, and recovery automation.

---

## Pillar 4: Performance Efficiency

Focuses on the efficient use of computing resources to meet requirements, and maintaining that efficiency as demand changes and technologies evolve.

### Design Principles

- Democratize advanced technologies
- Go global in minutes
- Use serverless architectures
- Experiment more often
- Consider mechanical sympathy

### Checklist

- [ ] **[Recommended]** Select compute resources (EC2, Lambda, Fargate, etc.) based on workload characteristics
- [ ] **[Recommended]** Choose storage solutions (S3, EBS, EFS, FSx) matched to access patterns and performance needs
- [ ] **[Recommended]** Select database engines and configurations optimized for query patterns and data models
- [ ] **[Recommended]** Design network architecture to minimize latency (CloudFront, Global Accelerator, placement groups)
- [ ] **[Recommended]** Use caching at multiple layers (ElastiCache, DAX, CloudFront, API Gateway caching)
- [ ] **[Recommended]** Implement load testing and benchmarking before production deployment
- [ ] **[Recommended]** Monitor resource utilization and set alarms for performance degradation
- [ ] **[Recommended]** Review new AWS services and instance types regularly for optimization opportunities
- [ ] **[Recommended]** Use auto-scaling and right-sizing tools (Compute Optimizer) to match resources to demand
- [ ] **[Recommended]** Evaluate trade-offs between consistency, latency, and throughput for each component
- [ ] **[Recommended]** Use asynchronous processing (SQS, SNS, EventBridge) to decouple and parallelize work
- [ ] **[Recommended]** Profile application code and optimize hot paths before scaling infrastructure

### Why This Matters

Performance efficiency is not just about speed; it is about using the right resources in the right configuration for your specific workload. Over-provisioning wastes money, under-provisioning degrades user experience. AWS continuously releases new instance types, managed services, and serverless options. Architectures that were optimal a year ago may no longer be the best choice.

---

## Pillar 5: Cost Optimization

Focuses on avoiding unnecessary costs, understanding spending, and selecting the most appropriate and right number of resource types.

### Design Principles

- Implement cloud financial management
- Adopt a consumption model
- Measure overall efficiency
- Stop spending money on undifferentiated heavy lifting
- Analyze and attribute expenditure

### Checklist

- [ ] **[Recommended]** Assign a Cloud Financial Management function or owner within the organization
- [ ] **[Recommended]** Implement tagging standards and enforce them for cost allocation and chargeback
- [ ] **[Critical]** Use AWS Cost Explorer, Budgets, and Cost Anomaly Detection for spending visibility
- [ ] **[Recommended]** Right-size instances and resources using Compute Optimizer and Trusted Advisor recommendations
- [ ] **[Recommended]** Purchase Savings Plans or Reserved Instances for stable, predictable workloads
- [ ] **[Recommended]** Use Spot Instances for fault-tolerant and flexible workloads
- [ ] **[Recommended]** Select appropriate storage tiers and implement lifecycle policies (S3 Intelligent-Tiering, Glacier)
- [ ] **[Recommended]** Evaluate managed services vs. self-managed to reduce operational overhead costs
- [ ] **[Recommended]** Decommission unused resources (idle instances, unattached EBS volumes, unused Elastic IPs)
- [ ] **[Recommended]** Measure cost per business outcome (cost per transaction, cost per user) not just total spend
- [ ] **[Recommended]** Review architecture periodically for cost optimization as new services and pricing models emerge
- [ ] **[Recommended]** Use AWS Graviton instances where compatible for better price-performance ratio

### Why This Matters

Cloud spending can grow unchecked without deliberate management. Cost optimization is not about cutting corners; it is about ensuring every dollar spent delivers business value. The pay-as-you-go model is only cost-effective if you match consumption to actual need. Organizations that treat cost optimization as an ongoing practice rather than a one-time exercise consistently achieve better outcomes.

---

## Pillar 6: Sustainability

Focuses on minimizing the environmental impacts of running cloud workloads.

### Design Principles

- Understand your impact
- Establish sustainability goals
- Maximize utilization
- Anticipate and adopt new, more efficient offerings
- Use managed services
- Reduce the downstream impact of your cloud workloads

### Checklist

- [ ] **[Recommended]** Select AWS Regions based on carbon intensity of the local electricity grid
- [ ] **[Recommended]** Analyze user behavior patterns and optimize for actual usage (scale down during off-peak)
- [ ] **[Recommended]** Implement efficient software patterns: minimize data movement, reduce polling, use event-driven architectures
- [ ] **[Recommended]** Optimize data storage: compress data, use lifecycle policies, deduplicate, and remove unnecessary copies
- [ ] **[Recommended]** Select the most efficient hardware: Graviton processors, right-sized instances, purpose-built accelerators
- [ ] **[Recommended]** Maximize utilization through auto-scaling, containerization, and serverless where appropriate
- [ ] **[Recommended]** Optimize development and deployment processes: reduce build frequency for unchanged components, use incremental builds
- [ ] **[Recommended]** Measure and track sustainability KPIs (carbon footprint per transaction, resource utilization rates)
- [ ] **[Recommended]** Use Amazon CodeGuru and profiling tools to identify and eliminate inefficient code paths
- [ ] **[Critical]** Minimize data transfer across regions and availability zones where possible
- [ ] **[Recommended]** Choose managed services over self-managed infrastructure to benefit from AWS efficiency at scale
- [ ] **[Recommended]** Set sustainability goals alongside performance, cost, and reliability targets in architecture decisions

### Why This Matters

Cloud computing is not inherently green; it simply shifts the environmental impact. AWS infrastructure is more energy-efficient than most on-premises data centers, but architects still bear responsibility for how efficiently they use those resources. Sustainability and cost optimization are often aligned: reducing waste lowers both bills and environmental impact.

---

## How to Use in Architecture Reviews

### When to Apply

- **New workload design**: Walk through all six pillars before finalizing architecture. Identify gaps and trade-offs explicitly.
- **Periodic reviews**: Schedule quarterly or semi-annual reviews of production workloads against the framework.
- **Post-incident**: After a significant incident, use the relevant pillar (usually Reliability or Security) to identify systemic gaps.
- **Before migration**: When moving workloads to AWS, use the framework to design the target architecture rather than lift-and-shift.
- **Cost reviews**: When cloud spend becomes a concern, focus on Cost Optimization and Performance Efficiency pillars together.

### How to Apply During a Design Session

1. **Start with business context**: Identify which pillars matter most for this workload. A financial trading system prioritizes Performance Efficiency and Reliability; a dev/test environment prioritizes Cost Optimization.
2. **Walk through each pillar systematically**: Use the checklists above as conversation starters. Not every item applies to every workload.
3. **Document trade-offs explicitly**: Record decisions where you intentionally deprioritized one pillar in favor of another (e.g., accepted higher cost for lower latency). Capture these as Architecture Decision Records (ADRs).
4. **Identify top risks**: For each pillar, identify the 2-3 highest-risk items and create action items to address them.
5. **Use the AWS Well-Architected Tool**: Run a formal review in the AWS console to generate a structured report and track improvements over time.
6. **Assign owners**: Each identified risk or improvement should have a clear owner and timeline.
7. **Revisit regularly**: Architecture is not a one-time activity. As workloads evolve, re-evaluate against the framework.

## Common Decisions (ADR Triggers)

- **Pillar prioritization** — which pillars to focus on first based on workload maturity and business needs
- **Cost optimization strategy** — reserved instances vs savings plans vs spot, rightsizing cadence
- **Resilience architecture** — single-region multi-AZ vs multi-region, RPO/RTO targets per workload tier
- **Security posture** — AWS-native security tools vs third-party, centralized vs distributed security model
- **Operational model** — IaC tooling (CloudFormation vs CDK vs Terraform), observability stack, deployment strategy
- **Performance optimization** — caching strategy, database selection, compute right-sizing methodology
- **Sustainability approach** — instance family selection for energy efficiency, right-sizing for carbon reduction
- **Well-Architected Review cadence** — how often to conduct reviews, remediation prioritization

## See Also

- `frameworks/azure-well-architected.md` — Azure Well-Architected Framework (five pillars)
- `frameworks/gcp-architecture-framework.md` — GCP Architecture Framework (six pillars)
- `providers/aws/vpc.md` — AWS VPC and networking configuration
- `general/cost.md` — Cloud cost optimization strategies
