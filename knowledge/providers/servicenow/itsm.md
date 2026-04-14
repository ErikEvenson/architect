# ServiceNow

## Scope

This file covers **ServiceNow** platform architecture for IT service management including instance architecture and deployment (single-instance vs multi-instance, data center selection), ITSM module configuration (incident, change, problem, request), CMDB design (CI classes, identification rules, discovery, reconciliation, health scoring), Flow Designer and workflow automation, Integration Hub and spoke-based integrations, Event Management for alert correlation, ITOM (discovery, service mapping, cloud management), Now Assist and Generative AI Controller (GenAI integration with external LLMs), licensing models (ITSM Standard, Professional, Enterprise), API integration patterns (REST, IntegrationHub, MID Server), and managed services operational patterns. For general ITSM integration patterns, see `general/itsm-integration.md`.

## Checklist

- [ ] **[Critical]** Is the ServiceNow instance architecture defined -- production, sub-production (dev, test, staging) instances with proper cloning schedule, update set promotion process, and instance separation to prevent development changes from reaching production without testing?
- [ ] **[Critical]** Is the CMDB data model designed with appropriate CI classes (server, application, business service), identification and reconciliation rules (IRE) to prevent duplicate CIs, and authoritative data sources defined per CI attribute?
- [ ] **[Critical]** Are integration patterns defined using appropriate mechanisms -- REST API (Table API, Import Set API) for external system sync, MID Server for on-premises data collection and discovery, IntegrationHub spokes for pre-built connectors -- with authentication (OAuth 2.0 preferred over basic auth) and rate limiting configured?
- [ ] **[Critical]** Is the change management process configured with appropriate change models (standard, normal, emergency), risk assessment automation, CAB workbench for approval workflows, and deployment windows aligned with business availability requirements?
- [ ] **[Recommended]** Is ServiceNow Discovery configured with appropriate MID Server placement (one per network segment/security zone), credential management (discovery credentials stored in ServiceNow, not shared accounts), and classification rules to correctly identify CI types?
- [ ] **[Recommended]** Is Event Management configured to correlate monitoring alerts into actionable incidents -- with alert rules, event correlation, suppression for known maintenance windows, and integration with monitoring tools (via connectors or REST)?
- [ ] **[Recommended]** Are Flow Designer workflows used instead of legacy workflows for new automation, with proper error handling, rollback actions, and subflows for reusable components?
- [ ] **[Recommended]** Is the service catalog structured with appropriate categories, catalog items, record producers, and fulfillment workflows that include approval steps and automated provisioning through Orchestration or IntegrationHub?
- [ ] **[Recommended]** Is the licensing model appropriate -- ITSM Standard (basic incident/change/problem), Professional (adds Performance Analytics, Virtual Agent, Predictive Intelligence), Enterprise (adds workforce optimization, process optimization) -- and are fulfiller vs requester license counts accurate?
- [ ] **[Optional]** Is Service Mapping configured to auto-discover application dependencies and create business service maps in the CMDB, rather than relying on manual relationship entry?
- [ ] **[Optional]** Is Performance Analytics configured with appropriate indicators (KPIs), breakdowns, and dashboards for ITSM metrics (MTTR, change success rate, SLA compliance) with data collection jobs scheduled at appropriate intervals?
- [ ] **[Optional]** Are domain separation or scoped applications used to isolate data and configuration for multi-tenant managed services scenarios, with appropriate domain visibility rules?
- [ ] **[Recommended]** Is Now Assist (ServiceNow GenAI) evaluated for the engagement -- Now Assist provides case/incident summarization, chat conversation summaries, code generation for ServiceNow scripting, natural language search, and knowledge article generation, built on the Generative AI Controller?
- [ ] **[Recommended]** Is the Generative AI Controller configured with the appropriate LLM provider -- pre-built spokes for Azure OpenAI, Google Vertex AI, and other providers, or the Generic LLM Connector for any OpenAI-compatible API endpoint (including custom RAG-augmented endpoints)?
- [ ] **[Optional]** Is a custom RAG integration evaluated via the Generic LLM Connector -- routing ServiceNow prompts through a domain-specific LLM endpoint that augments responses with organization-specific knowledge, rather than relying solely on generic LLM responses?
- [ ] **[Recommended]** Is an upgrade and patching strategy defined for ServiceNow -- including family release adoption timeline (N-1 is recommended), upgrade testing procedures on sub-production, and skipping behavior validation for customizations and integrations?

## Why This Matters

ServiceNow is the dominant enterprise ITSM platform with over 80% market share in large enterprises, making it a near-certain integration point in any managed services or enterprise architecture engagement. The platform's strength -- extreme configurability -- is also its primary risk: over-customization leads to upgrade difficulties, performance degradation, and technical debt that compounds with each release. CMDB quality is the foundation of effective ITSM processes; incidents cannot be correctly routed, changes cannot be impact-assessed, and services cannot be mapped without accurate CI data. Organizations that deploy ServiceNow without a CMDB strategy inevitably end up with thousands of orphaned or duplicate CIs that undermine every process built on top of them.

Integration architecture is critical because ServiceNow typically sits at the center of an IT ecosystem, connecting with monitoring tools, cloud platforms, identity providers, and communication systems. Poor integration patterns -- such as direct table manipulation instead of Import Set API, missing MID Server placement for on-premises resources, or synchronous API calls without retry logic -- lead to data inconsistencies and brittle integrations that break during ServiceNow upgrades. The MID Server architecture deserves special attention: improperly sized or placed MID Servers create bottlenecks for discovery, orchestration, and on-premises integrations.

## Common Decisions (ADR Triggers)

- **Single instance vs multi-instance** -- A single production instance simplifies administration, integration, and reporting. Multi-instance (separate instances per business unit or region) provides isolation but creates data silos, requires cross-instance integration, and multiplies licensing and administration costs. ServiceNow strongly recommends single-instance with domain separation for multi-tenancy. Choose multi-instance only when regulatory requirements mandate data isolation (e.g., government classifications).
- **CMDB-first vs process-first implementation** -- Deploying ITSM processes before establishing CMDB accuracy means incident routing and change impact rely on manual knowledge. CMDB-first (discovery, reconciliation, health scoring) before process activation ensures automation has reliable data. CMDB-first is recommended but requires discovery infrastructure (MID Servers, credentials, network access) as a prerequisite.
- **IntegrationHub vs custom REST integrations** -- IntegrationHub provides pre-built spokes (500+) for common platforms with low-code configuration, error handling, and logging. Custom REST integrations via Scripted REST APIs or outbound REST messages offer complete control but require development effort and maintenance. Use IntegrationHub spokes when available; custom integrations when spoke functionality is insufficient or when performance/volume requires optimization.
- **Event Management vs direct incident creation** -- Direct incident creation from monitoring tools (one alert = one incident) is simpler but causes incident storms during major outages. Event Management adds an abstraction layer that correlates multiple alerts into a single incident, applies suppression rules during maintenance windows, and enriches events with CMDB data. Event Management is recommended for any environment generating more than 100 alerts per day.
- **Platform customization vs configuration** -- Out-of-box (OOB) configuration using ServiceNow best practices ensures upgrade compatibility and platform support. Customization (modifying OOB scripts, tables, or behaviors) provides exact functionality but creates upgrade conflicts and voids platform support for affected areas. Follow the "configure before customize" principle; document all customizations with business justification and upgrade impact assessment.
- **Now Assist (GenAI) adoption vs deferral** -- Now Assist provides immediate productivity gains (incident summarization, knowledge generation, natural language search) but requires Pro or Enterprise licensing and Generative AI Controller configuration. The Generic LLM Connector enables routing prompts through custom RAG-augmented endpoints for domain-specific answers, but adds integration complexity. Evaluate whether out-of-box Now Assist features justify the licensing uplift, or whether a custom GenAI integration via the Generic LLM Connector better serves the use case.

## Now Assist and Generative AI Controller

ServiceNow's AI integration layer consists of two components:

**Now Assist** is ServiceNow's GenAI feature set, built on the Generative AI Controller:
- Case and incident summarization (auto-generates work notes from interaction history)
- Chat conversation summaries for agent handoff
- Code generation for ServiceNow scripting (Business Rules, Script Includes)
- Natural language search across knowledge bases and service catalog
- Knowledge article generation from resolved incidents

**Generative AI Controller** is the integration layer for connecting external LLMs:
- **Pre-built spokes** — connectors for Azure OpenAI, Google Vertex AI, and other major providers
- **Generic LLM Connector** — connect any OpenAI-compatible API endpoint, including custom endpoints that wrap a domain-specific knowledge base with RAG
- Prompt templates and response processing configurable per use case
- Token usage tracking and cost management

**Custom RAG integration pattern:** The Generic LLM Connector can point to a custom API that performs RAG over an organization-specific knowledge base before forwarding to an LLM. This enables ServiceNow workflows (incident resolution, change risk assessment, knowledge search) to receive domain-specific answers rather than generic LLM responses — without modifying ServiceNow's core platform.

**Licensing:** Now Assist features require ServiceNow Pro or Enterprise licensing. The Generative AI Controller is available with Pro+ licensing. LLM API costs (tokens) are separate from ServiceNow licensing.

## See Also

- `providers/servicenow/itsm-operations.md` -- SLA engine, hold_reason, Performance Analytics, state model, and automation placement
- `general/itsm-integration.md` -- general ITSM integration patterns and boundary decisions
- `general/managed-services-scoping.md` -- managed services scope definition and ITSM boundary decisions
- `general/ai-ml-services.md` -- cross-provider AI service strategy (model selection, RAG, cost patterns)
- `providers/azure/ai-ml-services.md` -- Azure OpenAI (common LLM backend for Now Assist)

## Reference Links

- [ServiceNow Product Documentation](https://docs.servicenow.com/) -- ITSM, CMDB, ITOM, Flow Designer, and Integration Hub configuration
- [ServiceNow Developer Portal](https://developer.servicenow.com/) -- REST API reference, scripting guides, and instance provisioning for development
- [ServiceNow Generative AI](https://www.servicenow.com/platform/generative-ai.html) -- Now Assist features, Generative AI Controller, and GenAI use cases
- [Now Assist](https://www.servicenow.com/platform/now-assist.html) -- Now Assist capabilities, supported workflows, and licensing requirements
- [Generative AI Controller FAQ](https://www.servicenow.com/community/now-assist-articles/generative-ai-controller-faq/ta-p/2686478) -- GenAI Controller configuration, LLM provider setup, and Generic LLM Connector
