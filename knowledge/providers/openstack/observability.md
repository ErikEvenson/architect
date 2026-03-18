# OpenStack Observability (Monitoring, Metering, Logging, Testing)

## Scope

Covers OpenStack observability stack: Ceilometer telemetry, Gnocchi metrics backend, Aodh alarming, Monasca monitoring-as-a-service, centralized logging (ELK/Loki), Prometheus integration, CloudKitty rating, OSProfiler/OpenTelemetry tracing, Rally benchmarking, and Tempest functional testing.

## Checklist

- [ ] **[Critical]** Is Ceilometer deployed for telemetry collection? (`ceilometer-agent-compute` on each hypervisor for VM metrics, `ceilometer-agent-notification` consuming oslo.messaging notifications from all services, polling interval tuned to balance granularity vs load -- default 600s often too slow for autoscaling)
- [ ] **[Critical]** Is centralized logging deployed for all OpenStack services? (Fluentd/Fluent Bit or Filebeat on each node shipping logs from `/var/log/nova/`, `/var/log/neutron/`, etc. to Elasticsearch/OpenSearch, Graylog, or Loki; structured JSON logging enabled where possible via oslo.log `[DEFAULT] use_json = True`)
- [ ] **[Critical]** Are OpenStack service healthcheck endpoints monitored? (`/healthcheck` endpoint on each API service via oslo.middleware, HAProxy health checks against API ports, synthetic checks with `openstack token issue` for end-to-end Keystone validation)
- [ ] **[Recommended]** Is Gnocchi configured as the metrics backend? (time-series database for Ceilometer metrics, storage driver selection: file/Ceph/Swift/S3, archive policies defining retention granularity -- e.g., `1m:7d,5m:30d,1h:365d` for 1-minute granularity for 7 days then roll up)
- [ ] **[Recommended]** Are Gnocchi archive policies sized for capacity? (metric count = resources x meters x archive policy points, Ceph or Swift backend recommended for production scale, `gnocchi-metricd` workers scaled to handle incoming measurements)
- [ ] **[Recommended]** Is Aodh configured for alarming? (threshold alarms on Gnocchi metrics for autoscaling and alerting, composite alarms combining multiple conditions with `and`/`or` operators, `event` alarms for reacting to specific OpenStack events, alarm actions as webhook URLs to Heat or external systems)
- [ ] **[Recommended]** Is Monasca evaluated as an alternative monitoring stack? (Retired as of Yoga -- monitoring-as-a-service with multi-tenant metric collection, Kafka-based pipeline; if currently using Monasca, plan migration to Prometheus/Grafana or Ceilometer/Gnocchi/Aodh)
- [ ] **[Recommended]** Are log retention and rotation policies defined? (logrotate for local logs, index lifecycle management in Elasticsearch/OpenSearch for centralized logs, separate indices per service for targeted retention, consider 30-90 day hot storage with cold/frozen tiers)
- [ ] **[Recommended]** Is Prometheus + Grafana integrated for infrastructure and service monitoring? (`openstack-exporter` for API-level metrics, `node_exporter` on all hosts, `libvirt_exporter` for hypervisor metrics, `ceph_exporter` for storage metrics — see [Ceph storage](../ceph/storage.md) for exporter configuration, custom Grafana dashboards per service)
- [ ] **[Recommended]** Is the openstack-exporter configured correctly? (Go-based exporter querying OpenStack APIs via `clouds.yaml` credentials, serves on port 9180; supports single-cloud mode at `/metrics` or multi-cloud mode at `/probe?cloud=<name>`; enable caching with configurable TTL to reduce API load; disable slow metrics like `nova_server_diagnostics` in large deployments; deploy one instance per cloud or use multi-cloud mode)
- [ ] **[Recommended]** Is Tempest used for functional validation? (`tempest run` after deployments and upgrades, `tempest.conf` configured for the specific cloud, custom test plugins for site-specific validation, integrated into CI/CD pipeline for pre-production verification)
- [ ] **[Recommended]** Are infrastructure capacity metrics tracked for planning? (compute: vCPU/RAM allocation ratio trends, storage: Ceph pool utilization and growth rate, network: bandwidth utilization per provider network, Keystone: token issuance rate and latency)
- [ ] **[Recommended]** Are oslo.messaging (RabbitMQ) health and performance monitored? (queue depth, message rate, consumer count, unacknowledged messages, cluster partition detection -- RabbitMQ problems cascade across all OpenStack services)
- [ ] **[Optional]** Is Rally used for performance benchmarking? (`rally task start` with scenario files for Nova boot, Cinder create, Neutron network creation throughput, baseline performance established before upgrades, results stored for trend analysis)
- [ ] **[Optional]** Is distributed tracing considered for API request debugging? (OSProfiler is in maintenance mode -- transition to OpenTelemetry with Jaeger recommended for new deployments; `--os-profile` on CLI for per-request tracing -- useful for diagnosing slow API calls)

## Why This Matters

OpenStack is composed of dozens of services communicating via REST APIs and message queues -- without comprehensive observability, failures cascade silently and root cause analysis becomes guesswork. Ceilometer polling intervals directly affect autoscaling responsiveness: a 600-second polling interval means 10-minute detection latency for scaling events. Gnocchi archive policy misconfiguration causes either excessive storage consumption or loss of granular historical data. RabbitMQ is the nervous system of OpenStack -- queue congestion in one service (e.g., Neutron agent heartbeats) can starve other services of message delivery. Log volume from a medium OpenStack deployment (50 compute nodes) can exceed 10 GB/day, requiring deliberate retention and aggregation strategy. Rally and Tempest are not optional extras -- they are the only reliable way to validate that an upgrade or configuration change has not introduced performance regression or functional breakage.

## Common Decisions (ADR Triggers)

- **Metrics stack** -- Ceilometer/Gnocchi/Aodh (native OpenStack, integrated with Heat autoscaling) vs Prometheus/Grafana (industry standard, large ecosystem, not OpenStack-native) -- Monasca is retired; integration depth vs ecosystem breadth
- **Logging stack** -- ELK/OpenSearch (full-text search, powerful, resource-heavy) vs Loki/Grafana (label-indexed, lightweight, pairs with Prometheus) vs Graylog (structured logging, built-in alerting) -- query capabilities vs resource footprint
- **Log shipping** -- Fluentd (flexible, plugin-rich, Ruby) vs Fluent Bit (lightweight C, low memory) vs Filebeat (Elastic ecosystem) -- footprint on compute nodes and destination compatibility
- **Alerting pipeline** -- Aodh alarms to Heat webhooks (native autoscaling) vs Prometheus Alertmanager (routing, silencing, grouping) vs PagerDuty/OpsGenie integration (incident management) -- operational workflow integration
- **Performance testing** -- Rally continuous benchmarking (proactive capacity insights) vs Rally only pre-upgrade (reactive validation) vs no performance testing (risk of undetected degradation) -- operational maturity level
- **Functional validation** -- Tempest in CI/CD (every change validated) vs Tempest post-upgrade only (periodic validation) vs manual smoke tests (lowest coverage) -- deployment confidence vs pipeline complexity
- **Tracing** -- OpenTelemetry with Jaeger (industry standard, recommended for new deployments) vs OSProfiler (native but maintenance mode) vs no tracing (log correlation only) -- debugging capability vs implementation effort
- **Metering for billing** -- Ceilometer + CloudKitty (rating engine for chargeback/showback) vs custom metering from Gnocchi/Prometheus (flexible but build-it-yourself) vs external billing platforms -- internal chargeback requirements

## OpenStack Exporter Configuration

The [openstack-exporter](https://github.com/openstack-exporter/openstack-exporter) is a Go-based Prometheus exporter that queries OpenStack APIs and exposes metrics for Nova, Neutron, Cinder, Glance, Keystone, Octavia, Heat, Swift, and 10+ other services.

**Deployment options:** Docker, Snap, Kolla-Ansible, Helm chart, or binary.

**Authentication** uses standard `clouds.yaml`:

```yaml
clouds:
  mycloud:
    auth:
      auth_url: https://keystone.example.com:5000/v3
      project_name: admin
      username: monitoring
      password: <from-secret>
      user_domain_name: Default
      project_domain_name: Default
    region_name: RegionOne
```

**Prometheus scrape config** — single-cloud mode (port 9180):

```yaml
- job_name: 'openstack'
  scrape_interval: 120s  # OpenStack API calls are slow; avoid overloading
  scrape_timeout: 60s
  static_configs:
  - targets: ['openstack-exporter:9180']
```

**Multi-cloud mode** — use `/probe` endpoint:

```yaml
- job_name: 'openstack'
  scrape_interval: 120s
  metrics_path: /probe
  params:
    cloud: ['mycloud']
  static_configs:
  - targets: ['openstack-exporter:9180']
```

**Performance tuning for large deployments:**
- Enable caching (`--cache`, `--cache-ttl 300s`) to reduce API calls
- Disable slow metrics that query per-instance diagnostics: `--disable-metric nova_server_diagnostics`
- Use domain filtering to limit scope when only monitoring specific projects
- Set `scrape_interval` to 120s+ (OpenStack API calls are expensive compared to typical exporters)

**Recommended exporter stack for a full OpenStack deployment:**

| Exporter | Port | Metrics |
|---|---|---|
| openstack-exporter | 9180 | API-level: servers, volumes, networks, images, quotas |
| node_exporter | 9100 | Host: CPU, memory, disk, network on all nodes |
| libvirt_exporter | 9177 | Hypervisor: per-VM CPU, memory, disk I/O, network I/O |
| ceph_exporter | 9283 | Storage: OSD latency, PG states, pool utilization (see [Ceph storage](../ceph/storage.md)) |
| ipmi_exporter | 9290 | Hardware: temperatures, fan speeds, power draw, hardware events |
| rabbitmq_exporter | 9419 | Messaging: queue depth, message rates, consumer counts |
| mysqld_exporter / postgres_exporter | 9104/9187 | Database: query latency, connections, replication lag |
| haproxy_exporter | 9101 | Load balancer: request rates, backend health, connection counts |

## Version Notes

| Feature | Pike (16) Oct 2017 | Queens (17) Feb 2018 | Rocky (18) Aug 2018 | Stein (19) Apr 2019 | Train (20) Oct 2019 | Ussuri (21) May 2020 | Victoria (22) Oct 2020 | Wallaby (23) Apr 2021 | Xena (24) Oct 2021 | Yoga (25) Mar 2022 | Zed (26) Oct 2022 | 2023.1 Antelope (27) | 2023.2 Bobcat (28) | 2024.1 Caracal (29) | 2024.2 Dalmatian (30) | 2025.1 Epoxy (31) | 2025.2 Flamingo (32) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ceilometer polling agent | GA | GA | GA (polling/notification split) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Ceilometer notification agent | GA | GA | GA (primary collection method) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Ceilometer pipeline refactoring | Monolithic | Polling + notification separated | GA (separate processes) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Gnocchi (metrics backend) | In-tree (integrated) | Independent project | Independent (GA) | GA (4.x) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Gnocchi storage drivers | File, Ceph, Swift | File, Ceph, Swift, S3 | Same + Redis | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Panko (event storage) | GA (integrated) | GA | GA | Deprecated notice | Deprecated | Deprecated | Deprecated | Deprecated | Retired | Retired | Retired | Retired | Retired | Retired | Retired | Retired | Retired |
| Aodh (alarming) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Aodh composite alarms | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Monasca (monitoring-as-a-service) | GA | GA | GA | GA | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Retired | Retired |
| CloudKitty (rating/billing) | GA | GA | GA (v2 API) | GA (v2 storage) | GA | GA | GA | GA | GA (Prometheus collector) | GA | GA | GA | GA | GA | GA | GA | GA |
| CloudKitty storage backends | SQL | SQL | SQL, InfluxDB | SQL, InfluxDB, OpenSearch | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| CloudKitty collectors | Ceilometer, Gnocchi | Same | Same + Monasca | Same | Same | Same | Same | Same | Prometheus added | GA | GA | GA | GA | GA | GA | GA | GA |
| OSProfiler (tracing) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA (maintenance) | GA (maintenance) | Maintenance mode | Maintenance mode (use OpenTelemetry) |
| Rally (benchmarking) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Tempest (functional testing) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Prometheus integration | Community | Community | Community (exporters) | Community (exporters) | Community | Community | Community | Community | Community | Community (openstack-exporter) | GA (recommended) | GA | GA | GA | GA | GA | GA |

**Key changes across releases:**
- **Ceilometer polling vs notification agents:** In Pike, Ceilometer was a monolithic service. Rocky separated it into distinct polling and notification agents. The notification agent (consuming oslo.messaging notifications) became the primary and recommended collection method, as it is event-driven and lower overhead. The polling agent is still needed for metrics not exposed via notifications (e.g., libvirt VM metrics on compute nodes) but should have its polling interval tuned to reduce load.
- **Gnocchi becoming independent:** Gnocchi was part of the Ceilometer project through Pike. In Queens it became an independent project with its own release cycle. This decoupling allowed Gnocchi to evolve faster and be used as a general-purpose time-series database beyond OpenStack telemetry. Gnocchi 4.x (Stein+) added performance improvements and new archive policy features.
- **Panko deprecation and retirement:** Panko (event storage for Ceilometer events) was deprecated in Stein and retired in Xena. Events should be forwarded to external systems (Elasticsearch/OpenSearch, SIEM platforms) via oslo.messaging notification listeners rather than stored in Panko. Organizations still using Panko should migrate event storage to their centralized logging stack.
- **Monasca status:** Monasca (monitoring-as-a-service with Kafka pipeline, multi-tenant metrics, and built-in alarming) entered maintenance mode in Train due to declining community activity. It is effectively retired as of Yoga. Organizations that adopted Monasca should plan migration to Prometheus/Grafana or Ceilometer/Gnocchi/Aodh stacks.
- **CloudKitty evolution:** CloudKitty (rating engine for chargeback/showback) introduced its v2 API and storage backend in Rocky/Stein, adding InfluxDB and OpenSearch as storage options. A Prometheus collector was added in Xena, enabling CloudKitty to rate metrics from Prometheus in addition to Gnocchi and Ceilometer. This makes CloudKitty compatible with both native OpenStack telemetry and Prometheus-based monitoring stacks.
- **Prometheus as recommended monitoring:** While not an official OpenStack project, Prometheus with the openstack-exporter has become the de facto standard for infrastructure monitoring in OpenStack deployments. Starting with Zed, many deployment tools (Kolla-Ansible, TripleO/Director) include Prometheus integration out of the box. Combined with Grafana dashboards, it provides richer visualization than native OpenStack telemetry.
- **OSProfiler to OpenTelemetry transition:** OSProfiler remains functional for per-request distributed tracing across OpenStack services but entered maintenance mode in 2024.1 (Caracal). For new deployments, OpenTelemetry with Jaeger is the recommended tracing approach. Existing OSProfiler users should plan migration to OpenTelemetry instrumentation.
- **Epoxy (2025.1) observability changes:** OSProfiler formally in maintenance mode -- OpenTelemetry recommended for all new tracing instrumentation. Monasca fully retired. Continued Prometheus integration improvements across deployment tools.
- **Flamingo (2025.2) observability changes:** Continued improvements to OpenTelemetry integration across OpenStack services. OSProfiler remains available but deprecated in favor of OpenTelemetry.

## See Also

- `general/observability.md` -- general observability patterns
- `providers/openstack/infrastructure.md` -- OpenStack infrastructure overview
- `providers/prometheus-grafana/observability.md` -- Prometheus and Grafana stack
- `providers/openstack/control-plane-ha.md` -- monitoring HA control plane health
