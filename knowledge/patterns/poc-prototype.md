# POC/Prototype Architecture Pattern

## Scope

Covers the architecture approach for proof-of-concept and prototype builds, including scope management, production readiness gap tracking, infrastructure minimization, and decision criteria for what to include vs skip. Applicable when validating an architecture hypothesis before committing to production implementation.

## Checklist

- [ ] **[Critical]** Define success criteria before starting: what specific questions must the POC answer? (performance target, integration feasibility, team capability, cost validation)
- [ ] **[Critical]** Time-box the POC with a fixed end date and decision milestone; define what happens at the end (proceed to production, pivot, or abandon)
- [ ] **[Critical]** Keep security basics even in POC: TLS for all endpoints, no default passwords, restricted network access, no secrets in source code
- [ ] **[Critical]** Create a "Production Readiness" gap document from day one tracking what was deliberately skipped and what must be added before production
- [ ] **[Critical]** Apply the decision filter: "Is this needed to validate the architecture?" — if no, skip it and document it in the gap tracker
- [ ] **[Recommended]** Use standard APIs and portable abstractions (Kubernetes, S3-compatible storage, PostgreSQL) to avoid vendor lock-in that would force a rewrite when moving to production
- [ ] **[Recommended]** Validate the CI/CD pipeline as part of the POC — deployment automation is an architecture concern, not a post-POC task
- [ ] **[Recommended]** Include basic observability (logging, metrics, one dashboard) to validate the monitoring approach and catch issues during POC testing
- [ ] **[Recommended]** Use cost-optimized infrastructure: spot/preemptible instances, minimal instance sizes, single-AZ, tear down when not in use
- [ ] **[Recommended]** Design the POC to run on a single node or minimal infrastructure — complexity should be in the application architecture, not the infrastructure
- [ ] **[Optional]** Avoid reserved capacity, savings plans, or long-term commitments during POC phase
- [ ] **[Optional]** Skip HA, multi-AZ, DR/backup, auto-scaling, WAF/DDoS protection, compliance hardening, and multi-region — document each as a production gap
- [ ] **[Optional]** Set up a simple load test to validate performance assumptions even if full performance testing is deferred to production hardening

## Why This Matters

A proof-of-concept exists to answer specific architectural questions with minimal investment. The most common failure mode is not building too little, but building too much -- teams spend months constructing production-grade infrastructure for an architecture that may be abandoned after validation. The second most common failure is building so little that the POC does not actually validate the architecture, leading to false confidence.

The key discipline is explicitly separating what must be proven now (architecture patterns, integration points, performance characteristics, team capability) from what can be added later (operational hardening, compliance, scalability infrastructure). Every component included in the POC should map to a specific question being validated. Everything excluded should be documented in the production readiness gap tracker so nothing is forgotten when the decision is made to proceed.

POCs that lack time-boxes and success criteria tend to drift into perpetual development, eventually becoming the production system by default -- without the hardening, testing, or operational readiness that production requires. This "POC-to-production drift" is one of the most common sources of technical debt and production incidents.

## Common Decisions (ADR Triggers)

- **POC scope: over-engineering vs under-engineering** -- Over-engineering builds production infrastructure for an unvalidated architecture, wasting time and money if the approach is abandoned. Under-engineering builds something so simplified that it does not actually prove the architecture works (e.g., mocking all integrations, skipping the hard parts). The right balance: implement the critical path end-to-end with real integrations, skip the operational hardening. If the POC does not exercise the risky parts of the architecture, it is not validating anything useful.
- **Single-node vs multi-node POC** -- Single-node (one VM, one K3s server, Docker Desktop) is fastest to set up and cheapest to run. Multi-node is only needed when the POC question specifically involves distributed behavior (consensus, cross-node networking, data replication). Default to single-node unless the architecture question requires distribution.
- **Real services vs managed services in POC** -- Using managed services (RDS, ElastiCache, managed Kafka) in the POC validates the integration but adds cost and cloud dependency. Self-hosted alternatives (PostgreSQL in Docker, Redis in Docker) reduce cost and keep the POC portable. Use managed services when the POC question is about integration with that specific service; use self-hosted when the service is just supporting infrastructure.
- **POC duration: 2 weeks vs 4 weeks vs 8 weeks** -- Two-week POCs work for validating a specific integration or library choice. Four-week POCs are typical for validating an end-to-end architecture with 2-3 services. Eight-week POCs are appropriate for complex distributed systems or when the team is learning a new technology stack simultaneously. Longer than 8 weeks is a red flag -- either the scope is too large or it has become a project rather than a POC.
- **Reuse POC code vs rewrite for production** -- If the POC was built with clean abstractions and standard patterns, significant portions can be carried forward. If the POC took shortcuts (hardcoded configuration, no error handling, no tests), plan a rewrite. Document this decision upfront so stakeholders have correct expectations about the POC-to-production timeline.

## Reference Architectures

### POC Decision Framework
```
For each component/capability, ask:

1. Does this validate an architecture question?
   YES → Include in POC
   NO  → Go to question 2

2. Does omitting this make the POC results invalid?
   YES → Include in POC (e.g., security basics, real integrations)
   NO  → Go to question 3

3. Can this be added incrementally after the POC?
   YES → Skip, add to Production Gap Tracker
   NO  → Include in POC (architectural decisions that are hard to retrofit)

Examples:
  TLS encryption          → Include (security basic, easy now, hard to retrofit)
  Multi-AZ deployment     → Skip (operational hardening, add later)
  CI/CD pipeline          → Include (validates deployment model)
  Auto-scaling            → Skip (optimization, add later)
  Monitoring basics       → Include (validates observability approach)
  Compliance hardening    → Skip (add during production hardening)
  Load balancer           → Depends (include if testing traffic patterns)
  DR/backup              → Skip (operational, add later)
```

### Single-Node POC Infrastructure
```
[Single VM / K3s Node]
  ├── Application services (Deployments)
  ├── Supporting services (PostgreSQL, Redis as pods)
  ├── Ingress (Traefik bundled with K3s)
  ├── Monitoring (lightweight: metrics-server + one Grafana dashboard)
  └── CI/CD (GitHub Actions → kubectl apply)

Cost: ~$30-50/month (t3.large or equivalent)
Setup time: 1-2 hours
Tear-down: stop/terminate instance when not in use

What this validates:
  ✓ Service-to-service communication patterns
  ✓ Data flow and integration points
  ✓ Deployment pipeline
  ✓ Basic performance characteristics
  ✓ Developer workflow

What this does NOT validate:
  ✗ High availability / failover
  ✗ Cross-zone networking
  ✗ Auto-scaling behavior
  ✗ Production-grade storage performance
  ✗ Multi-node scheduling
```

### POC to Production Gap Template
```
# Production Readiness Gap Tracker

## Infrastructure
- [ ] Multi-AZ deployment (currently single-node)
- [ ] Production-grade storage (currently hostpath/local)
- [ ] Load balancer with health checks (currently NodePort/Traefik)
- [ ] DNS and TLS certificate management (currently self-signed)
- [ ] Node auto-scaling (currently fixed size)

## Security
- [ ] Network policies (currently open pod-to-pod)
- [ ] Pod security standards (currently unrestricted)
- [ ] Secrets management (currently K8s Secrets, need external vault)
- [ ] Container image scanning in CI/CD
- [ ] RBAC fine-tuning (currently cluster-admin)

## Reliability
- [ ] Pod disruption budgets
- [ ] Health check tuning (liveness/readiness probes)
- [ ] Resource requests and limits validation
- [ ] Backup and restore procedures
- [ ] Disaster recovery plan and RTO/RPO targets

## Observability
- [ ] Full monitoring stack (Prometheus, Grafana, Alertmanager)
- [ ] Centralized logging (Loki/EFK/CloudWatch)
- [ ] Distributed tracing (Jaeger/Tempo)
- [ ] Alerting rules and on-call routing
- [ ] SLO/SLI definitions

## Operations
- [ ] Runbooks for common failure scenarios
- [ ] Upgrade and rollback procedures
- [ ] Capacity planning and load testing results
- [ ] Cost monitoring and optimization
- [ ] Compliance requirements (SOC2, HIPAA, etc.)

## CI/CD
- [ ] Multi-environment promotion (dev → staging → prod)
- [ ] Canary or blue/green deployment strategy
- [ ] Automated rollback on failure
- [ ] Integration and end-to-end test suites
- [ ] Infrastructure as Code (Terraform/Pulumi)
```
Copy this template at POC start. Check items as they are addressed. Remaining unchecked items form the production hardening backlog.

## See Also

- `general/testing-strategy.md` — Testing strategies applicable during POC validation
- `general/ci-cd.md` — CI/CD pipeline design validated during proof-of-concept
- `general/cost.md` — Cost management for POC infrastructure including spot instances and teardown
- `patterns/three-tier-web.md` — Common production architecture pattern that POCs often validate
