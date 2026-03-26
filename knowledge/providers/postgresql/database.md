# PostgreSQL

## Scope

This file covers **PostgreSQL** architecture decisions: version selection, streaming and logical replication, HA solutions (Patroni, repmgr), connection pooling (PgBouncer, Pgpool-II), vacuum tuning and autovacuum configuration, memory tuning (shared_buffers, work_mem, effective_cache_size, maintenance_work_mem), pgvector for AI/ML vector search, extensions ecosystem, migration from Oracle and SQL Server, and managed service options (Amazon RDS/Aurora PostgreSQL, Google Cloud SQL/AlloyDB, Azure Database for PostgreSQL). For general database strategy (engine selection, replication patterns, encryption), see `general/data.md`. For migration methodology and cutover planning, see `general/database-migration.md`.

## Checklist

- [ ] **[Critical]** Select a supported PostgreSQL major version with a clear upgrade strategy (each major version is supported for 5 years; new major versions require pg_upgrade or logical replication migration; plan upgrades at least annually to stay within the support window — running an unsupported version means no security patches, which is a compliance risk for regulated environments)
- [ ] **[Critical]** Design HA topology using a proven clustering solution (Patroni with etcd/ZooKeeper/Consul for automatic leader election and failover; repmgr for simpler environments with fewer automation requirements; ensure the consensus store itself is deployed as a cluster — a single-point-of-failure in the HA management layer defeats the purpose of clustering)
- [ ] **[Critical]** Configure streaming replication for data protection and read scaling (synchronous replication for zero-RPO within a datacenter; asynchronous replication for cross-region DR with sub-second lag in most cases; set appropriate values for max_wal_senders, wal_keep_size, and hot_standby_feedback — monitor replication lag continuously and alert when lag exceeds RPO thresholds)
- [ ] **[Critical]** Deploy connection pooling to prevent connection exhaustion (PgBouncer in transaction mode for highest connection multiplexing with minimal overhead; Pgpool-II when query load balancing and connection pooling are both needed; size the pool based on active query concurrency, not total application connections — PostgreSQL forks a process per connection, and performance degrades sharply beyond a few hundred connections even on large servers)
- [ ] **[Critical]** Tune autovacuum to prevent transaction ID wraparound and bloat (increase autovacuum_max_workers for databases with many tables; reduce autovacuum_vacuum_scale_factor for large tables so vacuuming starts earlier; monitor pg_stat_user_tables for dead tuple ratios and last vacuum times; set autovacuum_freeze_max_age appropriately — transaction ID wraparound forces a stop-the-world vacuum that can cause hours of downtime on large databases)
- [ ] **[Critical]** Size memory parameters based on available RAM and workload (shared_buffers at 25% of total RAM as a starting point; effective_cache_size at 50-75% of total RAM to inform the query planner; work_mem sized conservatively as it is per-sort-operation and multiplied by concurrent queries; maintenance_work_mem higher for vacuum and index creation — incorrect memory settings cause either excessive disk I/O or OS-level memory pressure and OOM kills)
- [ ] **[Recommended]** Define backup strategy using pg_basebackup, pgBackRest, or WAL-G (continuous WAL archiving for point-in-time recovery; base backups daily or weekly depending on database size and change rate; pgBackRest supports incremental backups, parallel backup/restore, and cloud storage targets; test restore procedures monthly — backup is only as good as the last verified restore)
- [ ] **[Recommended]** Evaluate logical replication for selective data distribution or zero-downtime upgrades (logical replication publishes specific tables to subscribers; enables cross-version replication for major version upgrades without downtime; supports data distribution to analytics systems or read replicas with different index strategies — logical replication does not replicate DDL changes, sequences, or large objects automatically)
- [ ] **[Recommended]** Assess managed PostgreSQL options for operational simplicity (Amazon RDS/Aurora PostgreSQL for AWS environments with automatic failover, backups, and patching; Google Cloud SQL or AlloyDB for GCP with AlloyDB offering columnar processing for analytics; Azure Database for PostgreSQL Flexible Server for Azure environments — managed services limit extension availability and parameter tunability compared to self-hosted)
- [ ] **[Recommended]** Plan extension strategy and validate availability on target platform (pg_stat_statements for query performance monitoring; PostGIS for geospatial data; pgvector for AI/ML vector similarity search; pg_cron for in-database scheduling; TimescaleDB for time-series workloads — managed services support a subset of extensions; verify required extensions are available before committing to a managed platform)
- [ ] **[Recommended]** Design migration approach from Oracle or SQL Server (use ora2pg for Oracle schema and PL/SQL conversion assessment; use pgloader or AWS SCT for SQL Server migration; map vendor-specific data types, stored procedures, and functions to PostgreSQL equivalents; plan for differences in transaction isolation, locking behavior, and NULL handling — budget 30-50% of migration effort for stored procedure conversion and application query testing)
- [ ] **[Optional]** Configure pgvector for AI/ML vector search workloads (install the pgvector extension and create vector columns with appropriate dimensions; use HNSW indexes for approximate nearest-neighbor search with tunable recall/speed trade-offs; IVFFlat indexes for lower memory usage on very large datasets — pgvector keeps vector search co-located with relational data, eliminating the need for a separate vector database in many cases)
- [ ] **[Optional]** Implement connection routing for read/write splitting (configure application-level routing using libpq target_session_attrs or a connection proxy; route read-only queries to replicas and read-write queries to the primary; use Pgpool-II or HAProxy with health checks for transparent routing — read/write splitting adds complexity and requires awareness of replication lag for consistency-sensitive reads)

## Why This Matters

PostgreSQL has become the default relational database for new projects and the most common migration target for organizations leaving Oracle or SQL Server, but its "easy to start, hard to master" nature creates operational risks that surface only at scale. A PostgreSQL instance with default settings will run acceptably for small workloads, but default autovacuum settings are insufficient for tables with millions of rows, default connection limits assume a handful of users, and default memory settings leave most available RAM unused. The difference between a well-tuned PostgreSQL deployment and a default one can be orders of magnitude in query performance and reliability.

The most dangerous PostgreSQL failure mode is transaction ID wraparound, which occurs when autovacuum cannot keep up with the rate of dead tuple accumulation. When the database approaches the 2-billion transaction limit without successful vacuuming, PostgreSQL refuses all write operations to prevent data corruption — an intentional safety mechanism that presents as a complete outage. This is entirely preventable with proper autovacuum configuration and monitoring, but organizations that treat PostgreSQL as "install and forget" routinely encounter this in production. Similarly, connection pooling is not optional for production PostgreSQL — the process-per-connection model means that even 500 idle connections consume significant memory and OS resources, and connection storms from application restarts or autoscaling events can saturate the server.

## Common Decisions (ADR Triggers)

### ADR: HA Solution Selection

**Context:** PostgreSQL requires an external tool to manage automatic failover, as it does not include built-in cluster management.

**Options:**

| Criterion | Patroni | repmgr | Cloud Managed (RDS/Cloud SQL) |
|---|---|---|---|
| Automatic Failover | Yes (via DCS consensus) | Yes (with repmgrd daemon) | Yes (built-in) |
| Consensus Store | etcd, ZooKeeper, or Consul required | Optional (witness server) | Not applicable |
| Split-Brain Prevention | Strong (DCS-based leader lock) | Moderate (depends on configuration) | Strong (provider-managed) |
| Operational Complexity | Moderate (manage DCS cluster) | Lower (fewer moving parts) | Lowest (fully managed) |
| Customization | High (extensive configuration) | Moderate | Limited (provider-controlled) |

**Decision drivers:** Operational team expertise, existing infrastructure (etcd/Consul already deployed for other services), split-brain risk tolerance, and whether the deployment is self-hosted or cloud-managed.

### ADR: Connection Pooling Strategy

**Context:** PostgreSQL's process-per-connection model requires a connection pooler to support high-concurrency workloads.

**Options:**
- **PgBouncer (transaction mode):** Lightweight, single-purpose pooler. Multiplexes hundreds of application connections onto a small number of database connections. Transaction mode releases connections between transactions, maximizing reuse. Does not support session-level features like prepared statements (in transaction mode) or LISTEN/NOTIFY.
- **PgBouncer (session mode):** Maintains a 1:1 mapping between client and server sessions. Supports all PostgreSQL features. Provides connection queueing but minimal multiplexing. Useful when prepared statements or session variables are required.
- **Pgpool-II:** Provides both connection pooling and query load balancing across read replicas. Supports automatic read/write splitting. Higher resource consumption and configuration complexity than PgBouncer. Better suited when a single tool must handle both pooling and routing.
- **Application-side pooling:** Built-in pooling in frameworks (e.g., SQLAlchemy pool, HikariCP). No additional infrastructure. Limits pool per application instance, not globally. Does not prevent connection storms during application scaling events.

**Decision drivers:** Concurrency requirements, need for read/write splitting, use of session-level features (prepared statements, temp tables), and operational preference for infrastructure-level vs. application-level pooling.

### ADR: Self-Hosted vs. Managed PostgreSQL

**Context:** The organization must decide between managing PostgreSQL on VMs/containers or using a cloud-managed service.

**Options:**
- **Self-hosted (VM or Kubernetes):** Full control over version, extensions, configuration, and upgrade timing. Requires DBA expertise for patching, backup, HA configuration, and performance tuning. Can use any PostgreSQL extension. Lowest per-instance cost but highest operational cost.
- **Amazon RDS / Aurora PostgreSQL:** Managed HA, automated backups, and push-button read replicas. Aurora offers storage auto-scaling and faster replication. Limited extension set and parameter group restrictions. Aurora Serverless v2 for variable workloads.
- **Google Cloud SQL / AlloyDB:** Cloud SQL for standard managed PostgreSQL. AlloyDB for analytics-heavy workloads with columnar engine and PostgreSQL compatibility. AlloyDB provides better performance for mixed OLTP/OLAP but is GCP-only.
- **Azure Database for PostgreSQL Flexible Server:** Managed service with zone-redundant HA. Supports most extensions. Integrates with Azure AD for authentication. Comparable to RDS in feature set.

**Decision drivers:** Extension requirements, DBA availability, cloud provider commitment, need for advanced features (custom WAL handling, specific extensions), and total cost of ownership including operational overhead.

## See Also

- `general/database-migration.md` — Database migration strategy, schema migration tooling, replication, and cutover planning
- `general/database-ha.md` — Database high availability patterns, replication topologies, and failover strategies
- `general/ai-ml-services.md` — AI/ML architecture including vector database considerations
- `providers/gcp/ai-ml-services.md` — GCP AI/ML services including AlloyDB AI integration
