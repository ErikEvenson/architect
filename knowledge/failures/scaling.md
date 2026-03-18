# Scaling Failure Patterns

## Scope

Covers common scaling failure patterns including missing auto-scaling, slow scaling response, thundering herd effects, cold start latency, resource quota exhaustion, AZ imbalance, and database bottlenecks. Does not cover general capacity planning (see `general/capacity-planning.md`) or compute architecture design (see `general/compute.md`).

## Checklist

- [ ] **[Critical]** **No auto-scaling configured for compute tier** — Goes wrong: traffic increases and the fixed number of instances becomes overwhelmed, response times spike, and the application returns errors or becomes unresponsive. Happens because: auto-scaling is deferred as a "later" optimization, or the team manually scales and nobody is available at 2 AM. Prevent by: configuring auto-scaling from day one with appropriate metrics (CPU, request count, queue depth), minimum/maximum instance counts, and testing scaling behavior under load.

- [ ] **[Critical]** **Auto-scaling too slow to respond to traffic spikes** — Goes wrong: a flash sale, viral event, or marketing campaign drives a sudden traffic spike, but new instances take 5-10 minutes to launch and warm up, causing degraded service during the spike. Happens because: scaling policies use long cooldown periods, instances have slow startup times (large AMIs, heavy initialization), or scaling is reactive to CPU rather than predictive. Prevent by: using target tracking scaling with short response times, pre-warming instances with scheduled scaling for known events, reducing instance startup time (smaller images, faster health checks), and considering serverless for spiky workloads.

- [ ] **[Recommended]** **Thundering herd on service recovery or cache rebuild** — Goes wrong: when a service or cache recovers from an outage, all waiting clients retry simultaneously, overwhelming the recovering service and causing it to fail again in a repeated crash-recover cycle. Happens because: clients have no backoff strategy, or retry logic uses fixed intervals without jitter. Prevent by: implementing exponential backoff with jitter in all clients, using circuit breakers to limit concurrent retries, rate-limiting recovery paths, and gradually ramping traffic back to recovered services.

- [ ] **[Recommended]** **Cold start latency in serverless or container platforms** — Goes wrong: users experience multi-second response times when functions or containers are scaling from zero or spinning up new instances, leading to timeouts and poor user experience. Happens because: cold starts are an inherent characteristic of serverless/container platforms, and the application does heavy initialization (database connections, model loading, dependency injection). Prevent by: using provisioned concurrency or minimum instance counts for latency-sensitive paths, optimizing initialization code, keeping deployment packages small, and routing latency-sensitive requests away from cold paths.

- [ ] **[Critical]** **Hitting account or service resource limits** — Goes wrong: deployments fail, auto-scaling stops working, or new resources cannot be created because account-level quotas (EC2 instance limits, EIP limits, Lambda concurrency, API Gateway throttling) are exhausted. Happens because: default service quotas are low and nobody requests increases proactively. Prevent by: auditing service quotas against projected capacity needs, requesting limit increases before they are needed, monitoring quota utilization, and including quota checks in capacity planning reviews.

- [ ] **[Critical]** **AZ imbalance causing uneven load distribution** — Goes wrong: one AZ has significantly more instances than others, so when that AZ fails, the remaining AZs lack capacity to absorb the traffic, and auto-scaling cannot launch new instances fast enough. Happens because: instance launches favor one AZ due to capacity constraints, or scaling policies do not enforce even distribution. Prevent by: configuring auto-scaling groups to balance across AZs, using multiple instance types for better availability, and testing that the system survives losing the largest AZ.

- [ ] **[Recommended]** **No capacity reservations for critical workloads** — Goes wrong: during a large-scale event (AWS re:Invent, Black Friday, regional incident), on-demand instance launches fail with InsufficientInstanceCapacity errors because the AZ is out of the requested instance type. Happens because: capacity reservations cost money even when idle, so teams avoid them. Prevent by: using capacity reservations or savings plans for baseline capacity, diversifying instance types and AZs, and pre-scaling for known high-traffic events.

- [ ] **[Critical]** **Database becomes the scaling bottleneck** — Goes wrong: the application tier scales horizontally to handle load, but all instances funnel requests to a single database that cannot scale, causing connection exhaustion, query queuing, and eventual outage. Happens because: application scaling is planned without considering downstream dependencies. Prevent by: right-sizing the database for peak load, using read replicas to distribute read traffic, implementing caching layers, considering database sharding for write-heavy workloads, and load testing the full stack (not just the application tier).

- [ ] **[Recommended]** **Queue backlog growing faster than consumers can process** — Goes wrong: a sustained traffic increase causes message queues to grow unboundedly, processing latency increases from seconds to hours, and eventually the queue storage fills or messages expire before processing. Happens because: consumer auto-scaling is not configured, or consumers hit a downstream bottleneck. Prevent by: auto-scaling consumers based on queue depth, setting up alerts on queue age and backlog size, implementing dead-letter queues for failed messages, and back-pressuring producers when consumers cannot keep up.

- [ ] **[Recommended]** **Scaling without considering downstream rate limits** — Goes wrong: the application scales up and increases request volume to a third-party API, payment processor, or internal service that has a rate limit, causing all requests beyond the limit to fail. Happens because: scaling plans focus on the application's own resources without mapping downstream dependency limits. Prevent by: documenting rate limits for all dependencies, implementing client-side rate limiting and request queuing, using bulkhead patterns to isolate dependency failures, and negotiating higher limits before scaling events.

- [ ] **[Recommended]** **Memory leaks causing gradual instance degradation** — Goes wrong: instances slowly consume more memory over hours or days until they OOM-kill, and if all instances degrade on similar timelines, the entire fleet becomes unhealthy simultaneously. Happens because: memory leaks are not caught in short-duration tests, and instances are long-lived without recycling. Prevent by: monitoring per-instance memory trends, setting up OOM alerts, recycling instances periodically (immutable deployments help), and running extended load tests to surface leaks before production.

- [ ] **[Critical]** **Stateful services preventing horizontal scaling** — Goes wrong: an application stores session data, uploaded files, or computation state in local memory or disk, so new instances cannot serve existing users, and the application cannot scale horizontally. Happens because: local state is the simplest implementation and works fine at small scale. Prevent by: externalizing state to a shared store (Redis, S3, database), using sticky sessions only as a temporary measure, and designing services to be stateless from the start.

- [ ] **[Critical]** **No load testing before major traffic events** — Goes wrong: the team assumes the architecture will handle projected traffic, but untested bottlenecks (connection limits, serialization overhead, slow endpoints) cause failures at a fraction of the expected load. Happens because: load testing is time-consuming and environments are expensive, so it is skipped or done at unrealistic scale. Prevent by: running load tests at 2x projected peak against a production-like environment, identifying and fixing bottlenecks iteratively, and making load testing a standard part of the release process for major changes.

- [ ] **[Recommended]** **Auto-scaling group using a single instance type** — Goes wrong: when the specified instance type is unavailable in an AZ (capacity constraints), auto-scaling cannot launch new instances, and the group gets stuck below desired capacity. Happens because: only one instance type is configured for simplicity. Prevent by: configuring mixed instance types with similar specs, using attribute-based instance type selection, and testing that the application runs correctly on all configured instance types.

## Why This Matters

Scaling failures often manifest at the worst possible time: during peak traffic events when revenue impact is highest. An application that works perfectly at normal load can collapse in minutes under a traffic spike if auto-scaling is misconfigured, cold starts are not mitigated, or downstream bottlenecks are not accounted for. These failures are preventable with deliberate design and regular load testing, but they are invisible until the moment they cause an outage.

## Common Decisions (ADR Triggers)

- **Auto-scaling strategy** — reactive (CPU-based) vs predictive vs scheduled, cooldown tuning
- **Instance type diversity** — single type vs mixed instances, spot vs on-demand mix
- **Capacity reservation approach** — reserved capacity vs on-demand with diverse types
- **Stateless architecture enforcement** — externalized state store selection, session management
- **Database scaling strategy** — vertical vs read replicas vs sharding, caching layer selection
- **Load testing cadence** — continuous in CI vs pre-release vs annual, tooling selection

## See Also

- `general/compute.md` — Compute architecture and auto-scaling design
- `general/capacity-planning.md` — Capacity planning and resource sizing
- `failures/data.md` — Data failure patterns including database as scaling bottleneck
- `general/container-orchestration.md` — Container orchestration scaling patterns
