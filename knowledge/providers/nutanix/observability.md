# Nutanix Observability and Monitoring

## Scope

Monitoring, alerting, analytics, and automation for Nutanix infrastructure: Prism Central multi-cluster monitoring, Prism Pro/Ultimate advanced analytics, capacity planning, log aggregation, SNMP integration, performance baselining (X-Ray), health checks (NCC), and automated remediation via playbooks.

## Checklist

- [ ] [Critical] Is Prism Central deployed as the single pane of glass for multi-cluster monitoring, with all Prism Element clusters registered and reporting metrics, alerts, and events to the central console?
- [ ] [Critical] Are alert policies configured in Prism Central with appropriate thresholds and notification channels (email, Slack webhook, PagerDuty, SNMP trap) for critical events -- disk failure, CVM down, host unreachable, storage runway exhaustion?
- [ ] [Optional] Is Pulse telemetry enabled (opt-in) to send cluster health data to Nutanix support for proactive case generation and hardware failure prediction, or explicitly disabled if data sovereignty requirements prohibit it?
- [ ] [Recommended] Is X-Ray performance benchmarking used to baseline cluster IOPS, latency, and throughput before production workload deployment, with results stored for comparison during performance investigations?
- [ ] [Recommended] Is Prism Pro (or Prism Ultimate) licensed and enabled for advanced analytics -- anomaly detection using machine learning, capacity forecasting with what-if scenarios, and automated playbook-based remediation?
- [ ] [Critical] Is capacity planning configured with Prism Central runway forecasting, showing projected days until CPU, memory, or storage exhaustion based on historical growth trends, with alerts at 90-day and 60-day runway thresholds?
- [ ] [Recommended] Are syslog forwarding rules configured on Prism Element (each cluster) and Prism Central to send audit logs, system events, and security alerts to a centralized log aggregation platform (Splunk, ELK, Graylog)?
- [ ] [Recommended] Is SNMP v3 (not v1/v2c) configured for integration with enterprise monitoring platforms (SolarWinds, Nagios, PRTG, Datadog), with SNMPv3 authentication and encryption to prevent credential exposure?
- [ ] [Optional] Are Prism Central custom dashboards created for different stakeholder views -- infrastructure team (host/CVM health, storage utilization), application teams (VM performance, IOPS per workload), and management (capacity runway, cost allocation)?
- [ ] [Recommended] Are Prism Central analysis charts used to correlate performance metrics across time -- VM IOPS vs storage latency vs CPU usage -- to identify root cause during performance incidents rather than examining metrics in isolation?
- [ ] [Optional] Is integration with third-party APM tools (Datadog, New Relic, Dynatrace) configured at the guest OS level for application-layer metrics, since Prism provides infrastructure metrics but not application-level observability?
- [ ] [Recommended] Are Prism Central playbooks configured for automated responses to common events -- e.g., send Slack notification on HA event, create ServiceNow ticket on disk failure, snapshot VM before scheduled maintenance?
- [ ] [Recommended] Is the NCC (Nutanix Cluster Check) health check tool run regularly (weekly or before maintenance windows) to identify configuration issues, inconsistencies, and pre-failure conditions?
- [ ] [Optional] Are Prism Central reports scheduled for weekly or monthly delivery to stakeholders, covering capacity utilization, VM sprawl (powered-off VMs), snapshot age, and cluster health summary?

## Why This Matters

Nutanix observability is centered on Prism Central, which aggregates metrics from all registered clusters and provides the analytics, alerting, and automation engine. Without Prism Central, each cluster is monitored independently through Prism Element, creating visibility silos. Prism Pro's anomaly detection uses machine learning to establish behavioral baselines for VM and infrastructure metrics, alerting on deviations that static thresholds would miss -- for example, a gradual increase in storage latency that stays below a fixed threshold but represents a 3x deviation from normal. Capacity runway forecasting prevents the common failure mode of running out of storage or compute mid-quarter with no budget for expansion. X-Ray is essential for establishing performance baselines before production deployment; without baselines, there is no objective way to determine if current performance is degraded. NCC (Nutanix Cluster Check) catches configuration drift, failed components, and pre-failure conditions that are not visible through normal monitoring -- it is the equivalent of a comprehensive health screening. Syslog and SNMP integration are critical for organizations with established monitoring platforms, as Prism Central cannot replace enterprise SIEM or APM tooling.

## Common Decisions (ADR Triggers)

- **Monitoring platform** -- Prism Central only (simple, Nutanix-native) vs Prism Central + external SIEM (Splunk/ELK for correlation and compliance) vs full replacement with Datadog/New Relic (cloud-native, multi-platform)
- **Prism licensing tier** -- Prism Starter (basic monitoring, included) vs Prism Pro (anomaly detection, playbooks, what-if planning) vs Prism Ultimate (full feature set including Flow, NCM Self-Service (formerly Calm) integration)
- **Alerting pipeline** -- Prism email alerts (simple) vs webhook to PagerDuty/Opsgenie (on-call rotation, escalation) vs SNMP traps to existing NMS (enterprise integration)
- **Log management** -- Prism Central built-in audit logs (limited retention, no correlation) vs syslog to Splunk/ELK (searchable, correlated, compliant) vs Nutanix-to-cloud log shipping
- **Capacity planning approach** -- Prism Central runway forecasting (built-in, trend-based) vs manual spreadsheet planning vs third-party capacity management (CloudPhysics, Densify)
- **Performance baselining** -- X-Ray synthetic benchmarks (repeatable, controlled) vs production workload observation (real-world but variable) vs vendor-provided reference metrics
- **Automation level** -- Manual response to alerts (simplest) vs Prism Central playbooks (automated remediation, Nutanix-native) vs external automation (ServiceNow workflows, Ansible Tower triggered by alerts)
