# Observability

## Scope

This file covers **what** observability decisions an architecture must address — logging, metrics, tracing, alerting, health checks, dashboards, SLOs, and on-call operations — regardless of cloud provider or platform. For provider-specific **how** (CloudWatch, Azure Monitor, GCP Cloud Monitoring), see the provider observability files linked in See Also.

## Checklist

- [ ] **[Critical]** Define the log aggregation strategy: select a log destination (ELK/OpenSearch, Loki, Splunk, cloud-native), enforce structured log format (JSON with correlation IDs, timestamps, severity levels), and route application logs and infrastructure logs to the same platform for unified search
- [ ] **[Critical]** Collect infrastructure metrics (CPU, memory, disk, network) and application metrics (request rate, error rate, latency percentiles — the RED method) from all services — decide between push-based (StatsD, CloudWatch agent) and pull-based (Prometheus scrape) collection models
- [ ] **[Critical]** Define alerting thresholds that distinguish actionable incidents from noise: set warning thresholds for trend awareness and critical thresholds that page on-call — every alert must have a documented runbook with specific remediation steps, not just "investigate"
- [ ] **[Critical]** Configure health checks for all services: liveness probes (is the process alive — restart if not), readiness probes (can the service accept traffic — remove from load balancer if not), and startup probes (has the service finished initializing) — misconfigured probes cause cascading failures during deployments
- [ ] **[Critical]** Define SLIs (service level indicators) and SLOs (service level objectives) for each service: availability (successful requests / total requests), latency (p50, p95, p99), and throughput — SLOs should be slightly below 100% to create error budget for deployments and experimentation
- [ ] **[Critical]** Establish log retention periods aligned with compliance and operational needs: operational logs typically 30-90 days hot storage, 1-3 years warm/cold for audit and compliance (HIPAA requires 6 years, PCI DSS 1 year, SOC 2 typically 1 year), and define tiering to control storage costs
- [ ] **[Recommended]** Implement distributed tracing across service boundaries (OpenTelemetry, Jaeger, Zipkin, AWS X-Ray, Datadog APM) — define trace sampling strategy (head-based vs. tail-based sampling) balancing cost against diagnostic completeness, with 100% sampling for error traces
- [ ] **[Recommended]** Collect custom application metrics for business-critical KPIs (queue depth, cache hit rate, payment processing latency, active user sessions, job completion rates) — these metrics often detect problems before infrastructure metrics show symptoms
- [ ] **[Recommended]** Design a dashboard strategy: create a service-level dashboard per service showing RED metrics, a platform-level dashboard showing cluster/infrastructure health, and an executive dashboard showing SLO compliance trends — avoid dashboard sprawl by retiring unused dashboards quarterly
- [ ] **[Recommended]** Select on-call alerting and incident management tooling (PagerDuty, Opsgenie, Grafana OnCall, cloud-native SNS/EventBridge) — define escalation policies (primary on-call, secondary, management), rotation schedules, and integrate with chat (Slack/Teams) for incident coordination
- [ ] **[Recommended]** Evaluate the cost of observability data before committing to high-cardinality metrics, verbose log levels, or 100% trace sampling — cloud-native logging (CloudWatch, Azure Monitor) and SaaS platforms (Datadog, Splunk) charge per GB ingested; set budgets and implement log filtering, metric aggregation, and sampling to control spend
- [ ] **[Recommended]** Design observability for containers and serverless: ensure container logs are captured from stdout/stderr via a log driver or DaemonSet (Fluent Bit, Fluentd), serverless functions emit structured logs and custom metrics, and ephemeral workloads include correlation IDs so traces survive container restarts
- [ ] **[Optional]** Deploy synthetic monitoring (external availability checks from multiple regions) to detect outages before users report them — configure synthetic probes for critical user journeys (login, checkout, API health endpoints) with alerting on failure
- [ ] **[Optional]** Implement APM (application performance monitoring) with code-level profiling and automatic service map discovery (Datadog APM, New Relic, Dynatrace, Elastic APM) — most valuable for complex microservice architectures where request flow spans many services

## Why This Matters

Observability is the difference between proactive incident management and reactive firefighting. Without structured logging, meaningful metrics, and distributed tracing, teams spend hours manually correlating timestamps across disparate systems during an outage — turning a 15-minute fix into a multi-hour incident. The cost of poor observability is measured in extended downtime, violated SLAs, lost customer trust, and engineer burnout from stressful on-call rotations with insufficient diagnostic tools.

Modern distributed architectures (microservices, serverless, multi-region) make observability exponentially more important because a single user request can traverse dozens of services, any of which might be the source of a latency spike or error. Without distributed tracing and correlation IDs, root cause analysis becomes guesswork. Without SLOs, teams have no objective measure of whether their service is "healthy enough" or whether to prioritize reliability work over feature development.

Observability also has a significant cost dimension that is frequently underestimated. High-cardinality metrics, verbose debug logging in production, and unsampled traces can generate terabytes of data per day, resulting in five- or six-figure monthly bills from SaaS observability platforms or substantial infrastructure costs for self-hosted solutions. Architecture decisions about log levels, metric cardinality, trace sampling rates, and retention tiers directly determine whether observability spending remains proportional to the value it provides.

## Common Decisions (ADR Triggers)

### ADR: Observability Stack Selection

**Context:** The organization needs a unified platform for logs, metrics, traces, and alerting across all services and infrastructure.

**Options:**

| Criterion | Cloud-Native (CloudWatch / Azure Monitor / GCP Ops) | Prometheus + Grafana + Loki | Datadog | Splunk + SignalFx | Elastic (ELK/OpenSearch) |
|---|---|---|---|---|---|
| Log Aggregation | Built-in, per-GB pricing | Loki (log labels, not full-text index) | Unified with metrics/traces | Enterprise search, powerful SPL query | Full-text search, rich query language |
| Metrics | CloudWatch Metrics / Azure Metrics / Cloud Monitoring | Prometheus TSDB, PromQL | Custom metrics, tags, host maps | SignalFx real-time streaming | Elasticsearch with Metricbeat |
| Tracing | X-Ray / App Insights / Cloud Trace | Jaeger or Tempo | Built-in APM, auto-instrumentation | Splunk APM | Elastic APM |
| Alerting | Native alerting + SNS/Action Groups | Alertmanager + Grafana Alerting | Built-in monitors, composite alerts | Splunk ITSI | Watcher or ElastAlert |
| Cost Model | Per-GB ingested + per-metric + API calls | Infrastructure cost (self-hosted) or Grafana Cloud subscription | Per-host + per-GB logs + per-span traces | Per-GB ingested (Splunk), per-host (SignalFx) | Per-node (self-hosted) or per-GB (Elastic Cloud) |
| Operational Overhead | Zero (managed) | Moderate-high (self-hosted) or low (Grafana Cloud) | Zero (SaaS) | Low (SaaS) or high (self-hosted) | Moderate-high (self-hosted) or low (Elastic Cloud) |
| Best Fit | Single-cloud, small-to-medium teams | Cost-conscious, Kubernetes-native, multi-cloud | Mid-to-large teams wanting single pane of glass | Large enterprise with existing Splunk investment | Organizations needing powerful log search and analytics |

**Decision drivers:** Single-cloud vs. multi-cloud deployment, team size and operational capacity, budget constraints (SaaS per-GB vs. self-hosted infrastructure), existing vendor relationships, and whether the organization already has investment in a specific platform.

### ADR: Log Aggregation Architecture

**Context:** Application and infrastructure logs must be collected, processed, and stored for operational troubleshooting and compliance audit.

**Options:**
- **Cloud-native logging (CloudWatch Logs, Azure Monitor Logs, GCP Cloud Logging):** Zero infrastructure to manage. Logs flow automatically from managed services. Per-GB pricing can be expensive at scale. Limited query language compared to dedicated log platforms.
- **Self-hosted Loki + Grafana:** Index-free log aggregation using labels (like Prometheus for logs). Very cost-effective at scale. Limited to label-based queries — not a full-text search engine. Ideal for Kubernetes environments with existing Prometheus/Grafana.
- **Self-hosted OpenSearch/Elasticsearch:** Full-text search with rich query capabilities. Requires significant cluster management (shards, replicas, index lifecycle). Higher infrastructure cost but no per-GB ingestion fees. Best for organizations that need powerful ad-hoc log analysis.
- **SaaS log platform (Datadog Logs, Splunk Cloud):** Fully managed with powerful search, dashboards, and alerting. Highest per-GB cost but zero operational overhead. Best for teams that prioritize speed over cost optimization.

**Decision drivers:** Log volume (GB/day), query complexity needs (simple grep vs. complex analytics), retention requirements, budget, and team willingness to operate log infrastructure.

### ADR: Alerting and On-Call Strategy

**Context:** The team needs to define what conditions trigger alerts, how alerts reach the on-call engineer, and how incidents are managed from detection through resolution.

**Options:**
- **Cloud-native alerting only (CloudWatch Alarms, Azure Monitor Alerts):** Simple threshold-based alerts routed to SNS/email/Slack. No escalation policies or on-call scheduling. Sufficient for small teams with informal on-call.
- **Dedicated incident management platform (PagerDuty, Opsgenie, Grafana OnCall):** On-call scheduling, escalation policies, incident timelines, post-mortem templates. Integrates with monitoring tools, chat, and ticketing. Essential for teams with formal SLAs and multiple on-call rotations.
- **ChatOps-driven alerting (Slack/Teams with bot integration):** Alerts posted to channels, acknowledged and managed via chat. Good visibility for the team. Risk of alert fatigue if channels are noisy. Works well as a supplement to a dedicated platform, not a replacement.

**Recommendation:** Use a dedicated incident management platform (PagerDuty or Opsgenie) for any production service with an SLA. Route critical alerts (page-worthy) to the on-call engineer's phone; route warning alerts to a Slack channel for awareness. Define escalation: if the primary on-call does not acknowledge within 5 minutes, escalate to secondary, then to engineering management.

### ADR: Trace Sampling Strategy

**Context:** Distributed tracing generates significant data volume. Tracing 100% of requests is ideal for debugging but expensive at scale.

**Options:**
- **Head-based sampling (probabilistic):** Decide whether to trace a request at the entry point (e.g., trace 10% of requests). Simple to implement. Statistically representative but may miss rare error conditions. All downstream services respect the sampling decision.
- **Tail-based sampling:** Collect all trace data temporarily, then decide which traces to keep after the request completes — always keep traces that contain errors, high latency, or specific attributes. Captures all interesting traces regardless of sampling rate. Requires a trace collector with buffering capacity (OpenTelemetry Collector with tail sampling processor).
- **100% sampling with short retention:** Trace every request but retain traces for only 24-48 hours. Best diagnostic completeness. Highest cost and storage requirements. Viable for low-to-medium traffic services.

**Decision drivers:** Request volume (traces per second), budget for trace storage, importance of capturing every error trace, and operational capacity to run tail-sampling infrastructure.

### ADR: SLO Framework

**Context:** The team needs to define and track SLOs to measure service reliability objectively and make data-driven decisions about reliability vs. feature investment.

**Options:**
- **Manual SLO tracking (spreadsheet/dashboard):** Define SLIs in monitoring tool, create dashboards showing SLO compliance. Simple to start. No automated error budget enforcement. Suitable for initial adoption.
- **SLO tooling (Sloth, OpenSLO, Nobl9, Datadog SLOs):** Automated SLI calculation, error budget burn rate alerts, and SLO compliance reporting. Reduces manual effort and provides consistent measurement. Requires upfront investment in SLI definition.
- **Full SRE practice with error budgets:** SLOs drive release decisions — when error budget is exhausted, freeze feature releases and focus on reliability. Requires organizational buy-in beyond engineering. Most effective at balancing reliability and velocity.

**Decision drivers:** Organizational maturity (SLOs require cultural adoption, not just tooling), number of services to track, whether SLOs are customer-facing commitments (SLAs) or internal targets, and team willingness to enforce error budget policies.

## Reference Links

- [OpenTelemetry](https://opentelemetry.io/)
- [Prometheus](https://prometheus.io/)
- [Grafana](https://grafana.com/)
- [Jaeger](https://www.jaegertracing.io/)
- [Fluent Bit](https://fluentbit.io/)
- [PagerDuty](https://www.pagerduty.com/)
- [OpenSLO](https://openslo.com/)

## See Also

- `providers/aws/observability.md` — AWS CloudWatch, X-Ray, and logging configuration
- `providers/azure/observability.md` — Azure Monitor, Application Insights, and Log Analytics
- `providers/gcp/observability.md` — GCP Cloud Monitoring, Cloud Logging, and Cloud Trace
- `general/security.md` — Audit logging requirements overlap with observability; coordinate log destinations and retention policies
- `general/disaster-recovery.md` — Observability is critical for detecting failover triggers and validating DR procedures
- `general/operational-runbooks.md` — Operational runbook design, incident response playbooks, and on-call documentation
