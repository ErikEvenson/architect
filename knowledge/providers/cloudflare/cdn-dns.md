# Cloudflare CDN, DNS, and Network Services

## Checklist

- [ ] DNS zone is active on Cloudflare with correct NS records at the registrar
- [ ] Proxy mode (orange cloud) is enabled for records that should receive CDN/security benefits; grey cloud for records that must expose origin IP (e.g., MX, direct SSH)
- [ ] SSL/TLS mode is set to **Full (Strict)** with a valid origin certificate; never use Flexible in production (creates unencrypted origin connection)
- [ ] Origin certificates issued via Cloudflare Origin CA are installed on the origin server (15-year lifetime, free, only trusted by Cloudflare edge)
- [ ] Always Use HTTPS and Automatic HTTPS Rewrites are enabled to eliminate mixed content
- [ ] Cache rules are configured per path: static assets with long TTLs, API routes set to bypass cache, HTML with short TTLs or bypass
- [ ] Browser TTL vs Edge TTL are set independently; Edge TTL controls how long Cloudflare caches, Browser TTL controls the Cache-Control header sent to clients
- [ ] Tiered Cache is enabled (free) to reduce origin requests by routing cache misses through upper-tier data centers before hitting origin
- [ ] Argo Smart Routing is evaluated for latency-sensitive applications (paid, typically 30% faster via optimized network paths)
- [ ] DDoS protection rules are reviewed: L3/L4 protection is automatic and unmetered; L7 HTTP DDoS rules can be tuned with sensitivity and action overrides
- [ ] Rate limiting rules are defined for authentication endpoints, API routes, and form submissions with appropriate thresholds and response codes
- [ ] Load balancing is configured with health checks (HTTP/HTTPS/TCP), appropriate steering policy (random, hash, geo, least-outstanding-requests, least-connections), and failover pools
- [ ] DNS CAA records are configured to authorize only Cloudflare (and any other required CAs) to issue certificates for the domain

## Why This Matters

Cloudflare sits in the request path for every user interaction. A misconfigured SSL mode (Flexible instead of Full Strict) silently creates an unencrypted hop between Cloudflare and the origin, defeating TLS guarantees. Incorrect proxy mode leaks origin server IPs, bypassing DDoS protection entirely. Cache rules that are too aggressive serve stale authenticated content; rules that are too conservative waste origin capacity. DNS propagation issues during migration can cause hours of downtime. These are day-one configuration decisions that are painful to fix after traffic is flowing.

## Common Decisions (ADR Triggers)

- **SSL/TLS mode selection**: Full (Strict) requires a valid origin cert but is the only truly secure option. Full trusts any cert including self-signed. Flexible should never be used but exists for origins that cannot serve HTTPS at all. Document the choice and the origin certificate strategy.
- **Orange cloud vs grey cloud per record**: Proxied records get CDN, WAF, and DDoS protection but cannot expose arbitrary TCP/UDP ports (without Spectrum). MX records, SRV records, and direct-access hosts must be grey-clouded. This decision affects the security boundary.
- **Cache strategy (cache everything vs default)**: Default behavior only caches static file extensions. "Cache Everything" page rules cache HTML but require careful cache key and TTL design to avoid serving authenticated content to anonymous users. Decide per path prefix.
- **Argo Smart Routing adoption**: Paid per-GB feature. Worth it for latency-sensitive global applications with origins in a single region. Less valuable when origins are already globally distributed. Measure baseline latency first.
- **Load balancer steering policy**: Random is simplest; geo-steering routes users to nearest pool but requires pools in multiple regions; least-outstanding-requests is best for heterogeneous pool members. Choice depends on origin topology.
- **Tiered Cache topology**: Smart Tiered Cache (automatic) vs custom topology. Custom is only available on Enterprise and useful when you need to control which upper-tier PoPs are used for compliance or latency reasons.
- **Cloudflare Spectrum for non-HTTP**: If the architecture requires protecting TCP/UDP services (game servers, SSH, RDP, MQTT) behind Cloudflare, Spectrum is required. This is an Enterprise feature for arbitrary protocols; Pro/Biz get limited port support.

## Reference Architectures

### Global Web Application with Regional Origins

```
Users (worldwide)
  |
  v
Cloudflare Edge (300+ PoPs)
  |-- DNS: proxied A/AAAA records
  |-- SSL: Full (Strict) with Origin CA certs
  |-- Cache: static assets (immutable, 1yr TTL)
  |         HTML (bypass or 60s TTL with cache tags)
  |         API (bypass cache)
  |-- Tiered Cache: enabled (Smart topology)
  |
  v
Cloudflare Load Balancer
  |-- Steering: geo (US users -> US pool, EU -> EU pool)
  |-- Health checks: HTTPS GET /healthz, 30s interval
  |-- Failover: cross-region (US fails -> EU absorbs)
  |
  +---> US Origin Pool (us-east-1)
  +---> EU Origin Pool (eu-west-1)
```

### API-First Architecture

```
API Clients
  |
  v
Cloudflare Edge
  |-- DNS: api.example.com (proxied)
  |-- SSL: Full (Strict)
  |-- Cache: bypass for all paths (or short TTL for GET-only read endpoints)
  |-- Rate limiting: 100 req/min per API key (custom rule on header)
  |-- DDoS: L7 HTTP rules with low sensitivity for API patterns
  |
  v
Origin API Servers
  |-- Cloudflare validates origin cert (Origin CA or public CA)
  |-- cf-connecting-ip header used for real client IP logging
  |-- cf-ray header used for request tracing
```

### Multi-Domain CDN with Shared Origin

```
Cloudflare Zone: example.com
  |-- www.example.com -> proxied CNAME -> origin-lb.example.com
  |-- static.example.com -> proxied CNAME -> origin-lb.example.com
  |     Cache: aggressive, Cache-Tag purging via API
  |-- api.example.com -> proxied A record -> API origin IP
  |     Cache: bypass

Cloudflare Zone: example.co.uk
  |-- Same origin, different cache/WAF rules
  |-- Geo-specific page rules for compliance

Origin (single cluster):
  |-- Routes based on Host header
  |-- Origin CA cert covers both domains (SAN)
```
