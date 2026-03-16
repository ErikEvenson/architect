# GCP Observability

## Checklist

- [ ] **[Critical]** Is Cloud Monitoring configured with workspaces scoped to the correct set of projects, with a designated metrics-scoping project for multi-project visibility?
- [ ] **[Optional]** Are custom metrics defined using the monitoring.googleapis.com/user/ prefix with appropriate metric kinds (gauge, delta, cumulative) and value types for application-specific KPIs?
- [ ] **[Recommended]** Are uptime checks configured for critical endpoints with appropriate check frequencies (1-15 min), regions, and content matching, feeding into alerting policies?
- [ ] **[Critical]** Are alerting policies configured with appropriate conditions (metric threshold, metric absence, forecasted), notification channels (PagerDuty, Slack, email), and documentation runbooks?
- [ ] **[Critical]** Is Cloud Logging configured with a log router that uses inclusion/exclusion filters to control log volume and cost, routing only actionable logs to storage sinks?
- [ ] **[Critical]** Are log sinks configured to route audit logs and security-critical logs to Cloud Storage (long-term archival), BigQuery (analytics), or Pub/Sub (SIEM integration)?
- [ ] **[Recommended]** Are log-based metrics created for application-specific error patterns, latency distributions, and business events that are not captured by default platform metrics?
- [ ] **[Recommended]** Is Cloud Trace enabled with appropriate sampling rates (default 1 request/1000 for App Engine, configurable for GKE/Compute) and propagation context across services?
- [ ] **[Recommended]** Is Error Reporting configured for all application runtimes with proper exception grouping, and are new error notifications routed to the development team?
- [ ] **[Optional]** Is Cloud Profiler deployed to production services for continuous CPU and heap profiling with minimal overhead (<5%), using the appropriate agent for each runtime?
- [ ] **[Recommended]** Is Managed Service for Prometheus deployed for GKE workloads, with PodMonitoring and ClusterPodMonitoring resources configured for scrape targets?
- [ ] **[Optional]** Are Grafana dashboards connected to Cloud Monitoring via the Google Cloud Monitoring data source plugin, or is Managed Grafana (via Marketplace) used for unified visualization?
- [ ] **[Recommended]** Are log retention periods configured per log bucket (default 30 days for _Default, 400 days for _Required), with custom buckets created for compliance-driven retention?
- [ ] **[Recommended]** Is the Operations Suite agent (Ops Agent) installed on Compute Engine VMs for system and application log/metric collection, replacing the legacy Monitoring and Logging agents?

## Why This Matters

GCP observability is built on the Google Cloud Operations Suite (formerly Stackdriver), which provides tightly integrated metrics, logging, tracing, and profiling. Unlike AWS CloudWatch, Cloud Monitoring uses a metrics-scoping project model where one project can monitor many others. Cloud Logging's log router is a powerful but cost-critical component: uncontrolled log ingestion is the most common source of unexpected observability costs. Log exclusion filters discard logs before ingestion charges apply, while sinks can route logs to cheaper storage tiers. Managed Service for Prometheus provides a fully managed, globally available Prometheus backend without managing Thanos or Cortex, making it the preferred metrics path for GKE workloads.

## Common Decisions (ADR Triggers)

- **Metrics backend** -- Cloud Monitoring custom metrics vs Managed Service for Prometheus vs self-hosted Prometheus, cost per time series considerations
- **Log routing architecture** -- _Default sink only vs custom sinks to BigQuery/Cloud Storage/Pub/Sub, per-project vs organization-level sinks
- **Log retention vs cost** -- default 30-day retention vs custom log buckets with extended retention, compliance-driven archival to Cloud Storage
- **Alerting strategy** -- Cloud Monitoring alerting policies vs Prometheus Alertmanager via Managed Prometheus vs PagerDuty native integration
- **Tracing approach** -- Cloud Trace with OpenTelemetry SDK vs Jaeger/Zipkin on GKE with custom backend, sampling rate tuning
- **Dashboard tooling** -- Cloud Monitoring dashboards vs Managed Grafana vs self-hosted Grafana, PromQL vs MQL query language
- **Profiling adoption** -- Cloud Profiler for all services vs selective profiling for latency-critical paths, always-on vs on-demand
- **Multi-project observability** -- single metrics-scoping project vs per-environment scoping projects, organization-level log sinks

## Reference Architectures

- [Google Cloud Architecture Center: DevOps and monitoring](https://cloud.google.com/architecture#devops-and-monitoring) -- reference architectures for observability pipelines, alerting, and SRE practices
- [Google Cloud Architecture Framework: Operational excellence - Monitoring](https://cloud.google.com/architecture/framework/operational-excellence/monitoring) -- best practices for metrics, logging, alerting, and incident response
- [Google Cloud: Managed Service for Prometheus](https://cloud.google.com/stackdriver/docs/managed-prometheus) -- reference architecture for Prometheus-compatible monitoring on GKE with global query federation
- [Google Cloud: Designing and deploying a log analytics pipeline](https://cloud.google.com/architecture) -- reference design for log routing, BigQuery analytics, and long-term archival
- [Google Cloud: Best practices for monitoring with Cloud Operations](https://cloud.google.com/monitoring/docs) -- reference patterns for workspace organization, custom metrics, and alerting policy design
