# Testing Strategy

## Scope

This file covers **cloud-native testing practices** including load testing, chaos engineering, synthetic monitoring, and test environment management. For deployment strategies (blue/green, canary), see `general/deployment.md`. For observability and alerting, see `general/observability.md`.

## Checklist

- [ ] **[Recommended]** What load testing tool is used? (k6, Locust, Gatling, JMeter — pick one and standardize)
- [ ] **[Critical]** Are performance baselines established for critical user journeys? (p50, p95, p99 latency targets)
- [ ] **[Recommended]** Is load testing integrated into CI/CD or run on a schedule?
- [ ] **[Critical]** Are SLIs defined and measured? (latency, error rate, throughput, saturation)
- [ ] **[Critical]** Are SLOs set with error budgets? (e.g., 99.9% availability = 43.8 min/month downtime budget)
- [ ] **[Recommended]** Is synthetic monitoring configured for critical paths? (Datadog Synthetics, CloudWatch Synthetics, Grafana Synthetic Monitoring)
- [ ] **[Recommended]** Is chaos engineering practiced? (Chaos Monkey, Litmus, Gremlin, AWS FIS — start small)
- [ ] **[Optional]** Are game days scheduled regularly? (quarterly recommended, involve oncall teams)
- [ ] **[Recommended]** Is canary analysis automated? (compare canary metrics against baseline before full rollout)
- [ ] **[Recommended]** How are integration tests run against cloud services? (localstack, testcontainers, ephemeral environments)
- [ ] **[Recommended]** Is there a test environment strategy? (ephemeral per-PR, shared staging, production-like load test env)
- [ ] **[Recommended]** Are failure injection tests run before major releases? (network partitions, dependency failures, resource exhaustion)
- [ ] **[Optional]** Is there a contract testing strategy for service-to-service APIs? (Pact, schema validation)

## Why This Matters

Production incidents are overwhelmingly caused by scenarios that were never tested. Load testing prevents capacity surprises during traffic spikes. Chaos engineering finds weaknesses before customers do. Without synthetic monitoring, you learn about outages from users instead of dashboards. SLOs without validation are fiction — testing proves they hold under real conditions.

Teams that skip testing strategy accumulate **confidence debt**: they believe the system works but have no evidence. This debt compounds and eventually results in extended outages during the worst possible moment (peak traffic, product launch, holiday season).

## Load Testing Tools Comparison

| Tool | Language | Protocol Support | Cloud-Native | Best For |
|------|----------|-----------------|--------------|----------|
| **k6** | JavaScript (ES6) | HTTP, gRPC, WebSocket | Grafana Cloud k6 | Developer-friendly scripting, CI/CD integration |
| **Locust** | Python | HTTP (extensible) | Distributed mode | Python teams, custom load shapes |
| **Gatling** | Scala/Java/Kotlin | HTTP, JMS, MQTT | Gatling Enterprise | JVM shops, complex scenarios |
| **JMeter** | Java (GUI + CLI) | HTTP, JDBC, LDAP, FTP | Distributed mode | Legacy teams, protocol variety |

### Recommendation

k6 is the default recommendation for cloud-native teams: it scripts in JavaScript, integrates with CI/CD natively, produces Prometheus-compatible metrics, and has low resource overhead. Use JMeter only if you need protocol support k6 lacks (JDBC, LDAP).

## Chaos Engineering Tools

| Tool | Type | Provider | Best For |
|------|------|----------|----------|
| **AWS FIS** | Managed service | AWS | AWS-native chaos (EC2, ECS, EKS, RDS) |
| **Litmus** | Open source | Any (Kubernetes) | K8s-native chaos experiments, CRD-based |
| **Gremlin** | SaaS | Any | Enterprise chaos with safety controls, GameDay platform |
| **Chaos Monkey** | Open source | Any | Random instance termination (Netflix origin) |

### Chaos Engineering Maturity Path

1. **Level 0 — Manual:** Kill a pod manually, observe what happens
2. **Level 1 — Scripted:** Automated failure injection in staging, manual observation
3. **Level 2 — Scheduled:** Regular chaos runs in staging with automated rollback
4. **Level 3 — Production:** Controlled chaos in production with blast radius limits
5. **Level 4 — Continuous:** Chaos experiments in CI/CD pipeline, automatic SLO validation

### Starting Chaos Engineering Safely

- Start in **staging**, not production
- Begin with **known failure modes** (instance termination, dependency timeout)
- Set **blast radius limits** (affect 1 AZ, 5% of traffic, single service)
- Have **rollback procedures** ready before every experiment
- Run during **business hours** with the team watching
- Document **steady state hypothesis** before each experiment

## Synthetic Monitoring

Synthetic monitors execute scripted transactions against your application on a schedule, detecting issues before users report them.

| Service | Provider | Features |
|---------|----------|----------|
| **Datadog Synthetics** | Datadog | API tests, browser tests, multi-step, private locations |
| **CloudWatch Synthetics** | AWS | Canary scripts (Node.js/Python), VPC access, screenshots |
| **Grafana Synthetic Monitoring** | Grafana Cloud | Distributed probes, k6-based scripting |
| **Checkly** | Independent | Playwright-based, monitoring-as-code, CI/CD integration |

### What to Monitor Synthetically

- **Login flow** — authentication is the front door
- **Core transaction** — the primary action customers pay for
- **Payment flow** — revenue-impacting paths
- **API health endpoints** — backend availability
- **Third-party integrations** — external dependency availability

## SLI/SLO Validation

### Defining SLIs

| SLI Type | Measurement | Example |
|----------|-------------|---------|
| **Availability** | Successful requests / total requests | 99.95% of HTTP requests return non-5xx |
| **Latency** | Request duration at percentile | p99 latency < 500ms |
| **Throughput** | Requests per second sustained | System handles 10,000 RPS |
| **Correctness** | Correct results / total results | 99.99% of calculations are accurate |

### SLO Error Budget Math

- **99.9% SLO** = 43.8 minutes downtime/month = 8.76 hours/year
- **99.95% SLO** = 21.9 minutes downtime/month = 4.38 hours/year
- **99.99% SLO** = 4.38 minutes downtime/month = 52.6 minutes/year

**Validate SLOs through testing:** Run load tests at expected peak traffic and measure whether SLIs hold. If p99 latency exceeds the SLO at 2x normal traffic, the SLO is aspirational, not achievable.

## Test Environment Strategy

| Environment | Purpose | Lifecycle | Data |
|-------------|---------|-----------|------|
| **Local/Dev** | Unit tests, component tests | Permanent per developer | Mocked/synthetic |
| **Ephemeral (per-PR)** | Integration tests, smoke tests | Created on PR, destroyed on merge | Synthetic seed data |
| **Staging** | Full integration, load tests, chaos | Permanent, production-like | Anonymized production data |
| **Load Test** | Performance validation | Spun up for test runs | Production-scale synthetic |
| **Production** | Canary analysis, synthetic monitoring | Permanent | Real data |

### Key Principles

- **Ephemeral environments** reduce cost and prevent "shared staging" bottlenecks
- **Production-like** means same instance types, same network topology, same configurations — not necessarily same scale
- **Data parity** is critical — tests against empty databases prove nothing
- **Infrastructure-as-code** makes ephemeral environments possible; without it, environment creation is too slow

## Game Day Planning

A game day is a structured exercise where teams practice responding to simulated incidents.

### Game Day Checklist

1. Define the scenario (e.g., "primary database fails over to replica")
2. Set objectives (e.g., "team detects issue within 5 minutes, restores service within 15")
3. Brief participants — oncall team, incident commander, observers
4. Execute the failure injection
5. Observe team response — do not intervene unless safety is at risk
6. Debrief — what worked, what broke, what needs improvement
7. Create action items with owners and deadlines

### Game Day Frequency

- **Quarterly** for critical systems
- **After major architecture changes** (new database, new region, new provider)
- **Before peak traffic events** (product launches, holiday season)

## Common Decisions (ADR Triggers)

- **Load testing tool selection** — k6 vs Locust vs Gatling; standardize across teams
- **Chaos engineering adoption** — which tool, where to start, production vs staging only
- **SLO definitions** — what percentiles, what error budget, who owns the budget
- **Test environment model** — ephemeral per-PR vs shared staging vs both
- **Synthetic monitoring scope** — which user journeys to cover, check frequency
- **Game day program** — frequency, scope, mandatory vs voluntary participation
- **Performance baseline process** — how often to re-baseline, what triggers re-evaluation

## See Also

- `general/deployment.md` — Canary and blue/green deployment strategies
- `general/observability.md` — Monitoring, alerting, and distributed tracing
- `general/capacity-planning.md` — Capacity modeling and scaling
- `general/disaster-recovery.md` — DR testing and failover validation
- `patterns/microservices.md` — Service-level testing patterns
