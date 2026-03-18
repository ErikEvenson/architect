# Azure Observability

## Scope

Azure monitoring, logging, and diagnostics services. Covers Log Analytics workspaces, Application Insights, Azure Monitor alerts and action groups, Network Watcher, Microsoft Sentinel (SIEM), data collection rules, and distributed tracing with W3C TraceContext.

## Checklist

- [ ] **[Critical]** Is a centralized Log Analytics workspace deployed with appropriate retention period (30-730 days) and pricing tier (per-GB vs commitment tier) for the expected ingestion volume?
- [ ] **[Critical]** Are diagnostic settings enabled for all Azure resources, streaming platform metrics and resource logs to the Log Analytics workspace?
- [ ] **[Recommended]** Is Application Insights configured for all application workloads with appropriate sampling rate to balance cost and telemetry fidelity?
- [ ] **[Critical]** Are Azure Monitor action groups configured with appropriate notification channels (email, SMS, webhook, ITSM, Logic App) and suppression rules to prevent alert fatigue?
- [ ] **[Critical]** Are metric alerts, log alerts, and activity log alerts defined for critical thresholds (CPU, memory, error rates, latency P95/P99, availability)?
- [ ] **[Optional]** Is Azure Monitor Workbooks used to create shared, interactive dashboards combining metrics, logs, and parameters for operational visibility?
- [ ] **[Recommended]** Is Network Watcher enabled in every region with NSG flow logs (version 2) streaming to Log Analytics for traffic analytics and anomaly detection?
- [ ] **[Optional]** Is Connection Monitor configured to continuously test connectivity between Azure VMs, on-premises endpoints, and external URLs with latency and packet-loss thresholds?
- [ ] **[Recommended]** Is Microsoft Sentinel (SIEM) deployed with data connectors for Entra ID (formerly Azure AD) sign-in logs, Azure Activity, Microsoft 365, and threat intelligence feeds?
- [ ] **[Optional]** Are Kusto Query Language (KQL) queries saved as functions in the workspace for reusable operational and security investigations?
- [ ] **[Recommended]** Is cost management for monitoring configured -- data collection rules (DCRs) filtering unnecessary logs, ingestion caps on Log Analytics, and daily caps on Application Insights?
- [ ] **[Optional]** Are Azure Dashboards configured for executive and operational views, pinning key metrics from Azure Monitor, Application Insights, and Resource Health?
- [ ] **[Recommended]** Is distributed tracing enabled end-to-end with Application Insights correlation across microservices using W3C TraceContext propagation?
- [ ] **[Optional]** Are smart detection and dynamic thresholds configured in Azure Monitor to detect anomalies without manually setting static alert thresholds?

## Why This Matters

Azure's observability stack is deeply integrated but spread across multiple services -- Azure Monitor for metrics, Log Analytics for logs, Application Insights for APM, and Sentinel for SIEM. Unlike AWS CloudWatch (which consolidates most telemetry), Azure requires explicit diagnostic settings on every resource to route telemetry to a workspace. Log Analytics workspace design (single vs multiple, cross-workspace queries) has significant cost and query-performance implications. Application Insights uses sampling by default, which can hide low-frequency errors if not tuned. NSG flow logs are essential for network visibility but generate substantial data volume that must be managed.

## Common Decisions (ADR Triggers)

- **Single vs multiple Log Analytics workspaces** -- centralized simplicity and cross-resource correlation vs data sovereignty, RBAC isolation, and cost allocation per team
- **Application Insights classic vs workspace-based** -- workspace-based is now recommended, enabling unified KQL queries and longer retention
- **Sampling strategy** -- adaptive sampling (auto-adjusts) vs fixed-rate sampling vs ingestion sampling; trade-off between cost and telemetry completeness
- **Azure Monitor vs third-party APM** -- native integration vs Datadog, Dynatrace, or New Relic for multi-cloud consistency
- **Microsoft Sentinel vs third-party SIEM** -- native Azure integration and KQL vs Splunk, Elastic, or Sumo Logic for existing toolchain investment
- **Data collection rules (DCRs) vs legacy agent** -- Azure Monitor Agent with DCRs replaces the deprecated Log Analytics Agent (MMA) by August 2024
- **Alert routing** -- action groups with ITSM connectors vs webhook to PagerDuty/Opsgenie for incident management

## Reference Architectures

- [Azure Architecture Center: Monitoring and diagnostics guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/monitoring) -- end-to-end observability patterns for health, availability, and performance monitoring
- [Azure Monitor best practices](https://learn.microsoft.com/en-us/azure/azure-monitor/best-practices) -- planning, configuration, and cost optimization for Azure Monitor deployment
- [Azure Well-Architected Framework: Monitoring](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/observability) -- operational excellence pillar guidance for observability and diagnostics
- [Microsoft Sentinel design workspace architecture](https://learn.microsoft.com/en-us/azure/sentinel/design-your-workspace-architecture) -- decision framework for single-tenant, multi-tenant, and multi-workspace Sentinel deployments
- [Azure Architecture Center: Enterprise monitoring with Azure Monitor](https://learn.microsoft.com/en-us/azure/architecture/example-scenario/monitoring/enterprise-monitoring) -- reference architecture for large-scale monitoring with Log Analytics and Sentinel

---

## See Also

- `general/observability.md` -- General observability patterns including metrics, logs, and traces
- `providers/azure/security.md` -- Microsoft Sentinel SIEM and Defender for Cloud integration
- `providers/azure/networking.md` -- Network Watcher and NSG Flow Logs for network observability
