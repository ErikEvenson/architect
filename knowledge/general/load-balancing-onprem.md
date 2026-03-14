# On-Premises Load Balancing

## Checklist

- [ ] **[Critical]** Is a VIP failover mechanism (keepalived VRRP or equivalent) deployed so that load balancer failure does not take down all ingress traffic?
- [ ] **[Critical]** Are backend health checks configured with appropriate intervals (2-5s), thresholds (3 failures to mark down), and health check URIs that exercise application dependencies (not just TCP connect)?
- [ ] **[Critical]** Is SSL/TLS termination handled at the load balancer with certificates managed through automated renewal (ACME/Let's Encrypt or internal CA), and are backend connections re-encrypted where compliance requires end-to-end encryption?
- [ ] **[Recommended]** Is the load balancing algorithm appropriate for the workload -- round-robin for stateless, least-connections for variable-duration requests, source-IP hash for basic session affinity?
- [ ] **[Recommended]** Are connection limits and rate limiting configured to prevent a single client or backend from consuming all resources (HAProxy stick tables, NGINX limit_req/limit_conn)?
- [ ] **[Recommended]** Is configuration reload tested to confirm zero-downtime (HAProxy supports seamless reload via `-sf` flag; NGINX supports `reload` signal without dropping connections)?
- [ ] **[Recommended]** Are access control lists (ACLs) configured to route traffic by hostname, path, or header to appropriate backends (multi-tenant or microservice routing)?
- [ ] **[Recommended]** Is logging configured to capture client IP (via X-Forwarded-For or PROXY protocol), response time, backend selected, and HTTP status for troubleshooting and capacity planning?
- [ ] **[Optional]** Is active-active load balancing deployed using DNS round-robin or ECMP to distribute traffic across multiple LB instances, rather than leaving one instance idle in standby?
- [ ] **[Optional]** Are connection draining and graceful shutdown configured so that backend servers removed from rotation complete in-flight requests before being fully detached?
- [ ] **[Optional]** Is caching enabled at the load balancer layer (NGINX proxy_cache or dedicated Varnish tier) for static assets to reduce backend load?
- [ ] **[Optional]** Are WebSocket and long-lived connection timeouts tuned separately from standard HTTP timeouts to prevent premature disconnection?
- [ ] **[Recommended]** Is monitoring in place for LB-specific metrics: active connections, backend response time, health check state changes, connection queue depth, and SSL handshake rate?

## Why This Matters

On-premises environments lack the managed load balancers available in public clouds (AWS ALB/NLB, Azure LB), so teams must build and operate their own ingress tier. A single load balancer without VIP failover becomes the most fragile point in the architecture -- every backend service can be healthy, but if the LB dies, all traffic stops. Poor health check configuration leads to traffic being sent to failed backends, causing intermittent errors that are difficult to diagnose. SSL termination at the LB centralizes certificate management and offloads CPU-intensive TLS handshakes from application servers, but misconfiguration can expose unencrypted traffic on the backend network. Rate limiting at the LB layer is the first line of defense against traffic spikes and abuse, preventing a single misbehaving client from degrading service for all users.

## Common Decisions (ADR Triggers)

- **HAProxy vs NGINX vs F5** -- HAProxy excels at pure L4/L7 load balancing with superior connection handling (millions of concurrent connections), NGINX adds caching and web serving capabilities, F5 BIG-IP provides enterprise features (iRules, GTM for DNS-based GSLB) at significant licensing cost ($50K-$200K+ per appliance pair). HAProxy and NGINX are free/open-source; NGINX Plus adds health checks, session persistence, and support (~$2,500/yr per instance). Decision depends on existing team expertise, feature requirements, and budget.
- **L4 (TCP/UDP) vs L7 (HTTP) load balancing** -- L4 is faster (no protocol parsing), supports any TCP protocol, and preserves client IP naturally, but cannot route by URL path or hostname. L7 enables content-based routing, header manipulation, and HTTP-specific health checks, but adds latency (~0.5-2ms) and requires SSL termination at the LB. Most web workloads benefit from L7; database and non-HTTP services require L4.
- **Active-passive vs active-active** -- Active-passive with keepalived VRRP is simpler: one LB handles all traffic, the standby takes over in 1-3 seconds on failure. Active-active (DNS round-robin or ECMP from upstream routers) uses both LB instances but requires session persistence or stateless backends, and DNS-based failover has TTL-dependent delay (30s-300s). ECMP provides fast failover but requires BGP or OSPF integration.
- **SSL termination point** -- Terminate at LB (simplest, best performance), re-encrypt to backend (compliance requirement for PCI-DSS or HIPAA in some interpretations), or SSL passthrough (LB cannot inspect traffic, no L7 routing). Most environments terminate at LB and use plain HTTP to trusted backend network.
- **Proxy protocol vs X-Forwarded-For** -- PROXY protocol preserves client IP at L4 without modifying HTTP headers (required for non-HTTP protocols), X-Forwarded-For works only for HTTP but is universally supported by applications. Backend applications must be configured to trust and parse whichever method is chosen.
- **Commercial appliance vs software LB** -- F5/Citrix ADC hardware appliances offer dedicated throughput (10-100 Gbps), FIPS-compliant SSL offload, and vendor support, but lock you into proprietary configuration and expensive support contracts. Software LBs (HAProxy, NGINX) run on commodity hardware or VMs, are easily automated with config management, and scale horizontally.

## Comparison Matrix

| Feature | HAProxy (OSS) | NGINX (OSS) | NGINX Plus | F5 BIG-IP LTM |
|---|---|---|---|---|
| L4 Load Balancing | Yes | Yes (stream module) | Yes | Yes |
| L7 Load Balancing | Yes | Yes | Yes | Yes |
| Active Health Checks | Yes | No (passive only) | Yes | Yes |
| SSL Termination | Yes | Yes | Yes | Yes (hardware offload) |
| Caching | No | Yes | Yes | Yes |
| WAF | No | ModSecurity (3rd party) | NGINX App Protect ($) | ASM module ($) |
| Session Persistence | Yes (cookie, source IP) | IP hash only | Yes (cookie, route) | Yes (advanced) |
| Rate Limiting | Yes (stick tables) | Yes (limit_req) | Yes | Yes (iRules) |
| Config Automation | Text config, API (2.x) | Text config | REST API | REST API, iControl |
| Connection Capacity | Millions | Hundreds of thousands | Hundreds of thousands | Millions (hardware) |
| Cost (HA pair) | Free | Free | ~$5,000/yr | $100,000-$400,000+ |
| Operational Complexity | Low | Low | Medium | High |

## HA Patterns

### Active-Passive with keepalived

```
                    VIP: 10.0.1.100
                    ┌──────────┐
          ┌─────────┤ keepalived├──────────┐
          │         │  VRRP    │           │
          ▼         └──────────┘           ▼
   ┌─────────────┐                 ┌─────────────┐
   │  HAProxy 1  │                 │  HAProxy 2  │
   │  MASTER     │                 │  BACKUP     │
   │  Priority 101│                │  Priority 100│
   └──────┬──────┘                 └──────┬──────┘
          │              Backends          │
          └──────┬───────┬───────┬─────────┘
                 ▼       ▼       ▼
              App 1   App 2   App 3
```

- keepalived sends VRRP advertisements every 1s (configurable)
- On MASTER failure, BACKUP assumes VIP within 3x advertisement interval (~3s)
- Health check scripts (`vrrp_script`) can demote MASTER if HAProxy process fails
- Preemption: decide whether original MASTER reclaims VIP on recovery (can cause flapping)

### Active-Active with ECMP

```
          Upstream Router (BGP/OSPF)
          ┌────────────────────────┐
          │  ECMP to both LBs     │
          └───────┬──────┬─────────┘
                  │      │
           ┌──────▼──┐ ┌─▼────────┐
           │ HAProxy 1│ │ HAProxy 2│
           │ BGP peer │ │ BGP peer │
           └────┬─────┘ └────┬─────┘
                │   Backends  │
                └──┬────┬──┬──┘
                   ▼    ▼  ▼
                App 1 App 2 App 3
```

- Both LBs advertise the same VIP via BGP (using ExaBGP or FRRouting)
- Upstream router distributes traffic via equal-cost multipath
- If one LB fails, it withdraws BGP route; convergence in seconds
- Requires stateless backends or shared session state (Redis, database)

## Reference Architectures

- **HAProxy official docs**: [Configuration Manual](https://docs.haproxy.org/) -- comprehensive reference for all directives including stick tables, ACLs, and health checks
- **NGINX Load Balancing Guide**: [HTTP Load Balancing](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/) -- upstream configuration, health checks (Plus), and session persistence
- **F5 BIG-IP Deployment Guides**: [F5 iApp Templates](https://www.f5.com/services/resources/deployment-guides) -- validated configurations for common applications (Exchange, SharePoint, SAP)
- **keepalived documentation**: [keepalived.org](https://www.keepalived.org/manpage.html) -- VRRP configuration, health check scripts, and notification scripts
- **Digital Ocean HAProxy HA tutorial**: Practical walkthrough of keepalived + HAProxy active-passive on Linux -- applicable pattern for any on-prem deployment
- **Red Hat HA Load Balancing**: RHEL documentation covers keepalived + HAProxy integration with SELinux and firewalld considerations
