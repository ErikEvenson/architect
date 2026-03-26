# OpenShift Observability

## Scope

OpenShift observability: built-in Prometheus/Alertmanager/Grafana stack, user workload monitoring, ServiceMonitor/PodMonitor, OpenShift Logging (LokiStack with Vector), ClusterLogForwarder, distributed tracing (Tempo, OpenTelemetry), and Network Observability operator.


## Checklist

- [ ] **[Critical]** Configure the built-in monitoring stack: Prometheus, Alertmanager, and Grafana (read-only in OCP; custom Grafana for write dashboards)
- [ ] **[Recommended]** Enable user workload monitoring via `cluster-monitoring-config` ConfigMap (`enableUserWorkload: true`)
- [ ] **[Recommended]** Define ServiceMonitor and PodMonitor CRDs for application metric scraping
- [ ] **[Critical]** Configure Alertmanager receivers: email, PagerDuty, Slack, webhook, or OpsGenie integration
- [ ] **[Recommended]** Create PrometheusRule CRDs for custom alerting rules (application SLOs, error budgets, saturation thresholds)
- [ ] **[Recommended]** Deploy OpenShift Logging operator with LokiStack (Vector as collector, Loki as store, ODF/S3 for object storage backend)
- [ ] **[Recommended]** Configure ClusterLogForwarder for log routing: forward to external systems (Splunk, Elasticsearch, Kafka, Syslog, CloudWatch)
- [ ] **[Optional]** Deploy distributed tracing: Tempo operator for trace storage, OpenTelemetry Collector operator for instrumentation
- [ ] **[Optional]** Install Network Observability operator for eBPF-based flow collection (NetObserv FlowCollector CR)
- [ ] **[Recommended]** Build capacity dashboards: CPU/memory utilization per namespace, PVC usage trends, node saturation metrics
- [ ] **[Recommended]** Configure retention policies: Prometheus TSDB retention (default 15d), Loki retention, external system retention alignment
- [ ] **[Recommended]** Set up must-gather and sos-report procedures for Red Hat support case diagnostics
- [ ] **[Optional]** Plan metric cardinality management: identify high-cardinality labels, set per-namespace scrape limits

## Why This Matters

OpenShift ships with a fully integrated monitoring stack based on Prometheus Operator, but the platform monitoring (control plane, node, and operator metrics) and user workload monitoring are separate concerns with separate configurations. Platform monitoring is configured via the `openshift-monitoring` namespace and the `cluster-monitoring-config` ConfigMap. User workload monitoring must be explicitly enabled and is managed via the `openshift-user-workload-monitoring` namespace with its own `user-workload-monitoring-config` ConfigMap.

The built-in Grafana in OpenShift is read-only -- it ships with pre-built dashboards for cluster health but does not support custom dashboards. Teams requiring custom dashboards must deploy a community Grafana instance (via operator or Helm) pointed at the Thanos Querier endpoint. This is a common surprise for teams migrating from self-managed Kubernetes with full Grafana access.

OpenShift Logging has shifted from the EFK stack (Elasticsearch, Fluentd, Kibana) to a Loki-based stack (Vector collector, Loki store, OpenShift Console log viewer). Loki requires object storage (S3, ODF MCG, Azure Blob, GCS) as its backend. The ClusterLogForwarder CRD controls log routing -- application logs, infrastructure logs, and audit logs can be sent to different destinations. Without explicit forwarding configuration, logs are only available in the cluster-local Loki instance.

Distributed tracing with the Tempo operator replaces the older Jaeger operator. The OpenTelemetry Collector operator provides vendor-neutral instrumentation, supporting OTLP, Jaeger, and Zipkin protocols. Tracing requires application instrumentation -- OpenTelemetry SDKs in application code or auto-instrumentation via the operator's `Instrumentation` CR (supported for Java, Python, Node.js, .NET, Go).

The Network Observability operator uses eBPF agents on each node to capture network flows without requiring application modification. Flows are enriched with Kubernetes metadata (namespace, pod, service) and visualized in the OpenShift Console's Network Traffic tab. This is invaluable for debugging connectivity issues, identifying unexpected traffic patterns, and validating NetworkPolicy effectiveness.

## Common Decisions (ADR Triggers)

- **In-cluster monitoring vs external observability platform**: The built-in stack is sufficient for cluster and basic application monitoring. Large-scale environments may need external Prometheus (Thanos/Cortex/Mimir), Datadog, Dynatrace, or Splunk Observability for cross-cluster correlation, longer retention, and advanced analytics.
- **Log retention and routing**: All logs to Loki (simple but storage-intensive) vs selective forwarding (app logs to Splunk, audit logs to SIEM, infra logs to Loki). ClusterLogForwarder supports pipeline filtering by namespace, label, and log level.
- **Tracing adoption**: Full distributed tracing (requires instrumentation investment) vs request logging with correlation IDs. Auto-instrumentation reduces effort but may not cover all frameworks. Sampling strategy (head-based vs tail-based) affects storage costs and diagnostic coverage.
- **Custom Grafana deployment**: Managed Grafana operator vs Helm-deployed community Grafana vs external Grafana Cloud. Consider dashboard-as-code (GrafanaDashboard CRDs) for GitOps-managed dashboards.
- **Metric federation**: Thanos sidecar on each cluster's Prometheus, federated to a central Thanos Querier for cross-cluster views. Required for multi-cluster environments managed by RHACM.
- **Network observability scope**: Enable on all nodes (comprehensive but generates high flow volume) vs targeted namespaces. Sampling rate configuration balances visibility vs storage costs.

## Reference Architectures

- **Standard production monitoring**: User workload monitoring enabled, ServiceMonitors per application, Alertmanager with PagerDuty (critical) and Slack (warning), Prometheus retention 30 days, custom Grafana with SLO dashboards, Loki with S3 backend for 90-day log retention.
- **Enterprise multi-cluster observability**: RHACM Observability (Thanos-based) for fleet-wide metrics, Grafana with cross-cluster dashboards, ClusterLogForwarder to centralized Splunk, Tempo for distributed tracing with 7-day retention, centralized alerting via global Alertmanager.
- **Compliance-focused observability**: Audit logs forwarded to SIEM (QRadar, Splunk), Compliance Operator scan results as Prometheus metrics, custom alerts for SCC violations and failed authentication attempts, network observability for traffic baseline and anomaly detection.
- **Developer-centric platform**: User workload monitoring with self-service ServiceMonitor creation, OpenShift Console integrated log viewer (Loki), Jaeger/Tempo UI for trace exploration, Grafana dashboards per team namespace, alert routing per team Slack channel.
- **Cost-optimized observability**: Prometheus with aggressive retention (7 days in-cluster, long-term in S3 via Thanos), Loki with lifecycle policies (hot/warm/cold tiers), sampling on traces (10% head-based), network observability with 50% flow sampling, must-gather on-demand for troubleshooting.

## Reference Links

- [OpenShift monitoring documentation](https://docs.openshift.com/container-platform/latest/monitoring/monitoring-overview.html) -- built-in Prometheus stack, alerting, and metrics collection
- [OpenShift logging documentation](https://docs.openshift.com/container-platform/latest/logging/cluster-logging.html) -- cluster logging with Loki, Elasticsearch, and log forwarding
- [OpenShift distributed tracing](https://docs.openshift.com/container-platform/latest/observability/distr_tracing/distr_tracing_arch/distr-tracing-architecture.html) -- Jaeger and OpenTelemetry-based distributed tracing

## See Also

- `general/observability.md` -- general observability patterns
- `providers/kubernetes/observability.md` -- Kubernetes observability patterns (upstream)
- `providers/prometheus-grafana/observability.md` -- Prometheus and Grafana stack
- `providers/openshift/infrastructure.md` -- infrastructure monitoring and capacity
