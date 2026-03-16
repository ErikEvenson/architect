# SaaS Multi-Tenant Architecture

## Overview

Multi-tenant SaaS architectures serve multiple customers (tenants) from shared infrastructure. The central challenge is balancing **isolation** (security, performance, compliance) against **efficiency** (cost, operational simplicity). Every architectural decision must consider the tenant dimension.

## Checklist

- [ ] **[Critical]** What is the tenant isolation model? (silo, pool, or bridge — decision depends on compliance, cost, and customer requirements)
- [ ] **[Critical]** How is per-tenant data isolated? (database-per-tenant, schema-per-tenant, row-level security, or hybrid)
- [ ] **[Critical]** Is noisy neighbor prevention implemented? (rate limiting, resource quotas, throttling per tenant)
- [ ] **[Critical]** How is tenant-aware routing handled? (subdomain, header, JWT claim, path prefix)
- [ ] **[Recommended]** Is tenant onboarding automated? (provisioning, configuration, data seeding, DNS)
- [ ] **[Critical]** How is billing and metering implemented? (usage tracking, plan enforcement, overage handling)
- [ ] **[Recommended]** Are SLA tiers supported? (different isolation, performance, or availability per pricing tier)
- [ ] **[Recommended]** Is data residency configurable per tenant? (regional deployment, data sovereignty compliance)
- [ ] **[Critical]** How is tenant admin separated from platform admin? (RBAC scoping, tenant-scoped operations)
- [ ] **[Recommended]** Is tenant-level monitoring and logging in place? (metrics per tenant, cost attribution)
- [ ] **[Recommended]** How are tenant-specific customizations handled? (feature flags, configuration, not code branches)
- [ ] **[Critical]** Is cross-tenant data leakage prevented at every layer? (API, database, cache, logs, error messages)
- [ ] **[Recommended]** Is tenant offboarding and data deletion automated? (GDPR right to erasure, data retention policies)

## Why This Matters

Multi-tenancy failures are catastrophic: a data leak between tenants is a company-ending event. A noisy neighbor incident degrades service for all customers simultaneously. Without proper metering, pricing cannot cover costs. Without automated onboarding, growth requires linear operations staff.

The isolation model is the most consequential architectural decision in SaaS — it affects every layer of the stack and is extremely expensive to change after launch. Getting this wrong means either over-spending on infrastructure (full silo for all tenants) or under-delivering on security (full pool without adequate isolation controls).

## Tenant Isolation Models

### Silo Model (Separate Infrastructure Per Tenant)

```
Tenant A                    Tenant B
┌─────────────────┐        ┌─────────────────┐
│  Load Balancer   │        │  Load Balancer   │
│  App Servers     │        │  App Servers     │
│  Database        │        │  Database        │
│  Cache           │        │  Cache           │
│  (Own VPC/VNet)  │        │  (Own VPC/VNet)  │
└─────────────────┘        └─────────────────┘
```

**Pros:** Strongest isolation, simplest compliance story, per-tenant scaling, per-tenant customization
**Cons:** Highest cost, operational complexity scales linearly, onboarding is slow without automation
**Best for:** Regulated industries (healthcare, finance), enterprise customers demanding dedicated infrastructure, tenants with vastly different scale requirements

### Pool Model (Shared Infrastructure, Logical Isolation)

```
Shared Infrastructure
┌──────────────────────────────────┐
│  Load Balancer                    │
│  App Servers (tenant context      │
│    in every request)              │
│  Shared Database (RLS or          │
│    schema-per-tenant)             │
│  Shared Cache (tenant-prefixed    │
│    keys)                          │
│  (Single VPC/VNet)                │
└──────────────────────────────────┘
    ▲           ▲           ▲
 Tenant A    Tenant B    Tenant C
```

**Pros:** Lowest cost per tenant, simplest operations, fastest onboarding, best resource utilization
**Cons:** Noisy neighbor risk, compliance complexity, blast radius affects all tenants, harder per-tenant customization
**Best for:** High-volume SaaS with many small tenants, B2C or SMB-focused products, self-serve onboarding

### Bridge Model (Hybrid)

```
Shared Control Plane
┌──────────────────────────────────┐
│  Routing / API Gateway            │
│  Authentication / Tenant Registry │
│  Billing / Metering               │
│  Admin Console                    │
└──────────┬───────────────────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
 Pool Tier     Silo Tier
┌──────────┐  ┌──────────┐
│ Shared    │  │ Dedicated │
│ compute + │  │ compute + │
│ shared DB │  │ own DB    │
│           │  │           │
│ Free/SMB  │  │ Enterprise│
│ tenants   │  │ tenants   │
└──────────┘  └──────────┘
```

**Pros:** Cost-efficient for small tenants, premium offering for enterprise, matches pricing tiers to isolation
**Cons:** Two operational models to maintain, complex routing logic, harder to test
**Best for:** SaaS products spanning SMB to enterprise, products with tiered pricing

## Data Isolation Strategies

| Strategy | Isolation Level | Cost | Complexity | Compliance |
|----------|----------------|------|------------|------------|
| **Database-per-tenant** | Highest | Highest | Medium (connection management) | Easiest to audit |
| **Schema-per-tenant** | High | Medium | Medium (migration coordination) | Good — clear boundaries |
| **Row-level security (RLS)** | Medium | Lowest | High (must be bulletproof) | Requires careful audit |
| **Hybrid** (RLS for pool, DB-per for silo) | Variable | Optimized | Highest | Matches tier requirements |

### Database-Per-Tenant

- Each tenant gets an isolated database instance or cluster
- Connection routing maps `tenant_id` → database endpoint
- Schema migrations must run across all tenant databases (automation critical)
- Consider **connection pooling** — 1,000 tenants × 10 connections = 10,000 connections to manage
- Provider options: RDS per tenant, Aurora with separate clusters, Azure SQL per DB

### Schema-Per-Tenant

- Single database server, separate schema (namespace) per tenant
- Cheaper than database-per-tenant, stronger isolation than RLS
- Schema migration runs per-schema (can be parallelized)
- Works well in PostgreSQL (`SET search_path`), SQL Server (schemas), MySQL (databases as schemas)
- Risk: Operational limit on number of schemas per server (typically hundreds, not thousands)

### Row-Level Security (RLS)

- Single database, single schema, `tenant_id` column on every table
- Database enforces row filtering via RLS policies (PostgreSQL RLS, SQL Server RLS)
- **Application-level filtering is not sufficient** — one missed WHERE clause leaks data
- Always use database-native RLS, not just application ORM filters
- Test extensively: direct SQL access, reporting queries, bulk operations, joins

```sql
-- PostgreSQL RLS example
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
    USING (tenant_id = current_setting('app.current_tenant')::uuid);
```

## Noisy Neighbor Prevention

| Layer | Technique | Implementation |
|-------|-----------|---------------|
| **API** | Per-tenant rate limiting | API Gateway throttling per API key/tenant ID |
| **Compute** | Resource quotas | K8s ResourceQuotas per namespace, container limits |
| **Database** | Connection limits per tenant | PgBouncer per-pool limits, max_connections per schema |
| **Cache** | Key-space quotas | Eviction policies, memory limits per tenant prefix |
| **Storage** | Quota enforcement | S3 bucket policies, Azure Blob quotas per container |
| **Queue** | Per-tenant queue or rate limiting | Separate queues per tenant, or message rate caps |

### Rate Limiting Strategy

```
Tier 1 (Free):       100 requests/minute,   1,000/hour,    10,000/day
Tier 2 (Pro):      1,000 requests/minute,  10,000/hour,   100,000/day
Tier 3 (Enterprise): Custom, negotiated per contract
```

## Tenant-Aware Routing

| Method | Pattern | Pros | Cons |
|--------|---------|------|------|
| **Subdomain** | `tenant-a.app.com` | Clean separation, easy SSL with wildcard | DNS management, wildcard certs |
| **Path prefix** | `app.com/tenant-a/...` | Simple routing, single domain | Pollutes URL namespace |
| **Header** | `X-Tenant-ID: tenant-a` | Clean URLs, flexible | Requires client cooperation |
| **JWT claim** | `{"tenant_id": "tenant-a"}` | Secure, no URL/header manipulation | Requires auth on every request |

**Recommendation:** Use **subdomain** for customer-facing access and **JWT claim** for API access. The tenant context should be established once at the edge (API gateway) and propagated through all internal services.

## Tenant Onboarding Automation

### Onboarding Steps (Automate All)

1. **Create tenant record** in tenant registry (ID, name, plan, region)
2. **Provision data store** (create database/schema/RLS policy)
3. **Configure DNS** (subdomain routing if applicable)
4. **Seed initial data** (default settings, sample data, admin user)
5. **Set quotas and limits** based on plan tier
6. **Enable monitoring** (tenant-scoped dashboards, alerts)
7. **Send welcome communications** (admin credentials, getting started guide)

### Target: Self-serve onboarding in under 60 seconds for pool-tier tenants.

## Billing and Metering

### Metering Architecture

```
Application → Usage Events → Event Stream → Metering Service → Billing System
                (Kafka/SQS)                  (aggregate,          (Stripe,
                                              deduplicate,         custom)
                                              rate)
```

### Common Metering Dimensions

| Dimension | Examples |
|-----------|----------|
| **API calls** | Requests per month, by endpoint |
| **Data storage** | GB stored, GB transferred |
| **Compute** | Execution time, vCPU-seconds |
| **Users** | Active users, seats provisioned |
| **Features** | Premium feature usage counts |

### Billing Models

- **Flat-rate:** Fixed price per tier per month (simple, predictable)
- **Usage-based:** Pay per unit consumed (fair, but unpredictable for customers)
- **Hybrid:** Base fee + usage overage (most common in practice)
- **Per-seat:** Price per user (common for B2B, easy to understand)

## Data Residency Per Tenant

For tenants with data sovereignty requirements (GDPR, data localization laws):

- **Regional deployments** — Deploy application stack in multiple regions
- **Tenant-to-region mapping** — Route tenant traffic to the region where their data resides
- **Cross-region replication** — Only for operational data, never replicate tenant data to non-approved regions
- **Regional database isolation** — Tenant data stays in-region; global metadata can be centralized

## Tenant Admin vs Platform Admin

| Capability | Tenant Admin | Platform Admin |
|------------|-------------|----------------|
| User management | Own tenant users only | All users, all tenants |
| Configuration | Own tenant settings | Global settings, tenant overrides |
| Data access | Own tenant data only | Cross-tenant (with audit logging) |
| Billing | View own invoices, update payment | Set pricing, view all billing |
| Support | Submit tickets | Manage all tickets, impersonate tenants |

**Critical rule:** Platform admin cross-tenant access must be audited, time-limited, and require justification (break-glass access pattern).

## SLA Tiers

| Tier | Availability | Support | Isolation | Customization |
|------|-------------|---------|-----------|---------------|
| **Free** | Best effort | Community/docs | Pool (shared everything) | None |
| **Pro** | 99.9% | Email, 24h response | Pool with guaranteed quotas | Feature flags |
| **Business** | 99.95% | Priority, 4h response | Bridge (dedicated compute) | Configuration |
| **Enterprise** | 99.99% | Dedicated CSM, 1h response | Silo (dedicated everything) | Custom integrations |

## Common Decisions (ADR Triggers)

- **Isolation model** — silo vs pool vs bridge; the foundational decision
- **Data isolation strategy** — database-per-tenant vs schema-per-tenant vs RLS
- **Routing mechanism** — subdomain vs path vs header vs JWT
- **Billing model** — flat-rate vs usage-based vs hybrid vs per-seat
- **Noisy neighbor strategy** — rate limiting approach, quota enforcement
- **Data residency** — single region vs multi-region, tenant-to-region mapping
- **Onboarding model** — self-serve vs sales-assisted vs white-glove
- **Customization approach** — feature flags vs configuration vs custom code (avoid custom code)
- **SLA tier mapping** — which tiers to offer, what isolation level per tier

## See Also

- `general/security.md` — Security controls applicable to multi-tenant systems
- `general/data.md` — Data architecture and storage patterns
- `general/identity.md` — Authentication and authorization (tenant-scoped RBAC)
- `general/api-design.md` — API design including tenant context propagation
- `patterns/microservices.md` — Service decomposition with tenant awareness
