# Change Management

## Scope

This file covers **change management practices for infrastructure and cloud environments**: change classification and approval workflows, Change Advisory Board (CAB) processes, maintenance windows, change management integration with CI/CD pipelines, ITSM tooling, risk assessment, post-implementation review, change freezes, and compliance-driven change control. For deployment strategies and rollback procedures, see [Deployment](deployment.md). For CI/CD pipeline design and GitOps, see [CI/CD](ci-cd.md). For governance frameworks and policy-as-code, see [Governance](governance.md). For compliance automation and audit controls, see [Compliance Automation](compliance-automation.md).

## Checklist

- [ ] **[Critical]** Define change types and their approval paths — standard changes (pre-approved, low-risk, repeatable, no CAB review needed), normal changes (require risk assessment and approval before implementation), and emergency changes (expedited approval for production-impacting incidents, documented retroactively) — and ensure every infrastructure modification is classified into one of these types
- [ ] **[Critical]** Establish a risk assessment framework for infrastructure changes — impact analysis (which services, users, and data are affected), blast radius estimation (single host vs. availability zone vs. region vs. global), rollback feasibility (can the change be reversed within the maintenance window), and a risk scoring matrix that determines the approval level required (peer review, team lead, CAB, executive)
- [ ] **[Critical]** Define rollback criteria and procedures for every change — specify measurable conditions that trigger rollback (error rate exceeds baseline by X%, latency degrades beyond SLO, health checks fail), maximum time-to-rollback targets, and ensure rollback plans are tested before the change is approved, not improvised during an incident
- [ ] **[Critical]** Integrate change management with CI/CD pipelines — automated change record creation from deployment events, deployment gates that verify change approval before production promotion, audit trail linking git commits to change tickets to deployment artifacts, and GitOps reconciliation as a form of continuous change control
- [ ] **[Critical]** Define change windows and maintenance windows — recurring windows for routine changes (weekly, off-peak hours), extended windows for major migrations, notification lead times for each change type (24 hours for standard, 72 hours for normal, immediate for emergency), and stakeholder communication templates for planned maintenance
- [ ] **[Recommended]** Modernize the Change Advisory Board (CAB) process — shift from weekly gate-based CAB meetings to lightweight, asynchronous approval for standard and low-risk changes; reserve synchronous CAB review for high-risk or cross-team changes; use automated risk scoring to route changes to the appropriate approval path; track CAB effectiveness metrics (approval lead time, change success rate, meeting duration)
- [ ] **[Recommended]** Integrate with an ITSM platform for change record lifecycle management — ServiceNow, Jira Service Management, or BMC Remedy for change request tracking, approval workflows, and audit reporting; ensure bidirectional integration between ITSM and CI/CD so change records are created and closed automatically; avoid manual ticket creation as the sole gate for deployments
- [ ] **[Recommended]** Implement post-implementation review (PIR) for failed or high-impact changes — conduct PIR within 48 hours of a failed change or major incident caused by a change, document root cause (process failure, inadequate testing, incorrect risk assessment, environmental difference), feed findings back into risk scoring models and change procedures, and track PIR action items to closure
- [ ] **[Recommended]** Define change freeze policies — scheduled freeze periods for fiscal close (SOX), holiday peak traffic, major business events, and regulatory audit windows; establish an exception process for emergency changes during freezes with executive approval and enhanced monitoring; communicate freeze calendars at least 30 days in advance
- [ ] **[Recommended]** Implement infrastructure drift detection as continuous change monitoring — use tools like Terraform state comparison, AWS Config, Azure Policy compliance, or Crossplane drift detection to identify unauthorized or undocumented changes; alert on drift and require remediation through the standard change process; treat detected drift as a change management failure to investigate
- [ ] **[Optional]** Adopt cloud-native change management patterns — GitOps as the change control system of record (every change is a pull request with review, approval, and audit trail), policy-as-code for automated change validation (OPA, Sentinel), progressive delivery as risk-managed change (canary deployments with automated rollback), and infrastructure-as-code plan review as change impact assessment
- [ ] **[Optional]** Implement change communication automation — automated status page updates (Statuspage, Instatus, Cachet) for planned maintenance, stakeholder notification via integration with email and messaging platforms, real-time change progress dashboards, and post-change summary reports distributed to affected teams

## Why This Matters

Change is the leading cause of production incidents. Industry data consistently shows that 60-80% of outages are caused by changes — deployments, configuration updates, infrastructure modifications, and maintenance activities. An effective change management process does not eliminate risk but makes it visible, assessed, and managed before impact reaches customers.

The tension in change management is between control and velocity. Traditional ITIL-style change management with weekly CAB meetings and multi-day approval cycles was designed for an era of quarterly releases. Modern cloud environments with daily or hourly deployments cannot tolerate that overhead — but they still need risk assessment, audit trails, and rollback planning. The solution is not to abandon change management but to automate it: pre-approved standard changes for routine deployments, automated risk scoring that routes changes to the appropriate approval level, and CI/CD pipelines that create and close change records without human intervention for low-risk changes.

Organizations subject to compliance frameworks (SOX, PCI-DSS, FedRAMP, HIPAA) face additional pressure. Auditors expect documented change records with approval trails, separation of duties between change requestor and approver, and evidence that changes were tested before production deployment. Failing to produce this evidence during an audit creates findings that can escalate to material weaknesses. The most efficient approach is to build compliance evidence generation into the deployment pipeline itself — every deployment automatically produces the change record, approval evidence, test results, and deployment log that auditors need.

## Common Decisions (ADR Triggers)

### ADR: Change Classification and Approval Model

**Context:** The organization must balance change velocity with risk management by defining how changes are classified and what approval each type requires.

**Options:**
- **Traditional ITIL model:** All changes go through CAB review. Provides maximum oversight but creates bottlenecks. Weekly CAB meetings become a scheduling constraint. Standard changes are pre-approved templates but creating new templates requires CAB approval.
- **Risk-tiered model:** Automated risk scoring routes changes to the appropriate approval level. Low-risk changes (standard, pre-approved patterns) proceed with peer review only. Medium-risk changes require team lead approval. High-risk changes (cross-service, database schema, network) require CAB or architecture review. Emergency changes use a streamlined approval with mandatory PIR.
- **GitOps-native model:** Pull request review and approval serves as the change record and approval. Branch protection rules enforce separation of duties. Automated tests and policy checks replace manual risk assessment. CAB is reserved for architectural changes only.

**Decision drivers:** Regulatory requirements (SOX, PCI, FedRAMP mandate documented approval trails), deployment frequency target, team size and on-call structure, and organizational risk tolerance.

### ADR: ITSM Platform Integration Strategy

**Context:** Change records must be tracked in a system of record, and the choice of platform and integration depth affects both compliance posture and developer experience.

**Options:**
- **Full ITSM integration (ServiceNow, BMC Remedy):** Bidirectional API integration between CI/CD and ITSM. Change records created automatically on deployment trigger, closed on successful completion. Provides comprehensive audit trail. High implementation complexity, vendor lock-in risk, and licensing cost.
- **Lightweight ITSM (Jira Service Management, Freshservice):** Lower licensing cost, easier API integration, familiar to development teams already using Jira. May lack enterprise ITSM features (CMDB, dependency mapping, advanced workflow).
- **GitOps as ITSM:** Git history and pull request metadata serve as the change record. Approval via PR review. No separate ITSM platform needed. Lowest friction but may not satisfy auditors who expect a dedicated change management system. Works well for cloud-native organizations without legacy ITSM requirements.

**Decision drivers:** Existing ITSM investment, auditor expectations, deployment volume (high-volume deployments make manual ITSM workflows impractical), and budget for licensing and integration development.

### ADR: Change Freeze Policy

**Context:** The organization must define when changes are restricted and how exceptions are handled during freeze periods.

**Options:**
- **Hard freeze with no exceptions:** No production changes during freeze windows. Simplest to enforce, eliminates change-related risk during critical periods. Can leave critical vulnerabilities unpatched and block incident remediation.
- **Hard freeze with emergency exception process:** No routine changes, but emergency changes (security patches, production-down fixes) proceed with executive approval and enhanced monitoring. Requires clear definition of what constitutes an emergency to prevent abuse.
- **Soft freeze with enhanced review:** Changes are permitted but require additional approval (manager + CAB chair) and enhanced monitoring during and after deployment. Maintains velocity for critical work but increases approval overhead.

**Decision drivers:** Business criticality of freeze periods (revenue impact of holiday outage vs. cost of delayed features), regulatory requirements (SOX fiscal close), historical incident rate during freeze-equivalent periods, and team availability during freeze windows.

### ADR: Drift Detection and Remediation Strategy

**Context:** Infrastructure changes made outside the approved change process (console clicks, manual CLI commands, undocumented automation) create configuration drift that undermines change management.

**Options:**
- **Detect and alert:** Monitor for drift using cloud-native tools (AWS Config, Azure Policy) or IaC state comparison (Terraform plan). Alert the responsible team and require remediation through the standard change process. Low friction but relies on team discipline.
- **Detect and auto-remediate:** Automatically revert unauthorized changes to the declared state (Crossplane, AWS Config auto-remediation, GitOps reconciliation). Prevents drift accumulation but can cause unintended disruption if the declared state is itself incorrect or if emergency changes were made intentionally.
- **Prevent and enforce:** Use IAM policies and service control policies to prevent console access and manual changes entirely. All changes must flow through IaC pipelines. Strictest control but requires mature IaC coverage and can block incident response if pipeline access is unavailable.

**Decision drivers:** IaC coverage maturity (cannot auto-remediate resources not managed by IaC), incident response requirements (operators may need console access during outages), compliance strictness, and team cloud maturity.

## Reference Links

- [ITIL 4 Change Enablement](https://www.axelos.com/certifications/itil-service-management)
- [ServiceNow Change Management](https://docs.servicenow.com/bundle/change-management/)
- [Jira Service Management Change Management](https://www.atlassian.com/software/jira/service-management/change-management)
- [BMC Helix ITSM](https://www.bmc.com/it-solutions/bmc-helix-itsm.html)
- [ArgoCD - GitOps](https://argo-cd.readthedocs.io/)
- [AWS Config Conformance Packs](https://docs.aws.amazon.com/config/latest/developerguide/conformance-packs.html)
- [Azure Policy Compliance](https://learn.microsoft.com/en-us/azure/governance/policy/)
- [DORA State of DevOps Reports](https://dora.dev/)
- [FedRAMP Change Management Controls (CM Family)](https://www.fedramp.gov/)
- [PCI-DSS Requirement 6 - Change Management](https://www.pcisecuritystandards.org/)

## See Also

- [Deployment](deployment.md) — deployment strategies, rollback procedures, and environment promotion
- [CI/CD](ci-cd.md) — pipeline design, artifact management, and GitOps deployment models
- [Governance](governance.md) — tagging, naming, account structure, policy-as-code, and organizational guardrails
- [Compliance Automation](compliance-automation.md) — automated compliance evidence and audit controls
- [Disaster Recovery](disaster-recovery.md) — failover procedures and recovery processes
- [Observability](observability.md) — monitoring, alerting, and incident correlation with change events
- [Security](security.md) — access controls, separation of duties, and audit logging
