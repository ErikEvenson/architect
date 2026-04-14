# Jira Service Management

## Scope

This file covers **Jira Service Management** (JSM, formerly Jira Service Desk) for IT service management including project configuration and service desk setup, request types and custom fields, SLA management and calendar configuration, automation rules for workflow optimization, Opsgenie integration for incident alerting and on-call management, Confluence knowledge base integration, Assets (formerly Insight) for CMDB functionality, API integration (REST), and Cloud vs Data Center deployment considerations. For general ITSM integration patterns, see `general/itsm-integration.md`.

## Checklist

- [ ] **[Critical]** Is the JSM project structure defined -- separate service projects per team or shared project with request types, with appropriate customer portal configuration, queues for agent triage, and workflow schemes mapped to ITIL processes (incident, change, problem, service request)?
- [ ] **[Critical]** Are SLAs configured with correct time metrics (time to first response, time to resolution), calendar definitions (business hours, 24x7, holidays), and SLA conditions that match contractual commitments, with breach notifications routed to appropriate managers?
- [ ] **[Critical]** Is Opsgenie integration configured for incident alerting with on-call schedules, escalation policies (time-based and condition-based), routing rules that direct alerts to the correct team, and heartbeat monitoring for critical integration endpoints?
- [ ] **[Critical]** Are customer permissions properly configured -- who can raise requests (organization members, email domain, open portal), who can view request history, and are internal comments separated from customer-visible comments to prevent information leakage?
- [ ] **[Recommended]** Are automation rules configured for common workflows -- auto-assignment based on request type or component, auto-transition on customer response, SLA breach escalation, and notification rules -- with rule execution limits monitored to stay within plan allowances?
- [ ] **[Recommended]** Is Confluence knowledge base linked to the service project, with knowledge articles surfaced during request creation to enable self-service deflection, and are article effectiveness metrics (views, helpful votes, deflection rate) tracked?
- [ ] **[Recommended]** Is Assets (CMDB) configured with appropriate object schemas, object types, and attributes for IT assets, with import sources defined (discovery tools, CSV, API) and reference attributes linking CIs to service projects for impact visibility?
- [ ] **[Recommended]** Are change management workflows configured with risk assessment fields, approval steps (via Jira approvers or integrated CAB process), implementation and backout plan fields, and post-implementation review requirements?
- [ ] **[Recommended]** Is the Cloud vs Data Center decision evaluated -- Cloud provides automatic upgrades, Atlassian-managed infrastructure, and Forge/Connect app ecosystem; Data Center provides self-hosted control, data residency, and SAML/SSO flexibility but requires infrastructure management and manual upgrades?
- [ ] **[Optional]** Are custom dashboards configured for ITSM metrics using JSM reports and Jira dashboards -- open vs resolved trend, SLA compliance percentage, mean time to resolution, request type distribution, and agent workload balance?
- [ ] **[Optional]** Is the REST API integration architecture defined for external system connectivity, including webhook configuration for outbound events, API token management (OAuth 2.0 for Cloud, PATs for Data Center), and rate limit handling (Cloud enforces rate limits per app)?
- [ ] **[Optional]** Are forms configured for structured data collection on complex request types, replacing free-text descriptions with validated fields that improve triage accuracy and enable automation?
- [ ] **[Recommended]** Is Atlassian Intelligence (Rovo) evaluated — AI-powered features including natural language to JQL search, AI work breakdown (epic to user stories), content generation, and AI agents that can be assigned work directly in Jira?
- [ ] **[Optional]** Is Atlassian's MCP (Model Context Protocol) support evaluated for connecting external AI agents to Jira and Confluence workflows?

## Why This Matters

Jira Service Management occupies a growing share of the ITSM market, particularly in organizations that already use Jira Software for development and want a unified platform for IT operations and DevOps collaboration. JSM's strength is its tight integration with the Jira ecosystem -- incidents can be linked directly to development issues, changes tracked alongside sprints, and knowledge managed in Confluence. However, JSM's ITSM capabilities are less mature than ServiceNow's for large-scale enterprise use: Assets (CMDB) lacks the depth of ServiceNow's CMDB with service mapping, automation rules have execution limits on lower-tier plans, and multi-department shared service management requires careful project and queue design to avoid confusion.

Opsgenie integration is a critical architectural component for incident management. Without properly configured on-call schedules and escalation policies, alerts from monitoring systems either wake everyone or reach no one. The transition from Opsgenie standalone to JSM-integrated incident management is a common migration scenario that requires careful mapping of existing alert rules, schedules, and integrations. The Cloud vs Data Center decision has become urgent with Atlassian's end-of-support for Server licenses, forcing organizations to migrate to either platform with significant architectural implications for data residency, SSO integration, and third-party app availability.

## Common Decisions (ADR Triggers)

- **JSM Cloud vs Data Center** -- Cloud provides the latest features (Atlassian Intelligence, cloud-native APIs, marketplace apps), automatic upgrades, and zero infrastructure management, but data resides in Atlassian's infrastructure (AWS regions) with limited data residency options. Data Center provides full data control, on-premises or private cloud deployment, and unlimited users with a flat license, but requires infrastructure teams for upgrades, scaling, and maintenance. Cloud is recommended for most organizations; Data Center for those with strict data sovereignty requirements or very large scale (10,000+ agents).
- **JSM vs ServiceNow** -- JSM is more cost-effective (Cloud pricing starts at $22.05/agent/month vs ServiceNow's enterprise pricing), simpler to configure, and integrates natively with Jira Software for DevOps workflows. ServiceNow offers deeper ITSM maturity (CMDB service mapping, Performance Analytics, ITOM), broader enterprise workflow capabilities (HR, Security Operations, Customer Service), and dominates large enterprise RFPs. Choose JSM for mid-market organizations or DevOps-oriented teams; ServiceNow for large enterprises requiring comprehensive ITSM with complex workflows.
- **Opsgenie integrated vs standalone** -- JSM Premium includes Opsgenie-equivalent functionality (incident management, on-call, alerting) directly within JSM. Standalone Opsgenie provides a dedicated alerting platform that can integrate with any ITSM tool, not just JSM. Use integrated JSM Premium when JSM is the primary ITSM tool; standalone Opsgenie when alerting needs to feed multiple ITSM platforms or when existing Opsgenie configurations should not be disrupted.
- **Single project vs multi-project structure** -- A single service project simplifies customer experience (one portal) and reporting but can become unwieldy with many request types and queues. Multiple projects (per department or service area) provide cleaner separation but fragment the customer portal and require cross-project reporting. Use a single project for organizations with fewer than 50 request types; multiple projects when teams need independent workflows and queue management.
- **Assets (CMDB) vs external CMDB** -- JSM Assets provides native CMDB within the Atlassian ecosystem with direct linking to issues and automation rule integration. External CMDBs (ServiceNow CMDB, Device42, Lansweeper) may offer more sophisticated discovery, reconciliation, and service mapping. Use Assets when JSM is the primary ITSM platform and CMDB needs are moderate; external CMDB when advanced discovery and service dependency mapping are required.
- **Atlassian Intelligence adoption** -- Rovo AI features require Cloud Premium or Enterprise plans and Atlassian Intelligence to be enabled by an org admin. Evaluate whether AI-powered JQL search, work breakdown, and Rovo agents add value for the team's workflow maturity level. Consider data residency implications — Atlassian Intelligence processes data through third-party LLMs. Organizations with strict data sovereignty requirements should review Atlassian's AI data handling policies before enabling.

## AI and GenAI Capabilities

**Atlassian Intelligence / Rovo** — AI assistant embedded across Jira and Confluence. Key features: NL→JQL translation (search Jira using plain English), AI work breakdown (auto-suggest user stories from epics), generative AI editor (draft and rewrite content), and AI-powered summarization. Rovo agents can be assigned work in Jira, iterate via comments, and be embedded in automated workflows. February 2026: Atlassian announced open beta of agents in Jira with MCP support for third-party agent integration.

## See Also

- `providers/atlassian/jsm-operations.md` -- SLA engine mechanics, automation rule limits, queue design, approvals, linked-issue discipline
- `providers/servicenow/itsm-operations.md` -- ServiceNow operational parity (SLA engine, hold_reason, Performance Analytics)
- `general/itsm-integration.md` -- general ITSM integration patterns and boundary decisions
- `general/managed-services-scoping.md` -- managed services scope definition and ITSM tool selection

## Reference Links

- [Jira Service Management Documentation](https://support.atlassian.com/jira-service-management-cloud/) -- request types, SLAs, automation rules, and service desk configuration
- [Jira Service Management Assets (CMDB)](https://support.atlassian.com/jira-service-management-cloud/docs/manage-assets-with-jira-service-management/) -- asset schemas, object types, and CMDB configuration
- [Opsgenie Documentation](https://support.atlassian.com/opsgenie/) -- incident alerting, on-call schedules, escalation policies, and integration with JSM
