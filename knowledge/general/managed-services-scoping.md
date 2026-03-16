# Managed Services Scoping for Migration Engagements

## Scope

This file covers **commercial and operational scoping decisions** when a migration engagement includes post-migration managed services. Addresses ITSM tooling decisions, contract structure impact on architecture, SLA definition, operational readiness, and the questions an architect must ask when the deliverable extends beyond migration into ongoing operations. For technical migration planning, see `general/workload-migration.md`. For capacity planning, see `general/capacity-planning.md`. For disaster recovery SLA design, see `general/disaster-recovery.md`.

## Checklist

### ITSM Tooling

- [ ] **[Critical]** Is the ITSM tool identified? (ServiceNow, BMC Helix/Remedy, Jira Service Management, Freshservice, ManageEngine, Cherwell, custom) Both the customer's tool and the managed services provider's tool must be documented.
- [ ] **[Critical]** Is the ITSM ownership model defined? Options: (A) Customer-owned ITSM, provider operates within it; (B) Provider-owned ITSM, customer gets portal/dashboard access; (C) Dual ITSM with bi-directional integration.
- [ ] **[Critical]** If dual ITSM, is integration scope defined? (Incident sync, change request flow, CMDB federation, SLA reporting, escalation routing) Each integration point adds implementation effort and ongoing maintenance.
- [ ] **[Critical]** Is the CMDB update responsibility defined? Who keeps the CMDB current post-migration -- the provider, the customer, or shared? This is frequently overlooked and causes operational drift.
- [ ] **[Recommended]** Is the change management process defined? Who approves changes to the managed infrastructure -- customer CAB, provider CAB, or joint? Turnaround time for emergency vs. standard changes.
- [ ] **[Recommended]** Is the incident escalation matrix documented? L1/L2/L3 ownership boundaries, response time targets per severity level, customer notification thresholds.
- [ ] **[Optional]** Is self-service provisioning in scope? If the customer expects to provision VMs, storage, or networks without raising tickets, the architecture must include self-service portals (Nutanix Self-Service/Calm, ServiceNow CMDB integration, Terraform modules).

### Contract and Commercial Structure

- [ ] **[Critical]** Is the contract duration documented? Duration affects hardware amortization, license procurement strategy (perpetual vs. subscription), and refresh cycle planning.
- [ ] **[Critical]** Is the contract start date defined? This determines when managed services obligations begin -- often different from the migration start date.
- [ ] **[Critical]** Is the pricing model defined? Common models: per-VM/month, per-core/month, per-TB/month, fixed monthly fee, tiered by environment (prod/non-prod). The model drives architecture decisions (e.g., per-VM pricing discourages many small VMs).
- [ ] **[Critical]** Are hardware refresh responsibilities defined? Who owns the hardware lifecycle -- provider procures and refreshes, customer procures and provider operates, or leased from a third party? Refresh cycles (typically 5 years) must align with contract duration.
- [ ] **[Recommended]** Is the scope boundary between migration and managed services clearly defined? (Migration ends at cutover validation and hypercare; managed services begins at steady-state handoff) Gaps between these phases cause operational risk.
- [ ] **[Recommended]** Are growth provisions included? If VM count, storage, or site count grows beyond the initial scope, what is the commercial mechanism -- pre-agreed unit rates, renegotiation triggers, auto-scaling tiers?
- [ ] **[Recommended]** Is the exit strategy defined? At contract end, what happens -- transition to another provider, transition to customer self-management, contract renewal? Data extraction, knowledge transfer, and decommission responsibilities must be defined.
- [ ] **[Optional]** Are penalty/credit mechanisms defined for SLA misses? Financial credits, service level step-up plans, or termination triggers for persistent underperformance.

### SLA Definition

- [ ] **[Critical]** Are availability SLAs defined per environment tier? Typical tiers: Production (99.9% = 8.7 hrs/year downtime), Pre-production (99.5%), Development (99.0% or best-effort). SLA drives redundancy architecture decisions.
- [ ] **[Critical]** Are RPO and RTO targets defined per workload tier? (Recovery Point Objective = max data loss; Recovery Time Objective = max downtime after failure) These directly drive backup frequency, replication topology, and DR architecture.
- [ ] **[Critical]** Are patching SLAs defined? (Critical security patches within 72 hours, standard patches within 30 days, maintenance windows per site/region) Patching cadence affects change management workload and staffing.
- [ ] **[Critical]** Are incident response time SLAs defined? (P1/Critical: 15 min response, P2/High: 30 min, P3/Medium: 4 hrs, P4/Low: 8 hrs) Response time vs. resolution time must be distinguished.
- [ ] **[Recommended]** Are performance SLAs defined? (VM boot time < 60s, storage latency < 5ms for prod, network throughput guarantees) Performance SLAs require monitoring infrastructure and baseline establishment.
- [ ] **[Recommended]** Is the SLA measurement and reporting cadence defined? (Monthly SLA reports, quarterly business reviews, annual contract reviews) Reporting requires observability tooling and dashboards.
- [ ] **[Optional]** Are SLA exclusions documented? (Planned maintenance windows, customer-caused outages, force majeure, third-party dependencies) Clear exclusions prevent disputes.

### Operational Readiness

- [ ] **[Critical]** Is the monitoring and alerting stack defined? (Prism Central alerts, Prometheus/Grafana, Datadog, PRTG, SolarWinds, or customer-preferred tooling) Must be deployed and tested before managed services go-live.
- [ ] **[Critical]** Are runbooks prepared for common operational tasks? (VM provisioning, storage expansion, cluster scaling, firmware updates, backup restore, DR failover) Runbooks are the bridge between architecture and operations.
- [ ] **[Critical]** Is the on-call rotation defined? (24x7, business hours only, follow-the-sun across regions) On-call staffing drives managed services cost significantly.
- [ ] **[Critical]** Is the handoff plan from migration team to operations team documented? (Knowledge transfer sessions, shadowing period, hypercare window, escalation path during transition)
- [ ] **[Recommended]** Are capacity management procedures defined? (Monthly capacity reviews, growth trend analysis, procurement lead time for expansion, threshold alerts at 70%/80%/90% utilization)
- [ ] **[Recommended]** Is the security operations scope defined? (Vulnerability scanning cadence, patch management, access reviews, incident response for security events, compliance audit support)
- [ ] **[Optional]** Is automation scope defined? (Infrastructure-as-code for provisioning, automated patching pipelines, self-healing scripts, ChatOps integration) Automation reduces operational cost but requires upfront investment.

### Architecture Implications

- [ ] **[Critical]** Does the architecture support the defined SLAs? (If 99.9% availability is required, is the infrastructure designed with redundancy to support it -- N+1 nodes, RF3 storage, multi-site DR?)
- [ ] **[Critical]** Is the monitoring architecture designed to measure SLA compliance? (Synthetic monitoring for availability, storage latency dashboards for performance SLAs, backup success rate tracking for RPO compliance)
- [ ] **[Recommended]** Is the architecture designed for operational efficiency? (Standardized VM templates, automated provisioning workflows, consistent naming and tagging for CMDB accuracy, centralized log aggregation)
- [ ] **[Recommended]** Is multi-tenancy considered if the provider manages multiple customers on shared infrastructure? (Network isolation, storage isolation, Prism Central project-level RBAC, separate backup domains)

## Why This Matters

Migration engagements that include managed services fail when the architecture is designed only for the migration phase. An architecture that migrates 7,000 VMs successfully but cannot be efficiently operated, monitored, and maintained in steady state is a failure from the managed services perspective. The most expensive surprises come from:

1. **ITSM integration underestimation** -- bi-directional ITSM sync between customer and provider tools can take 3-6 months to implement and test, often not budgeted in the migration timeline.

2. **SLA-architecture mismatch** -- agreeing to 99.9% availability SLAs on infrastructure designed for 99.5% creates persistent SLA misses and financial penalties. The architecture must be designed to the SLA, not the other way around.

3. **Operational staffing gaps** -- the team that designs and migrates is rarely the team that operates. Knowledge transfer is frequently inadequate, and the operations team discovers architecture decisions they don't understand during the first major incident.

4. **Contract-architecture misalignment** -- a 3-year contract with 5-year hardware refresh assumptions, or per-VM pricing that doesn't account for VM sprawl, creates financial pressure that degrades service quality over time.

The architect's role is to surface these operational and commercial considerations during the design phase, not after the migration is complete. Every SLA commitment should trace to an architecture decision that supports it.

## Common Decisions (ADR Triggers)

- **ITSM integration model** -- customer tool, provider tool, or dual with integration; complexity and cost implications for each; CMDB ownership and update responsibility
- **SLA tier structure** -- how many tiers (typically 3-4), what availability/RPO/RTO targets per tier, which workloads map to which tier; drives infrastructure redundancy design
- **Monitoring stack selection** -- Prism-native vs. third-party vs. customer-mandated tooling; integration with ITSM for automated incident creation; dashboard access for customer vs. provider
- **On-call model** -- 24x7 vs. business hours vs. follow-the-sun; staffing requirements; escalation to vendor support (Nutanix, Microsoft, etc.)
- **Automation investment** -- manual operations (lower upfront cost, higher ongoing cost) vs. automated operations (higher upfront, lower ongoing); IaC tooling selection (Terraform, Ansible, Nutanix NCM)
- **Contract-aligned hardware lifecycle** -- align hardware refresh with contract term; lease vs. purchase; end-of-contract hardware disposition

## See Also

- `general/workload-migration.md` -- Migration strategy and wave planning
- `general/disaster-recovery.md` -- DR architecture and RPO/RTO design
- `general/capacity-planning.md` -- Capacity planning methodology
- `general/observability.md` -- Monitoring, alerting, and dashboarding
- `general/governance.md` -- Change management, compliance, and audit
