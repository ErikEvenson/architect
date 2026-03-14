# Dev/POC DNS Patterns

## Checklist

- [ ] **[Critical]** Is a real domain with proper DNS configured for any staging or production environment, rather than relying on nip.io or sslip.io?
- [ ] **[Critical]** Are Let's Encrypt rate limits understood before using nip.io/sslip.io domains? (50 certs/week per registered domain, shared across all users of nip.io)
- [ ] **[Critical]** Is the transition path from dev DNS (nip.io) to production DNS (real domain) documented before starting the project?
- [ ] **[Recommended]** Is nip.io or sslip.io used for POC and dev environments to avoid DNS registration overhead?
- [ ] **[Recommended]** Is Traefik ACME configured with HTTP-01 challenge (not DNS-01) when using nip.io/sslip.io domains?
- [ ] **[Recommended]** Are CI/CD ephemeral environments using wildcard nip.io addresses tied to the cluster's external IP?
- [ ] **[Recommended]** Is a fallback plan in place if nip.io/sslip.io becomes unavailable? (service is free, community-run, no SLA)
- [ ] **[Recommended]** Is the local development environment using localhost or 127.0.0.1.nip.io for service access?
- [ ] **[Optional]** Is dnsmasq configured for local development to avoid dependency on external DNS resolution services?
- [ ] **[Optional]** Is a wildcard DNS record (*.dev.example.com) configured on a real domain for team-shared dev environments?
- [ ] **[Optional]** Are /etc/hosts entries documented for environments where TLS is not required?
- [ ] **[Optional]** Is Docker Desktop's host.docker.internal hostname used for container-to-host communication in local dev?
- [ ] **[Optional]** Is sslip.io evaluated as an alternative to nip.io for IPv6 support requirements?

## Why This Matters

Setting up proper DNS for every development environment adds friction and delays. Wildcard DNS services like nip.io and sslip.io eliminate this by resolving any subdomain containing an IP address directly to that IP -- no registration, no configuration, no cost. This lets teams spin up dev and POC environments with valid hostnames (and even TLS certificates) in minutes. However, these services are unsuitable for anything beyond experimentation: they offer no SLA, share rate limits across all users, lack DNSSEC, and are blocked by some corporate firewalls. Teams that skip planning the transition to real DNS often find themselves stuck on dev patterns in staging or production.

## How nip.io and sslip.io Work

Both services use wildcard DNS to resolve any subdomain containing an IP address to that IP:

- **nip.io**: Any subdomain resolves to the embedded IP address. For example, `app.10.0.0.1.nip.io` resolves to `10.0.0.1`. Works with any valid IPv4 address. Free, no registration required.
- **sslip.io**: Same concept as nip.io, alternative provider. Additionally supports IPv6 addresses (e.g., `app.2601-0646.sslip.io` using dashes instead of colons). Also free, no registration.

Both services work by parsing the IP address from the hostname at query time -- there is no database of records to manage.

### Let's Encrypt Integration

Traefik (and other ACME clients) can obtain valid TLS certificates for nip.io/sslip.io domains:

- **HTTP-01 challenge works**: The ACME server resolves the nip.io hostname to the embedded IP, reaches the Traefik instance, and validates the challenge.
- **DNS-01 challenge does NOT work**: You do not control the nip.io/sslip.io DNS zone, so you cannot create the required TXT record.
- **Rate limits are shared**: Let's Encrypt allows 50 certificates per week per registered domain. Since `nip.io` is the registered domain, all users worldwide share this limit. During busy periods, certificate issuance may fail.

### When to Use

- POC and proof-of-concept deployments
- Local and team development environments
- CI/CD ephemeral environments (e.g., per-PR preview deploys)
- Demos and workshops
- Learning and experimentation

### When NOT to Use

- Staging or production environments
- Anything customer-facing
- Anything requiring reliable, guaranteed DNS resolution
- Environments requiring DNSSEC
- Networks where corporate firewalls block wildcard DNS services
- Any environment where Let's Encrypt rate limit exhaustion is unacceptable

### Limitations

- **No DNSSEC**: nip.io and sslip.io do not sign their zones, so responses cannot be validated.
- **Shared rate limits**: Let's Encrypt certificate issuance competes with every other user of the same wildcard DNS service.
- **Third-party dependency**: If nip.io or sslip.io goes down, all DNS resolution stops. There is no SLA.
- **Corporate firewall blocking**: Some enterprise firewalls block or filter nip.io/sslip.io queries.
- **No custom records**: You cannot add TXT, MX, CNAME, or other record types.

## Local Development Patterns

| Approach | TLS | Setup | Use Case |
|----------|-----|-------|----------|
| `localhost` / `127.0.0.1` | Self-signed or none | None | Simplest local dev |
| `127.0.0.1.nip.io` | Let's Encrypt (if port 80 reachable) | None | Local dev with real hostname |
| `/etc/hosts` entries | Self-signed or none | Manual file edit | Multiple local services, no TLS needed |
| `host.docker.internal` | None | Docker Desktop built-in | Container-to-host communication |
| dnsmasq | Self-signed | Install + configure | Local DNS for *.test or custom TLDs |

## Transition Path

```
POC / Dev                    Staging / Production
─────────────────────────    ─────────────────────────
app.10.0.0.1.nip.io     →   app.dev.example.com
                         →   app.staging.example.com
                         →   app.example.com

nip.io (free, no setup)  →   Real domain + Route53/CloudFlare
HTTP-01 Let's Encrypt    →   DNS-01 Let's Encrypt or ACM
Shared rate limits       →   Dedicated rate limits
No SLA                   →   DNS provider SLA
```

Plan the real domain and DNS provider early. The application configuration (ingress rules, certificate issuers, environment variables) will change during this transition.

## Common Decisions (ADR Triggers)

- **nip.io vs sslip.io** -- functionally equivalent; sslip.io adds IPv6 support, nip.io has longer track record
- **Wildcard DNS service vs /etc/hosts** -- convenience and TLS capability vs zero external dependency
- **Wildcard DNS service vs dnsmasq** -- zero setup vs full local DNS control without external dependency
- **Wildcard DNS service vs real domain for dev** -- zero cost and instant setup vs reliability and dedicated rate limits
- **When to transition to real DNS** -- typically at the staging boundary; do not carry nip.io patterns past dev/POC

## Reference Architectures

- [nip.io](https://nip.io/) -- wildcard DNS service documentation and examples
- [sslip.io](https://sslip.io/) -- alternative wildcard DNS with IPv6 support
- [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/) -- understanding certificate issuance limits for shared domains
- [Traefik ACME / Let's Encrypt](https://doc.traefik.io/traefik/https/acme/) -- configuring automatic TLS certificate provisioning with HTTP-01 challenge
- [dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html) -- lightweight local DNS/DHCP server for development environments
