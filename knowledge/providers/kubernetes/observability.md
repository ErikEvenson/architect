# Kubernetes Observability

## Scope

Kubernetes observability: Prometheus deployment, metrics-server, kube-state-metrics, logging stack selection (Fluent Bit, Loki, Elasticsearch), distributed tracing (OpenTelemetry), event collection, Grafana dashboards, Alertmanager, and long-term metric storage (Thanos, Mimir).


## Checklist

- [ ] **[Recommended]** Deploy Prometheus for metrics collection: evaluate kube-prometheus-stack (Prometheus Operator + Grafana + alerting rules) vs lightweight Prometheus (single binary)
- [ ] **[Recommended]** Install metrics-server for core resource metrics (CPU/memory) required by HPA and `kubectl top`; do not confuse with Prometheus (different purpose)
- [ ] **[Recommended]** Deploy kube-state-metrics to expose Kubernetes object state as Prometheus metrics (deployment replicas, pod phase, node conditions, PVC status)
- [ ] **[Recommended]** Select logging stack: Fluentd (feature-rich, plugin ecosystem) vs Fluent Bit (lightweight, preferred for K8s) vs Vector (Rust-based, high performance) as collectors; Loki (label-indexed) vs Elasticsearch (full-text search) as backends
- [ ] **[Recommended]** Plan distributed tracing: OpenTelemetry SDK instrumentation, collector deployment (sidecar vs DaemonSet vs Deployment), backend (Jaeger, Tempo, Zipkin, or cloud-native)
- [ ] **[Recommended]** Configure Kubernetes event collection: events have 1-hour default TTL; export to persistent storage via event-exporter or kube-eventer for post-incident analysis
- [ ] **[Recommended]** Design custom metrics pipeline for HPA: Prometheus Adapter (exposes Prometheus queries as Kubernetes custom metrics API) or KEDA (wider scaler support)
- [ ] **[Recommended]** Plan Grafana dashboard strategy: use upstream community dashboards as base (kube-prometheus-stack includes 20+ dashboards), customize per-team views
- [ ] **[Recommended]** Configure alerting pipeline: Prometheus Alertmanager for routing, grouping, inhibition, and silencing; integrate with PagerDuty/Slack/OpsGenie
- [ ] **[Recommended]** Evaluate OpenTelemetry Collector as a unified telemetry pipeline (metrics, logs, traces) to reduce agent proliferation
- [ ] **[Recommended]** Plan storage retention: Prometheus local storage (15-day default), long-term with Thanos or Cortex or Mimir for multi-cluster aggregation and extended retention
- [ ] **[Recommended]** Implement SLO monitoring: define SLIs (latency p99, error rate, availability), use Pyrra or Sloth to generate SLO-based alerting rules and burn-rate alerts

## Why This Matters

Kubernetes adds layers of abstraction (pods, services, controllers, operators) that obscure what is happening at the infrastructure and application level. Without purpose-built observability, common failure modes are invisible: pods stuck in CrashLoopBackOff on a Friday night, PVCs pending due to zone mismatch, memory leaks causing OOM kills, DNS resolution failures causing intermittent 5xx errors. The three pillars (metrics, logs, traces) each address different debugging needs. Metrics detect problems (CPU spike, error rate increase). Logs provide context (stack traces, error messages). Traces identify bottlenecks across distributed services. Kubernetes-specific metrics (kube-state-metrics, etcd metrics, kubelet metrics) are essential for understanding cluster health independently of application health.

## Common Decisions (ADR Triggers)

- **Prometheus vs cloud-native monitoring (CloudWatch, Cloud Monitoring, Azure Monitor)**: Prometheus is the Kubernetes standard with deep integration (ServiceMonitor CRDs, native metric format). Cloud-native monitoring is simpler to operate but often has Kubernetes metric gaps, higher cost at scale, and weaker PromQL support. Use Prometheus for Kubernetes-native monitoring; cloud-native for infrastructure outside Kubernetes. Many teams run both.
- **Loki vs Elasticsearch for log storage**: Loki indexes only labels (cheaper, simpler) and requires label-based queries. Elasticsearch indexes full text (richer search) but is expensive to operate and scale. Loki is the default choice for Kubernetes-native logging (pairs with Grafana). Elasticsearch is better when full-text search across unstructured logs is a primary use case or when an existing ELK investment exists.
- **Fluent Bit vs Fluentd vs Vector**: Fluent Bit is lightweight (C, ~15MB memory) and optimized for Kubernetes log collection. Fluentd (Ruby) has a richer plugin ecosystem but higher resource usage. Vector (Rust) offers high performance and a unified pipeline for logs and metrics. Use Fluent Bit as the default Kubernetes log collector; Vector for high-throughput or unified pipelines.
- **Jaeger vs Tempo for trace storage**: Jaeger is mature with a full UI and supports multiple backends (Elasticsearch, Cassandra, Kafka). Tempo is Grafana's trace backend (pairs with Grafana for visualization, uses object storage for cost-effective retention). Choose Tempo for Grafana-centric stacks; Jaeger for teams that need the Jaeger UI or already run Elasticsearch/Cassandra.
- **Prometheus local storage vs Thanos/Mimir**: Local Prometheus retention is limited by disk and not durable across pod restarts. Thanos adds long-term storage (S3/GCS), multi-cluster querying, and downsampling. Mimir (from Grafana Labs) provides similar capabilities with a simpler architecture. Use local Prometheus for single small clusters; Thanos/Mimir for multi-cluster, long-term retention, or high-availability Prometheus.
- **OpenTelemetry Collector vs purpose-built agents**: OTel Collector handles metrics, logs, and traces in a single agent, reducing DaemonSet proliferation. But it is more complex to configure and less mature than purpose-built tools (Fluent Bit for logs, Prometheus for metrics). Use OTel Collector when standardizing on OpenTelemetry across the stack; purpose-built agents for simpler deployments.

## Reference Architectures

### Full Observability Stack (Grafana-Centric)
```
[Application Pods]
  - OTel SDK (traces + metrics)          [kube-state-metrics]  [metrics-server]
  - stdout/stderr (logs)                        |                     |
        |                                       |                     |
  [Fluent Bit DaemonSet] --> [Loki]       [Prometheus]          [HPA/VPA/kubectl top]
  (log collection)           (log store)   (scrape targets)
        |                       |               |
        +-------+-------+-------+-------+-------+
                |                               |
          [Grafana]                       [Alertmanager]
          - Log dashboards (Loki)         - PagerDuty
          - Metric dashboards (Prometheus) - Slack
          - Trace visualization (Tempo)    - OpsGenie
          - SLO dashboards (Pyrra)
                |
          [OTel Collector] --> [Tempo]
          (receive traces)     (trace store, S3 backend)
```
Fluent Bit collects container logs as a DaemonSet, forwards to Loki. Prometheus scrapes metrics from pods (via ServiceMonitor), kube-state-metrics, and node-exporter. OTel Collector receives traces from application SDKs and forwards to Tempo. Grafana provides unified dashboards across all three signals. Alertmanager routes alerts based on severity and team ownership.

### Multi-Cluster Monitoring with Thanos
```
[Cluster A]                    [Cluster B]
+-------------------+          +-------------------+
| Prometheus        |          | Prometheus        |
| + Thanos Sidecar  |          | + Thanos Sidecar  |
| (upload to S3)    |          | (upload to S3)    |
+-------------------+          +-------------------+
         |                              |
         +---------- [S3 Bucket] -------+
                         |
                  [Thanos Store Gateway]
                  (reads from S3)
                         |
                  [Thanos Querier]
                  (federated PromQL)
                         |
                  [Thanos Compactor]
                  (downsampling, retention)
                         |
                  [Grafana]
                  (multi-cluster dashboards)
```
Each cluster runs Prometheus with a Thanos sidecar that uploads blocks to S3. Thanos Store Gateway reads historical data from S3. Thanos Querier provides a unified PromQL endpoint across all clusters and time ranges. Compactor handles downsampling (5m, 1h resolution for old data) and retention enforcement. Grafana connects to Thanos Querier for multi-cluster visibility.

### SLO-Based Alerting
```
[SLI Definition]
  - Request latency p99 < 500ms
  - Error rate < 0.1%
  - Availability > 99.9%
        |
  [Pyrra / Sloth]
  - Generates PrometheusRule CRs
  - Multi-window burn-rate alerts
  - 1h/6h windows for fast burn
  - 3d/30d windows for slow burn
        |
  [Alertmanager]
  - Fast burn (>14.4x) --> Page (PagerDuty)
  - Slow burn (>1x)    --> Ticket (Jira/Slack)
        |
  [Grafana SLO Dashboard]
  - Error budget remaining
  - Burn rate trend
  - Time to budget exhaustion
```
SLO-based alerting replaces threshold-based alerts (CPU > 80%) with business-meaningful alerts (error budget burning too fast). Multi-window burn rates detect both sudden spikes (fast burn: alert in minutes) and gradual degradation (slow burn: alert in hours). This reduces alert fatigue by tying alerts to user-facing impact rather than infrastructure metrics.

## See Also

- `general/observability.md` -- general observability patterns
- `providers/prometheus-grafana/observability.md` -- Prometheus and Grafana stack configuration
- `providers/kubernetes/compute.md` -- HPA custom metrics pipeline
- `providers/kubernetes/operations.md` -- operational tooling and debugging
