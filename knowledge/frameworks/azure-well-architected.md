# Azure Well-Architected Framework

The Azure Well-Architected Framework provides architectural guidance for building high-quality solutions on Microsoft Azure. It is organized into five pillars that serve as the foundation for workload quality across the cloud.

---

## Pillar 1: Reliability

Focuses on ensuring a workload performs its intended function correctly and consistently. This includes the ability to recover from failures, meet availability targets, and handle demand changes.

### Design Principles

- Design for business requirements
- Design for resilience
- Design for recovery
- Design for operations
- Keep it simple

### Checklist

- [ ] Define availability targets (SLAs, SLOs, SLIs) for each workload tier based on business requirements
- [ ] Identify and mitigate single points of failure using redundancy across Availability Zones and regions
- [ ] Implement health modeling to distinguish between healthy, degraded, and unhealthy states
- [ ] Design for self-healing using Azure auto-restart, auto-scaling, and health probes
- [ ] Use retry policies with exponential backoff and circuit breaker patterns for transient fault handling
- [ ] Implement geo-redundancy for data (GRS/GZRS storage, geo-replication for databases)
- [ ] Define and test disaster recovery procedures with documented RTO and RPO targets
- [ ] Use Azure Traffic Manager or Front Door for multi-region traffic routing and failover
- [ ] Conduct failure mode analysis (FMA) during design to identify and mitigate potential failures
- [ ] Implement structured chaos engineering tests using Azure Chaos Studio
- [ ] Monitor reliability metrics and set alerts for SLO breaches using Azure Monitor
- [ ] Design workload components to degrade gracefully rather than fail completely under stress

### Why This Matters

Reliability is the most critical pillar because no other quality matters if the system is unavailable. Azure provides a wide array of redundancy and resilience features, but they must be deliberately designed into the architecture. Many outages stem not from Azure platform failures but from application-level design gaps: missing health checks, inadequate retry logic, or untested failover procedures. A reliable system is one that has been designed for failure and tested under failure conditions.

---

## Pillar 2: Security

Focuses on protecting the workload from threats, including data, identity, network, and application-level security concerns.

### Design Principles

- Plan resources and how to harden them
- Automate and use least privilege
- Classify and encrypt data
- Monitor and validate continuously
- Evolve with the threat landscape

### Checklist

- [ ] Use Microsoft Entra ID (Azure AD) for identity management with conditional access policies and MFA
- [ ] Implement least-privilege access using Azure RBAC and Privileged Identity Management (PIM)
- [ ] Segment networks using Virtual Networks, NSGs, and Azure Firewall with zero-trust principles
- [ ] Encrypt data at rest (Azure Storage Service Encryption, TDE for databases) and in transit (TLS 1.2+)
- [ ] Use Azure Key Vault for all secrets, certificates, and encryption key management
- [ ] Enable Microsoft Defender for Cloud for security posture management and threat protection
- [ ] Implement Azure DDoS Protection for public-facing workloads
- [ ] Use managed identities instead of credentials for service-to-service authentication
- [ ] Scan container images and application dependencies for vulnerabilities in the CI/CD pipeline
- [ ] Establish security baselines using Azure Policy and monitor compliance continuously
- [ ] Log all security events to a centralized SIEM (Microsoft Sentinel) for detection and response
- [ ] Conduct regular threat modeling using STRIDE or similar methodology during design reviews

### Why This Matters

Azure operates under a shared responsibility model: Microsoft secures the platform, but customers must secure their workloads, data, and identities. The expanding threat landscape means security must be automated and continuous, not a one-time gate. Microsoft Entra ID and Azure Policy provide powerful tools, but misconfiguration remains the leading cause of cloud security incidents. Defense in depth -- layering identity, network, application, and data controls -- is essential.

---

## Pillar 3: Cost Optimization

Focuses on reducing unnecessary expenditure and improving operational efficiency while maintaining full workload capability.

### Design Principles

- Develop cost-management discipline
- Design with a cost-efficiency mindset
- Design for usage optimization
- Design for rate optimization
- Monitor and optimize over time

### Checklist

- [ ] Establish a cost model and budget for each workload using Azure Cost Management + Billing
- [ ] Implement a tagging strategy for cost allocation, chargeback, and showback across teams
- [ ] Right-size compute resources using Azure Advisor recommendations and utilization data
- [ ] Use Azure Reserved Instances or Savings Plans for predictable, steady-state workloads
- [ ] Leverage Azure Spot VMs for fault-tolerant, interruptible batch and development workloads
- [ ] Select appropriate storage tiers (Hot, Cool, Cold, Archive) and configure lifecycle management
- [ ] Choose PaaS and serverless options (App Service, Functions, Cosmos DB serverless) over IaaS where feasible
- [ ] Set budget alerts and anomaly detection to catch unexpected spending early
- [ ] Shut down or scale down non-production environments outside business hours using automation
- [ ] Review Azure Advisor cost recommendations monthly and act on applicable suggestions
- [ ] Measure cost efficiency as cost per business unit (transaction, user, request) not just absolute spend
- [ ] Evaluate Azure Hybrid Benefit and dev/test pricing for applicable workloads

### Why This Matters

Cloud spending grows organically and can quickly exceed expectations. Azure provides granular billing data and optimization tools, but without organizational discipline, waste accumulates. Common sources of waste include oversized VMs, orphaned disks, always-on dev/test environments, and suboptimal storage tiering. Cost optimization is a continuous practice, not a one-time cleanup. The most effective approach combines technical right-sizing with financial governance and team accountability.

---

## Pillar 4: Operational Excellence

Focuses on the processes and practices that keep a workload running in production, including deployment, monitoring, and incident management.

### Design Principles

- Embrace DevOps culture
- Establish development standards
- Evolve operations with observability
- Deploy with confidence
- Automate for efficiency

### Checklist

- [ ] Use infrastructure as code (Bicep, ARM templates, Terraform) for all Azure resource provisioning
- [ ] Implement CI/CD pipelines (Azure DevOps, GitHub Actions) with automated testing and staged rollouts
- [ ] Instrument applications with Application Insights for distributed tracing, metrics, and logs
- [ ] Define and monitor operational health using Azure Monitor dashboards and workbooks
- [ ] Create and maintain runbooks in Azure Automation for routine operational tasks
- [ ] Implement blue-green or canary deployment strategies to reduce deployment risk
- [ ] Establish incident management processes with clear escalation paths and on-call rotations
- [ ] Conduct blameless post-incident reviews and feed learnings back into processes and automation
- [ ] Use Azure Resource Graph for cross-subscription inventory and compliance queries
- [ ] Automate compliance and governance checks using Azure Policy and management groups
- [ ] Maintain documentation for architecture decisions, operational procedures, and recovery plans
- [ ] Set up alerts with appropriate severity levels and actionable notifications (avoid alert fatigue)

### Why This Matters

Operational excellence bridges the gap between development and production. Without it, deployments are risky, incidents drag on, and teams cannot improve. Azure provides extensive monitoring and automation tools, but tools alone are insufficient. The organizational practices -- blameless postmortems, infrastructure as code discipline, deployment standards -- determine whether operations are predictable and improving or chaotic and reactive.

---

## Pillar 5: Performance Efficiency

Focuses on the ability of a workload to scale and meet the demands placed on it by users in an efficient manner.

### Design Principles

- Negotiate realistic performance targets
- Design to meet capacity requirements
- Achieve and sustain performance
- Improve efficiency through optimization
- Test and monitor proactively

### Checklist

- [ ] Define performance targets (latency, throughput, response time) based on user expectations and SLAs
- [ ] Select compute SKUs and configurations appropriate for workload characteristics and scale requirements
- [ ] Implement horizontal scaling with Azure VM Scale Sets, App Service auto-scale, or AKS cluster autoscaler
- [ ] Use Azure CDN or Front Door to cache static content and reduce latency for global users
- [ ] Implement application-level caching with Azure Cache for Redis for frequently accessed data
- [ ] Choose database services and tiers matched to query patterns (Cosmos DB, SQL Database, PostgreSQL Flexible)
- [ ] Use Azure Load Testing to validate performance under expected and peak load conditions
- [ ] Monitor performance metrics continuously and set alerts for degradation using Application Insights
- [ ] Optimize data access patterns: use read replicas, partitioning, and appropriate indexing strategies
- [ ] Evaluate asynchronous messaging patterns (Service Bus, Event Hubs) to decouple and scale components
- [ ] Profile application code to identify bottlenecks before scaling infrastructure
- [ ] Review Azure Advisor performance recommendations and new SKU options periodically

### Why This Matters

Performance directly impacts user experience and business outcomes. Slow applications lose users; systems that cannot scale under load lose revenue. Azure provides elastic scaling capabilities, but the architecture must be designed to take advantage of them. Common mistakes include monolithic designs that cannot scale horizontally, synchronous calls that create bottlenecks, and reliance on vertical scaling alone. Performance testing before production is essential -- assumptions about performance are frequently wrong.

---

## How to Use in Architecture Reviews

### When to Apply

- **New Azure workload design**: Evaluate all five pillars before committing to an architecture. Use the Azure Well-Architected Review assessment tool for structured guidance.
- **Workload modernization**: When migrating or modernizing existing applications on Azure, focus on pillars that represent the biggest gaps (often Reliability and Performance Efficiency for legacy workloads).
- **Architecture Decision Records**: Reference specific pillar guidance when documenting trade-off decisions.
- **Periodic health checks**: Conduct quarterly reviews using Azure Advisor and the Well-Architected assessment to track improvement.
- **Post-incident reviews**: Map incidents to pillar gaps to identify systemic improvements.

### How to Apply During a Design Session

1. **Prioritize pillars for the workload**: A customer-facing e-commerce application may weight Reliability and Performance Efficiency highest; an internal analytics platform may prioritize Cost Optimization. All pillars matter, but relative priority guides trade-off decisions.
2. **Walk through each pillar checklist**: Use the items as discussion prompts. Mark items as addressed, not applicable, or requiring follow-up.
3. **Identify Azure service choices**: For each component, evaluate whether the selected Azure service aligns with the pillar requirements. Consider PaaS and serverless options before IaaS.
4. **Document trade-offs**: When optimizing one pillar conflicts with another (e.g., multi-region for reliability increases cost), document the decision and rationale as an ADR.
5. **Run the Azure Well-Architected Review**: Use the official assessment at https://learn.microsoft.com/en-us/assessments/azure-architecture-review to get tailored recommendations.
6. **Create an action plan**: Prioritize identified gaps by business impact and create work items with owners and timelines.
7. **Integrate with Azure Advisor**: Enable Advisor recommendations aligned with each pillar for continuous, automated feedback.
