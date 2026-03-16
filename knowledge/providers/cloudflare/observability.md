# Cloudflare Observability

## Scope

Covers Cloudflare Logpush, Web Analytics, GraphQL Analytics API, Analytics Engine, Trace, health checks, Instant Logs, origin monitoring, BGP/Radar monitoring, and SIEM integration. Use alongside `security.md` for WAF/firewall event analysis and `workers.md` for Workers-specific metrics.

## Checklist

- [ ] [Critical] Configure Logpush jobs for HTTP request logs, firewall events, and Spectrum events to a supported destination (S3, R2, Splunk, Datadog, Azure Blob, GCS, Sumo Logic)
- [ ] [Recommended] Set up Web Analytics for privacy-first, cookie-free client-side analytics (no PII collection, GDPR-friendly)
- [ ] [Recommended] Evaluate GraphQL Analytics API for custom dashboards and programmatic access to zone-level, account-level, and DNS analytics
- [ ] [Critical] Configure health checks for origin servers (HTTP/HTTPS/TCP) with appropriate intervals, thresholds, and notification channels
- [ ] [Optional] Plan real-time log streaming via Logpush Instant Logs for debugging (WebSocket-based, not for production ingestion)
- [ ] [Critical] Design log retention strategy: Cloudflare retains analytics for limited periods (72 hours for most free/pro plans); Logpush to own storage for long-term retention
- [ ] [Recommended] Set up origin monitoring alerts for 5xx error spikes, latency increases, and origin health check failures
- [ ] [Optional] Evaluate Cloudflare Radar and route leak detection for BGP monitoring if using BYOIP or Magic Transit
- [ ] [Recommended] Configure Workers analytics and Durable Objects metrics for serverless workload observability
- [ ] [Recommended] Plan cost model for Logpush: log volume can be significant at scale; filter fields and sample if needed
- [ ] [Recommended] Integrate Cloudflare logs with existing SIEM (Splunk, Elastic, Sentinel) for security event correlation
- [ ] [Critical] Set up notifications (email, PagerDuty, webhook) for DDoS attacks, SSL certificate expiry, and origin unreachable events
- [ ] [Optional] Evaluate Analytics Engine for custom server-side metrics from Workers (write data points with dimensions and blobs, query via SQL API); suitable for high-cardinality metrics without Logpush overhead
- [ ] [Optional] Evaluate Trace for distributed tracing of Workers requests across Service Bindings, Durable Object calls, and external fetches; provides request-level visibility into multi-Worker architectures

## Why This Matters

Cloudflare processes requests at its edge before they reach origin infrastructure, which means critical observability data (client geolocation, cache hit ratios, WAF rule matches, bot scores, DDoS mitigation events) exists only within Cloudflare's platform. Without proper log export and analytics configuration, teams have a blind spot covering everything between the client and the origin. Cloudflare's built-in analytics dashboards provide real-time summaries, but Logpush is essential for long-term retention, compliance, and correlation with origin-side telemetry. The GraphQL Analytics API enables custom queries that go beyond the dashboard, including time-series aggregation and filtering by any request attribute.

## Common Decisions (ADR Triggers)

- **Logpush destination: R2 vs external (S3/Splunk/Datadog)**: R2 has zero egress fees and tight Cloudflare integration, making it cost-effective for archival. External destinations (Splunk, Datadog) are better when logs must feed into existing alerting and correlation pipelines. Many teams use both: R2 for retention, Datadog for real-time alerting.
- **Sampling vs full log ingestion**: At millions of requests per second, Logpush generates terabytes of logs. Use Logpush filters (added 2023) to select specific fields and filter by status code, host, or action. Alternatively, use Analytics API for aggregated queries and reserve full logs for incident investigation.
- **Web Analytics vs third-party RUM (Datadog RUM, New Relic Browser)**: Cloudflare Web Analytics is free, privacy-first, and requires no cookies. However, it lacks session replay, user journey mapping, and error tracking. Use it as a lightweight complement, not a replacement, for full RUM solutions.
- **Dashboard vs GraphQL API vs Logpush for reporting**: Dashboards for ad-hoc investigation. GraphQL API for automated reporting and custom metrics. Logpush for compliance, forensics, and SIEM integration. These are complementary, not exclusive.
- **Instant Logs vs Logpush**: Instant Logs streams via WebSocket in real-time but is limited to 60 minutes and not suitable for production monitoring. Use for debugging during deployments or incident response. Logpush is the durable, production-grade solution.

## Reference Architectures

### Centralized Log Pipeline
```
[Cloudflare Edge]
    |
    +-- Logpush (HTTP Requests) -----> [R2 Bucket] -----> [Athena / BigQuery for ad-hoc queries]
    |                                       |
    +-- Logpush (Firewall Events) --> [Datadog / Splunk] --> [Alerting + SIEM Correlation]
    |
    +-- Logpush (DNS Logs) ---------> [S3 / GCS] ---------> [Compliance Archive]
```
Separate Logpush jobs per log type allow different routing. R2 for cost-effective archival with query-on-demand via external engines. Datadog or Splunk for real-time alerting on WAF blocks, bot detections, and DDoS events. DNS logs to cold storage for compliance retention (90-day / 1-year requirements).

### Origin Health Monitoring
```
[Cloudflare Health Checks] --> [Origin Pool]
        |                          |
   [Check Results]          [5xx / Timeout Detection]
        |                          |
   [Load Balancer Steering]   [Logpush (Health Check Events)]
        |                          |
   [Failover to Secondary]   [PagerDuty / Webhook Alert]
```
Cloudflare health checks probe origins independently of client traffic. Failed checks trigger automatic failover in the load balancer. Health check events export via Logpush feed into incident management. Configure check intervals (60s for standard, 5-15s for critical services with Enterprise) and consecutive failure thresholds to avoid flapping.

### Edge Analytics Stack
```
[Client Request] --> [Cloudflare Edge]
                          |
                    [Analytics Engine (server-side)]
                    [Web Analytics (client-side JS)]
                          |
                    [GraphQL Analytics API]
                          |
                    [Custom Dashboard (Grafana / Retool)]
```
Use Workers Analytics Engine for custom server-side metrics (counters, timers) without Logpush overhead. Web Analytics provides client-side Core Web Vitals. GraphQL API aggregates both for custom dashboards. This avoids high-volume log ingestion for metrics that can be computed at the edge.
