# AWS Database

## Scope

Consolidated overview of AWS database services and selection framework. Covers database selection decision framework (relational vs NoSQL vs graph vs time-series vs in-memory vs ledger), DocumentDB (MongoDB-compatible), Neptune (graph), Timestream (time-series), Keyspaces (Cassandra-compatible), MemoryDB (Redis-compatible durable), QLDB (ledger), cross-service comparison, database connectivity patterns, and migration paths. RDS/Aurora, DynamoDB, and ElastiCache are covered in dedicated files and cross-referenced here.

## Checklist

- [ ] **[Critical]** Is the database engine selected based on the data model and access patterns -- relational (RDS/Aurora) for complex queries, joins, and transactions; key-value/document (DynamoDB) for known access patterns at scale; document (DocumentDB) for MongoDB-compatible workloads; graph (Neptune) for relationship traversal; time-series (Timestream) for IoT and metrics; wide-column (Keyspaces) for Cassandra-compatible high-throughput; in-memory (MemoryDB) for durable sub-millisecond latency; caching (ElastiCache) for ephemeral acceleration?
- [ ] **[Critical]** Is DocumentDB configured with the appropriate instance class and cluster topology -- primary instance for writes with up to 15 read replicas across AZs, storage auto-scaling up to 128 TiB, and TLS encryption enabled by default? Are MongoDB compatibility limitations understood (DocumentDB emulates MongoDB 3.6/4.0/5.0 API but does not support all features -- no client-side field-level encryption, limited aggregation pipeline stages, no change streams resume across cluster restarts)?
- [ ] **[Critical]** Is Neptune configured with the appropriate query language for the workload -- Gremlin for property graph traversals (path finding, recommendation engines), SPARQL for RDF and linked data (knowledge graphs, ontologies), or openCypher for Cypher-compatible graph queries? Is Neptune Serverless evaluated for variable or unpredictable graph workloads to avoid over-provisioning?
- [ ] **[Recommended]** Is Neptune database configured with Multi-AZ deployment for production, with up to 15 read replicas for read-heavy graph queries, and is Neptune Analytics evaluated for running graph algorithms (PageRank, shortest path, community detection) on large datasets without impacting the operational database?
- [ ] **[Recommended]** Is Timestream configured with appropriate retention policies -- memory store retention (hours to days) for recent high-throughput ingestion and queries, magnetic store retention (days to years) for cost-effective long-term storage? Are scheduled queries configured to pre-aggregate data for dashboard workloads, reducing query costs on raw data?
- [ ] **[Recommended]** Is Keyspaces evaluated for Cassandra-compatible workloads that benefit from serverless operations -- on-demand capacity (pay-per-request) vs provisioned capacity with auto-scaling? Are partition key and clustering column designs validated for even distribution, with understanding that Keyspaces supports CQL but does not support all Apache Cassandra features (no lightweight transactions with IF NOT EXISTS on collections, no custom types in certain contexts)?
- [ ] **[Recommended]** Is MemoryDB evaluated instead of ElastiCache when the workload requires both sub-millisecond read latency and data durability (Multi-AZ transactional log for persistence)? MemoryDB provides Redis-compatible API with data durability guarantees, while ElastiCache prioritizes caching performance with optional persistence.
- [ ] **[Recommended]** Are database connectivity patterns selected appropriately -- RDS Proxy for connection pooling with Lambda and serverless workloads (reduces connection overhead and failover time), VPC endpoints (PrivateLink) for DynamoDB, Timestream, Keyspaces, and QLDB to keep traffic within the VPC, and security group referencing (not CIDR) for VPC-deployed databases?
- [ ] **[Recommended]** Is the migration path between database types planned using AWS Database Migration Service (DMS) for heterogeneous migrations, with Schema Conversion Tool (SCT) for schema translation? Are homogeneous migrations (same engine) using native tools (pg_dump/restore, mongodump/mongorestore, mysqldump) for simplicity and speed?
- [ ] **[Critical]** Are all database services deployed with encryption at rest (KMS customer-managed keys for compliance), encryption in transit (TLS), and IAM-based authentication where supported (Neptune, Timestream, Keyspaces, QLDB natively use IAM; RDS and DocumentDB support IAM authentication as an option)?
- [ ] **[Recommended]** Is the cost model understood for each service -- DocumentDB (instance-hours + I/O + storage), Neptune (instance-hours + I/O + storage, Serverless uses NCUs), Timestream (writes per GB + storage per GB + queries scanned per GB), Keyspaces (read/write request units or provisioned capacity + storage), MemoryDB (node-hours + data transfer)?
- [ ] **[Optional]** Is QLDB evaluated only for legacy or in-flight projects requiring an immutable ledger with cryptographic verification? (QLDB end-of-support is July 31, 2025 -- no new accounts can create QLDB ledgers; plan migration to alternative services such as DynamoDB with audit trails, Aurora with application-level immutability, or Amazon Managed Blockchain)
- [ ] **[Optional]** Is a polyglot persistence strategy documented when using multiple database engines -- defining which data model maps to which service, how data synchronization works across services (DMS, Streams, EventBridge), and how operational complexity scales with the number of distinct database technologies?

## Cross-Service Comparison

| Service | Data Model | Latency | Max Storage | Serverless Option | Multi-Region | Primary Use Case |
|---|---|---|---|---|---|---|
| **RDS/Aurora** | Relational | Low ms | 128 TiB (Aurora) | Aurora Serverless v2 | Global Database | OLTP, complex queries |
| **DynamoDB** | Key-value, document | Single-digit ms | Unlimited | On-demand mode | Global tables | Known access patterns at scale |
| **ElastiCache** | Key-value, data structures | Sub-ms | 635 GiB/node | ElastiCache Serverless | No (single region) | Caching, ephemeral data |
| **DocumentDB** | Document (MongoDB) | Low ms | 128 TiB | Elastic clusters | Global clusters | MongoDB-compatible workloads |
| **Neptune** | Graph (property + RDF) | Low ms | 128 TiB | Neptune Serverless | Global Database | Relationships, knowledge graphs |
| **Timestream** | Time-series | Low ms | Unlimited | Serverless-native | No (single region) | IoT, DevOps metrics, analytics |
| **Keyspaces** | Wide-column (Cassandra) | Single-digit ms | Unlimited | Serverless-native | Multi-Region replication | Cassandra-compatible workloads |
| **MemoryDB** | Key-value, data structures | Sub-ms reads, low ms writes | 635 GiB/node | No | Multi-Region (preview) | Durable in-memory primary DB |
| **QLDB** | Ledger (document) | Low ms | 100 GB/ledger | Serverless-native | No | Immutable audit (end-of-support Jul 2025) |

## Database Connectivity Patterns

### RDS Proxy

RDS Proxy sits between applications and RDS/Aurora databases, providing connection pooling, multiplexing, and faster failover. Critical for Lambda-to-database connectivity where rapid function scaling creates thousands of short-lived connections. RDS Proxy reduces failover time by up to 66% by maintaining connections to standby instances. Supports IAM authentication and Secrets Manager integration for credential management.

### VPC Endpoints (PrivateLink)

Serverless database services (DynamoDB, Timestream, Keyspaces, QLDB) are accessed via public endpoints by default. VPC gateway endpoints (DynamoDB) and interface endpoints (Timestream, Keyspaces, QLDB, DocumentDB) keep traffic within the AWS network, avoiding NAT gateway data processing charges and improving security posture. Interface endpoints incur per-hour and per-GB charges but eliminate data transfer through NAT gateways.

### Cross-Account and Cross-VPC Access

For multi-account architectures, database access patterns include VPC peering or Transit Gateway for VPC-deployed databases (RDS, Aurora, DocumentDB, Neptune, ElastiCache, MemoryDB), and VPC endpoints for serverless services. Resource Access Manager (RAM) can share Aurora DB clusters across accounts. Security group referencing works across peered VPCs using the account-id/sg-id format.

## Migration Paths

| Source | Target | Tool | Notes |
|---|---|---|---|
| On-premises MySQL/PostgreSQL | RDS/Aurora | DMS + SCT | Full load + CDC for minimal downtime |
| On-premises MongoDB | DocumentDB | DMS | Online migration with change streams |
| On-premises Cassandra | Keyspaces | cqlsh COPY or custom tooling | No native DMS support for Keyspaces as target |
| Self-managed Redis | MemoryDB or ElastiCache | Online migration tool or snapshot import | Snapshot-based for initial load, replication for cutover |
| DynamoDB | Aurora | DMS | When workload evolves to need relational queries |
| RDS/Aurora | DynamoDB | DMS or custom ETL | When access patterns become key-value dominant |
| Oracle/SQL Server | Aurora PostgreSQL | DMS + SCT | Heterogeneous migration with schema conversion |
| QLDB | DynamoDB + application audit | Custom export + DynamoDB Streams | Required before July 2025 end-of-support |
| Timestream | Timestream for InfluxDB | Export/import | For InfluxDB-compatible workloads |

## Why This Matters

AWS offers 15+ purpose-built database services, and selecting the wrong one is expensive to reverse. Each database is optimized for a specific data model and access pattern -- using a relational database for graph traversals or a key-value store for ad-hoc queries results in poor performance and escalating costs. The most common and costly mistake is defaulting to a relational database for every workload when a purpose-built service would be significantly more efficient.

DocumentDB is frequently misunderstood as a drop-in MongoDB replacement -- it implements the MongoDB wire protocol but has compatibility gaps that surface during migration. Neptune's value depends entirely on whether the workload genuinely requires relationship traversal; storing graph data that is only queried with simple lookups wastes the graph engine's overhead. Timestream provides significant cost savings over storing time-series data in relational databases but requires understanding its dual-tier storage model to avoid unexpected query costs on magnetic store data.

MemoryDB fills a gap between ElastiCache (fast but volatile) and traditional databases (durable but slower) -- it is appropriate when Redis data structures are needed as a primary database, not just a cache. Keyspaces eliminates Cassandra operational burden but does not support the full Cassandra feature set, making compatibility testing essential before migration.

QLDB reached end-of-support on July 31, 2025. Any existing QLDB ledgers must be migrated to alternative services. Do not recommend QLDB for new projects.

## Common Decisions (ADR Triggers)

- **Relational vs NoSQL vs purpose-built** -- RDS/Aurora for complex queries and ACID transactions vs DynamoDB for scale and known access patterns vs purpose-built (Neptune, Timestream, Keyspaces, MemoryDB) for specific data models; defaulting to relational increases cost and complexity for non-relational workloads
- **DocumentDB vs DynamoDB for document workloads** -- DocumentDB for MongoDB-compatible applications requiring rich queries, aggregation pipelines, and secondary indexes with familiar MongoDB drivers vs DynamoDB for key-value/document workloads with known access patterns and massive scale; DocumentDB requires cluster management while DynamoDB is fully serverless
- **DocumentDB vs self-managed MongoDB on EC2** -- DocumentDB for reduced operational burden with trade-off of MongoDB compatibility gaps vs self-managed MongoDB for full feature compatibility (transactions, change streams resume, client-side encryption) with significant operational overhead
- **Neptune vs relational joins** -- Neptune for workloads requiring multi-hop relationship traversal (social networks, fraud detection, recommendation engines, knowledge graphs) vs relational JOINs for simple 1-2 hop relationships where graph overhead is not justified
- **Neptune Serverless vs provisioned** -- Serverless (scales in Neptune Capacity Units) for variable graph query workloads and development environments vs provisioned instances for predictable, high-throughput graph query workloads
- **Timestream vs time-series in Aurora/RDS** -- Timestream for native time-series optimization (automatic partitioning, retention policies, interpolation functions, scheduled queries) vs PostgreSQL TimescaleDB extension in RDS for teams wanting a single relational engine for both transactional and time-series data
- **Keyspaces vs self-managed Cassandra** -- Keyspaces for serverless Cassandra-compatible access with no cluster management vs self-managed Cassandra on EC2 for full feature compatibility, tunable consistency, and workloads requiring Cassandra-specific features not available in Keyspaces
- **MemoryDB vs ElastiCache** -- MemoryDB when Redis data structures are the primary data store requiring durability (Multi-AZ transactional log, no data loss on failover) vs ElastiCache when used as a cache layer in front of another database (eventual data loss on failover acceptable); MemoryDB write latency is slightly higher due to durability guarantees
- **Single-engine vs polyglot persistence** -- single database engine for operational simplicity vs multiple purpose-built engines for workload optimization; polyglot persistence increases operational overhead, monitoring complexity, and cross-service data consistency challenges
- **Database connectivity** -- RDS Proxy for serverless-to-database connection pooling vs application-level pooling (PgBouncer, HikariCP) for container/EC2 workloads vs direct connections for low-connection-count applications

## Reference Links

- [AWS Database Services overview](https://aws.amazon.com/products/databases/) -- service comparison and selection guidance for all AWS database offerings
- [AWS Prescriptive Guidance: Database strategy](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-database-migration/) -- framework for selecting and migrating to purpose-built databases on AWS
- [Amazon DocumentDB Developer Guide](https://docs.aws.amazon.com/documentdb/latest/developerguide/) -- cluster architecture, MongoDB compatibility, scaling, and security configuration
- [Amazon Neptune User Guide](https://docs.aws.amazon.com/neptune/latest/userguide/) -- graph data model selection (property graph vs RDF), query languages, serverless configuration, and best practices
- [Amazon Timestream Developer Guide](https://docs.aws.amazon.com/timestream/latest/developerguide/) -- time-series data modeling, retention tiers, scheduled queries, and integration with IoT and DevOps tooling
- [Amazon Keyspaces Developer Guide](https://docs.aws.amazon.com/keyspaces/latest/devguide/) -- CQL compatibility, capacity modes, table design, and migration from Apache Cassandra
- [Amazon MemoryDB Developer Guide](https://docs.aws.amazon.com/memorydb/latest/devguide/) -- durability architecture, Multi-AZ replication, and comparison with ElastiCache
- [AWS Database Migration Service User Guide](https://docs.aws.amazon.com/dms/latest/userguide/) -- heterogeneous and homogeneous migration patterns, Schema Conversion Tool, and change data capture
- [AWS Architecture Center: Databases](https://aws.amazon.com/architecture/databases/) -- reference architectures for database selection, migration, and multi-database patterns

---

## See Also

- `providers/aws/rds-aurora.md` -- RDS and Aurora relational database architecture, Multi-AZ, read replicas, Global Database, Serverless v2
- `providers/aws/dynamodb.md` -- DynamoDB key-value and document database, partition design, capacity modes, Streams, global tables
- `providers/aws/elasticache.md` -- ElastiCache with Valkey, Redis OSS, and Memcached for caching workloads
- `providers/aws/vpc.md` -- VPC endpoints, private subnets, and security group patterns for database connectivity
- `providers/aws/secrets-manager.md` -- Credential rotation for database passwords
- `providers/aws/migration-services.md` -- AWS DMS and broader migration tooling
- `general/data.md` -- General data architecture patterns and database selection criteria
- `general/database-migration.md` -- Database migration strategies
