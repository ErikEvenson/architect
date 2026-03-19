# CDN-Fronted On-Premises Architecture

## Scope

Covers placing a CDN (Cloudflare, Akamai, Fastly, Azure Front Door) in front of on-premises origin servers to provide global caching, DDoS protection, and WAF capabilities. Applicable when on-premises infrastructure serves external users and needs edge acceleration or security hardening without migrating to the cloud.

## Checklist

- [ ] **[Critical]** Is the CDN origin configured with the correct on-prem public IP or hostname, and is the origin reachable over a stable internet circuit with sufficient bandwidth for peak origin-pull traffic?
- [ ] **[Critical]** Is TLS between the CDN edge and the on-prem origin configured in "Full (Strict)" mode, using a publicly trusted certificate or CDN-issued origin certificate on the origin server?
- [ ] **[Critical]** Is the origin firewall restricted to only allow inbound traffic from the CDN provider's published IP ranges, blocking all other direct-to-origin access to prevent bypassing CDN WAF and DDoS protections?
- [ ] **[Critical]** Is the WAF at the CDN edge enabled with OWASP Core Rule Set (CRS), bot protection, and rate limiting rules appropriate for the application's traffic patterns?
- [ ] **[Recommended]** Are cache rules configured to serve static assets (images, CSS, JS, fonts) from CDN edge with long TTLs (1h-1y), while dynamic content (API responses, HTML) either bypasses cache or uses short TTLs with proper Cache-Control headers?
- [ ] **[Recommended]** Is DNS configured with a CNAME to the CDN endpoint (e.g., `example.cdn.cloudflare.net`), and is the origin's real IP address not exposed in DNS history, certificate transparency logs, or email headers?
- [ ] **[Recommended]** Is CDN origin failover configured so that if the primary on-prem site is unreachable, traffic fails over to a DR site or maintenance page with appropriate health check intervals (30-60s)?
- [ ] **[Recommended]** Are CDN health checks configured to probe a dedicated health endpoint on the origin (not just TCP connect) that validates application dependencies (database, cache, etc.)?
- [ ] **[Recommended]** Is cache purge integrated into the deployment pipeline so that stale static assets are invalidated when new versions are deployed? (Cloudflare: Purge API or dashboard, free for all plans; Fastly: instant purge via API <150ms propagation; Akamai: Fast Purge API; Azure Front Door: purge via API or portal — for high-frequency deployments, consider versioned asset URLs like `app.v2.js` instead of purge-based invalidation to avoid purge costs and propagation delays)
- [ ] **[Optional]** Are custom page rules or edge functions (Cloudflare Workers, Fastly VCL, Akamai EdgeWorkers) configured for URL rewrites, redirects, or header manipulation to offload logic from the origin?
- [ ] **[Optional]** Is real user monitoring (RUM) or CDN analytics enabled to track cache hit ratios, origin response times, and edge-to-origin bandwidth for capacity planning?
- [ ] **[Optional]** Are origin request headers configured to pass the real client IP (CF-Connecting-IP, X-Forwarded-For, True-Client-IP) and the application is configured to trust and log this header?
- [ ] **[Recommended]** Is bandwidth budgeting in place for origin-pull traffic, accounting for cache miss ratio (typically 5-20% for static-heavy sites, 50-80% for dynamic/API) multiplied by total traffic volume?

## Why This Matters

On-prem infrastructure lacks the global edge presence and built-in DDoS protection of cloud-native services. Fronting on-prem with a CDN bridges this gap: it provides global caching (reducing origin bandwidth and latency for end users by 50-80%), enterprise-grade DDoS mitigation (absorbing volumetric attacks that would saturate on-prem internet circuits), and WAF capabilities without deploying and managing on-prem WAF appliances. However, misconfiguration can negate these benefits entirely. If the origin's real IP is exposed, attackers can bypass the CDN and hit the origin directly. If TLS between CDN and origin is set to "Flexible" instead of "Full Strict," the connection between CDN and origin is unencrypted, creating a false sense of security. If cache rules are too aggressive, users see stale content; if too conservative, the CDN provides no performance benefit and all traffic hits the origin. Origin failover through CDN is often simpler and faster than DNS-based failover because CDN health checks can trigger failover in 30-60 seconds versus DNS TTL propagation delays.

## Common Decisions (ADR Triggers)

- **CDN provider selection** -- Cloudflare (generous free tier, integrated WAF/DDoS, Workers for edge compute, ~$20/mo Pro, ~$200/mo Business, Enterprise custom), Akamai (largest edge network, complex configuration, enterprise pricing $5K-$50K+/mo), Fastly (real-time purge <150ms, VCL-based customization, $50/mo minimum + bandwidth), Azure Front Door (integrates with Azure services, good for hybrid cloud, ~$35/mo base + per-request). Decision depends on budget, required edge locations, configurability needs, and existing vendor relationships.
- **Cache strategy for dynamic content** -- No cache (simplest, highest origin load), short TTL with stale-while-revalidate (reduces origin load while keeping content fresh within seconds), edge-side includes (ESI) for mixing cached and dynamic fragments (complex, supported by Akamai and Fastly). API responses are typically not cached unless they are read-heavy and tolerance for staleness exists.
- **Origin certificate strategy** -- Use CDN-issued origin certificates (Cloudflare Origin CA, valid 15 years, only trusted by CDN edge -- provides strong binding), publicly trusted certificates from Let's Encrypt or commercial CA (works if you need to test origin directly), or mutual TLS (mTLS) between CDN and origin for highest security (CDN presents client cert, origin validates it).
- **WAF rule strictness** -- Paranoia Level 1 (low false positives, catches obvious attacks) vs Level 2-3 (more rules, more false positives, requires tuning). Start at PL1, monitor for 2-4 weeks in log-only mode, then enforce. Custom rules for application-specific patterns (e.g., block SQL keywords in specific parameters).
- **Single CDN vs multi-CDN** -- Single CDN is simpler and cheaper; multi-CDN (using DNS-based traffic management like NS1 or Citrix ITM) provides resilience against CDN outages and optimizes performance by routing users to the fastest CDN. Multi-CDN adds significant operational complexity and is typically only justified at very high traffic volumes (>10 Gbps sustained).
- **Origin shielding** -- Enabling an intermediate CDN cache tier (shield POP) between edge and origin reduces origin load by consolidating cache misses through a single node. Reduces origin connections but adds ~5-20ms latency on cache misses. Worth enabling for origins with limited bandwidth or connection capacity.

## Architecture Diagram

```
  Users (Global)
       │
       ▼
  ┌──────────────────────────────────┐
  │         CDN Edge Network          │
  │  ┌─────────┐  ┌──────────────┐   │
  │  │  Cache   │  │  WAF / DDoS  │   │
  │  │  (Static)│  │  Protection  │   │
  │  └────┬─────┘  └──────┬───────┘   │
  │       │    Cache Miss  │           │
  │       └───────┬────────┘           │
  │               ▼                    │
  │     ┌─────────────────┐            │
  │     │  Origin Shield  │ (optional) │
  │     │  (single POP)   │            │
  │     └────────┬────────┘            │
  └──────────────┼─────────────────────┘
                 │ TLS (Full Strict)
                 │ CDN IPs only (firewall)
                 ▼
  ┌──────────────────────────────────┐
  │     On-Prem Origin (Primary)      │
  │  ┌──────────┐  ┌──────────────┐  │
  │  │   Load    │  │  App Servers │  │
  │  │  Balancer │──│  (backend)   │  │
  │  └──────────┘  └──────────────┘  │
  └──────────────────────────────────┘
                 │ (failover)
  ┌──────────────────────────────────┐
  │      DR Site (Secondary)          │
  │  (CDN origin failover target)     │
  └──────────────────────────────────┘
```

## CDN-to-Origin Security Hardening

1. **Firewall allowlisting**: Download CDN provider IP ranges (Cloudflare publishes at `https://www.cloudflare.com/ips/`, Akamai via SiteShield API, Fastly via API) and update firewall rules. Automate updates as CDN IPs change quarterly.
2. **Authenticated origin pulls (mTLS)**: CDN presents a client certificate when connecting to origin; origin's load balancer validates the cert. Prevents any non-CDN traffic even if the IP allowlist is stale.
3. **Origin header validation**: Set a custom secret header at the CDN edge (e.g., `X-Origin-Auth: <secret>`), validate it at the origin load balancer, reject requests without it.
4. **Hide origin IP**: Ensure the origin IP is not in public DNS records (use separate IPs for mail, SSH, etc.), not in historical DNS databases (SecurityTrails, Censys), and not in TLS certificate transparency logs (use CDN-issued origin certs).

## Reference Architectures

- **Cloudflare with on-prem origin**: [Cloudflare Origin Configuration](https://developers.cloudflare.com/fundamentals/setup/) -- SSL modes, origin certificates, firewall rules, and page rules for cache control
- **Akamai Property Manager**: [Akamai Developer Docs](https://techdocs.akamai.com/property-mgr/docs) -- origin configuration, caching behaviors, SiteShield for IP allowlisting
- **Fastly with on-prem**: [Fastly Origin Configuration](https://docs.fastly.com/en/guides/working-with-hosts) -- VCL-based cache logic, health checks, shielding, and origin failover
- **Azure Front Door with on-prem**: [AFD with custom origins](https://learn.microsoft.com/en-us/azure/frontdoor/) -- origin groups, health probes, WAF policies, and Private Link for Azure-connected origins
- **OWASP ModSecurity CRS**: [Core Rule Set](https://coreruleset.org/) -- standard WAF rule set used by CDN WAFs and on-prem WAF deployments
- **Cloudflare IP ranges**: `https://www.cloudflare.com/ips/` -- must be integrated into firewall automation

## See Also

- `general/tls-certificates.md` — TLS certificate management including origin certificates
- `general/networking.md` — Network architecture and DNS management
- `patterns/hybrid-cloud.md` — Hybrid cloud patterns when on-prem is combined with cloud services
- `general/security.md` — Security controls including WAF and DDoS protection
