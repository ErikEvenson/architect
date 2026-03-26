# Cloudflare Security Services

## Scope

Covers Cloudflare WAF (managed and custom rules), Bot Management, Turnstile, Zero Trust Access, Cloudflare Tunnel, Gateway, API Shield, mTLS, Cloudflare Email Security, Browser Isolation, CASB, and DLP. Use alongside `providers/cloudflare/networking.md` for tunnel architecture and `providers/cloudflare/cdn-dns.md` for DDoS and SSL/TLS configuration.

## Checklist

- [ ] [Critical] WAF is enabled with Cloudflare Managed Ruleset and OWASP Core Ruleset; paranoia level is set appropriately (PL1 for most applications, PL2+ introduces false positives that must be tuned)
- [ ] [Recommended] Custom WAF rules are created for application-specific threats: blocking unexpected content types, enforcing required headers, restricting HTTP methods per path
- [ ] [Critical] Rate limiting rules are configured for login endpoints (e.g., 5 requests/10 seconds per IP), password reset, account creation, and any endpoint that triggers expensive operations
- [ ] [Recommended] Bot management is configured: verified bots (Googlebot, etc.) are allowed, automated threats are challenged or blocked based on bot score thresholds (typically score < 30 = bot)
- [ ] [Recommended] Turnstile is deployed on public forms as a CAPTCHA alternative; widget mode (managed, non-interactive, invisible) is chosen based on UX requirements
- [ ] [Critical] Zero Trust Access policies are configured for internal applications: identity provider integration (Okta, Entra ID, Google Workspace), device posture checks, and session duration limits
- [ ] [Critical] Cloudflare Tunnel (cloudflared) replaces VPN for exposing internal services; no public inbound ports required on origin infrastructure
- [ ] [Recommended] Gateway DNS and HTTP policies filter outbound traffic from corporate networks: block malware domains, enforce SaaS tenant restrictions, log DNS queries for threat hunting
- [ ] [Recommended] API Shield is configured for API endpoints: schema validation (upload OpenAPI spec), sequence enforcement, and volumetric abuse detection per endpoint
- [ ] [Optional] mTLS client certificates are deployed for machine-to-machine authentication where applicable; Cloudflare can validate client certs at the edge before requests reach origin
- [ ] [Recommended] Cloudflare Email Security is configured for phishing protection if email flows through or is evaluated by Cloudflare; DMARC management is enabled for domain spoofing prevention
- [ ] [Optional] Browser Isolation is enabled for high-risk web browsing: rendering pages in Cloudflare's cloud and streaming draw commands to the user's browser, preventing data exfiltration and drive-by downloads
- [ ] [Recommended] Security headers are set via Transform Rules or Workers: Content-Security-Policy, X-Frame-Options, Strict-Transport-Security, X-Content-Type-Options

## Why This Matters

Cloudflare processes requests before they reach the origin, making it the first and most scalable line of defense. A WAF misconfiguration (wrong paranoia level, disabled rulesets, or overly broad exceptions) either blocks legitimate traffic or fails to stop attacks. Zero Trust replaces the castle-and-moat VPN model, but misconfigured Access policies can lock out employees or expose internal tools to the internet. Bot management without tuning either blocks search engine crawlers (killing SEO) or lets credential-stuffing bots through. API Shield without schema validation lets malformed requests reach application logic that may not handle them safely. These security layers are interconnected: WAF, bot management, rate limiting, and Access all evaluate the same request, and their interaction determines whether a request is allowed, challenged, or blocked.

## Common Decisions (ADR Triggers)

- **WAF paranoia level**: PL1 catches common attacks with minimal false positives. PL2 adds stricter rules that flag unusual but sometimes legitimate patterns (encoded characters, uncommon headers). PL3/PL4 are for high-security environments that can tolerate significant tuning effort. Document the level and the exception process.
- **Managed Challenge vs JS Challenge vs Block**: Managed Challenge (recommended default) lets Cloudflare choose between a non-interactive check and an interactive puzzle. JS Challenge requires JavaScript execution (blocks simple bots but annoys some users). Block drops the request entirely. The action choice per rule affects both security and user experience.
- **Zero Trust Access vs traditional VPN**: Cloudflare Tunnel + Access replaces VPN with per-application identity-aware access. Eliminates network-level lateral movement. However, it requires every internal application to be individually published and configured with Access policies. Legacy applications that require network-level access may still need a VPN or WARP client with Gateway policies.
- **Turnstile widget mode**: Managed mode auto-selects visible or invisible based on risk. Non-interactive never shows a puzzle but may have higher false-negative rates. Invisible provides no visual widget. Choice depends on whether the form is high-value (login, payment) or low-friction (comments, search).
- **API Shield schema validation enforcement**: Start in log-only mode to identify legitimate traffic that would be blocked, then switch to blocking. Strict enforcement of OpenAPI schemas at the edge prevents malformed input from reaching the application but requires keeping the schema definition in sync with API changes.
- **Browser Isolation scope**: Isolate all browsing (high security, higher latency and cost) vs isolate only risky categories (uncategorized sites, newly registered domains) vs isolate on-demand (user clicks a link flagged as risky). Balance security posture against user experience and per-seat cost.
- **CASB integration scope**: Cloudflare's CASB scans SaaS applications (Google Workspace, Microsoft 365, Slack, GitHub) for misconfigurations and data exposure. Decide which SaaS applications are in scope, what severity findings trigger alerts vs automated remediation, and who owns the response process.

## Reference Architectures

### Public Web Application Security Stack

```
Internet Traffic
  |
  v
Cloudflare Edge
  |
  +-- Layer 3/4 DDoS Mitigation (automatic, unmetered)
  |
  +-- Layer 7 DDoS Rules (adaptive, auto-tuned)
  |
  +-- Bot Management
  |     Score < 2: verified bot (allow)
  |     Score 2-29: likely bot (managed challenge)
  |     Score 30+: likely human (allow)
  |
  +-- WAF (evaluation order matters)
  |     1. Custom Rules (IP allowlists, geo-blocks, header checks)
  |     2. Rate Limiting Rules (per-path thresholds)
  |     3. Cloudflare Managed Ruleset (known CVEs, attack signatures)
  |     4. OWASP Core Ruleset (PL1, anomaly score threshold 60)
  |     5. Cloudflare Leaked Credentials Check
  |
  +-- Transform Rules
  |     Add security headers (CSP, HSTS, X-Frame-Options)
  |     Remove server version headers
  |
  +-- SSL/TLS (Full Strict)
  |
  v
Origin Server
  |-- Validates cf-connecting-ip for logging
  |-- Checks cf-worker header if Workers are in the path
  |-- Firewall allows only Cloudflare IP ranges
```

### Zero Trust Corporate Access

```
Employees / Contractors
  |
  +-- WARP Client installed (device posture: disk encryption, OS version, EDR running)
  |
  v
Cloudflare Gateway
  |-- DNS filtering: block malware, phishing, C2 domains
  |-- HTTP filtering: block file uploads to shadow IT SaaS
  |-- Browser Isolation: enabled for uncategorized + newly registered domains
  |-- DLP: inspect outbound traffic for PII patterns (SSN, credit card)
  |
  v
Cloudflare Access (per-application policies)
  |
  +-- Internal Dashboard (dashboard.internal.example.com)
  |     Policy: require Okta group "engineering" + device posture pass
  |     Tunnel: cloudflared running in Kubernetes (2 replicas)
  |     Target: dashboard-service.internal:8080
  |
  +-- Admin Panel (admin.internal.example.com)
  |     Policy: require Okta group "platform-admins" + hard key MFA
  |     Session duration: 1 hour (re-auth required)
  |     Tunnel: cloudflared on admin-server
  |     Target: localhost:3000
  |
  +-- SSH Access (ssh.example.com)
  |     Policy: require Okta + short-lived SSH certificate
  |     Browser-rendered terminal (no local SSH client needed)
  |     Audit log: full session recording
```

### API Security with Shield and mTLS

```
External API Consumers
  |
  v
Cloudflare Edge
  |
  +-- mTLS Validation
  |     Client presents certificate issued by Cloudflare-managed CA
  |     or customer-uploaded root CA
  |     Requests without valid client cert -> 403
  |
  +-- API Shield
  |     OpenAPI 3.0 spec uploaded
  |     Schema validation: block requests with unknown fields,
  |       wrong types, missing required fields
  |     Sequence enforcement: /login must precede /account
  |     Volumetric detection: per-session, per-endpoint thresholds
  |
  +-- WAF Custom Rules
  |     Enforce Content-Type: application/json
  |     Block requests > 1 MB body
  |     Require X-API-Version header
  |
  +-- Rate Limiting
  |     Per client cert fingerprint:
  |       /api/v1/*: 1000 req/min
  |       /api/v1/export: 10 req/hour
  |
  v
API Origin Servers
  |-- cf-client-cert-* headers contain cert details
  |-- Application-level authz (scopes, roles) still required
```

## Reference Links

- [Cloudflare WAF Documentation](https://developers.cloudflare.com/waf/) -- managed rulesets, custom rules, rate limiting, and OWASP configuration
- [Cloudflare Zero Trust](https://developers.cloudflare.com/cloudflare-one/policies/access/) -- Access policies, identity provider integration, and device posture checks
- [Cloudflare API Shield](https://developers.cloudflare.com/api-shield/) -- schema validation, sequence enforcement, and volumetric abuse detection

## See Also

- `general/security.md` -- general security architecture patterns
- `providers/cloudflare/networking.md` -- Tunnel architecture and ZTNA
- `providers/cloudflare/cdn-dns.md` -- DDoS protection and SSL/TLS
- `providers/cloudflare/workers.md` -- edge security with Workers
