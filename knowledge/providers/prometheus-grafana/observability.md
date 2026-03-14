# Open-Source Observability Stack (Prometheus, Grafana, Loki, AlertManager)

## Checklist

- [ ] **[Critical]** Is Prometheus retention configured appropriately for the environment (15d default is often insufficient for capacity planning; extend to 30-90d for local, or configure remote write to Thanos/Cortex/Mimir for long-term storage)?
- [ ] **[Critical]** Is Prometheus sized correctly for the active time series count -- each active series consumes ~1-2 KB of RAM, so 1M active series requires ~2-4 GB RAM for ingestion alone, plus query overhead?
- [ ] **[Critical]** Are alerting rules defined for infrastructure essentials (node down, disk >85%, memory >90%, certificate expiry <30d) and routed through AlertManager to appropriate on-call channels (PagerDuty, Slack, email)?
- [ ] **[Critical]** Is AlertManager configured with proper routing tree, grouping (group_by: [alertname, cluster]), group_wait (30s), group_interval (5m), and repeat_interval (4h) to prevent alert storms?
- [ ] **[Recommended]** Are recording rules created for frequently queried expensive expressions (e.g., pre-compute `rate(http_requests_total[5m])` into `job:http_requests:rate5m`) to reduce query-time CPU load?
- [ ] **[Recommended]** Is Grafana provisioning configured for dashboards-as-code (JSON/YAML in Git, deployed via provisioning directory or Grafana API) to prevent dashboard drift and enable version control?
- [ ] **[Recommended]** Is Grafana authentication integrated with the organization's identity provider (LDAP, OIDC via Keycloak/Okta/Azure AD, or SAML) rather than relying on local accounts?
- [ ] **[Recommended]** Is Loki label design reviewed to avoid high-cardinality labels (never use user_id, request_id, or IP as labels -- these should be structured log fields queried with LogQL filters)?
- [ ] **[Recommended]** Are Promtail or Grafana Alloy agents deployed on all hosts with appropriate pipeline stages to parse log formats, extract structured fields, and attach environment/service labels?
- [ ] **[Optional]** Is Prometheus federation configured for multi-cluster environments, with a global Prometheus scraping aggregated metrics from cluster-level Prometheus instances?
- [ ] **[Optional]** Is Loki retention configured with table_manager or compactor retention (e.g., 30d for application logs, 90d for audit/security logs) to manage storage growth?
- [ ] **[Optional]** Are Grafana plugins installed for specialized data sources (e.g., Elasticsearch, Zabbix, SNMP) or visualization needs (flowchart, diagram panels)?
- [ ] **[Recommended]** Is a node_exporter deployed on every Linux host and windows_exporter on every Windows host, with blackbox_exporter probing external endpoints (HTTP, TCP, ICMP, DNS)?

## Why This Matters

Commercial monitoring solutions (Datadog, New Relic, Splunk) carry per-host or per-GB pricing that becomes prohibitive at scale in on-prem environments -- a 200-node deployment with Datadog can easily exceed $100K/yr. The Prometheus/Grafana/Loki stack provides equivalent capabilities (metrics, dashboards, alerting, log aggregation) at zero licensing cost, with the trade-off of operational responsibility. However, this stack requires deliberate sizing and configuration. Prometheus is a single-node, in-memory time-series database by design -- it does not cluster natively, and running out of RAM causes OOM kills that create monitoring blackouts during the exact incidents you need visibility into. Loki's label-based architecture is fundamentally different from Elasticsearch's full-text indexing; misunderstanding this leads to either massive index bloat (too many labels) or unusable query performance (no labels, grep through everything). AlertManager's routing tree is the single most impactful configuration for on-call experience -- misconfigured grouping causes either alert floods (hundreds of individual alerts during an outage) or silently dropped alerts.

## Common Decisions (ADR Triggers)

- **Long-term storage backend** -- Thanos (sidecar pattern, object storage, globally queryable, battle-tested at scale), Cortex (multi-tenant, horizontally scalable, complex to operate), Grafana Mimir (Cortex successor by Grafana Labs, simplified deployment, enterprise features), or VictoriaMetrics (single binary, high performance, drop-in Prometheus replacement with built-in long-term storage). Thanos is the most widely deployed; Mimir is gaining adoption rapidly. VictoriaMetrics is simplest operationally if you do not need multi-tenancy.
- **Grafana OSS vs Grafana Cloud** -- Self-hosted Grafana is free but requires infrastructure and operational effort. Grafana Cloud provides managed Prometheus (Mimir), Loki, and Grafana with a generous free tier (10K metrics series, 50GB logs/mo) and per-usage pricing. For teams without deep observability expertise, Grafana Cloud eliminates the operational burden at ~$8/user/mo plus usage. On-prem agents (Grafana Alloy) can remote-write to Grafana Cloud.
- **Log aggregation: Loki vs Elasticsearch/OpenSearch** -- Loki is cheaper to operate (indexes only labels, not log content) and integrates natively with Grafana, but LogQL is less powerful than Elasticsearch KQL for complex full-text search. Elasticsearch is better for security/SIEM use cases (correlating across diverse log sources) but requires significant memory and storage (plan 1 GB RAM per 1 TB indexed data). Choose Loki for operational logs, Elasticsearch for security analytics.
- **Agent: Promtail vs Grafana Alloy vs OpenTelemetry Collector** -- Promtail is Loki-specific (simple, reliable). Grafana Alloy (formerly Grafana Agent) is a unified agent that can scrape Prometheus metrics, collect logs (replacing Promtail), and receive OpenTelemetry traces. OpenTelemetry Collector is vendor-neutral and supports multiple backends. If using only the Grafana stack, Alloy simplifies to one agent per host.
- **Deployment: VMs vs containers** -- Prometheus and Grafana run well on VMs (systemd services) or in containers (Docker Compose, Kubernetes). For on-prem without Kubernetes, VM deployment with Ansible/Puppet is simpler. For Kubernetes environments, use the kube-prometheus-stack Helm chart, which deploys Prometheus Operator, Grafana, AlertManager, and node_exporter with sensible defaults.
- **AlertManager receivers** -- PagerDuty for critical/P1 (phone call escalation), Slack/Teams for warning/P2-P3 (chat notification), email for informational. Define escalation paths: if P1 is not acknowledged within 15 minutes, escalate to secondary on-call. Use inhibition rules so that "host down" suppresses all service alerts on that host.

## Stack Sizing Guidelines

### Small Environment (<50 VMs)

| Component | CPU | RAM | Storage | Notes |
|---|---|---|---|---|
| Prometheus | 2 vCPU | 4 GB | 100 GB SSD | ~50K active series, 30d retention |
| Grafana | 1 vCPU | 2 GB | 10 GB | SQLite backend sufficient |
| Loki | 2 vCPU | 4 GB | 200 GB | Filesystem chunk store |
| AlertManager | 1 vCPU | 512 MB | 1 GB | Co-locate with Prometheus |
| **Total** | **6 vCPU** | **10.5 GB** | **311 GB** | Can co-locate on 1-2 VMs |

### Medium Environment (50-500 VMs)

| Component | CPU | RAM | Storage | Notes |
|---|---|---|---|---|
| Prometheus | 4 vCPU | 16 GB | 500 GB SSD | ~500K active series, 30d retention |
| Grafana | 2 vCPU | 4 GB | 20 GB | PostgreSQL backend for HA |
| Loki | 4 vCPU | 8 GB | 1 TB | S3/MinIO chunk store recommended |
| AlertManager | 1 vCPU | 1 GB | 5 GB | Clustered (2-3 instances) |
| **Total** | **11 vCPU** | **29 GB** | **1.5 TB** | Separate VMs per component |

### Large Environment (500+ VMs)

| Component | CPU | RAM | Storage | Notes |
|---|---|---|---|---|
| Prometheus | 8+ vCPU | 32-64 GB | 1+ TB NVMe | ~2M+ active series, remote write to Thanos/Mimir |
| Thanos/Mimir | 8+ vCPU | 16-32 GB | Object storage (S3/MinIO) | Handles long-term queries |
| Grafana | 4 vCPU | 8 GB | 50 GB | HA pair with PostgreSQL, caching proxy |
| Loki | 8+ vCPU | 16-32 GB | Object storage (S3/MinIO) | Distributed mode (read/write/backend) |
| AlertManager | 2 vCPU | 2 GB | 10 GB | 3-node cluster |
| **Total** | **30+ vCPU** | **74-138 GB** | **1+ TB local + object storage** | Consider dedicated monitoring cluster |

## Key Configuration Patterns

### Prometheus Cardinality Management

High cardinality is the primary cause of Prometheus performance issues. Monitor with:
- `prometheus_tsdb_head_series` -- total active series (alert if growing unexpectedly)
- `topk(10, count by (__name__)({__name__=~".+"}))` -- top 10 metric names by series count
- Use `metric_relabel_configs` to drop unused labels or entire metrics at scrape time
- Set `sample_limit` per scrape job to prevent a single target from exploding cardinality

### Loki Label Design

```
Good labels (low cardinality):
  {job="nginx", env="production", cluster="dc1"}

Bad labels (high cardinality - DO NOT USE):
  {job="nginx", user_id="12345", request_id="abc-def-ghi"}
```

Query high-cardinality fields with LogQL filter expressions instead:
```
{job="nginx"} |= "user_id=12345" | json | line_format "{{.message}}"
```

## Reference Architectures

- **Prometheus documentation**: [prometheus.io/docs](https://prometheus.io/docs/) -- scrape configuration, recording rules, remote write, federation, and operational best practices
- **Thanos project**: [thanos.io](https://thanos.io/) -- sidecar, store gateway, compactor, and querier architecture for global view across Prometheus instances
- **Grafana Mimir**: [grafana.com/docs/mimir](https://grafana.com/docs/mimir/latest/) -- horizontally scalable long-term storage, drop-in Prometheus remote write target
- **Grafana Loki**: [grafana.com/docs/loki](https://grafana.com/docs/loki/latest/) -- architecture overview, deployment modes (monolithic, simple scalable, microservices), and LogQL reference
- **kube-prometheus-stack Helm chart**: [github.com/prometheus-community/helm-charts](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) -- production-ready Kubernetes deployment with Prometheus Operator
- **Awesome Prometheus alerts**: [samber/awesome-prometheus-alerts](https://github.com/samber/awesome-prometheus-alerts) -- community-curated alerting rules for common infrastructure and applications
- **Grafana dashboards**: [grafana.com/grafana/dashboards](https://grafana.com/grafana/dashboards/) -- community dashboards (Node Exporter Full: ID 1860, Kubernetes: ID 315)
