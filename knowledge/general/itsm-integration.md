# ITSM Integration

## Scope

This file covers **IT Service Management integration** patterns for architecture designs including incident management workflows, change management processes, problem management, CMDB federation and data flow, SLA management and reporting, service catalog design, integration patterns (API, webhook, email, event-driven), ITSM tool selection criteria for managed services engagements, customer vs provider ITSM boundary decisions, and ITIL 4 alignment. For specific ITSM platform implementation details, see the relevant provider knowledge files. For operational runbook design, see `general/operational-runbooks.md`.

## Checklist

- [ ] **[Critical]** Is the ITSM integration boundary clearly defined -- which system is the system of record for incidents, changes, and CIs, and what data flows between customer ITSM and provider ITSM (if applicable) with defined direction and ownership?
- [ ] **[Critical]** Is incident management integrated with monitoring -- are alerts automatically creating incidents with appropriate severity mapping (P1-P4), assignment rules, and escalation paths that match SLA response/resolution targets?
- [ ] **[Critical]** Is change management integrated with the deployment pipeline -- are standard changes pre-approved for CI/CD deployments, normal changes requiring CAB approval tracked with implementation plans, and emergency change processes documented with retroactive review?
- [ ] **[Critical]** Is the CMDB data model defined with CI classes, relationships (runs-on, depends-on, hosted-on), and discovery/reconciliation mechanisms that keep the CMDB accurate without manual entry -- stale CMDB data is worse than no CMDB?
- [ ] **[Recommended]** Are SLA definitions machine-readable and tracked in the ITSM platform with automated clock start/stop (business hours vs 24x7), pause conditions (pending customer), and breach notifications configured for each service tier?
- [ ] **[Recommended]** Is the integration pattern chosen appropriately -- REST API for real-time bidirectional sync, webhooks for event-driven notifications, email for legacy systems, and message queue for high-volume asynchronous processing?
- [ ] **[Recommended]** Is the service catalog designed with request fulfillment workflows that include approval chains, automated provisioning where possible, and estimated delivery times aligned with operational capacity?
- [ ] **[Recommended]** Is there a defined process for CMDB federation when multiple ITSM tools exist -- including CI deduplication rules, authoritative source per CI type, and reconciliation frequency to prevent data conflicts?
- [ ] **[Recommended]** Are problem management processes integrated with incident data to enable trend analysis -- recurring incident correlation, known error database (KEDB) maintenance, and root cause analysis documentation that feeds back into architectural improvements?
- [ ] **[Optional]** Is a multi-ITSM integration hub (iPaaS or custom middleware) deployed when more than two ITSM platforms need bidirectional sync, to avoid point-to-point integration complexity?
- [ ] **[Optional]** Are ITSM metrics (MTTR, MTTI, change success rate, SLA compliance %) dashboarded and reviewed regularly to drive continuous improvement of both the ITSM processes and the underlying architecture?
- [ ] **[Optional]** Is knowledge management integrated with incident resolution -- auto-suggesting knowledge articles during incident triage, capturing resolution steps as new articles, and measuring article deflection rates?

## Why This Matters

ITSM integration is the connective tissue between architecture design and operational reality. A well-designed system that lacks proper incident routing, change control, and CMDB accuracy will suffer from slow incident response, unauthorized changes causing outages, and an inability to assess the impact of proposed changes. In managed services engagements, the boundary between customer and provider ITSM systems is one of the most contentious and error-prone areas -- unclear ownership of the incident lifecycle leads to tickets falling into gaps, SLA clock disputes, and customer dissatisfaction. CMDB accuracy directly affects change impact analysis: if the CMDB does not reflect actual dependencies, a "low-risk" change can cascade into a major outage.

The integration pattern choice has lasting architectural implications. REST API integrations provide real-time sync but create tight coupling between systems. Webhook-based patterns are more resilient but require idempotent receivers and retry logic. Email-based integration is often used as a stopgap but introduces parsing fragility and loses structured data. For environments with multiple ITSM platforms (common in acquisitions or managed services), a hub-and-spoke integration pattern through middleware avoids the N-squared problem of point-to-point connections.

## Common Decisions (ADR Triggers)

- **Single ITSM vs federated ITSM** -- A single ITSM platform simplifies workflows and reporting but may not be feasible when customer and provider each maintain their own systems. Federated ITSM requires integration middleware, field mapping, and clear ownership rules. Single platform is preferred; federation is accepted when organizational boundaries make consolidation impractical.
- **Customer ITSM vs provider ITSM for managed services** -- Provider-operated ITSM gives full control over workflows and SLA tracking but requires customers to adopt a new portal. Customer-retained ITSM keeps users in familiar tools but limits provider workflow customization. Hybrid approaches (provider ITSM with customer portal access) balance both but add integration complexity.
- **CMDB discovery automation vs manual** -- Automated discovery (agent-based or agentless) keeps the CMDB current but requires network access, credentials management, and reconciliation rules. Manual CMDB maintenance is simpler to implement but degrades rapidly as environments change. Automated discovery is strongly recommended for any environment with more than 50 CIs.
- **Monitoring-to-incident automation level** -- Fully automated incident creation from alerts reduces MTTR but can create incident storms during major outages. Semi-automated (alert creates incident draft, human confirms) adds delay but prevents noise. Event correlation and suppression rules should be implemented before enabling full automation.
- **Standard change pre-approval scope** -- Broadly defined standard changes (all CI/CD deployments, all patching) accelerate delivery but reduce change oversight. Narrowly defined standard changes maintain control but slow velocity. The scope should be risk-based: low-risk, repeatable, well-tested changes qualify as standard; anything touching shared infrastructure or having broad blast radius requires normal change process.

## See Also

- `managed-services-scoping.md` -- managed services scope definition including ITSM boundary decisions
- `governance.md` -- IT governance frameworks and decision-making processes
- `operational-runbooks.md` -- operational runbook design and maintenance
