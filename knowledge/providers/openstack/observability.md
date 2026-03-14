# OpenStack Observability (Monitoring, Metering, Logging, Testing)

## Checklist

- [ ] Is Ceilometer deployed for telemetry collection? (`ceilometer-agent-compute` on each hypervisor for VM metrics, `ceilometer-agent-notification` consuming oslo.messaging notifications from all services, polling interval tuned to balance granularity vs load -- default 600s often too slow for autoscaling)
- [ ] Is Gnocchi configured as the metrics backend? (time-series database for Ceilometer metrics, storage driver selection: file/Ceph/Swift/S3, archive policies defining retention granularity -- e.g., `1m:7d,5m:30d,1h:365d` for 1-minute granularity for 7 days then roll up)
- [ ] Are Gnocchi archive policies sized for capacity? (metric count = resources x meters x archive policy points, Ceph or Swift backend recommended for production scale, `gnocchi-metricd` workers scaled to handle incoming measurements)
- [ ] Is Aodh configured for alarming? (threshold alarms on Gnocchi metrics for autoscaling and alerting, composite alarms combining multiple conditions with `and`/`or` operators, `event` alarms for reacting to specific OpenStack events, alarm actions as webhook URLs to Heat or external systems)
- [ ] Is Monasca evaluated as an alternative monitoring stack? (monitoring-as-a-service with multi-tenant metric collection, Kafka-based pipeline, built-in anomaly detection, deterministic and statistical alarm types, Grafana plugin for dashboards -- more scalable than Ceilometer/Gnocchi for large deployments)
- [ ] Is centralized logging deployed for all OpenStack services? (Fluentd/Fluent Bit or Filebeat on each node shipping logs from `/var/log/nova/`, `/var/log/neutron/`, etc. to Elasticsearch/OpenSearch, Graylog, or Loki; structured JSON logging enabled where possible via oslo.log `[DEFAULT] use_json = True`)
- [ ] Are log retention and rotation policies defined? (logrotate for local logs, index lifecycle management in Elasticsearch/OpenSearch for centralized logs, separate indices per service for targeted retention, consider 30-90 day hot storage with cold/frozen tiers)
- [ ] Is Prometheus + Grafana integrated for infrastructure and service monitoring? (`openstack-exporter` for API-level metrics, `node_exporter` on all hosts, `libvirt_exporter` for hypervisor metrics, `ceph_exporter` for storage metrics, custom Grafana dashboards per service)
- [ ] Are OpenStack service healthcheck endpoints monitored? (`/healthcheck` endpoint on each API service via oslo.middleware, HAProxy health checks against API ports, synthetic checks with `openstack token issue` for end-to-end Keystone validation)
- [ ] Is Rally used for performance benchmarking? (`rally task start` with scenario files for Nova boot, Cinder create, Neutron network creation throughput, baseline performance established before upgrades, results stored for trend analysis)
- [ ] Is Tempest used for functional validation? (`tempest run` after deployments and upgrades, `tempest.conf` configured for the specific cloud, custom test plugins for site-specific validation, integrated into CI/CD pipeline for pre-production verification)
- [ ] Are infrastructure capacity metrics tracked for planning? (compute: vCPU/RAM allocation ratio trends, storage: Ceph pool utilization and growth rate, network: bandwidth utilization per provider network, Keystone: token issuance rate and latency)
- [ ] Are oslo.messaging (RabbitMQ) health and performance monitored? (queue depth, message rate, consumer count, unacknowledged messages, cluster partition detection -- RabbitMQ problems cascade across all OpenStack services)
- [ ] Is distributed tracing considered for API request debugging? (OSProfiler for OpenStack-native request tracing across services, integration with Jaeger or Zipkin, `--os-profile` on CLI for per-request tracing -- useful for diagnosing slow API calls)

## Why This Matters

OpenStack is composed of dozens of services communicating via REST APIs and message queues -- without comprehensive observability, failures cascade silently and root cause analysis becomes guesswork. Ceilometer polling intervals directly affect autoscaling responsiveness: a 600-second polling interval means 10-minute detection latency for scaling events. Gnocchi archive policy misconfiguration causes either excessive storage consumption or loss of granular historical data. RabbitMQ is the nervous system of OpenStack -- queue congestion in one service (e.g., Neutron agent heartbeats) can starve other services of message delivery. Log volume from a medium OpenStack deployment (50 compute nodes) can exceed 10 GB/day, requiring deliberate retention and aggregation strategy. Rally and Tempest are not optional extras -- they are the only reliable way to validate that an upgrade or configuration change has not introduced performance regression or functional breakage.

## Common Decisions (ADR Triggers)

- **Metrics stack** -- Ceilometer/Gnocchi/Aodh (native OpenStack, integrated with Heat autoscaling) vs Monasca (scalable, multi-tenant, Kafka-based) vs Prometheus/Grafana (industry standard, large ecosystem, not OpenStack-native) -- integration depth vs ecosystem breadth
- **Logging stack** -- ELK/OpenSearch (full-text search, powerful, resource-heavy) vs Loki/Grafana (label-indexed, lightweight, pairs with Prometheus) vs Graylog (structured logging, built-in alerting) -- query capabilities vs resource footprint
- **Log shipping** -- Fluentd (flexible, plugin-rich, Ruby) vs Fluent Bit (lightweight C, low memory) vs Filebeat (Elastic ecosystem) -- footprint on compute nodes and destination compatibility
- **Alerting pipeline** -- Aodh alarms to Heat webhooks (native autoscaling) vs Prometheus Alertmanager (routing, silencing, grouping) vs PagerDuty/OpsGenie integration (incident management) -- operational workflow integration
- **Performance testing** -- Rally continuous benchmarking (proactive capacity insights) vs Rally only pre-upgrade (reactive validation) vs no performance testing (risk of undetected degradation) -- operational maturity level
- **Functional validation** -- Tempest in CI/CD (every change validated) vs Tempest post-upgrade only (periodic validation) vs manual smoke tests (lowest coverage) -- deployment confidence vs pipeline complexity
- **Tracing** -- OSProfiler (native, per-request) vs Jaeger/OpenTelemetry (industry standard, requires instrumentation) vs no tracing (log correlation only) -- debugging capability vs implementation effort
- **Metering for billing** -- Ceilometer + CloudKitty (rating engine for chargeback/showback) vs custom metering from Gnocchi/Prometheus (flexible but build-it-yourself) vs external billing platforms -- internal chargeback requirements

## Version Notes

| Feature | Pike (16) Oct 2017 | Queens (17) Feb 2018 | Rocky (18) Aug 2018 | Stein (19) Apr 2019 | Train (20) Oct 2019 | Ussuri (21) May 2020 | Victoria (22) Oct 2020 | Wallaby (23) Apr 2021 | Xena (24) Oct 2021 | Yoga (25) Mar 2022 | Zed (26) Oct 2022 | 2023.1 Antelope (27) | 2023.2 Bobcat (28) | 2024.1 Caracal (29) | 2024.2 Dalmatian (30) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ceilometer polling agent | GA | GA | GA (polling/notification split) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Ceilometer notification agent | GA | GA | GA (primary collection method) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Ceilometer pipeline refactoring | Monolithic | Polling + notification separated | GA (separate processes) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Gnocchi (metrics backend) | In-tree (integrated) | Independent project | Independent (GA) | GA (4.x) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Gnocchi storage drivers | File, Ceph, Swift | File, Ceph, Swift, S3 | Same + Redis | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Panko (event storage) | GA (integrated) | GA | GA | Deprecated notice | Deprecated | Deprecated | Deprecated | Deprecated | Retired | Retired | Retired | Retired | Retired | Retired | Retired |
| Aodh (alarming) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Aodh composite alarms | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Monasca (monitoring-as-a-service) | GA | GA | GA | GA | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Maintenance mode | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Effectively retired | Effectively retired |
| CloudKitty (rating/billing) | GA | GA | GA (v2 API) | GA (v2 storage) | GA | GA | GA | GA | GA (Prometheus collector) | GA | GA | GA | GA | GA | GA |
| CloudKitty storage backends | SQL | SQL | SQL, InfluxDB | SQL, InfluxDB, OpenSearch | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| CloudKitty collectors | Ceilometer, Gnocchi | Same | Same + Monasca | Same | Same | Same | Same | Same | Prometheus added | GA | GA | GA | GA | GA | GA |
| OSProfiler (tracing) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA (maintenance) | GA (maintenance) |
| Rally (benchmarking) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Tempest (functional testing) | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA | GA |
| Prometheus integration | Community | Community | Community (exporters) | Community (exporters) | Community | Community | Community | Community | Community | Community (openstack-exporter) | GA (recommended) | GA | GA | GA | GA |

**Key changes across releases:**
- **Ceilometer polling vs notification agents:** In Pike, Ceilometer was a monolithic service. Rocky separated it into distinct polling and notification agents. The notification agent (consuming oslo.messaging notifications) became the primary and recommended collection method, as it is event-driven and lower overhead. The polling agent is still needed for metrics not exposed via notifications (e.g., libvirt VM metrics on compute nodes) but should have its polling interval tuned to reduce load.
- **Gnocchi becoming independent:** Gnocchi was part of the Ceilometer project through Pike. In Queens it became an independent project with its own release cycle. This decoupling allowed Gnocchi to evolve faster and be used as a general-purpose time-series database beyond OpenStack telemetry. Gnocchi 4.x (Stein+) added performance improvements and new archive policy features.
- **Panko deprecation and retirement:** Panko (event storage for Ceilometer events) was deprecated in Stein and retired in Xena. Events should be forwarded to external systems (Elasticsearch/OpenSearch, SIEM platforms) via oslo.messaging notification listeners rather than stored in Panko. Organizations still using Panko should migrate event storage to their centralized logging stack.
- **Monasca status:** Monasca (monitoring-as-a-service with Kafka pipeline, multi-tenant metrics, and built-in alarming) entered maintenance mode in Train due to declining community activity. It is effectively retired as of Yoga. Organizations that adopted Monasca should plan migration to Prometheus/Grafana or Ceilometer/Gnocchi/Aodh stacks.
- **CloudKitty evolution:** CloudKitty (rating engine for chargeback/showback) introduced its v2 API and storage backend in Rocky/Stein, adding InfluxDB and OpenSearch as storage options. A Prometheus collector was added in Xena, enabling CloudKitty to rate metrics from Prometheus in addition to Gnocchi and Ceilometer. This makes CloudKitty compatible with both native OpenStack telemetry and Prometheus-based monitoring stacks.
- **Prometheus as recommended monitoring:** While not an official OpenStack project, Prometheus with the openstack-exporter has become the de facto standard for infrastructure monitoring in OpenStack deployments. Starting with Zed, many deployment tools (Kolla-Ansible, TripleO/Director) include Prometheus integration out of the box. Combined with Grafana dashboards, it provides richer visualization than native OpenStack telemetry.
- **OSProfiler maintenance mode:** OSProfiler remains functional for per-request distributed tracing across OpenStack services but has entered maintenance mode in recent releases. For new deployments, OpenTelemetry with Jaeger is the recommended tracing approach.
