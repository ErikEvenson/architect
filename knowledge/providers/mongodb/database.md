# MongoDB

## Scope

This file covers **MongoDB** architecture decisions: Atlas vs self-hosted deployment, replica set configuration, sharding strategy and shard key design, schema design patterns (embedding vs referencing), aggregation pipeline optimization, change streams for event-driven architectures, Atlas Search for full-text and vector search, read/write concern tuning, connection management, and migration from relational databases. For general database strategy (engine selection, replication patterns, encryption), see `general/data.md`. For migration methodology and cutover planning, see `general/database-migration.md`.

## Checklist

- [ ] **[Critical]** Design shard key to distribute data evenly and support query patterns (a monotonically increasing shard key like ObjectId or timestamp creates a "hot shard" where all writes go to one shard; use a hashed shard key for write distribution or a compound shard key that matches your most common query filter; the shard key is immutable after collection creation in versions before 5.0, and resharding in 5.0+ requires significant I/O — choosing the wrong shard key is the most expensive MongoDB mistake because it often requires rebuilding the entire cluster)
- [ ] **[Critical]** Configure replica set with appropriate members and voting topology (minimum 3 members for automatic failover — 2 data-bearing + 1 arbiter is acceptable for cost savings but provides no read scaling or redundancy beyond the primary; prefer 3 data-bearing members; set priority to control failover targets; configure hidden members for analytics or backup workloads that should never become primary — a replica set with fewer than 3 voting members cannot elect a new primary if one member is unavailable)
- [ ] **[Critical]** Select appropriate read concern and write concern for data durability requirements (write concern "majority" ensures data is acknowledged by a majority of replica set members before confirming the write; read concern "majority" returns only data that has been acknowledged by a majority; "local" read concern is faster but may return data that could be rolled back during failover — financial or compliance-sensitive applications must use majority read/write concern, as "w:1" writes can be lost during primary failover)
- [ ] **[Critical]** Design schema following document model best practices (embed related data that is always accessed together to avoid $lookup joins; reference data with independent access patterns or that would exceed the 16 MB document size limit; avoid unbounded arrays that grow indefinitely as they cause document migration on disk and eventual size limit violations; use the Bucket pattern for time-series data, the Outlier pattern for documents with occasional large arrays, and the Computed pattern for pre-aggregated analytics)
- [ ] **[Critical]** Plan connection management to prevent connection exhaustion (each MongoDB driver maintains a connection pool; default maxPoolSize is typically 100 per MongoClient instance; with microservices architectures, total connections = instances x pool size and can easily exceed mongod's default 65,536 connection limit; use connection string options to set maxPoolSize, minPoolSize, and maxIdleTimeMS — in Kubernetes, account for pod autoscaling multiplying connection counts; MongoDB Atlas has connection limits per tier that cannot be increased)
- [ ] **[Recommended]** Evaluate Atlas vs self-hosted deployment model (Atlas provides automated backups, scaling, monitoring, and security defaults; Atlas serverless instances for variable workloads eliminate capacity planning; self-hosted provides full control over configuration, storage engine tuning, and version timing; Atlas dedicated clusters for production, shared clusters only for development — Atlas charges for data transfer, backup storage, and Atlas Search nodes separately, which can significantly increase costs beyond the base cluster price)
- [ ] **[Recommended]** Design indexes to support query patterns and avoid collection scans (create compound indexes that match query filters and sort orders following the ESR rule — Equality, Sort, Range; use partial indexes to reduce index size when queries filter on a subset of documents; use TTL indexes for automatic document expiration; monitor slow queries via the profiler and explain plans — every query without a supporting index performs a collection scan, which degrades linearly as data grows and can saturate disk I/O)
- [ ] **[Recommended]** Configure change streams for event-driven integration (change streams provide a real-time stream of document-level changes; require a replica set or sharded cluster; use resume tokens for exactly-once processing semantics; change streams are the recommended replacement for the deprecated oplog tailing approach — change stream cursors consume an open connection and server resources per watcher; plan for connection overhead when multiple services watch the same collection)
- [ ] **[Recommended]** Plan aggregation pipeline optimization for analytics workloads (use $match and $project early in the pipeline to reduce documents processed in later stages; $lookup performs left outer joins but is expensive on sharded collections — the "from" collection must be on the same database and unsharded, or on the same shard in MongoDB 5.1+; use $merge or $out to materialize aggregation results for dashboard queries; consider Atlas Data Lake or Atlas SQL Interface for complex analytics instead of real-time aggregation)
- [ ] **[Recommended]** Implement backup and point-in-time recovery strategy (Atlas provides continuous backups with point-in-time recovery to any second within a configurable retention window; self-hosted environments should use mongodump for logical backups of smaller databases, or filesystem snapshots with mongod's fsyncLock for consistent point-in-time backups of large databases; Percona Backup for MongoDB provides cluster-wide consistent backups for sharded clusters — mongodump on large databases can take hours and impact performance without oplog replay for point-in-time recovery)
- [ ] **[Recommended]** Evaluate Atlas Search for full-text and vector search requirements (Atlas Search uses Apache Lucene under the hood and runs on dedicated search nodes; supports fuzzy matching, facets, autocomplete, synonyms, and custom scoring; Atlas Vector Search enables semantic search with vector embeddings stored alongside operational data; search indexes are eventually consistent, typically seconds behind writes — Atlas Search eliminates the need for a separate Elasticsearch cluster for many search use cases but adds cost for dedicated search node tiers)
- [ ] **[Optional]** Configure queryable encryption or client-side field-level encryption for sensitive data (Queryable Encryption allows queries on encrypted fields without server-side decryption; CSFLE encrypts fields before they leave the driver using AWS KMS, Azure Key Vault, GCP KMS, or a local key; both approaches ensure the database server never sees plaintext for sensitive fields — Queryable Encryption is available in MongoDB 7.0+ and has query type limitations; CSFLE requires driver support and key management infrastructure)
- [ ] **[Optional]** Plan time-series collection strategy for IoT or metrics data (MongoDB 5.0+ native time-series collections optimize storage and query performance for timestamped data; specify timeField and optional metaField at collection creation; uses columnar compression for 20-30x storage reduction compared to regular collections; supports secondary indexes on meta and time fields — time-series collections are append-optimized and do not support individual document updates or deletes, only bulk TTL-based expiration)

## Why This Matters

MongoDB's document model provides flexibility that relational databases do not, but this flexibility creates its own class of architectural mistakes. The most common failure pattern is treating MongoDB like a relational database — normalizing data across collections and relying on $lookup for joins, which eliminates the performance advantages of the document model. The second most common failure is schema-less development without schema validation, which leads to inconsistent documents that break application logic and make queries unpredictable.

Shard key selection is the single most consequential MongoDB architecture decision. A poorly chosen shard key creates "jumbo chunks" that cannot be split or migrated, leading to unbalanced shards where one node handles disproportionate load while others sit idle. In pre-5.0 versions, the only remedy is to dump and reload the entire collection with a new shard key. Even with MongoDB 5.0+ resharding support, the process is I/O intensive and can impact production performance for hours on large collections.

Connection management is another area where MongoDB deployments fail at scale. Unlike connection-pooled relational databases with lightweight per-connection overhead, each MongoDB connection consumes approximately 1 MB of RAM on the server. In microservices architectures with many small services, the aggregate connection count across all service instances can exhaust server memory before CPU or disk becomes the bottleneck. Atlas tier connection limits compound this problem — an M30 instance supports a maximum of 2,000 connections, which can be consumed quickly by a dozen services each running 20 pods with a pool size of 10.

## Common Decisions (ADR Triggers)

### ADR: Atlas vs Self-Hosted MongoDB

**Context:** The organization must decide between MongoDB Atlas (fully managed) and self-hosted MongoDB (on VMs or Kubernetes).

**Options:**

| Criterion | MongoDB Atlas | Self-Hosted (VM) | Self-Hosted (Kubernetes) |
|---|---|---|---|
| Operational Overhead | Lowest (fully managed) | High (manual patching, backups, HA) | Moderate (operator-managed, but K8s complexity) |
| Cost Model | Per-hour cluster + data transfer + backup | Infrastructure + DBA time | Infrastructure + K8s overhead + DBA time |
| Customization | Limited (managed configuration) | Full control | Full control |
| Built-in Search | Atlas Search and Vector Search | Requires separate Elasticsearch | Requires separate Elasticsearch |
| Multi-Region | Built-in Global Clusters | Manual replica set across regions | Complex cross-cluster replication |
| Security | SOC 2, HIPAA, PCI DSS compliant | Customer-managed | Customer-managed |

**Decision drivers:** Operational team MongoDB expertise, total cost of ownership including personnel, multi-region requirements, search feature needs, and compliance certification requirements.

### ADR: Embedding vs Referencing Data Model

**Context:** MongoDB schema design requires deciding which related data to embed within documents versus reference across collections.

**Options:**
- **Embed (denormalize):** Store related data in nested subdocuments or arrays within the parent document. Optimal when related data is always accessed with the parent, has a bounded size, and does not need independent access. Single-document reads and writes are atomic in MongoDB. Risk of exceeding 16 MB document limit with unbounded arrays.
- **Reference (normalize):** Store related data in separate collections with ObjectId references. Requires $lookup or multiple queries to assemble related data. Optimal for many-to-many relationships, independently accessed entities, or data that would create unbounded document growth. Provides flexibility for evolving access patterns.
- **Hybrid (Extended Reference):** Embed frequently accessed fields from the referenced document while maintaining the reference. Reduces $lookup frequency for common queries. Requires application-level management to keep embedded copies consistent with the source document.

**Decision drivers:** Query access patterns, data relationship cardinality (1:1, 1:few, 1:many, many:many), document growth rate, data consistency requirements, and whether related data is read independently.

### ADR: Sharding Strategy

**Context:** The collection has grown beyond what a single replica set can serve in terms of storage or throughput, requiring horizontal scaling via sharding.

**Options:**
- **Hashed Shard Key:** Hash of a single field (often _id). Provides even write distribution across shards. Does not support range queries on the shard key — all range queries become scatter-gather operations. Best for write-heavy workloads where queries filter on non-shard-key fields.
- **Ranged Shard Key:** Uses field value ranges to partition data. Supports range queries on the shard key that target a single shard (targeted queries). Risks hotspotting if the key is monotonically increasing. Best when range queries on the shard key are the primary access pattern.
- **Compound Shard Key:** Combines multiple fields (e.g., tenant_id + timestamp). First field provides coarse partitioning (e.g., per tenant), subsequent fields provide fine-grained distribution. Best for multi-tenant applications where queries always include the tenant identifier.

**Decision drivers:** Write distribution requirements, primary query patterns (point lookups vs range scans), data growth pattern (monotonic vs distributed), multi-tenancy isolation needs, and whether queries include the shard key.

## See Also

- `general/data.md` — General database strategy, engine selection, and replication patterns
- `general/database-migration.md` — Migration methodology, schema conversion, and cutover planning
- `general/database-ha.md` — Database high availability patterns and failover strategies
- `providers/aws/dynamodb.md` — AWS DynamoDB for serverless NoSQL workloads
- `providers/elasticsearch/search.md` — Elasticsearch for search workloads (alternative to Atlas Search)

## Reference Links

- [MongoDB Architecture Guide](https://www.mongodb.com/docs/manual/core/) -- document model, replication, sharding, and storage engine internals
- [MongoDB Atlas Documentation](https://www.mongodb.com/docs/atlas/) -- managed service configuration, Atlas Search, Atlas Vector Search, and serverless instances
- [MongoDB Schema Design Best Practices](https://www.mongodb.com/developer/products/mongodb/schema-design-anti-pattern-summary/) -- embedding vs referencing patterns and common anti-patterns
- [MongoDB Sharding Documentation](https://www.mongodb.com/docs/manual/sharding/) -- shard key selection, chunk migration, and balancer configuration
- [MongoDB University](https://learn.mongodb.com/) -- free courses on schema design, aggregation, and MongoDB administration
