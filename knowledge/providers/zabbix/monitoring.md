# Zabbix

## Scope

This file covers **Zabbix** open-source monitoring platform including server and proxy architecture for distributed monitoring, agent deployment (Zabbix Agent, Agent 2), template design and management, trigger expressions and actions for alerting, low-level discovery (LLD) for automatic entity detection, web monitoring for HTTP endpoint checks, Zabbix vs Prometheus comparison for different use cases, horizontal scaling strategies (proxies, database partitioning), and ticketing system integration (ServiceNow, Jira, email). For general observability patterns, see `general/observability.md`.

## Checklist

- [ ] **[Critical]** Is the Zabbix server sized appropriately for the monitored environment -- database backend (PostgreSQL recommended for large deployments, with TimescaleDB extension for long-term metric storage), server memory and CPU for trigger evaluation, and cache sizes (ValueCacheSize, HistoryCacheSize) tuned to avoid performance bottlenecks?
- [ ] **[Critical]** Are Zabbix proxies deployed for remote sites, network segments, or large environments (1,000+ hosts) to distribute data collection load, reduce server-to-agent network traffic, and provide monitoring continuity during server maintenance or network interruptions?
- [ ] **[Critical]** Is the agent deployment strategy defined -- Zabbix Agent (C-based, mature, lightweight) vs Agent 2 (Go-based, plugin architecture, supports native Prometheus metric scraping, Docker monitoring, and modern data sources) -- with configuration management automating agent installation and template assignment?
- [ ] **[Critical]** Are templates designed following best practices -- cloned from built-in templates rather than modifying originals, organized by function (OS, application, hardware), using macros for environment-specific thresholds, and version-controlled for change tracking?
- [ ] **[Recommended]** Are trigger expressions tuned to minimize false positives -- using `avg()`, `last()`, and `count()` functions with appropriate evaluation periods, hysteresis (different thresholds for problem and recovery), and trigger dependencies to suppress downstream alerts during upstream failures?
- [ ] **[Recommended]** Is low-level discovery (LLD) configured for dynamic environments -- auto-discovering network interfaces, filesystems, database instances, and services, with appropriate discovery intervals (every 1-4 hours) and keep-lost-resources periods to handle transient entities?
- [ ] **[Recommended]** Are actions configured with escalation steps -- initial notification to the responsible team, escalation to management after SLA-defined intervals, and recovery notifications to close the loop -- with media types appropriate for severity (email for warnings, SMS/webhook for critical)?
- [ ] **[Recommended]** Is database housekeeping configured with appropriate retention periods -- history (raw data, 7-30 days), trends (aggregated hourly data, 365 days), and events (problem/resolution history, 365 days) -- using partitioning (PostgreSQL range partitioning or TimescaleDB hypertables) for performant data deletion?
- [ ] **[Recommended]** Is the Zabbix API used for automation -- host registration from CMDB or provisioning systems, bulk template assignment, and report generation -- with API user authentication (API tokens in Zabbix 5.4+) and rate limiting to prevent server overload?
- [ ] **[Optional]** Is web monitoring configured for critical HTTP/HTTPS endpoints with multi-step scenarios (login, navigate, verify content), appropriate check intervals (1-5 minutes), and authentication support (basic, NTLM, form-based)?
- [ ] **[Optional]** Is the Zabbix frontend deployed behind a reverse proxy with TLS termination, and is frontend performance optimized (PHP-FPM tuning, separate web server from Zabbix server) for environments with many concurrent dashboard users?
- [ ] **[Optional]** Are Zabbix trend prediction and anomaly detection features evaluated -- Zabbix provides ML-based trend prediction for capacity planning and anomaly detection for baseline deviation alerting, but does not offer GenAI or natural language features?
- [ ] **[Optional]** Are Grafana dashboards used alongside or instead of native Zabbix dashboards via the Zabbix data source plugin, providing more flexible visualization options while retaining Zabbix as the data collection and alerting engine?

## Why This Matters

Zabbix is the most widely deployed open-source monitoring platform, particularly prevalent in on-premises and hybrid environments where its zero licensing cost, agent-based monitoring model, and support for SNMP, IPMI, and WMI make it the natural choice for infrastructure monitoring. Unlike Prometheus (which requires exporters and a pull model), Zabbix provides a complete monitoring solution out of the box -- server, agents, alerting, visualization, and reporting -- making it accessible to operations teams without deep monitoring engineering expertise. However, Zabbix's monolithic architecture requires careful database sizing and maintenance; a Zabbix deployment monitoring 5,000+ hosts can generate millions of metrics that overwhelm an un-tuned PostgreSQL or MySQL database within months.

Template design is the single most impactful architectural decision in a Zabbix deployment. Well-designed templates with appropriate macros, discovery rules, and trigger expressions enable consistent monitoring across thousands of hosts with minimal per-host configuration. Poorly designed templates -- with hardcoded thresholds, excessive items (collecting metrics that are never reviewed), or missing dependencies -- generate alert fatigue and consume database resources unnecessarily. The proxy architecture is essential for distributed monitoring: without proxies, all agent connections terminate at the central server, creating a single point of failure and a network bottleneck for remote sites.

## Common Decisions (ADR Triggers)

- **Zabbix vs Prometheus** -- Zabbix provides a complete monitoring solution with built-in alerting, visualization, and agent-based collection suited for traditional infrastructure (VMs, bare metal, network devices). Prometheus excels in Kubernetes-native environments with its pull model, PromQL, and tight integration with cloud-native tools. Zabbix supports SNMP, WMI, and IPMI natively; Prometheus requires exporters. Zabbix stores data in a relational database (long-term history); Prometheus uses a time-series database with limited retention. Use Zabbix for mixed on-premises environments; Prometheus for Kubernetes-centric workloads; both can coexist with Zabbix Agent 2 scraping Prometheus endpoints.
- **PostgreSQL vs MySQL vs TimescaleDB backend** -- PostgreSQL offers better performance for large deployments (partitioning, parallel queries, JSON support). MySQL/MariaDB is simpler to operate but struggles with large table maintenance (ALTER TABLE locks). TimescaleDB (PostgreSQL extension) provides automatic partitioning, compression (10-20x), and continuous aggregates purpose-built for time-series data. TimescaleDB is recommended for any deployment expecting more than 50,000 NVPS (new values per second).
- **Agent vs agentless monitoring** -- Agent-based monitoring (Zabbix Agent/Agent 2) provides deep OS and application metrics, active checks, and log monitoring. Agentless monitoring (SNMP, IPMI, SSH, HTTP) avoids agent deployment overhead but provides limited metric depth. Use agents for servers and workstations; SNMP for network devices, storage, and UPS; IPMI for hardware health; SSH checks only when agent installation is not permitted.
- **Centralized vs distributed architecture** -- Centralized (single Zabbix server) is simpler but creates a single point of failure and requires all agents to reach the server directly. Distributed (Zabbix proxies at each site) provides local data buffering (survives WAN outages), reduces central server load, and enables monitoring across network boundaries. Deploy proxies for any site with more than 100 hosts or connected via WAN/VPN.
- **Native alerting vs external integration** -- Zabbix native alerting (email, SMS, webhook) is sufficient for simple environments. For complex escalation, on-call rotation, and multi-channel notification, integrate with dedicated alerting platforms (PagerDuty, Opsgenie) via webhook media type. Use native alerting for small-to-medium deployments; external alerting platform when on-call management requires schedule rotation, acknowledgment tracking, and escalation policies.
- **AI/ML feature sufficiency** -- Zabbix trend prediction and anomaly detection provide traditional ML capabilities but lack GenAI features (no natural language queries, no AI assistant, no autonomous investigation); organizations requiring AI-powered operations should evaluate whether to pair Zabbix with an AI-capable platform or replace it.

## AI and GenAI Capabilities

**ML-Based Features** — Zabbix provides trend prediction (forecasting future values based on historical data) and anomaly detection (identifying deviations from baseline patterns). These are traditional ML features, not GenAI — there is no natural language query, AI assistant, or LLM integration. For organizations requiring AI-powered investigation, natural language querying, or autonomous remediation, Zabbix should be paired with an AI-capable platform or replaced by one.

Note: Zabbix's open-source model means AI features lag behind commercial platforms. This is a trade-off of the zero-license-cost model.

## See Also

- `general/observability.md` -- general observability architecture patterns and pillar design
- `providers/prometheus-grafana/observability.md` -- Prometheus and Grafana for comparison and coexistence patterns

## Reference Links

- [Zabbix Documentation](https://www.zabbix.com/documentation/current/en) -- server/proxy architecture, agent deployment, template design, and trigger configuration
- [Zabbix API Reference](https://www.zabbix.com/documentation/current/en/manual/api) -- REST API for automation, host management, and template provisioning
- [Zabbix Best Practices](https://www.zabbix.com/documentation/current/en/manual/installation/requirements) -- sizing, database selection, and distributed monitoring with proxies
