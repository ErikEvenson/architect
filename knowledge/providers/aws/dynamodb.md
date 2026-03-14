# AWS DynamoDB

## Checklist

- [ ] Design primary key carefully: partition key alone (unique item access) or composite key (partition key + sort key for hierarchical data and range queries); key design determines data distribution and query patterns
- [ ] Evaluate single-table design vs multi-table design: single-table maximizes query efficiency by co-locating related entities for single-request access patterns but increases complexity; multi-table is simpler for teams new to DynamoDB
- [ ] Choose capacity mode: on-demand (pay per request, auto-scales to any level, ~6x unit cost) vs provisioned (predictable pricing, requires capacity planning, supports reserved capacity for 1/3-year discounts up to 77% savings)
- [ ] Configure auto-scaling for provisioned capacity with target utilization (typically 70%), scale-in cooldown (5-15 minutes to prevent thrashing), and scale-out cooldown (0-1 minute for fast response)
- [ ] Design Global Secondary Indexes (GSI) for alternative access patterns: each GSI is a full table copy consuming separate throughput; limit to 20 GSIs per table; project only needed attributes to reduce storage and write costs
- [ ] Use Local Secondary Indexes (LSI) only when you need an alternative sort key on the same partition key; LSIs must be created at table creation time, share the table's throughput, and enforce a 10 GB per partition key limit
- [ ] Enable DynamoDB Streams for change data capture: choose stream view type (KEYS_ONLY, NEW_IMAGE, OLD_IMAGE, NEW_AND_OLD_IMAGES); Lambda triggers process stream records with exactly-once per-item guarantee within a shard
- [ ] Configure Time To Live (TTL) on a designated attribute for automatic item expiration at no cost; expired items are deleted within 48 hours and appear in Streams with a deletion marker for downstream processing
- [ ] Enable point-in-time recovery (PITR) for continuous backups with 35-day recovery window; supports restore to any second within the window to a new table; on-demand backups for long-term retention
- [ ] Implement DAX (DynamoDB Accelerator) for microsecond read latency on read-heavy workloads; DAX is a write-through cache requiring no application code changes (same API); choose r-type instances for memory-intensive caching
- [ ] Configure global tables for multi-region active-active replication with sub-second replication latency; requires DynamoDB Streams enabled, same table name in all regions, and on-demand or provisioned capacity in each region
- [ ] Avoid hot partitions by distributing writes across partition keys; use write sharding (append random suffix to partition key) for high-throughput counters; adaptive capacity automatically isolates hot items but doesn't prevent throttling
- [ ] Use DynamoDB transactions (TransactWriteItems, TransactGetItems) for ACID operations across up to 100 items or 4 MB; transactions cost 2x the WCU/RCU of non-transactional operations

## Why This Matters

DynamoDB provides single-digit millisecond latency at any scale with zero operational overhead -- no patching, no capacity planning (on-demand mode), no replication configuration (global tables). However, it requires fundamentally different data modeling compared to relational databases. Data must be modeled around access patterns rather than normalized relationships, and key design decisions made at table creation are difficult or impossible to change later.

Poor partition key design leads to hot partitions and throttling even when aggregate capacity is sufficient. Missing or excessive GSIs waste throughput and storage. Choosing the wrong capacity mode can result in 6x cost overruns (on-demand for predictable workloads) or throttling during traffic spikes (provisioned without auto-scaling). Understanding these tradeoffs before building is critical because DynamoDB's schema-on-write approach means restructuring requires table migration.

## Common Decisions (ADR Triggers)

- **DynamoDB vs relational database (RDS/Aurora)** -- DynamoDB for known, finite access patterns requiring single-digit millisecond latency at any scale, key-value or document data models, and serverless architectures. Relational databases for complex ad-hoc queries, JOIN-heavy access patterns, strict referential integrity, and data models that evolve with unknown future query needs. DynamoDB is a poor fit if you need flexible querying, aggregations, or if you cannot enumerate access patterns upfront.
- **Single-table vs multi-table design** -- Single-table design stores multiple entity types (users, orders, products) in one table using overloaded partition/sort keys (e.g., PK=USER#123, SK=ORDER#456). This enables fetching related entities in a single Query operation, reducing latency and cost. Multi-table design is simpler to understand, works well with DynamoDB's on-demand backups per table, and avoids the learning curve. Use single-table for high-performance microservices; multi-table for team simplicity and when access patterns don't require cross-entity queries.
- **On-demand vs provisioned capacity** -- On-demand is ideal for new tables with unknown traffic, spiky/unpredictable workloads, and when development simplicity outweighs cost optimization. Provisioned is better for predictable workloads where reserved capacity discounts apply. On-demand costs ~$1.25 per million writes and ~$0.25 per million reads; provisioned with reserved capacity can reduce this by 53-77%. On-demand can instantly handle up to 2x the previous peak; for truly sudden spikes beyond 2x, provisioned with appropriate auto-scaling may be more reliable.
- **DAX vs ElastiCache** -- DAX is a drop-in write-through cache for DynamoDB with API compatibility (same SDK calls). ElastiCache (Redis/Memcached) is a general-purpose cache that can aggregate data from multiple sources. Use DAX for read-heavy DynamoDB workloads with simple caching needs. Use ElastiCache when caching computed results, session data, or data from multiple sources, or when you need data structures beyond key-value.
- **DynamoDB Streams vs Kinesis Data Streams for DynamoDB** -- DynamoDB Streams retain data for 24 hours with 2 simultaneous consumers per shard. Kinesis Data Streams for DynamoDB supports up to 365-day retention, multiple consumers via enhanced fan-out, and integration with Kinesis ecosystem (Firehose, Analytics). Use Kinesis when you need more than 2 consumers or longer retention.
- **Global tables vs application-managed replication** -- Global tables provide managed multi-region active-active with last-writer-wins conflict resolution. This is sufficient for most use cases but may not work for applications needing custom conflict resolution. If conflicts must be merged rather than overwritten, consider application-level replication via DynamoDB Streams to Lambda.

## Reference Architectures

### Serverless API with Single-Table Design
API Gateway -> Lambda -> DynamoDB single table. Entity types: User (PK=USER#id), Order (PK=USER#id, SK=ORDER#timestamp), Product (PK=PRODUCT#id). GSI1 inverted index (GSI1PK=ORDER#id) for order lookup. GSI2 for product category queries. On-demand capacity for unpredictable traffic. DAX cluster in front for read-heavy product catalog queries.

### Event Sourcing with DynamoDB Streams
DynamoDB table (PK=AggregateID, SK=EventVersion) storing domain events. DynamoDB Streams (NEW_IMAGE) -> Lambda function -> EventBridge for publishing to downstream services. Materialized views in separate DynamoDB tables built from stream processing. PITR enabled for recovery. TTL on projection tables for time-bounded data.

### Multi-Region Active-Active Application
DynamoDB global table replicated across us-east-1, eu-west-1, ap-southeast-1. Route 53 latency-based routing to nearest API Gateway. Lambda functions read/write to local regional table. Last-writer-wins conflict resolution acceptable for user profiles and preferences. Sensitive operations (payments) route to a single designated primary region via explicit API design to avoid conflicts.

### Time-Series Data with TTL
DynamoDB table with PK=DeviceID, SK=Timestamp. Hot data in DynamoDB with TTL set to 90 days for automatic cleanup. DynamoDB Streams -> Kinesis Data Firehose -> S3 (Parquet) for long-term analytics storage before TTL expiration. Separate GSI on status attribute for active alert queries. On-demand capacity for IoT workloads with unpredictable device counts.
