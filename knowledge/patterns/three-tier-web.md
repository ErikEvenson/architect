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

## Cost Benchmarks

> **Disclaimer:** Prices are rough estimates based on AWS us-east-1 pricing as of early 2025. Actual costs vary by region, reserved instance commitments, and usage patterns. Prices change over time — always verify with the provider's pricing calculator.

### Small (100 RPS)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Compute | 2x t3.medium (ALB + ASG) | $60 |
| Database | db.t3.medium RDS PostgreSQL (Multi-AZ) | $130 |
| Cache | cache.t3.micro ElastiCache Redis | $25 |
| CDN | CloudFront (50 GB transfer, 1M requests) | $10 |
| Networking | NAT Gateway (1, 30 GB processed) | $45 |
| Load Balancer | ALB | $25 |
| Monitoring | CloudWatch basic | $15 |
| **Total** | | **~$310/mo** |

### Medium (1,000 RPS)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Compute | 4x m6i.large (ALB + ASG) | $560 |
| Database | db.r6g.large RDS PostgreSQL (Multi-AZ) + 1 read replica | $550 |
| Cache | cache.r6g.large ElastiCache Redis (2-node) | $300 |
| CDN | CloudFront (500 GB transfer, 10M requests) | $60 |
| Networking | NAT Gateway (2 AZs, 200 GB processed) | $100 |
| Load Balancer | ALB | $40 |
| WAF | AWS WAF (managed rules, 10M requests) | $30 |
| Monitoring | CloudWatch + enhanced monitoring | $50 |
| **Total** | | **~$1,690/mo** |

### Large (10,000 RPS)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Compute | 12x m6i.xlarge (ALB + ASG) | $3,360 |
| Database | db.r6g.2xlarge RDS PostgreSQL (Multi-AZ) + 3 read replicas | $3,200 |
| Cache | cache.r6g.xlarge ElastiCache Redis cluster (6-node) | $1,800 |
| CDN | CloudFront (5 TB transfer, 100M requests) | $500 |
| Networking | NAT Gateway (3 AZs, 2 TB processed) | $320 |
| Load Balancer | ALB | $100 |
| WAF | AWS WAF (managed + custom rules, 100M requests) | $250 |
| Monitoring | CloudWatch + X-Ray + dashboards | $200 |
| **Total** | | **~$9,730/mo** |

### Biggest Cost Drivers

1. **Database** — typically 30-40% of total cost at all scales. Multi-AZ doubles the instance cost. Read replicas add linearly.
2. **Compute** — scales linearly with traffic. Right-sizing instances and using reserved instances (1yr/3yr) can save 30-60%.
3. **NAT Gateway** — often a surprise cost. $0.045/GB data processing charge adds up. Use VPC endpoints for AWS service traffic to avoid NAT costs.

### Optimization Tips

- Use **Savings Plans** or **Reserved Instances** for steady-state compute and database (30-60% savings).
- Add **VPC Gateway Endpoints** for S3 and DynamoDB (free, avoids NAT costs).
- Use **CloudFront** aggressively — CDN egress is cheaper than origin egress.
- Consider **Aurora Serverless v2** for variable-traffic databases (pay per ACU).
- Enable **S3 Intelligent-Tiering** for static assets with variable access patterns.
- Right-size cache nodes using **ElastiCache reserved nodes**.

## Security Group Rules

| Source | Destination | Port | Purpose |
|--------|------------|------|---------|
| CDN/Internet | ALB | 443 | HTTPS ingress |
| ALB | App servers | App port | Application traffic |
| App servers | Cache | 6379 | Redis/Memcached |
| App servers | Database | 3306/5432 | Database queries |
| App servers | NAT GW | 443 | Outbound HTTPS |
