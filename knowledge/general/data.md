# Data Management and Database Strategy

## Scope

This file covers **what** data management decisions need to be made during architecture design: database engine selection, replication, backup, encryption, compliance, schema management, and performance tuning. For provider-specific **how** (managed service configuration, pricing tiers, region availability), see the provider data files listed in See Also.

## Checklist

- [ ] **[Critical]** Select database engine type based on data model and query patterns (relational for ACID transactions and complex joins; document for flexible schema and nested objects; key-value for session state and caching; graph for relationship-heavy traversal; time-series for metrics, IoT, and log data — most projects need more than one type)
- [ ] **[Critical]** Define replication strategy aligned with RPO and consistency requirements (synchronous replication for zero data loss at higher latency cost; asynchronous replication for lower latency with potential data lag; multi-region active-active for global availability with conflict resolution complexity)
- [ ] **[Critical]** Establish backup strategy with explicit RPO, retention, and restore testing schedule (continuous WAL archiving for point-in-time recovery; daily snapshots for coarse-grained recovery; cross-region backup copies for disaster scenarios — test restores quarterly, not just during DR exercises)
- [ ] **[Critical]** Implement encryption at rest using provider-managed keys, customer-managed keys (CMK), or HSM-backed keys (provider-managed is simplest; CMK gives revocation control and audit trail; HSM meets FIPS 140-2 Level 3 for regulated industries — key rotation policy must be defined regardless)
- [ ] **[Critical]** Enforce encryption in transit for all database connections (TLS 1.2+ minimum; mutual TLS for service-to-database authentication in zero-trust environments; certificate rotation automation to prevent expiry outages)
- [ ] **[Critical]** Determine data residency and sovereignty requirements before selecting regions (some jurisdictions require data to remain in-country; others require data to be accessible to local authorities; multi-region designs must account for GDPR cross-border transfer rules, Schrems II implications, and sector-specific regulations)
- [ ] **[Critical]** Design failover strategy with explicit RTO targets (automatic failover with managed services provides minutes-level RTO but risks split-brain without proper fencing; manual failover gives operator control but extends RTO to hours; multi-AZ automatic failover is standard for production; cross-region failover requires promotion procedures and DNS/routing changes)
- [ ] **[Critical]** Identify compliance requirements and map them to database controls (PCI-DSS requires encryption, access logging, and network segmentation; HIPAA requires audit trails and BAAs with cloud providers; GDPR requires right-to-deletion capability, data portability, and breach notification procedures; SOC 2 requires access controls and change management)
- [ ] **[Recommended]** Assess expected data volume, growth rate, and access patterns to inform engine and tier selection (10 GB and 10 TB are fundamentally different architecture problems; write-heavy workloads may need write-optimized storage engines like LSM-tree; read-heavy workloads benefit from B-tree indexes and read replicas)
- [ ] **[Recommended]** Design connection pooling strategy to prevent connection exhaustion (application-side pooling via HikariCP, SQLAlchemy pool, or pgBouncer in transaction mode; serverless databases may need proxy-based pooling like RDS Proxy or PgBouncer to handle connection storms from Lambda/Cloud Functions)
- [ ] **[Recommended]** Plan read replica topology for read-heavy workloads (same-region replicas for read scaling; cross-region replicas for latency reduction and DR readiness; application-level routing to direct reads to replicas and writes to primary — beware replication lag causing stale reads in async setups)
- [ ] **[Recommended]** Define database migration and schema management approach (version-controlled migrations via Flyway, Liquibase, or Alembic; blue-green database deployments for zero-downtime schema changes; backward-compatible migrations that allow rollback — never run destructive DDL without a tested rollback plan)
- [ ] **[Recommended]** Evaluate caching layer requirements and eviction strategy (read-through cache with TTL for frequently accessed, rarely changing data; write-behind cache for absorbing write bursts; cache-aside pattern for application-controlled consistency — size the cache to hold the working set, not the full dataset)
- [ ] **[Optional]** Design data archival and lifecycle management for aging data (partition tables by date for efficient archival; move cold data to cheaper storage tiers or separate databases; maintain query access to archived data via federated queries or materialized views for compliance reporting)
- [ ] **[Optional]** Evaluate managed vs self-hosted database trade-offs (managed services reduce operational burden but limit tuning options and increase vendor lock-in; self-hosted provides full control but requires dedicated DBA expertise for patching, upgrades, HA configuration, and backup management)

## Why This Matters

Data is the most valuable and least replaceable component of any system. While compute and networking can be rebuilt in hours, lost or corrupted data may be unrecoverable. A database engine mismatch — such as forcing a graph traversal workload into a relational schema or cramming time-series telemetry into a document store — creates performance problems that no amount of hardware can solve, eventually requiring a costly re-architecture.

Replication and failover strategy directly determine how much data the business loses (RPO) and how long it stays down (RTO) during an incident. Synchronous replication guarantees zero data loss but adds write latency; asynchronous replication is faster but means the replica is always slightly behind. Organizations that defer this decision until a failure occurs discover their actual RPO and RTO the hard way — and the answer is rarely acceptable to the business.

Encryption and compliance are not optional add-ons. Regulatory requirements like GDPR, PCI-DSS, and HIPAA impose specific controls on how data is stored, accessed, transmitted, and deleted. Retrofitting encryption or audit logging onto an existing database is significantly more disruptive than designing it in from the start. Key management decisions — especially who holds the keys and how rotation works — have long-term operational implications that are difficult to change later.

## Common Decisions (ADR Triggers)

### ADR: Database Engine Selection

**Context:** The application requires persistent data storage, and the team must choose an engine that matches the data model, query patterns, and operational requirements.

**Options:**

| Criterion | Relational (PostgreSQL, MySQL) | Document (MongoDB, Cosmos DB) | Key-Value (Redis, DynamoDB) | Time-Series (TimescaleDB, InfluxDB) | Graph (Neo4j, Neptune) |
|---|---|---|---|---|---|
| Data Model | Structured, normalized tables | Flexible JSON/BSON documents | Simple key-to-value pairs | Timestamped metric data | Nodes and edges |
| Query Strength | Complex joins, aggregations, transactions | Nested document queries, flexible schema | Sub-millisecond lookups by key | Time-range queries, downsampling | Relationship traversal, path finding |
| ACID Support | Full | Document-level (multi-doc varies) | Limited (varies by engine) | Varies | Full (Neo4j), varies (others) |
| Scaling Model | Vertical + read replicas | Horizontal sharding native | Horizontal sharding native | Time-based partitioning | Vertical primarily |
| Best Fit | Business data, transactions, reporting | Content management, catalogs, user profiles | Session state, caching, feature flags | Monitoring, IoT, financial tick data | Social networks, fraud detection, knowledge graphs |

**Decision drivers:** Data structure predictability, transaction requirements, query complexity, scale trajectory, and team expertise with the engine.

### ADR: Replication and Failover Model

**Context:** The database must survive infrastructure failures while meeting the application's consistency and availability requirements.

**Options:**
- **Single-region, multi-AZ synchronous replication:** Zero RPO within a region, automatic failover in 1-2 minutes. Standard for production workloads. Does not protect against regional outages.
- **Cross-region asynchronous replication:** RPO of seconds to minutes depending on lag. Protects against regional disasters. Requires application-level handling of stale reads from replicas and promotion procedures for failover.
- **Multi-region active-active (e.g., CockroachDB, Cosmos DB, Spanner):** Writes accepted in any region with distributed consensus. Lowest latency for global users. Highest complexity and cost; requires conflict resolution strategy and careful partition design.
- **Manual failover with cold standby:** Lowest cost, highest RTO (hours). Acceptable for non-critical systems where extended downtime is tolerable.

**Decision drivers:** RPO/RTO requirements, geographic distribution of users, consistency model tolerance (strong vs. eventual), operational maturity, and budget.

### ADR: Encryption Key Management

**Context:** Data at rest must be encrypted, and the organization must decide who manages the encryption keys.

**Options:**
- **Provider-managed keys (default):** Cloud provider generates, stores, and rotates keys automatically. Zero operational burden. No customer control over key lifecycle; provider has theoretical access.
- **Customer-managed keys (CMK) in cloud KMS:** Customer controls key creation, rotation schedule, and revocation via AWS KMS, Azure Key Vault, or GCP Cloud KMS. Audit trail for key usage. Requires IAM policy management; accidental key deletion causes permanent data loss.
- **External HSM (CloudHSM, on-prem HSM):** Keys never leave FIPS 140-2 Level 3 validated hardware. Required by some financial and government regulations. Highest cost and operational complexity; HSM cluster must be highly available.

**Recommendation:** Use customer-managed keys in cloud KMS for most production workloads. Reserve HSM for workloads with explicit regulatory mandates. Provider-managed keys are acceptable for non-sensitive or development environments.

### ADR: Schema Migration Strategy

**Context:** The database schema will evolve over the application lifecycle, and changes must be applied without data loss or extended downtime.

**Options:**
- **Sequential versioned migrations (Flyway, Alembic, Liquibase):** Each change is a numbered, version-controlled script. Applied in order. Supports rollback scripts. Standard approach for most teams.
- **Blue-green database deployment:** Run old and new schema versions in parallel during transition. Zero-downtime for schema changes. Requires double storage temporarily and backward-compatible application code.
- **Expand-contract pattern:** Add new columns/tables first (expand), migrate data, update application, then remove old structures (contract). Safe for zero-downtime deployments. Requires multiple deployment cycles to complete a single change.

**Decision drivers:** Downtime tolerance, deployment frequency, team size, and whether the application supports running against multiple schema versions simultaneously.

## See Also

- `providers/aws/rds-aurora.md` — AWS RDS and Aurora database configuration
- `providers/aws/dynamodb.md` — AWS DynamoDB NoSQL database
- `providers/azure/data.md` — Azure database and data services
- `providers/gcp/data.md` — GCP database and data services
- `general/enterprise-backup.md` — Backup tools and strategies (complements the backup checklist items here)
- `general/security.md` — Broader security controls including data access and audit
- `general/data-analytics.md` — Data analytics and warehousing architecture, ETL/ELT, and data mesh patterns
