# Three-Tier Web Application

## Overview

A three-tier architecture separates presentation (web), business logic (application), and data storage into distinct tiers. Each tier can be scaled, secured, and maintained independently.

## Checklist

- [ ] **[Recommended]** Is the web tier serving static assets separately from dynamic content? (CDN + object storage recommended)
- [ ] **[Recommended]** Is there a caching layer between the app tier and database? (Redis/Memcached)
- [ ] **[Recommended]** How are user sessions managed? (stateless app servers + external session store recommended)
- [ ] **[Critical]** Is the load balancer configured for health checks on the app tier?
- [ ] **[Critical]** Are app servers in private subnets with no direct internet access?
- [ ] **[Critical]** Is the database in an isolated subnet accessible only from the app tier?
- [ ] **[Recommended]** Is there a WAF protecting the web tier? (OWASP top 10 rules)
- [ ] **[Critical]** Is TLS terminated at the load balancer or passed through?
- [ ] **[Recommended]** Is there connection pooling between app tier and database?
- [ ] **[Critical]** Is the app tier horizontally scalable? (no local state, shared-nothing)
- [ ] **[Recommended]** Are database read replicas used to offload read traffic?
- [ ] **[Optional]** Is there a content delivery strategy for global users? (CDN, multi-region)
- [ ] **[Optional]** How are file uploads handled? (direct to object storage recommended, not through app servers)
- [ ] **[Recommended]** Is rate limiting configured at the load balancer or WAF?

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

## Why This Matters

The three-tier architecture is the most common web application pattern because it provides clear separation of concerns, independent scaling per tier, and well-understood security boundaries. Storing session state on app servers breaks horizontal scaling. Serving static files from app servers wastes compute. Putting app servers in public subnets creates unnecessary attack surface. Single AZ deployment eliminates high availability. Missing WAF leaves the application vulnerable to OWASP top 10 attacks. No connection pooling leads to database connection exhaustion under load.

## Common Decisions (ADR Triggers)

- **CDN and static asset strategy** — CDN provider, cache invalidation approach, origin failover
- **Session management** — external session store (Redis) vs sticky sessions vs stateless JWTs
- **Caching layer** — Redis vs Memcached, cache-aside vs write-through, eviction policy
- **Database read replica strategy** — when to add replicas, routing logic, consistency trade-offs
- **WAF rule management** — managed rules vs custom rules, false positive handling
- **TLS termination** — at load balancer vs passthrough to app servers, certificate management
- **Auto-scaling configuration** — scaling metric, thresholds, cooldown, minimum/maximum instances
- **File upload handling** — direct-to-S3 with presigned URLs vs through app servers

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

### Azure Estimates

> **Disclaimer:** Azure prices are approximate, based on East US region pricing as of early 2025. Actual costs vary by region, commitment tier, and usage patterns. Always verify with the Azure Pricing Calculator.

#### Small (100 RPS)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Compute | 2x B2s VMs (VMSS) | $60 |
| Database | Azure SQL S2 (50 DTUs, zone-redundant) | $150 |
| Cache | Azure Cache for Redis C0 (Basic) | $20 |
| CDN | Azure Front Door (50 GB transfer, 1M requests) | $40 |
| Networking | NAT Gateway (1, 30 GB processed) | $40 |
| Load Balancer | Application Gateway v2 | $25 |
| Monitoring | Azure Monitor basic | $15 |
| **Total** | | **~$350/mo** |

#### Medium (1,000 RPS)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Compute | 4x D2s_v5 VMs (VMSS) | $560 |
| Database | Azure SQL P2 (250 DTUs, zone-redundant) + 1 read replica | $600 |
| Cache | Azure Cache for Redis C2 (Standard, 2-node) | $320 |
| CDN | Azure Front Door (500 GB transfer, 10M requests) | $100 |
| Networking | NAT Gateway (2 AZs, 200 GB processed) | $90 |
| Load Balancer | Application Gateway v2 (WAF tier) | $55 |
| WAF | Azure WAF on Front Door (10M requests) | $35 |
| Monitoring | Azure Monitor + Application Insights | $60 |
| **Total** | | **~$1,820/mo** |

#### Large (10,000 RPS)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Compute | 12x D4s_v5 VMs (VMSS) | $3,400 |
| Database | Azure SQL Hyperscale (8 vCores, zone-redundant) + 3 read replicas | $3,500 |
| Cache | Azure Cache for Redis P2 (Premium, clustered 6-node) | $1,900 |
| CDN | Azure Front Door Premium (5 TB transfer, 100M requests) | $600 |
| Networking | NAT Gateway (3 AZs, 2 TB processed) | $300 |
| Load Balancer | Application Gateway v2 (WAF tier) | $120 |
| WAF | Azure WAF on Front Door (custom + managed rules) | $280 |
| Monitoring | Azure Monitor + Application Insights + Log Analytics | $250 |
| **Total** | | **~$10,350/mo** |

### GCP Estimates

> **Disclaimer:** GCP prices are approximate, based on us-central1 region pricing as of early 2025. Actual costs vary by region, commitment tier, and usage patterns. Always verify with the GCP Pricing Calculator.

#### Small (100 RPS)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Compute | 2x e2-medium (MIG + HTTP LB) | $50 |
| Database | Cloud SQL PostgreSQL db-custom-2-4096 (HA) | $120 |
| Cache | Memorystore Redis Basic 1 GB | $35 |
| CDN | Cloud CDN (50 GB transfer, 1M requests) | $8 |
| Networking | Cloud NAT (1, 30 GB processed) | $35 |
| Load Balancer | External HTTP(S) LB | $20 |
| Monitoring | Cloud Monitoring basic | $10 |
| **Total** | | **~$278/mo** |

#### Medium (1,000 RPS)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Compute | 4x n2-standard-2 (MIG + HTTP LB) | $490 |
| Database | Cloud SQL PostgreSQL db-custom-4-16384 (HA) + 1 read replica | $520 |
| Cache | Memorystore Redis Standard 5 GB (2-node) | $280 |
| CDN | Cloud CDN (500 GB transfer, 10M requests) | $50 |
| Networking | Cloud NAT (2 regions, 200 GB processed) | $80 |
| Load Balancer | External HTTP(S) LB | $25 |
| Cloud Armor | Cloud Armor WAF (10M requests) | $30 |
| Monitoring | Cloud Monitoring + Cloud Trace | $45 |
| **Total** | | **~$1,520/mo** |

#### Large (10,000 RPS)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Compute | 12x n2-standard-4 (MIG + HTTP LB) | $2,950 |
| Database | AlloyDB (8 vCPUs, HA) + 3 read pool nodes | $3,100 |
| Cache | Memorystore Redis Standard 25 GB (6-node cluster) | $1,650 |
| CDN | Cloud CDN (5 TB transfer, 100M requests) | $400 |
| Networking | Cloud NAT (3 regions, 2 TB processed) | $280 |
| Load Balancer | External HTTP(S) LB | $80 |
| Cloud Armor | Cloud Armor WAF (managed + custom rules) | $220 |
| Monitoring | Cloud Monitoring + Cloud Trace + Cloud Logging | $180 |
| **Total** | | **~$8,860/mo** |

### Provider Comparison

> **Disclaimer:** All prices are approximate monthly estimates as of early 2025. Actual costs vary significantly based on region, commitment discounts, negotiated contracts, and usage patterns. Always verify with each provider's pricing calculator.

| Scale | AWS | Azure | GCP |
|-------|-----|-------|-----|
| Small (100 RPS) | ~$310/mo | ~$350/mo | ~$278/mo |
| Medium (1,000 RPS) | ~$1,690/mo | ~$1,820/mo | ~$1,520/mo |
| Large (10,000 RPS) | ~$9,730/mo | ~$10,350/mo | ~$8,860/mo |

**Notes:**
- GCP tends to be slightly cheaper for compute due to sustained-use discounts applied automatically.
- Azure Front Door bundles WAF + CDN + load balancing, which can simplify architecture but may cost more than a la carte AWS components.
- All three providers offer significant discounts (30-60%) for 1-year or 3-year commitments on compute and database.

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
