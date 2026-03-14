# Observability

## Checklist

- [ ] Where are application logs sent? What format? (structured JSON recommended)
- [ ] Where are infrastructure/system logs sent?
- [ ] What metrics are collected? (CPU, memory, disk, request rate, error rate, latency)
- [ ] Are custom application metrics needed? (business KPIs, queue depths, cache hit rates)
- [ ] What alerting thresholds are defined? Who gets notified?
- [ ] Is distributed tracing enabled? (request flows across services)
- [ ] Are network flow logs enabled?
- [ ] What is the log retention period?
- [ ] Are dashboards defined for operational visibility?
- [ ] Is there a centralized log aggregation system?
- [ ] Are health checks configured for all services? (liveness and readiness)
- [ ] Is synthetic monitoring needed? (external availability checks)
- [ ] Are SLIs/SLOs defined for the service?

## Why This Matters

You can't fix what you can't see. Missing observability means longer incident response times, undetected performance degradation, and inability to do root cause analysis. Compliance frameworks also require audit logging.

## Common Decisions (ADR Triggers)

- **Observability stack** — cloud-native vs third-party (Datadog, New Relic, Splunk)
- **Log aggregation approach** — centralized vs distributed
- **Alerting strategy** — what triggers pages vs warnings
- **Tracing implementation** — sampling rate, which services
- **Log retention policy** — how long, where archived
