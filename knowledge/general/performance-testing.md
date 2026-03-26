# Performance Testing

## Scope

This file covers **performance testing strategy and execution** including load testing tools, test types (load, stress, soak, spike, breakpoint), capacity validation, performance budgets, bottleneck identification, production load testing, and APM integration. For general testing strategy (chaos engineering, synthetic monitoring, SLOs), see `general/testing-strategy.md`. For capacity planning and sizing, see `general/capacity-planning.md`. For observability and metrics collection, see `general/observability.md`.

## Checklist

### Test Strategy and Planning

- [ ] **[Critical]** Is a performance testing strategy defined before going to production? (test types, environments, acceptance criteria, cadence)
- [ ] **[Critical]** Are performance baselines established for all critical paths? (measure current p50, p95, p99 latency, throughput, error rate under normal load)
- [ ] **[Critical]** Are performance budgets defined and enforced? (page load < 3s, API response < 200ms p95, time-to-interactive < 5s)
- [ ] **[Recommended]** Is there a dedicated performance testing environment that mirrors production? (same instance types, network topology, data volume)
- [ ] **[Recommended]** Are performance tests integrated into CI/CD pipelines? (automated regression detection on every build or nightly)
- [ ] **[Optional]** Is there a performance testing center of excellence or guild? (shared tooling, expertise, test libraries across teams)

### Load Testing Tool Selection

- [ ] **[Critical]** Is a single load testing tool standardized across the organization? (avoid tool sprawl — pick one primary tool)
- [ ] **[Recommended]** Can load tests be written as code and version-controlled? (k6 scripts, Locust Python files, Gatling Scala simulations)
- [ ] **[Recommended]** Does the tool support the required protocols? (HTTP/HTTPS, gRPC, WebSocket, GraphQL, JDBC, AMQP)
- [ ] **[Recommended]** Can the tool generate load from distributed agents? (cloud-based load generation to avoid client-side bottlenecks)
- [ ] **[Optional]** Does the tool integrate with your observability stack? (Prometheus metrics export, Grafana dashboards, Datadog integration)

### Performance Test Types

- [ ] **[Critical]** Are load tests run at expected peak traffic levels? (validate the system handles 1x, 2x, and 3x normal peak)
- [ ] **[Critical]** Are stress tests run to find the breaking point? (gradually increase load until errors or latency exceeds SLOs — know your ceiling)
- [ ] **[Recommended]** Are soak tests run for extended duration? (8-24 hours at normal load to detect memory leaks, connection pool exhaustion, log disk fill)
- [ ] **[Recommended]** Are spike tests run to validate autoscaling? (sudden 10x traffic spike — measure recovery time and error rate during scale-up)
- [ ] **[Optional]** Are breakpoint tests run to determine maximum capacity? (binary search for the exact RPS where p99 latency exceeds SLO)
- [ ] **[Optional]** Are configuration tests run to compare tuning changes? (A/B comparison of JVM heap sizes, connection pool sizes, thread counts)

### Capacity Validation

- [ ] **[Critical]** Is production capacity validated against growth projections? (if traffic doubles in 12 months, can infrastructure handle it today?)
- [ ] **[Critical]** Are database queries tested under realistic data volumes? (test with production-scale data, not empty databases — query plans change with data size)
- [ ] **[Recommended]** Are autoscaling policies validated with load tests? (confirm scale-up triggers fire correctly, scale-down does not cause oscillation)
- [ ] **[Recommended]** Are downstream dependencies included in capacity validation? (third-party APIs, shared databases, message queues, cache layers)
- [ ] **[Recommended]** Is capacity headroom quantified? (know the gap between current peak and maximum capacity — target 30-50% headroom)

### Bottleneck Identification

- [ ] **[Critical]** Are application-level metrics collected during load tests? (CPU, memory, GC pauses, thread pool utilization, connection pool usage)
- [ ] **[Critical]** Are database metrics correlated with load test results? (slow queries, lock contention, connection count, replication lag)
- [ ] **[Recommended]** Is distributed tracing enabled during performance tests? (identify which service or query is the bottleneck in a multi-service call chain)
- [ ] **[Recommended]** Are infrastructure metrics collected at all tiers? (load balancer, application, cache, database, network — identify the tier that saturates first)
- [ ] **[Recommended]** Are flame graphs or CPU profiles captured during load tests? (identify hot code paths — do not guess, measure)
- [ ] **[Optional]** Is network-level analysis performed? (packet captures, TCP retransmissions, DNS resolution latency, TLS handshake overhead)

### Production Load Testing

- [ ] **[Recommended]** Is traffic replay used for realistic load generation? (capture and replay production traffic patterns using GoReplay, tcpreplay, or ALB access logs)
- [ ] **[Recommended]** Is dark launching used to validate new services under production load? (route shadow traffic to new version without affecting users)
- [ ] **[Recommended]** Are feature flags used to gradually expose new code paths to production load? (canary by percentage, not all-or-nothing)
- [ ] **[Optional]** Is production load testing performed during off-peak windows? (synthetic load added to real traffic to test capacity ceiling safely)
- [ ] **[Optional]** Are load test requests tagged to distinguish them from real traffic? (custom headers, separate metrics dimensions, excluded from billing)

### Synthetic Monitoring and Continuous Validation

- [ ] **[Recommended]** Are synthetic transactions running continuously against production? (login, core workflow, payment — detect degradation before users report it)
- [ ] **[Recommended]** Are synthetic monitors deployed from multiple geographic locations? (detect regional latency issues, CDN misconfigurations, DNS problems)
- [ ] **[Recommended]** Do synthetic monitors alert on performance regression, not just availability? (alert if p95 response time increases 20% from baseline)
- [ ] **[Optional]** Are real user monitoring (RUM) metrics compared against synthetic results? (synthetic shows potential, RUM shows actual user experience)

### APM Integration

- [ ] **[Critical]** Is an APM tool deployed and collecting traces in all environments? (New Relic, Datadog APM, Dynatrace, Elastic APM, Grafana Tempo)
- [ ] **[Recommended]** Are APM traces correlated with load test execution windows? (overlay load test timeline on APM dashboards to pinpoint degradation)
- [ ] **[Recommended]** Are service-level transaction maps used to identify dependency bottlenecks? (APM service maps show where latency accumulates across services)
- [ ] **[Optional]** Is AI-powered anomaly detection enabled in APM? (automatic baseline deviation alerts — Dynatrace Davis, New Relic Lookout)

### SLA and Performance Budget Validation

- [ ] **[Critical]** Are SLA performance requirements documented and testable? (contractual: "API responses < 500ms at p99 under 1000 RPS")
- [ ] **[Critical]** Are performance budgets validated in CI/CD? (fail the build if bundle size exceeds budget, if API latency regresses, if Lighthouse score drops)
- [ ] **[Recommended]** Are performance budgets broken down by component? (frontend: LCP < 2.5s, FID < 100ms, CLS < 0.1; backend: p95 < 200ms per endpoint)
- [ ] **[Recommended]** Is there a performance regression alert for production? (compare current week p95 against previous week — alert on sustained degradation)

## Why This Matters

Performance problems are the most expensive bugs to fix in production. A 100ms increase in latency can reduce conversion rates by 7% (Akamai). A 1-second delay in page load drops customer satisfaction by 16% (Aberdeen Group). Yet most teams discover performance issues only after deployment, when the fix requires architectural changes rather than simple code optimizations.

Performance testing done correctly provides **predictive capacity data** — you know exactly how many users your system can handle, which component will fail first, and how much growth headroom you have. Without it, capacity planning is guesswork and every traffic spike is a gamble.

The most common failure mode is testing with unrealistic data volumes. A query that returns in 2ms on a development database with 1,000 rows may take 30 seconds on a production database with 50 million rows because the query planner chooses a sequential scan instead of an index scan. Always test with production-scale data.

Soak testing catches an entire class of bugs that other test types miss: memory leaks that accumulate over hours, connection pool leaks that exhaust database connections after thousands of requests, log files that fill disks over days, and timer/scheduler drift that causes resource contention after extended uptime.

## Load Testing Tools Comparison

| Tool | Language | Protocol Support | Distributed Mode | Cloud Offering | Best For |
|------|----------|-----------------|------------------|----------------|----------|
| **k6** | JavaScript (ES6) | HTTP, gRPC, WebSocket, Redis, Kafka | k6 operator (K8s) | Grafana Cloud k6 | Developer-friendly scripting, CI/CD integration, low overhead |
| **Locust** | Python | HTTP (extensible via plugins) | Built-in distributed | Locust Cloud | Python teams, custom load shapes, simple setup |
| **Gatling** | Scala/Java/Kotlin | HTTP, JMS, MQTT, gRPC | Gatling Enterprise | Gatling Enterprise Cloud | JVM shops, complex scenarios, detailed HTML reports |
| **JMeter** | Java (GUI + CLI) | HTTP, JDBC, LDAP, FTP, JMS, SOAP | Remote testing | BlazeMeter, OctoPerf | Protocol variety, non-developer users, legacy teams |
| **Artillery** | JavaScript/YAML | HTTP, WebSocket, Socket.io, gRPC | Artillery Cloud | Artillery Cloud | Serverless testing, YAML-based scenarios |
| **Vegeta** | Go | HTTP | CLI-based | None | Simple HTTP load testing, scripted pipelines |
| **wrk/wrk2** | Lua (scripting) | HTTP | Single machine | None | Quick benchmarks, constant-throughput testing |

### Recommendation

**k6** is the default recommendation for most teams: scripts in JavaScript, integrates natively with CI/CD, exports Prometheus metrics, runs in Kubernetes via the k6 operator, and has minimal resource overhead. Use **Locust** if your team is Python-native. Use **Gatling** for JVM-heavy organizations. Use **JMeter** only when you need protocol support others lack (JDBC, LDAP, JMS).

## Performance Test Types Explained

### Load Test

Run at **expected peak production traffic** for a sustained period (15-60 minutes). Validates that the system meets SLOs under normal peak conditions. This is the most important test type and should run on every release.

**Example:** 500 concurrent users performing a mix of read (80%) and write (20%) operations for 30 minutes. Acceptance criteria: p95 latency < 200ms, error rate < 0.1%.

### Stress Test

**Gradually increase** load beyond expected peak until the system degrades or fails. Identifies the breaking point and how the system behaves under overload (graceful degradation vs. cascading failure).

**Example:** Ramp from 500 to 5,000 concurrent users over 30 minutes. Record the exact user count where p99 latency exceeds 1 second and where error rate exceeds 1%.

### Soak Test (Endurance Test)

Run at **normal or moderate load** for an **extended duration** (8-72 hours). Detects slow-building issues: memory leaks, connection pool exhaustion, thread leaks, GC pressure accumulation, log disk filling, certificate expiration in-flight.

**Example:** 200 concurrent users for 24 hours. Monitor memory usage trend — any upward slope indicates a leak.

### Spike Test

Apply a **sudden, extreme load increase** to test autoscaling response and recovery. Measures time-to-scale and user impact during the scaling window.

**Example:** Jump from 100 to 2,000 concurrent users in 10 seconds, hold for 5 minutes, then drop back to 100. Measure: how many requests failed during scale-up, how long until p95 latency returned to baseline.

### Breakpoint Test

**Binary search** for the exact throughput (RPS) or concurrency level where a specific SLO is violated. Provides a precise capacity number for planning.

**Example:** Target: find the RPS where p99 latency exceeds 500ms. Start at 100 RPS, increase by 50 RPS every 2 minutes. Result: "System supports 850 RPS within SLO."

## Bottleneck Identification Methodology

### The Four Golden Signals Under Load

1. **Latency** — Is response time increasing? Check: application processing, database queries, external API calls, network round trips
2. **Traffic** — Is the system receiving the expected load? Check: load balancer metrics, request rate at each tier
3. **Errors** — Are error rates climbing? Check: HTTP 5xx, connection timeouts, circuit breaker trips, queue overflow
4. **Saturation** — Which resource is hitting limits? Check: CPU utilization, memory pressure, disk I/O, connection pool usage, thread pool exhaustion

### Systematic Bottleneck Hunting

1. **Start from the outside in** — check load balancer, then application, then cache, then database
2. **Look for saturation first** — the component at highest utilization percentage is usually the bottleneck
3. **Check connection pools** — exhausted connection pools cause queuing that looks like slow application code
4. **Profile, do not guess** — use flame graphs (async-profiler, py-spy, pprof) to find hot code paths
5. **Check garbage collection** — GC pauses cause latency spikes that are invisible without GC logging
6. **Verify network** — TCP retransmissions, connection resets, and DNS resolution delays are often overlooked

## Performance Budget Framework

### Frontend Budgets (Core Web Vitals)

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | < 2.5s | 2.5s - 4.0s | > 4.0s |
| **FID** (First Input Delay) / **INP** (Interaction to Next Paint) | < 100ms / < 200ms | 100-300ms / 200-500ms | > 300ms / > 500ms |
| **CLS** (Cumulative Layout Shift) | < 0.1 | 0.1 - 0.25 | > 0.25 |
| **TTFB** (Time to First Byte) | < 800ms | 800ms - 1.8s | > 1.8s |

### Backend Budgets

| Metric | Typical Target | Notes |
|--------|---------------|-------|
| **API p50 latency** | < 50ms | Internal service-to-service |
| **API p95 latency** | < 200ms | User-facing endpoints |
| **API p99 latency** | < 500ms | Tail latency — affects 1 in 100 users |
| **Error rate** | < 0.1% | Non-retryable errors |
| **Throughput** | 2-3x current peak | Capacity headroom |
| **Cold start** | < 1s | Serverless functions, container startup |

### Enforcing Budgets in CI/CD

- **Bundle size gates:** Fail the build if JavaScript bundle exceeds 200KB gzipped
- **Lighthouse CI:** Run Lighthouse in CI, fail if performance score drops below threshold
- **k6 thresholds:** Define pass/fail criteria in k6 scripts (`http_req_duration{p(95)}<200`)
- **API latency checks:** Compare load test p95 against baseline, fail if regression exceeds 10%

## Production Load Testing Patterns

### Traffic Replay

Capture production traffic and replay it against a test environment for realistic load patterns:

- **GoReplay (gor):** Capture and replay HTTP traffic in real-time or from files
- **ALB/CloudFront access logs:** Parse logs to recreate request patterns in k6 or Locust scripts
- **tcpreplay:** Network-level packet replay for lower-level protocol testing

### Dark Launching (Shadow Traffic)

Route a copy of production traffic to a new version without affecting user responses:

- Use service mesh mirroring (Istio traffic mirroring, Linkerd traffic splitting)
- Compare new version performance against production baseline
- Validate new database schemas, cache strategies, or algorithm changes under real load

### Canary Load Validation

Before full rollout, send a percentage of production traffic to the new version:

- Start at 1-5% of traffic, monitor error rate and latency
- Use automated canary analysis (Kayenta, Flagger, Argo Rollouts) to compare metrics
- Automatically roll back if canary performance degrades

## Common Decisions (ADR Triggers)

- **Load testing tool selection** — k6 vs Locust vs Gatling vs JMeter; standardize across teams to share expertise and scripts
- **Performance test environment strategy** — dedicated always-on environment vs ephemeral spin-up vs testing in production
- **Performance budget thresholds** — what latency, throughput, and error rate constitute a release gate failure
- **Production load testing approach** — traffic replay vs synthetic load vs shadow traffic; risk tolerance for production testing
- **APM tool selection** — Datadog vs New Relic vs Dynatrace vs open source (Jaeger + Grafana); cost vs features tradeoff
- **Performance regression policy** — what percentage regression blocks a release; who has authority to override
- **Soak test frequency and duration** — every release vs weekly vs monthly; 8 hours vs 24 hours vs 72 hours
- **Capacity validation cadence** — quarterly re-validation vs triggered by growth milestones vs continuous
- **Client-side vs server-side performance ownership** — who owns frontend Core Web Vitals vs backend API latency

## Reference Links

- [k6 Documentation](https://grafana.com/docs/k6/latest/) — Load testing tool documentation and scripting guides
- [Locust Documentation](https://docs.locust.io/en/stable/) — Python-based load testing framework
- [Gatling Documentation](https://docs.gatling.io/) — JVM-based load testing with Scala/Java/Kotlin
- [Google Web Vitals](https://web.dev/vitals/) — Core Web Vitals metrics and thresholds
- [Google Lighthouse](https://developer.chrome.com/docs/lighthouse/) — Automated auditing for performance, accessibility, and best practices
- [k6 Operator for Kubernetes](https://grafana.com/docs/k6/latest/set-up/set-up-distributed-k6/usage/executing-with-k6-operator/) — Running distributed k6 tests in Kubernetes
- [Grafana Cloud k6](https://grafana.com/products/cloud/k6/) — Managed cloud load testing service
- [GoReplay](https://goreplay.org/) — Open-source HTTP traffic replay tool
- [Istio Traffic Mirroring](https://istio.io/latest/docs/tasks/traffic-management/mirroring/) — Shadow traffic for production testing
- [Flagger Canary Analysis](https://flagger.app/) — Progressive delivery with automated canary analysis
- [async-profiler](https://github.com/async-profiler/async-profiler) — Low-overhead Java profiler for flame graphs
- [py-spy](https://github.com/benfred/py-spy) — Sampling profiler for Python programs
- [Akamai Performance Research](https://www.akamai.com/resources/research-paper/akamai-online-retail-performance-report) — Impact of latency on conversion rates

## See Also

- `general/testing-strategy.md` — Broader testing strategy including chaos engineering, SLOs, and test environments
- `general/capacity-planning.md` — Capacity modeling, growth projections, and scaling strategies
- `general/observability.md` — Monitoring, alerting, distributed tracing, and APM setup
- `general/deployment.md` — Canary and blue/green deployment strategies with performance validation
- `general/ci-cd.md` — CI/CD pipeline design including quality gates
- `patterns/microservices.md` — Service-level performance testing patterns
- `failures/scaling.md` — Common scaling failure patterns and how performance testing prevents them
