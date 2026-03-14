# Observability

## Scope

This file covers **what** observability decisions need to be made. For provider-specific **how**, see the provider observability files.

## Checklist

- [ ] **[Critical]** Where are application logs sent? What format? (structured JSON recommended)
- [ ] **[Critical]** Where are infrastructure/system logs sent?
- [ ] **[Critical]** What metrics are collected? (CPU, memory, disk, request rate, error rate, latency)
- [ ] **[Optional]** Are custom application metrics needed? (business KPIs, queue depths, cache hit rates)
- [ ] **[Critical]** What alerting thresholds are defined? Who gets notified?
- [ ] **[Recommended]** Is distributed tracing enabled? (request flows across services)
- [ ] **[Recommended]** Are network flow logs enabled?
- [ ] **[Recommended]** What is the log retention period?
- [ ] **[Recommended]** Are dashboards defined for operational visibility?
- [ ] **[Recommended]** Is there a centralized log aggregation system?
- [ ] **[Critical]** Are health checks configured for all services? (liveness and readiness)
- [ ] **[Optional]** Is synthetic monitoring needed? (external availability checks)
- [ ] **[Recommended]** Are SLIs/SLOs defined for the service?

## Why This Matters

You can't fix what you can't see. Missing observability means longer incident response times, undetected performance degradation, and inability to do root cause analysis. Compliance frameworks also require audit logging.

## Common Decisions (ADR Triggers)

- **Observability stack** — cloud-native vs third-party (Datadog, New Relic, Splunk)
- **Log aggregation approach** — centralized vs distributed
- **Alerting strategy** — what triggers pages vs warnings
- **Tracing implementation** — sampling rate, which services
- **Log retention policy** — how long, where archived

## See Also

- `providers/aws/observability.md` — AWS CloudWatch, X-Ray, and logging
- `providers/azure/observability.md` — Azure Monitor and Application Insights
- `providers/gcp/observability.md` — GCP Cloud Monitoring and Logging
