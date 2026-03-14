# Three-Tier Web Application

## Overview

A three-tier architecture separates presentation (web), business logic (application), and data storage into distinct tiers. Each tier can be scaled, secured, and maintained independently.

## Checklist

- [ ] Is the web tier serving static assets separately from dynamic content? (CDN + object storage recommended)
- [ ] Is there a caching layer between the app tier and database? (Redis/Memcached)
- [ ] How are user sessions managed? (stateless app servers + external session store recommended)
- [ ] Is the load balancer configured for health checks on the app tier?
- [ ] Are app servers in private subnets with no direct internet access?
- [ ] Is the database in an isolated subnet accessible only from the app tier?
- [ ] Is there a WAF protecting the web tier? (OWASP top 10 rules)
- [ ] Is TLS terminated at the load balancer or passed through?
- [ ] Is there connection pooling between app tier and database?
- [ ] Is the app tier horizontally scalable? (no local state, shared-nothing)
- [ ] Are database read replicas used to offload read traffic?
- [ ] Is there a content delivery strategy for global users? (CDN, multi-region)
- [ ] How are file uploads handled? (direct to object storage recommended, not through app servers)
- [ ] Is rate limiting configured at the load balancer or WAF?

## Tier Boundaries

```
Internet → CDN/WAF → Load Balancer → App Servers → Cache → Database
                                   → Object Storage (static assets, uploads)
```

### Web/Presentation Tier
- CDN for static assets and edge caching
- WAF for request filtering
- Load balancer for traffic distribution
- TLS termination

### Application Tier
- Stateless app servers in auto-scaling group
- External session store (Redis)
- Secrets retrieved from secrets manager
- Outbound internet via NAT gateway (for external APIs)

### Data Tier
- Primary database with read replicas
- Caching layer for frequently accessed data
- Encrypted at rest and in transit
- Automated backups with point-in-time recovery

## Common Mistakes

- Storing session state on app servers (breaks horizontal scaling)
- Serving static files from app servers (wastes compute, slow)
- Putting app servers in public subnets (security risk)
- Single AZ deployment (no HA)
- No caching layer (unnecessary database load)
- Missing WAF (vulnerable to OWASP top 10)
- No connection pooling (database connection exhaustion under load)

## Security Group Rules

| Source | Destination | Port | Purpose |
|--------|------------|------|---------|
| CDN/Internet | ALB | 443 | HTTPS ingress |
| ALB | App servers | App port | Application traffic |
| App servers | Cache | 6379 | Redis/Memcached |
| App servers | Database | 3306/5432 | Database queries |
| App servers | NAT GW | 443 | Outbound HTTPS |
