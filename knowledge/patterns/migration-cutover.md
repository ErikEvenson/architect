# Migration Cutover Runbook Pattern

## Scope

Covers the execution mechanics of production cutover events, including DNS-based traffic switching, rollback procedures, validation checklists, and communication timelines. Applicable to any migration where production traffic must be redirected from a source environment to a target environment.

## Checklist

- [ ] **[Critical]** Reduce DNS TTL to 300 seconds (or lower) at least 24-48 hours before cutover window
- [ ] **[Critical]** Document and test rollback procedure end-to-end, including data sync-back if target receives writes
- [ ] **[Critical]** Verify all services deployed, configured, and passing health checks on target environment
- [ ] **[Critical]** Confirm data migration is complete and validated (row counts, checksums, sample queries all pass)
- [ ] **[Critical]** Define explicit rollback decision criteria: what metrics/failures trigger a rollback, who makes the call
- [ ] **[Recommended]** Set up war room communications: dedicated Slack channel, Zoom bridge, on-call rotation contacts
- [ ] **[Recommended]** Notify stakeholders at T-1 week, T-1 day, T-1 hour, and at cutover start/completion
- [ ] **[Recommended]** Run end-to-end functional tests on target (login, CRUD operations, key business workflows) before switching DNS
- [ ] **[Recommended]** Confirm monitoring is active on both source and target: metrics, logs, alerting, external synthetics
- [ ] **[Recommended]** Pre-stage rollback DNS records so reverting is a single API call or click, not a manual edit
- [ ] **[Recommended]** Schedule cutover during lowest-traffic period with realistic window duration plus 50% buffer
- [ ] **[Optional]** Set up external monitoring (Pingdom, Datadog Synthetics, UptimeRobot) to confirm availability from outside
- [ ] **[Optional]** Prepare customer-facing communication (status page update, email template) for cutover notification
- [ ] **[Optional]** Establish a change freeze on source environment 24-48 hours before cutover to prevent drift
- [ ] **[Optional]** Plan decommission timeline: keep source environment running for 1-2 weeks post-cutover as safety net

## Why This Matters

The cutover window is the highest-risk moment in any migration. Everything before it is reversible preparation; everything after it is production reality. A botched cutover results in downtime, data loss, or — worst case — a split-brain situation where both source and target receive writes with no clear reconciliation path.

The most common cutover failures are preventable: DNS TTL not reduced in advance (users cached the old IP for hours), no tested rollback plan (the team discovers rollback is broken mid-crisis), incomplete validation (the service appears up but critical functionality is broken), and cutover during peak hours (maximizing blast radius when something goes wrong).

A well-practiced cutover with a clear runbook, pre-staged rollback, and defined success/failure criteria converts a high-stress event into a methodical procedure. Teams that rehearse their cutover in staging catch 80% of the issues that would have hit them in production.

## Common Decisions (ADR Triggers)

### ADR: Cutover Strategy Selection
**Context:** Need to switch production traffic from source environment to target environment.
**Options:**
- **Big bang cutover** — All traffic switches at once during a maintenance window. Source goes read-only, final data sync runs, DNS updates, validation, done. Simplest but requires downtime.
- **Blue-green with DNS** — Target environment runs in parallel. DNS switch moves all traffic. Rollback is DNS revert. Near-zero downtime but requires full parallel infrastructure cost.
- **Canary / weighted routing** — Gradually shift traffic percentage (10%, 25%, 50%, 100%) using weighted DNS (Route 53, Cloudflare load balancing) or L7 load balancer. Lowest risk but most complex. Requires both environments to share data layer or accept data partitioning during rollout.
- **Per-service rolling cutover** — Migrate services one at a time rather than all at once. Each service cutover is a smaller risk event. Requires services to work across environments during transition (cross-environment API calls, shared databases).

**Decision criteria:** For small environments (< 10 services), big bang with a maintenance window is simplest and most predictable. For large environments or zero-downtime requirements, blue-green with DNS is the standard approach. Canary routing is appropriate when the target environment's performance characteristics are unknown and gradual validation is needed. Per-service rolling cutover works when services are loosely coupled and can operate independently across environments.

### ADR: Rollback Window and Data Reconciliation
**Context:** After cutover, how long is rollback feasible, and what happens to data written to the target during the cutover window?
**Options:**
- **Short rollback window (< 1 hour)** — If target receives no writes (read-only validation period before enabling writes), rollback is clean DNS revert. Simplest but delays full cutover.
- **Medium rollback window (1-24 hours)** — Target receives writes. Rollback requires reverse data sync (target → source). Must plan for this: continuous replication back to source, or accept data loss for the rollback window.
- **No rollback** — Commit fully. Fix forward only. Appropriate when rollback complexity exceeds fix-forward risk (e.g., schema changes that are not backward compatible).

**Decision criteria:** Always plan for rollback unless the team has explicitly decided fix-forward is the strategy. Define the maximum rollback window: once it passes, the team commits to the target. Common trigger: after 24-72 hours of stable operation on target, rollback path is decommissioned.

### ADR: DNS Provider and Propagation Strategy
**Context:** DNS is the traffic routing mechanism for cutover. Provider capabilities affect cutover speed and rollback options.
**Options:**
- **Cloudflare** — Proxied records update near-instantly (Cloudflare edge re-routes). Unproxied records respect TTL. API-driven updates via `curl` or Terraform.
- **AWS Route 53** — TTL-based propagation. Weighted routing policies enable canary. Health check integration for automatic failover. API/CLI updates via `aws route53 change-resource-record-sets`.
- **Self-hosted (Designate, BIND)** — Full control but slower propagation if downstream resolvers cache aggressively. No global anycast network.

**Decision criteria:** If already using Cloudflare with proxied records, leverage instant propagation for fastest cutover. If using Route 53, reduce TTL well in advance and plan for propagation delay. For self-hosted DNS, consider temporarily delegating the cutover zone to a cloud DNS provider for the migration event.

## Reference Architectures

### Standard Blue-Green Cutover with DNS

```
T-48h: Reduce DNS TTL
  DNS: app.example.com → source-lb (TTL 300s, was 3600s)

T-24h: Final data sync + validation
  Source DB ──(pg_dump/DMS sync)──> Target DB
  Source S3 ──(rclone sync)──> Target Object Storage
  Validate: row counts, checksums, functional tests on target

T-0: Cutover window opens
  1. Source → read-only (or maintenance mode)
  2. Final incremental sync (capture last writes)
  3. Validate final sync
  4. Update DNS: app.example.com → target-lb
  5. Verify DNS propagation:
     dig +short app.example.com @8.8.8.8
     dig +short app.example.com @1.1.1.1
     nslookup app.example.com (from multiple locations)
  6. Wait for TTL expiry (300s)
  7. Confirm traffic flowing to target (access logs, metrics)
  8. Run validation checklist (see below)
  9. Enable writes on target
  10. Announce cutover complete

T+0 to T+1h: Active monitoring
  Watch: error rates, latency, throughput, logs
  Rollback trigger: error rate > 5%, latency > 2x baseline, critical functionality broken

T+24h: First stability milestone
T+72h: Second stability milestone — consider decommission planning
T+2w: Decommission source (after final backup)
```

### Rollback Procedure

```
ROLLBACK DECISION
  Trigger: [define criteria — error rate, latency, data integrity failure]
  Decision maker: [name/role]
  Time limit: rollback must be initiated within [X] minutes of trigger

ROLLBACK STEPS
  1. DNS revert: app.example.com → source-lb
     (pre-staged record — single API call)
     Route 53: aws route53 change-resource-record-sets --hosted-zone-id Z... \
       --change-batch file://rollback-dns.json
     Cloudflare: curl -X PATCH api.cloudflare.com/client/v4/zones/.../dns_records/...

  2. Wait for DNS propagation (TTL 300s = 5 min worst case)

  3. Re-enable writes on source (if source was set to read-only)

  4. If target received writes during cutover:
     a. Identify writes made to target (audit log, timestamp range)
     b. Export delta from target
     c. Apply delta to source (manual review required)
     d. OR: accept data loss for rollback window (document this risk in advance)

  5. Verify traffic flowing to source
  6. Post-rollback: investigate root cause, plan retry
```

### Validation Checklist Template

```
POST-CUTOVER VALIDATION

Infrastructure:
  [ ] All target VMs/containers running and healthy
  [ ] Load balancer health checks passing (all backends green)
  [ ] SSL/TLS certificates valid and serving correctly
  [ ] Network connectivity between all service tiers confirmed

Application:
  [ ] Login/authentication working (test with real credentials)
  [ ] CRUD operations functional (create, read, update, delete test records)
  [ ] Key business workflows complete end-to-end
  [ ] API endpoints responding with correct status codes
  [ ] Background jobs/workers processing (check queue depths)
  [ ] Scheduled tasks/cron jobs registered and firing

Data:
  [ ] Database connections established from all application instances
  [ ] Read queries returning expected data
  [ ] Write queries persisting correctly
  [ ] Cache warm-up complete (or acceptable cold-cache performance)

Monitoring:
  [ ] Metrics flowing to monitoring system (Prometheus, CloudWatch, Datadog)
  [ ] Logs aggregating correctly (Loki, ELK, CloudWatch Logs)
  [ ] Alerts configured and test alert fires successfully
  [ ] External synthetic checks passing (Pingdom, Datadog Synthetics)

Performance:
  [ ] Response time within acceptable range (compare to source baseline)
  [ ] Throughput at expected levels
  [ ] Error rate below threshold (< 0.1% for healthy service)
  [ ] No resource exhaustion (CPU, memory, disk, connections)
```

### Communication Timeline Template

```
T-1 week:  Email to stakeholders — "Migration scheduled for [date], [time]-[time]"
           Include: what's changing, expected impact, who to contact

T-1 day:   Reminder to stakeholders — "Migration tomorrow, [time]"
           Include: maintenance window duration, status page URL

T-1 hour:  War room opens — team assembles
           Slack channel: #migration-cutover-[date]
           Zoom bridge: [link]
           On-call: [primary], [secondary], [escalation]

T-0:       Status page update — "Scheduled maintenance in progress"
           Slack announcement — "Cutover starting now"

T+done:    Status page update — "Maintenance complete, all systems operational"
           Slack/email — "Cutover complete. Monitoring for stability."

T+24h:     Stakeholder update — "24h post-cutover: all systems stable"
           OR: "Issues identified and resolved: [summary]"
```

### Common Cutover Mistakes and Mitigations

| Mistake | Consequence | Mitigation |
|---------|-------------|------------|
| DNS TTL not reduced in advance | Users hit old IP for hours after switch | Reduce TTL to 300s at T-48h minimum |
| No tested rollback plan | Panic during failed cutover, extended outage | Rehearse rollback in staging, pre-stage DNS records |
| Incomplete validation | Service appears up but critical paths broken | Scripted validation checklist, test real workflows |
| Cutover during peak hours | Maximum user impact if something fails | Schedule during lowest-traffic window |
| Not monitoring both environments | Cannot compare source vs target behavior | Dashboards for both, side-by-side during cutover |
| Forgetting source read-only | Split-brain: writes go to both source and target | Explicit step to disable writes on source before DNS switch |
| No change freeze before cutover | Last-minute source changes create drift | Freeze source changes 24-48h before cutover |
| Single person cutover | No backup if primary operator makes error or is unavailable | Minimum 2 people, defined roles (operator + validator) |

## See Also

- `general/disaster-recovery.md` — DR planning including rollback and failback strategies
- `patterns/datacenter-relocation.md` — Full datacenter relocation where cutover is one phase of a larger program
- `general/hybrid-dns.md` — DNS management across environments relevant to DNS-based cutover
- `general/database-migration.md` — Database migration and data synchronization for cutover events
