# Azure Database

## Checklist

- [ ] **[Critical]** Is the Azure SQL deployment model selected based on workload requirements -- single database (isolated, simple), elastic pool (shared resources across databases), managed instance (SQL Server compatibility), or Hyperscale (up to 128 TB, rapid scale-out)?
- [ ] **[Critical]** Is Cosmos DB configured with the optimal consistency level for the workload -- Strong (linearizable), Bounded Staleness (ordered with lag), Session (default, read-your-writes), Consistent Prefix, or Eventual? (Cosmos DB offers 99.999% SLA for multi-region accounts)
- [ ] **[Critical]** Is the Cosmos DB partition key selected to ensure even data distribution, avoid hot partitions, and align with the most frequent query filter? Are hierarchical partition keys evaluated for multi-tenant or large container workloads (enables sub-partitioning with up to 3 levels for more efficient cross-partition queries)?
- [ ] **[Recommended]** Is Cosmos DB Request Unit (RU) sizing based on measured workload patterns -- provisioned throughput (predictable, manual/autoscale) vs serverless (intermittent, pay-per-request)?
- [ ] **[Recommended]** Is Azure Database for PostgreSQL Flexible Server deployed with appropriate compute tier (Burstable for dev/test, General Purpose for production, Memory Optimized for caching workloads)?
- [ ] **[Recommended]** Is Azure Cache for Redis deployed with the correct tier -- Basic (dev/test, no SLA) vs Standard (replicated, 99.9% SLA) vs Premium (clustering, geo-replication, VNet) vs Enterprise (Redis modules, Active-Active geo)?
- [ ] **[Critical]** Are automated backups configured with appropriate retention -- Azure SQL (7-35 days PITR), Cosmos DB (continuous backup with 7/30-day PITR), PostgreSQL Flexible Server (7-35 days)?
- [ ] **[Critical]** Are private endpoints configured for all database services, disabling public network access for Azure SQL, Cosmos DB, PostgreSQL, Redis, and MySQL?
- [ ] **[Recommended]** Is Azure SQL Transparent Data Encryption (TDE) using customer-managed keys (CMK) in Key Vault for compliance requirements beyond the default service-managed keys?
- [ ] **[Recommended]** Is connection pooling configured appropriately -- Azure SQL with max pool size tuned per application instance, PostgreSQL with PgBouncer (built into Flexible Server), Cosmos DB with direct mode (TCP) for lowest latency?
- [ ] **[Recommended]** Are read replicas or geo-replication configured for read-heavy workloads and disaster recovery -- Azure SQL active geo-replication or auto-failover groups, Cosmos DB multi-region writes, PostgreSQL read replicas?
- [ ] **[Recommended]** Is Azure Database for MySQL Flexible Server evaluated against PostgreSQL Flexible Server for MySQL-dependent applications, with zone-redundant high availability and same-zone or cross-zone read replicas? (Note: Azure Database for MySQL Single Server was retired on September 16, 2024 -- all Single Server instances must be migrated to Flexible Server)
- [ ] **[Recommended]** Are database monitoring and alerting configured -- Azure SQL Intelligent Insights, Cosmos DB metrics (RU consumption, throttled requests, partition hotness), Query Performance Insight for PostgreSQL?
- [ ] **[Optional]** Is Redis clustering enabled for Premium/Enterprise tier with appropriate shard count for workloads exceeding single-node memory or throughput limits?

## Why This Matters

Azure provides purpose-built database services spanning relational (Azure SQL, PostgreSQL, MySQL), NoSQL (Cosmos DB), and caching (Redis). Azure SQL is uniquely positioned with no direct equivalent in AWS -- it offers SQL Server compatibility with cloud-native features like serverless auto-pause, Hyperscale storage disaggregation, and elastic pools. Cosmos DB's five consistency levels are a distinctive differentiator but are frequently misconfigured; Session consistency (the default) is correct for most workloads but Strong consistency is required when absolute linearizability is needed (at 2x RU cost). Partition key selection in Cosmos DB is irreversible and the single most impactful design decision -- a poor choice causes hot partitions and throttling. PostgreSQL Flexible Server with built-in PgBouncer has made third-party connection pooling largely unnecessary for Azure PostgreSQL workloads.

## Common Decisions (ADR Triggers)

- **Azure SQL tier** -- single database (simple isolation) vs elastic pool (cost sharing across 10-100 databases with variable load) vs managed instance (full SQL Server engine, cross-database queries, SQL Agent) vs Hyperscale (128 TB scale, rapid backup/restore)
- **Azure SQL purchasing model** -- DTU-based (bundled compute/IO, simpler) vs vCore-based (independent compute/storage scaling, reserved capacity discounts, Azure Hybrid Benefit for existing SQL Server licenses)
- **Cosmos DB vs Azure SQL** -- globally distributed multi-model NoSQL with tunable consistency vs relational with ACID transactions; cost model (RU-based vs vCore/DTU-based) fundamentally different
- **Cosmos DB provisioned vs serverless vs autoscale** -- predictable throughput (manual RU allocation) vs pay-per-request (max 5,000 RU/s per container) vs autoscale (scales 10-100% of configured max RU/s)
- **Cosmos DB API selection** -- NoSQL (native, recommended), MongoDB (wire-compatible), PostgreSQL (distributed Citus), Cassandra, Gremlin (graph), Table; API cannot be changed after account creation
- **PostgreSQL vs MySQL on Azure** -- PostgreSQL Flexible Server (richer extension ecosystem, advanced query planner, JSONB) vs MySQL Flexible Server (simpler, wider legacy application compatibility)
- **Redis tier and topology** -- Standard (single replica) vs Premium (up to 10 shards, 530 GB, geo-replication) vs Enterprise (Redis modules: RediSearch, RedisJSON, RedisTimeSeries, Active-Active geo for 99.999% SLA)

## Reference Architectures

- [Azure Architecture Center: Choose a data store](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/data-store-overview) -- decision tree for selecting the right Azure database service based on data model, consistency, and scale requirements
- [Azure Architecture Center: Cosmos DB multi-region](https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/globally-distributed-mission-critical-applications-using-cosmos-db) -- reference architecture for globally distributed applications with multi-region writes and automatic failover
- [Azure SQL Hyperscale architecture](https://learn.microsoft.com/en-us/azure/azure-sql/database/service-tier-hyperscale) -- storage disaggregation architecture enabling 128 TB databases with instant backups and rapid scale-out read replicas
- [Azure Well-Architected Framework: Azure SQL](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-sql-database) -- reliability, security, cost optimization, and performance best practices for Azure SQL deployments
- [Azure Architecture Center: Caching guidance](https://learn.microsoft.com/en-us/azure/architecture/best-practices/caching) -- patterns for cache-aside, read-through, and write-behind with Azure Cache for Redis
