# GCP Architecture Framework

The Google Cloud Architecture Framework provides best practices and implementation recommendations to help architects, developers, and administrators design and operate cloud topologies on Google Cloud. It is organized into six pillars that cover the full spectrum of cloud workload quality.

---

## Pillar 1: System Design

Focuses on designing cloud systems that meet functional and non-functional requirements using Google Cloud services and patterns effectively.

### Design Principles

- Design for change and growth
- Use managed services where possible
- Design for horizontal scalability
- Decouple components for independent deployment
- Design for observability from the start

### Checklist

- [ ] **[Critical]** Define system requirements (availability, latency, throughput, data residency) before selecting services
- [ ] **[Critical]** Choose between regional, multi-regional, and global architectures based on user distribution and availability needs
- [ ] **[Recommended]** Use managed services (Cloud Run, Cloud SQL, BigQuery, Pub/Sub) to reduce operational burden
- [ ] **[Recommended]** Design for loose coupling using asynchronous messaging (Pub/Sub, Cloud Tasks) between components
- [ ] **[Recommended]** Implement API-first design with Cloud Endpoints or Apigee for service interfaces
- [ ] **[Recommended]** Select appropriate compute platforms: GKE for containerized workloads, Cloud Run for stateless services, Compute Engine for custom VM requirements
- [ ] **[Recommended]** Design data architecture with appropriate storage (Cloud Storage, Firestore, Spanner, BigQuery) matched to access patterns
- [ ] **[Recommended]** Use VPC design with shared VPCs and proper subnet segmentation for network isolation
- [ ] **[Recommended]** Plan for multi-tenancy, data partitioning, and resource isolation in shared-service architectures
- [ ] **[Recommended]** Document architecture decisions and system design rationale in Architecture Decision Records
- [ ] **[Recommended]** Design for portability where business requirements warrant it (containers, Kubernetes, open standards)
- [ ] **[Recommended]** Plan capacity and quotas: understand Google Cloud quota limits and request increases proactively

### Why This Matters

System design is the foundation on which all other pillars depend. Decisions made during initial design -- such as choosing between a monolith and microservices, selecting managed vs. self-managed services, or determining regional vs. multi-regional deployment -- have long-lasting implications for reliability, cost, and operational complexity. Google Cloud offers a broad set of managed services that can dramatically reduce operational overhead, but selecting the right service for each use case requires understanding workload characteristics and trade-offs.

---

## Pillar 2: Operational Excellence

Focuses on deploying, operating, and monitoring workloads to ensure reliable delivery and continuous improvement.

### Design Principles

- Automate everything that can be automated
- Monitor all layers of the stack
- Manage change through code and automation
- Practice incident management discipline
- Continuously improve processes

### Checklist

- [ ] **[Recommended]** Use infrastructure as code (Terraform, Deployment Manager, or Pulumi) for all Google Cloud resource provisioning
- [ ] **[Recommended]** Implement CI/CD pipelines with Cloud Build or external tools (GitHub Actions, GitLab CI) with automated testing
- [ ] **[Critical]** Instrument applications with Cloud Trace, Cloud Logging, and Cloud Monitoring for full observability
- [ ] **[Critical]** Define SLIs, SLOs, and error budgets following Google SRE practices for each service
- [ ] **[Critical]** Create Cloud Monitoring dashboards and alerting policies aligned with SLOs
- [ ] **[Recommended]** Implement progressive rollout strategies (canary deployments, traffic splitting in Cloud Run or GKE)
- [ ] **[Recommended]** Use Cloud Deploy for managed continuous delivery pipelines with approval gates
- [ ] **[Critical]** Establish incident management processes with defined roles (incident commander, communications lead)
- [ ] **[Critical]** Conduct blameless postmortems for all significant incidents and track action items to completion
- [ ] **[Recommended]** Automate routine operational tasks using Cloud Functions, Cloud Scheduler, and Workflows
- [ ] **[Recommended]** Maintain runbooks for common operational scenarios and emergency procedures
- [ ] **[Recommended]** Use Organization Policy constraints and resource hierarchy (org, folders, projects) for governance

### Why This Matters

Google pioneered Site Reliability Engineering (SRE), and its Architecture Framework reflects those principles. Operational excellence on Google Cloud means treating operations as a software problem: automating toil, defining measurable objectives (SLOs), and using error budgets to balance reliability with development velocity. Without operational discipline, even well-designed systems degrade over time as changes introduce drift, monitoring gaps widen, and incident response becomes ad hoc.

---

## Pillar 3: Security, Privacy, and Compliance

Focuses on protecting data, systems, and workloads while meeting regulatory and compliance requirements.

### Design Principles

- Apply defense in depth
- Use Google-managed security services
- Enforce least privilege everywhere
- Encrypt by default
- Automate security controls

### Checklist

- [ ] **[Critical]** Use Google Cloud Identity or Cloud Identity Platform for centralized identity management with MFA
- [ ] **[Critical]** Implement least-privilege IAM using predefined roles, custom roles, and IAM Conditions
- [ ] **[Critical]** Use VPC Service Controls to create security perimeters around sensitive Google Cloud services
- [ ] **[Critical]** Enable Security Command Center (Premium) for asset discovery, vulnerability scanning, and threat detection
- [ ] **[Recommended]** Enforce organization policies for resource location, public access prevention, and service restrictions
- [ ] **[Critical]** Use customer-managed encryption keys (CMEK) with Cloud KMS for sensitive data at rest
- [ ] **[Recommended]** Implement private networking: Private Google Access, Private Service Connect, and internal-only endpoints
- [ ] **[Recommended]** Secure container workloads with Binary Authorization, container scanning, and GKE Workload Identity
- [ ] **[Critical]** Store secrets in Secret Manager with automated rotation and IAM-controlled access
- [ ] **[Critical]** Enable VPC Flow Logs and Cloud Audit Logs for all projects; centralize logs in a dedicated project
- [ ] **[Recommended]** Implement data loss prevention (DLP) scanning for sensitive data in storage and data pipelines
- [ ] **[Critical]** Conduct compliance mapping against relevant standards (SOC 2, ISO 27001, HIPAA, PCI DSS) using Assured Workloads where applicable

### Why This Matters

Google Cloud encrypts data at rest and in transit by default, but security is a shared responsibility. Misconfigured IAM, overly permissive network rules, and unprotected APIs are the leading causes of cloud security incidents across all providers. VPC Service Controls and Organization Policies are uniquely powerful on Google Cloud but require deliberate configuration. Privacy and compliance requirements (GDPR, HIPAA, data residency) must be addressed at the architecture level, not bolted on afterward.

---

## Pillar 4: Reliability

Focuses on building systems that perform their intended functions and recover quickly from disruptions.

### Design Principles

- Define and measure reliability targets
- Build redundancy at every layer
- Design for graceful degradation
- Automate failure detection and recovery
- Test reliability through controlled experiments

### Checklist

- [ ] **[Critical]** Define availability targets and error budgets using SLIs and SLOs for each service
- [ ] **[Critical]** Deploy across multiple zones within a region for standard high availability
- [ ] **[Critical]** Implement multi-region architectures for workloads requiring very high availability (99.99%+)
- [ ] **[Critical]** Use regional or multi-regional storage classes for data durability and availability
- [ ] **[Critical]** Implement health checks and auto-healing with managed instance groups or GKE pod probes
- [ ] **[Recommended]** Design for graceful degradation: serve cached or static responses when backend services are impaired
- [ ] **[Critical]** Use Cloud Load Balancing (global or regional) for traffic distribution and automatic failover
- [ ] **[Recommended]** Implement retry logic with exponential backoff and jitter for all inter-service calls
- [ ] **[Recommended]** Back up critical data using automated snapshot schedules and cross-region replication
- [ ] **[Critical]** Test disaster recovery procedures regularly, including full failover and data restoration
- [ ] **[Recommended]** Use Chaos engineering practices to validate resilience assumptions under failure conditions
- [ ] **[Critical]** Monitor against SLOs and use error budget policies to govern the pace of change

### Why This Matters

Google's SRE philosophy frames reliability as the most fundamental feature: if a system is not reliable, users cannot access any other feature. The error budget model provides a quantitative framework for making trade-offs between reliability and feature velocity. Google Cloud's global infrastructure (global load balancers, Spanner's multi-region capabilities, regional managed services) enables high availability, but the architecture must be designed to use these capabilities correctly. Untested disaster recovery plans are indistinguishable from no plan at all.

---

## Pillar 5: Cost Optimization

Focuses on maximizing the business value of Google Cloud investments by eliminating waste and selecting the most cost-effective resources.

### Design Principles

- Establish cloud financial governance
- Measure cost per business outcome
- Optimize resource utilization
- Use committed and preemptible pricing strategically
- Continuously review and improve

### Checklist

- [ ] **[Critical]** Set up billing accounts, budgets, and alerts using Cloud Billing and Budgets API
- [ ] **[Recommended]** Implement a labeling strategy for cost allocation across teams, projects, and environments
- [ ] **[Recommended]** Use billing export to BigQuery for detailed cost analysis and custom reporting
- [ ] **[Recommended]** Right-size Compute Engine instances using Recommender and Cloud Monitoring utilization data
- [ ] **[Recommended]** Purchase Committed Use Discounts (CUDs) for stable, predictable workloads
- [ ] **[Recommended]** Use Preemptible VMs or Spot VMs for fault-tolerant batch processing and development workloads
- [ ] **[Recommended]** Select appropriate Cloud Storage classes (Standard, Nearline, Coldline, Archive) with lifecycle rules
- [ ] **[Recommended]** Evaluate serverless options (Cloud Run, Cloud Functions, BigQuery) for variable and unpredictable workloads
- [ ] **[Recommended]** Shut down or scale non-production environments outside business hours using Cloud Scheduler and automation
- [ ] **[Recommended]** Identify and clean up unused resources: idle VMs, orphaned disks, unattached static IPs
- [ ] **[Recommended]** Use Active Assist recommendations (idle resources, right-sizing, CUD suggestions) and act on them monthly
- [ ] **[Recommended]** Measure unit economics: track cost per request, cost per user, or cost per data pipeline run

### Why This Matters

Google Cloud's per-second billing and sustained use discounts provide cost advantages, but they do not prevent waste. Cost optimization requires organizational discipline: tagging resources, monitoring spending, right-sizing infrastructure, and choosing the right pricing model for each workload. Serverless and autoscaling services align cost with usage naturally, but only when the architecture is designed to take advantage of them. The most common sources of waste on Google Cloud are oversized VMs, always-on development environments, and data stored in the wrong storage class.

---

## Pillar 6: Performance Optimization

Focuses on designing systems that meet performance requirements and maintain responsiveness as scale increases.

### Design Principles

- Define measurable performance targets
- Select services matched to workload requirements
- Design for horizontal scalability
- Optimize data access patterns
- Monitor and tune continuously

### Checklist

- [ ] **[Recommended]** Define latency, throughput, and concurrency targets for each user-facing and backend service
- [ ] **[Recommended]** Select machine types and configurations (CPU, memory, GPU, TPU) matched to workload profiles
- [ ] **[Recommended]** Use Cloud CDN and Cloud Load Balancing to cache content and route users to the nearest serving location
- [ ] **[Recommended]** Implement Memorystore (Redis or Memcached) for application-level caching of frequently accessed data
- [ ] **[Recommended]** Design database schemas and queries for performance: use appropriate indexes, partitioning, and read replicas
- [ ] **[Recommended]** Use autoscaling for compute (GKE HPA/VPA, managed instance groups, Cloud Run concurrency) to match demand
- [ ] **[Recommended]** Implement asynchronous processing with Pub/Sub and Cloud Tasks to decouple latency-sensitive paths
- [ ] **[Recommended]** Use Cloud Profiler and Cloud Trace to identify application-level performance bottlenecks
- [ ] **[Recommended]** Conduct load testing with representative traffic patterns before production launches
- [ ] **[Recommended]** Optimize network performance: use Premium Tier networking, place resources close to users, minimize cross-region traffic
- [ ] **[Recommended]** Evaluate BigQuery, Dataflow, and Dataproc for large-scale data processing performance requirements
- [ ] **[Recommended]** Review and adopt new Google Cloud features (new machine families, service enhancements) that improve performance

### Why This Matters

Performance is a feature that directly affects user satisfaction and business outcomes. Slow responses increase abandonment, and systems that cannot handle peak load result in lost revenue. Google Cloud provides high-performance infrastructure (custom machine types, global network, purpose-built processors like TPUs), but performance must be designed into the architecture. Common pitfalls include chatty inter-service communication, missing caches, unoptimized database queries, and synchronous processing where asynchronous patterns would be more appropriate. Performance testing must be done under realistic conditions before launch, not after users report problems.

---

## How to Use in Architecture Reviews

### When to Apply

- **Greenfield projects on Google Cloud**: Walk through all six pillars during initial architecture design. Use the checklists to validate that the design addresses each area.
- **Migration to Google Cloud**: Focus on System Design and Reliability pillars to ensure the target architecture takes advantage of Google Cloud capabilities rather than replicating on-premises patterns.
- **SRE practice adoption**: Use the Reliability and Operational Excellence pillars to establish SLO-based reliability practices aligned with Google SRE principles.
- **Cost governance initiatives**: Use the Cost Optimization pillar alongside billing analysis to identify savings opportunities and establish ongoing governance.
- **Compliance and security reviews**: Use the Security, Privacy, and Compliance pillar to map controls to regulatory requirements.

### How to Apply During a Design Session

1. **Establish context and priorities**: Identify the workload type, user base, compliance requirements, and business criticality. This determines which pillars receive the most attention and where trade-offs are acceptable.
2. **Review System Design first**: This pillar sets the foundation. Validate that service selections, network topology, and data architecture are sound before reviewing other pillars.
3. **Apply Google SRE principles**: For Reliability and Operational Excellence, frame discussions around SLIs, SLOs, and error budgets. This quantitative approach makes reliability discussions more productive than abstract availability percentages.
4. **Use checklists as conversation guides**: Not every item applies to every workload. Use the items to prompt discussion and identify gaps, not as a rigid compliance exercise.
5. **Document trade-offs as ADRs**: When pillar recommendations conflict (e.g., multi-region for reliability vs. single-region for cost), document the decision, alternatives considered, and rationale.
6. **Leverage Google Cloud tools**: Use Active Assist Recommender, Security Command Center, and Cloud Monitoring to validate architecture decisions with data rather than assumptions.
7. **Plan for iteration**: Architecture reviews are not one-time events. Schedule follow-up reviews and use SLO dashboards, cost reports, and security findings to track improvement over time.

## Common Decisions (ADR Triggers)

- **Pillar prioritization** — which pillars to focus on first based on workload characteristics and team maturity
- **Compute platform selection** — GKE vs Cloud Run vs Compute Engine, managed vs self-managed trade-offs
- **Data architecture** — BigQuery vs Cloud SQL vs Spanner, storage tier selection, data residency
- **Security posture** — Security Command Center tier, BeyondCorp adoption, VPC Service Controls scope
- **Cost optimization** — committed use discounts vs sustained use, preemptible/spot VM strategy, active assist
- **Operational model** — IaC tooling (Terraform vs Config Connector vs Pulumi), Cloud Monitoring vs third-party
- **Reliability architecture** — regional vs multi-regional, Chaos Studio adoption, SLO-based alerting
- **Architecture review cadence** — framework assessment frequency, risk-based prioritization of improvements
