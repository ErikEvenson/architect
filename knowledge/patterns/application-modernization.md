# Application Modernization Patterns

## Scope

Covers strategies for modernizing legacy applications, including the 6Rs framework (rehost, replatform, refactor, repurchase, retire, retain), strangler fig pattern, domain-driven decomposition, monolith-to-microservices migration, application portfolio rationalization, modernization assessment criteria, anti-corruption layers, and feature parity vs feature evolution. Applicable when organizations need to modernize legacy systems to improve agility, reduce technical debt, enable cloud adoption, or address end-of-life platforms.

## Overview

Application modernization transforms legacy applications to leverage modern platforms, architectures, and practices. The approach ranges from simple rehosting (lift-and-shift) to complete refactoring into cloud-native microservices. Selecting the right strategy per application requires systematic portfolio assessment balancing business value, technical risk, and investment.

## Checklist

### Portfolio Assessment

- [ ] **[Critical]** Has a full application portfolio inventory been completed? (application name, owner, technology stack, dependencies, business criticality)
- [ ] **[Critical]** What are the modernization drivers for each application? (end-of-life platform, scalability limits, compliance gaps, cost reduction, time-to-market)
- [ ] **[Critical]** Has each application been scored using a rationalization framework? (business value vs technical fitness, TIME model, Gartner 5Rs+)
- [ ] **[Recommended]** Are application interdependencies mapped? (upstream/downstream systems, shared databases, integration points, data flows)
- [ ] **[Recommended]** Is there a clear business case for each modernization initiative? (cost of keeping vs cost of modernizing, expected ROI timeline)
- [ ] **[Optional]** Has the portfolio been grouped into migration waves based on dependency analysis and risk tolerance?

### 6Rs Strategy Selection

- [ ] **[Critical]** Has each application been assigned a disposition using the 6Rs? (rehost, replatform, refactor, repurchase, retire, retain)
- [ ] **[Critical]** For rehost candidates: are there hidden dependencies on on-premises infrastructure? (local file shares, hardware dongles, multicast, low-latency LAN)
- [ ] **[Recommended]** For replatform candidates: what is the minimum change needed to gain cloud benefits? (managed database, containerization, PaaS runtime)
- [ ] **[Critical]** For refactor candidates: is the expected business value sufficient to justify the cost and risk of rearchitecting?
- [ ] **[Recommended]** For repurchase candidates: has a SaaS gap analysis been performed? (feature coverage, customization limits, data migration path, integration capabilities)
- [ ] **[Recommended]** For retire candidates: is there a data archival and compliance retention plan?
- [ ] **[Optional]** For retain candidates: what is the trigger condition for revisiting the decision? (license expiry, support end-of-life, compliance mandate)

### Strangler Fig Pattern

- [ ] **[Critical]** Is there a clear boundary for routing traffic between the legacy and modern systems? (API gateway, reverse proxy, load balancer)
- [ ] **[Critical]** Can individual features or routes be migrated independently without breaking the whole application?
- [ ] **[Recommended]** Is there a shared data layer or does the new system need its own data store? (dual-write risks, data synchronization strategy)
- [ ] **[Recommended]** How is feature parity tracked between legacy and modern implementations? (feature matrix, acceptance criteria per migrated capability)
- [ ] **[Recommended]** What is the rollback strategy if a migrated feature has issues? (traffic routing back to legacy, blue-green switching)
- [ ] **[Optional]** Is there a sunset timeline for the legacy system once all features are migrated?

### Domain-Driven Decomposition

- [ ] **[Critical]** Have bounded contexts been identified through domain analysis? (event storming, domain storytelling, context mapping)
- [ ] **[Critical]** Are bounded context boundaries aligned with team ownership and organizational structure?
- [ ] **[Recommended]** Have shared kernels and integration patterns between contexts been defined? (published language, open host service, conformist)
- [ ] **[Recommended]** Is there a ubiquitous language documented for each bounded context?
- [ ] **[Optional]** Has a context map been created showing relationships between all bounded contexts? (upstream/downstream, partnership, customer-supplier)

### Monolith-to-Microservices Migration

- [ ] **[Critical]** Is the monolith well-understood? (codebase documentation, module boundaries, database schema ownership, runtime behavior profiling)
- [ ] **[Critical]** What is the decomposition strategy? (by business capability, by subdomain, by data ownership, by team boundary)
- [ ] **[Recommended]** Has a modular monolith been considered as an intermediate step before full microservices? (lower operational complexity, same deployment unit, enforced module boundaries)
- [ ] **[Critical]** How will the shared database be decomposed? (schema splitting, database-per-service, change data capture for synchronization)
- [ ] **[Recommended]** How are cross-cutting concerns handled during the transition? (authentication, logging, tracing, configuration)
- [ ] **[Recommended]** Is there a feature toggle or canary strategy for gradually routing traffic to extracted services?
- [ ] **[Optional]** What is the minimum viable platform needed before extracting the first service? (CI/CD, container orchestration, service discovery, observability)

### Anti-Corruption Layer

- [ ] **[Critical]** Is there an anti-corruption layer between the legacy system and new services? (translation of legacy data models, protocol adaptation)
- [ ] **[Recommended]** Does the anti-corruption layer handle data format translation, protocol bridging, and semantic mapping?
- [ ] **[Recommended]** Is the anti-corruption layer implemented as a separate deployable component with its own lifecycle?
- [ ] **[Optional]** Is the anti-corruption layer designed to be temporary and removable once the legacy system is decommissioned?

### Feature Parity vs Feature Evolution

- [ ] **[Critical]** Has the team decided between strict feature parity and feature evolution for the modernized system?
- [ ] **[Recommended]** If pursuing feature parity: is there a complete feature inventory of the legacy system including undocumented behaviors?
- [ ] **[Recommended]** If pursuing feature evolution: are new capabilities prioritized alongside migration work to demonstrate business value early?
- [ ] **[Critical]** How will users be transitioned? (big bang cutover, phased migration by user group, opt-in beta)
- [ ] **[Optional]** Is there a plan for handling features that exist in the legacy system but are rarely used? (usage analytics, feature retirement)

### Risk and Governance

- [ ] **[Critical]** Is there a rollback plan for each modernization phase? (ability to revert to the legacy system)
- [ ] **[Recommended]** How is data consistency maintained during the transition period? (dual-write, event sourcing, CDC)
- [ ] **[Recommended]** Are there compliance or regulatory constraints that affect the modernization approach? (data residency, audit trails, validation requirements)
- [ ] **[Optional]** Is there an organizational change management plan? (training, documentation, support model transition)

## Why This Matters

Application modernization is one of the highest-risk, highest-reward initiatives in enterprise IT. Choosing the wrong strategy per application wastes budget -- refactoring a low-value application that should have been repurchased, or rehosting a system that needs fundamental rearchitecting. The strangler fig pattern is widely recommended but poorly implemented when teams lack clear routing boundaries or try to migrate too many features at once. Database decomposition is consistently the hardest part of monolith-to-microservices migration and is underestimated in nearly every project. Without an anti-corruption layer, new services become polluted with legacy data models and coupling, defeating the purpose of modernization. Feature parity mandates often double project timelines because they require reimplementing rarely-used features -- yet skipping features without usage data creates user trust issues. Portfolio rationalization without dependency mapping leads to migration waves that break critical integrations.

## Common Decisions (ADR Triggers)

- **6R disposition per application** -- which strategy applies to each application and why, business value justification, reassessment criteria
- **Strangler fig routing mechanism** -- API gateway vs reverse proxy vs DNS-based routing, traffic splitting approach, rollback mechanics
- **Database decomposition strategy** -- schema-per-service vs shared database with access control, change data capture vs dual-write, data synchronization approach
- **Modular monolith vs direct microservices** -- whether to introduce module boundaries within the monolith first or extract services directly, risk tolerance assessment
- **Anti-corruption layer placement** -- which legacy system boundaries need ACLs, whether the ACL is owned by the legacy team or the new service team
- **Feature parity scope** -- strict parity vs opportunity to evolve, feature retirement criteria, user transition strategy
- **Modernization sequencing** -- which applications/components to modernize first, dependency-driven wave planning, quick wins vs strategic investments
- **Build vs buy for replaced capabilities** -- when to repurchase (SaaS) vs refactor in-house, evaluation criteria for SaaS alternatives

## Reference Links

- [AWS Migration Modernization](https://aws.amazon.com/cloud-migration/) -- AWS guides for application migration and modernization strategies
- [Azure Migration Center](https://azure.microsoft.com/en-us/solutions/migration/) -- Azure tools and guidance for application modernization
- [Google Cloud Application Modernization](https://cloud.google.com/solutions/application-modernization) -- GCP application modernization patterns and tools
- [Martin Fowler: Strangler Fig Application](https://martinfowler.com/bliki/StranglerFigApplication.html) -- Original description of the strangler fig pattern for incremental legacy replacement
- [Domain-Driven Design Reference](https://www.domainlanguage.com/ddd/reference/) -- Eric Evans' DDD reference for bounded contexts and context mapping
- [Sam Newman: Monolith to Microservices](https://samnewman.io/books/monolith-to-microservices/) -- Patterns for decomposing monolithic applications into microservices
- [AWS Prescriptive Guidance: Application Portfolio Assessment](https://docs.aws.amazon.com/prescriptive-guidance/latest/application-portfolio-assessment-guide/introduction.html) -- Structured approach to portfolio rationalization and 6Rs disposition
- [TOGAF Application Portfolio Management](https://pubs.opengroup.org/togaf-standard/business-architecture/application-portfolio-management.html) -- Enterprise architecture framework for application portfolio rationalization

## See Also

- `patterns/microservices.md` -- Microservices decomposition, communication patterns, and observability
- `patterns/migration-cutover.md` -- Cutover procedures for migrating workloads between environments
- `patterns/migration-coexistence.md` -- Coexistence patterns during migration periods
- `general/workload-migration.md` -- Workload migration planning and execution
- `general/database-migration.md` -- Database migration strategies and tools
- `patterns/hybrid-cloud.md` -- Hybrid cloud architecture for transitional states during modernization
- `patterns/event-driven.md` -- Event-driven patterns useful for decoupling during decomposition
- `general/api-design.md` -- API design principles for service contracts in modernized architectures
