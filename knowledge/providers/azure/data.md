# Azure Data Services

## Checklist

- [ ] **[Critical]** Is Azure SQL Database chosen for relational workloads, with the appropriate purchasing model? (vCore for predictable performance, DTU for simpler workloads, Hyperscale for large databases)
- [ ] **[Critical]** Is Azure SQL configured with zone-redundant high availability (available in Premium, Business Critical, and Hyperscale tiers)?
- [ ] **[Critical]** Is auto-failover groups configured for Azure SQL when cross-region disaster recovery is required?
- [ ] **[Critical]** Is Cosmos DB selected for globally distributed, multi-model workloads, with the appropriate consistency level chosen? (strong, bounded staleness, session, consistent prefix, eventual)
- [ ] **[Recommended]** Are Cosmos DB Request Units (RUs) right-sized, with autoscale configured for variable workloads and provisioned throughput for predictable workloads?
- [ ] **[Recommended]** Is Cosmos DB multi-region write enabled only when the application can handle conflict resolution, otherwise using single-write with read replicas?
- [ ] **[Recommended]** Is Azure Cache for Redis deployed in private subnets with the appropriate tier? (Standard for basic caching, Premium for persistence/clustering, Enterprise for RediSearch/RedisBloom)
- [ ] **[Recommended]** Is Azure Cache for Redis zone-redundant (Premium and Enterprise tiers) for production workloads?
- [ ] **[Critical]** Are geo-replication configurations tested for failover and failback procedures with documented RTO/RPO?
- [ ] **[Critical]** Is Transparent Data Encryption (TDE) enabled with customer-managed keys for Azure SQL and Cosmos DB?
- [ ] **[Critical]** Are Private Endpoints configured for all data services to prevent public network access?
- [ ] **[Critical]** Are database connections using managed identity authentication where supported instead of connection strings with passwords?
- [ ] **[Optional]** Is Azure SQL Intelligent Performance (automatic tuning, Query Performance Insight) enabled for self-tuning and diagnostics?
- [ ] **[Recommended]** Are long-term backup retention (LTR) policies configured for compliance, with backups stored in a separate region?

## Why This Matters

Azure data services have unique pricing models (DTU vs vCore, Request Units) that significantly affect cost. Cosmos DB consistency level selection directly impacts performance, availability, and correctness. Azure SQL tiers determine available features like zone redundancy and read scale-out. Misconfigured geo-replication creates false confidence in disaster recovery capability.

## Common Decisions (ADR Triggers)

- **Azure SQL vs Cosmos DB** -- relational with transactions vs globally distributed multi-model
- **Azure SQL purchasing model** -- vCore (resource control) vs DTU (bundled) vs Hyperscale (100TB+, rapid scale)
- **Cosmos DB API selection** -- NoSQL (native) vs PostgreSQL vs MongoDB vs Cassandra vs Gremlin vs Table
- **Cosmos DB consistency level** -- strong (highest latency) vs session (most popular) vs eventual (lowest latency)
- **Caching tier** -- Azure Cache for Redis Standard vs Premium (clustering, persistence) vs Enterprise (Redis modules)
- **Azure SQL Managed Instance vs Azure SQL Database** -- near-100% SQL Server compatibility vs fully managed PaaS
- **Serverless compute** -- Azure SQL Serverless with auto-pause for intermittent workloads vs provisioned for always-on

## Reference Architectures

- [Azure Architecture Center: Data architectures](https://learn.microsoft.com/en-us/azure/architecture/data-guide/) -- comprehensive data architecture guide covering relational, NoSQL, caching, and analytics
- [Azure Architecture Center: Azure SQL Database high availability](https://learn.microsoft.com/en-us/azure/azure-sql/database/high-availability-sla) -- reference architectures for Azure SQL geo-replication and failover groups
- [Azure Architecture Center: Cosmos DB multi-region design](https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/globally-distributed-mission-critical-applications-using-cosmos-db) -- reference architecture for globally distributed applications with Cosmos DB
- [Azure Well-Architected Framework: Azure SQL Database](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-sql-database) -- reliability, security, and cost optimization guidance for Azure SQL
- [Azure Architecture Center: Caching guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching) -- reference patterns for Azure Cache for Redis in application architectures
