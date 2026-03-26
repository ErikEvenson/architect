# Datadog

## Scope

This file covers **Datadog** observability platform including agent deployment and configuration (host-based, containerized, serverless), APM (distributed tracing, service catalog, service-level objectives), infrastructure monitoring (host metrics, cloud integrations, container monitoring), log management (ingestion, indexing, archiving, log pipelines), synthetic monitoring (API tests, browser tests, private locations), Real User Monitoring (RUM), pricing model analysis (per-host infrastructure, per-GB logs, per-APM-host, custom metrics), integration catalog usage, Datadog vs open-source cost comparison, and hybrid/multi-cloud monitoring strategies. For general observability architecture, see `general/observability.md`.

## Checklist

- [ ] **[Critical]** Is the Datadog agent deployment strategy defined -- host-based agent for VMs and bare metal, DaemonSet for Kubernetes, sidecar or library injection for APM, serverless integration for Lambda/Cloud Functions -- with agent version pinning and update rollout process?
- [ ] **[Critical]** Is the pricing model understood and cost controls implemented -- infrastructure monitoring is per-host ($15-$23/host/month), APM is per-underlying-host ($31-$40/host/month), logs are per-ingested-GB ($0.10/GB ingested + $1.70/million indexed events/month), and custom metrics are charged per metric ($0.05/custom metric/month above allotment)?
- [ ] **[Critical]** Are log management pipelines configured with appropriate filters, processors, and exclusion rules to control ingestion costs -- indexing only actionable logs, archiving raw logs to S3/GCS/Azure Blob for compliance, and using log patterns to reduce noise?
- [ ] **[Critical]** Is APM configured with appropriate trace sampling rates -- head-based sampling to control ingestion volume while retaining 100% of error and high-latency traces, and are service-level objectives (SLOs) defined for critical services?
- [ ] **[Recommended]** Are monitors (alerts) configured with appropriate thresholds, evaluation windows, and notification channels, using composite monitors for multi-condition alerting and anomaly detection for workloads with variable baselines?
- [ ] **[Recommended]** Are dashboards organized with a hierarchy -- executive overview, service-level dashboards, and component-level dashboards -- using template variables for environment/region filtering and shared across teams with appropriate access controls?
- [ ] **[Recommended]** Is synthetic monitoring deployed for critical user journeys with API tests for endpoint availability and browser tests for UI workflows, including private locations for internal application monitoring?
- [ ] **[Recommended]** Are tagging conventions standardized across all telemetry (metrics, traces, logs) -- consistent tags for environment, service, team, and cost center -- to enable correlation across data types and accurate cost attribution?
- [ ] **[Recommended]** Is the cost comparison documented between Datadog and open-source alternatives (Prometheus + Grafana + Loki/ELK) -- considering not just licensing but operational overhead, storage costs, retention capabilities, and feature parity for the specific use case?
- [ ] **[Optional]** Is RUM configured for customer-facing web applications to capture user session data, performance metrics (Core Web Vitals), and error tracking, with session replay enabled for critical applications?
- [ ] **[Recommended]** Is Bits AI evaluated for autonomous alert triage and incident resolution -- Bits AI SRE, Dev Agent, and Security Analyst agents read telemetry from across the environment to autonomously investigate alerts, suggest root causes, and recommend remediation actions?
- [ ] **[Recommended]** Is Datadog LLM Observability evaluated for monitoring AI/LLM workloads -- provides end-to-end tracing of AI agent operations, tracking inputs, outputs, latency, token usage, and errors across frameworks like OpenAI Agent SDK, LangGraph, and CrewAI?
- [ ] **[Optional]** Are Datadog Notebooks or integrated postmortem templates used for incident response documentation, linking monitors, traces, and logs in a single investigation timeline?
- [ ] **[Optional]** Is the Datadog API used for programmatic monitor/dashboard management (monitoring-as-code via Terraform Datadog provider or datadog-api-client) to enable version-controlled observability configuration?

## Why This Matters

Datadog has become the default observability platform for cloud-native environments, offering a unified view across infrastructure, applications, and logs with minimal operational overhead. Its strength -- comprehensive, fully managed observability -- comes at a cost that can escalate rapidly without careful management. Organizations routinely see Datadog bills grow 3-5x beyond initial estimates due to uncontrolled custom metric emission, log indexing without exclusion filters, and APM deployed to every service regardless of criticality. A 500-host environment with APM, logs, and synthetic monitoring can easily reach $20,000-$50,000+/month. Understanding the pricing model and implementing cost controls from day one is not optional -- it is an architectural requirement.

The agent deployment model significantly impacts both coverage and cost. In Kubernetes environments, the DaemonSet deployment provides per-node infrastructure monitoring, but APM requires additional configuration (library injection, admission controller, or sidecar). Hybrid environments (cloud VMs, on-premises servers, Kubernetes clusters) require a unified tagging strategy so that dashboards and monitors work consistently across platforms. Without standardized tags, teams end up with fragmented visibility and duplicated monitoring effort.

## Common Decisions (ADR Triggers)

- **Datadog vs open-source (Prometheus + Grafana + Loki/ELK)** -- Datadog eliminates operational overhead (no Prometheus scaling, no Elasticsearch cluster management) and provides superior correlation across metrics, traces, and logs in a single UI. Open-source provides zero licensing cost but requires significant engineering effort for deployment, scaling, retention, and HA -- typically 0.5-2 FTE for a production-grade stack. Choose Datadog when engineering time is more expensive than licensing; open-source when budget is constrained and in-house expertise exists. Hybrid approaches (Prometheus for Kubernetes metrics, Datadog for APM and logs) can optimize cost but fragment visibility.
- **Log indexing vs archiving strategy** -- Indexing all logs enables search and alerting but costs $1.70/million events/month (indexed). Archiving to object storage costs only the storage fee (~$0.02/GB/month) but requires rehydration for search. The recommended pattern is: index error, warning, and audit logs; archive everything for compliance; use Logging without Limits to ingest all logs for live tail and metrics extraction without indexing.
- **APM scope -- all services vs critical path only** -- Full APM coverage provides complete distributed trace visibility but APM is priced per underlying host ($31-$40/host/month). In large microservice environments (100+ services on 50+ hosts), selective APM deployment to critical-path services reduces cost while maintaining visibility where it matters most. Use trace propagation headers for context across instrumented and non-instrumented services.
- **Single Datadog organization vs multi-org** -- A single organization provides unified visibility and simpler management. Multi-org (separate Datadog accounts per business unit or environment) provides cost isolation and access control but prevents cross-org correlation. Use a single organization with RBAC and teams for most scenarios; multi-org only when strict financial or data isolation is required.
- **Committed use pricing vs on-demand** -- Datadog offers committed use discounts (annual or multi-year) with 20-40% savings over on-demand pricing, but requires accurate forecasting. Over-commitment wastes budget; under-commitment incurs overage charges. Start on-demand for 3-6 months to establish baseline usage, then negotiate committed pricing based on actual consumption with 10-20% growth buffer.
- **Bits AI adoption** -- enable autonomous alert triage (faster MTTR, reduced toil) vs manual investigation workflows (more control, no AI dependency); LLM Observability for teams deploying AI applications.

## AI and GenAI Capabilities

**Bits AI** — Datadog's autonomous AI agents for DevOps. Three agents: Bits AI SRE (alert triage, incident investigation, root cause analysis), Bits AI Dev Agent (code-level debugging from traces), and Bits AI Security Analyst (threat investigation from security signals). Used by 2,000+ enterprise customers. Reduces MTTR by automating the investigation workflow that previously required manual telemetry correlation.

**LLM Observability** — Monitor AI applications in production. Provides end-to-end tracing across AI agent operations with visibility into inputs, outputs, latency, token usage, and errors at each step. SDK automatically tracks operations built with OpenAI Agent SDK, LangGraph, CrewAI, Bedrock Agent SDK, and other frameworks. Includes AI Guard for prompt injection detection and sensitive data scanning.

## See Also

- `general/observability.md` -- general observability architecture patterns and pillar design
- `providers/prometheus-grafana/observability.md` -- Prometheus and Grafana for open-source monitoring comparison

## Reference Links

- [Datadog Documentation](https://docs.datadoghq.com/) -- agent deployment, APM, infrastructure monitoring, log management, and integrations
- [Datadog Pricing](https://docs.datadoghq.com/account_management/billing/) -- per-host, per-GB, and custom metrics pricing model details
- [Datadog API Reference](https://docs.datadoghq.com/api/) -- REST API for automation, dashboard creation, and monitor management
