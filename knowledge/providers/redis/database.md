# Redis

## Scope

This file covers **Redis** (and Valkey) architecture decisions: clustering topology (Redis Cluster vs Sentinel), persistence modes (RDB snapshots vs AOF), data structure selection and memory optimization, caching patterns vs primary datastore use cases, memory management and eviction policies, Redis Stack (Search, JSON, Time Series, Graph, Probabilistic), pub/sub and Streams for messaging, Lua scripting and Functions, and managed service options (Amazon ElastiCache/MemoryDB, Azure Cache for Redis, Google Memorystore). For general caching strategy and CDN patterns, see `general/data.md`. For AWS-specific ElastiCache configuration, see `providers/aws/elasticache.md`.

## Checklist

- [ ] **[Critical]** Select clustering topology based on availability and scaling requirements (Redis Sentinel provides automatic failover for a single primary with read replicas — suitable for datasets under 25 GB; Redis Cluster provides data sharding across multiple primaries for horizontal scaling of both data and throughput — required when dataset exceeds single-node memory; Sentinel and Cluster are mutually exclusive topologies that require different client configurations and have different failure modes)
- [ ] **[Critical]** Choose persistence strategy based on durability requirements (RDB snapshots provide point-in-time backups at configurable intervals with fork-based snapshotting — fast recovery but potential data loss between snapshots; AOF logs every write operation with configurable fsync policies: always, everysec, or no — everysec balances durability and performance; use both RDB and AOF together for production: RDB for fast restarts and AOF for minimal data loss; disable persistence entirely only for pure cache use cases where data loss is acceptable — RDB fork can cause latency spikes on instances with large datasets due to copy-on-write memory overhead)
- [ ] **[Critical]** Configure memory management and eviction policy appropriate to workload (set maxmemory to 75-80% of available RAM to leave room for fragmentation, replication buffers, and fork overhead; select eviction policy: volatile-lru for cache-with-TTL workloads, allkeys-lru for pure cache, noeviction for primary datastore use cases; monitor memory fragmentation ratio — a ratio above 1.5 indicates significant fragmentation requiring a restart or active-defrag enablement; Redis uses jemalloc, and fragmentation is common with many small keys that are written and deleted frequently)
- [ ] **[Critical]** Design key naming conventions and access patterns to avoid hot keys (use colon-separated hierarchical naming like "service:entity:id:field"; avoid keys that receive disproportionate read/write traffic — a single hot key bottlenecks the thread that handles it since Redis is single-threaded per shard; distribute hot data across multiple keys using consistent hashing or bucketing; use hash tags in Redis Cluster carefully — "{user:123}" forces all matching keys to the same slot, which is necessary for multi-key operations but creates hot slots if overused)
- [ ] **[Critical]** Determine whether Redis serves as cache, primary datastore, or both (cache use case: data exists in another system of record, TTLs on all keys, eviction policy enabled, data loss is inconvenient but not catastrophic; primary datastore: Redis is the source of truth, persistence is mandatory, eviction must be disabled, backup and recovery procedures must be tested — mixing cache and primary datastore in the same Redis instance creates risk where eviction policies can delete primary data to make room for cache entries)
- [ ] **[Recommended]** Select optimal data structures for each use case (Strings for simple key-value and counters; Hashes for object fields to reduce memory vs individual keys; Sorted Sets for leaderboards, rate limiting, and time-based queues; Sets for unique membership and intersection/union operations; Lists for queues and recent activity feeds; Streams for append-only event logs with consumer groups — using Strings for everything wastes 30-50% more memory than using Hashes for objects with multiple fields, due to per-key overhead)
- [ ] **[Recommended]** Plan replication and cross-region strategy (Redis replication is asynchronous by default — replicas may serve stale reads during network partitions; WAIT command provides synchronous replication but blocks the client; for cross-region DR, use active-passive replication with promotion procedures; Redis does not support multi-master replication natively — Active-Active requires Redis Enterprise or application-level conflict resolution; managed services like MemoryDB for Redis provide strong consistency guarantees that open-source Redis does not)
- [ ] **[Recommended]** Evaluate managed Redis services for operational simplicity (Amazon ElastiCache for ephemeral caching with automatic failover; Amazon MemoryDB for Redis as a durable primary database with strong consistency; Azure Cache for Redis with Enterprise tier for Redis Stack modules; Google Memorystore for Redis with automatic failover — managed services handle patching, monitoring, and scaling but limit access to redis.conf, restrict certain commands like CONFIG, KEYS, and DEBUG, and may lag behind open-source versions)
- [ ] **[Recommended]** Implement connection pooling and pipeline optimization (create a connection pool per application instance with appropriate min/max connections; use pipelining to batch multiple commands and reduce round-trip latency — pipelining can improve throughput 5-10x for batch operations; use MULTI/EXEC transactions for atomic multi-command operations; avoid KEYS command in production as it blocks the server during a full keyspace scan — use SCAN for iterative key enumeration)
- [ ] **[Recommended]** Evaluate Valkey as an open-source alternative to Redis (Valkey is a Linux Foundation fork of Redis created after Redis changed to dual-license; API-compatible with Redis 7.2; backed by AWS, Google, Oracle, and Ericsson; Amazon ElastiCache and MemoryDB have migrated to Valkey; Valkey maintains the BSD-3 license — evaluate Valkey for new deployments where Redis licensing terms are a concern, and plan for the ecosystem split where Redis Ltd. features like Redis Stack modules may diverge from Valkey)
- [ ] **[Optional]** Configure Redis Stack modules for extended functionality (RediSearch for full-text search and secondary indexing; RedisJSON for native JSON document storage and querying; RedisTimeSeries for time-series data with downsampling and aggregation; RedisBloom for probabilistic data structures like Bloom filters, Count-Min Sketch, and Top-K — Redis Stack modules consume additional memory and CPU; ensure the managed service tier supports the required modules, as not all tiers include Stack)
- [ ] **[Optional]** Design pub/sub or Streams architecture for messaging (Pub/Sub for fire-and-forget fan-out messaging with no persistence or acknowledgment; Streams for durable, replayable event logs with consumer groups and acknowledgment — Streams are the recommended replacement for Pub/Sub when at-least-once delivery is required; Streams consumer groups provide Kafka-like semantics with XREADGROUP and XACK; pub/sub messages are lost if no subscriber is connected, and in Redis Cluster, pub/sub messages are broadcast to all nodes, consuming cross-node bandwidth)

## Why This Matters

Redis is the most widely deployed in-memory data store, used as both a cache and increasingly as a primary database, but its apparent simplicity hides operational complexity that surfaces at scale. The single-threaded execution model that makes Redis fast and predictable also means a single slow command (KEYS, SMEMBERS on a large set, unoptimized Lua script) blocks all other operations. In production, a developer running KEYS in a debugging session can cause a multi-second outage across all services that depend on that Redis instance.

Memory management is the primary operational challenge. Redis stores all data in RAM, and unlike disk-based databases, running out of memory causes immediate data loss through eviction or outright rejection of writes. The gap between "allocated memory" and "used memory" is often surprising — memory fragmentation, replication buffers, and fork overhead for persistence can consume 2-3x the raw data size. Organizations that provision Redis based on dataset size alone routinely encounter out-of-memory events when persistence operations or replica synchronization double the memory footprint.

The most dangerous anti-pattern is using Redis as a primary datastore without understanding its durability guarantees. With the default AOF everysec configuration, up to one second of writes can be lost during a crash. With RDB-only persistence, the loss window is the interval between snapshots (often 5-15 minutes). Organizations that store financial transactions or session state in Redis without alternative persistence discover these gaps during their first server failure.

## Common Decisions (ADR Triggers)

### ADR: Redis Cluster vs Sentinel

**Context:** The organization needs Redis high availability and must choose between Sentinel (failover only) and Cluster (sharding + failover).

**Options:**

| Criterion | Redis Sentinel | Redis Cluster |
|---|---|---|
| Data Sharding | No (single primary) | Yes (up to 16,384 hash slots across primaries) |
| Max Dataset Size | Limited by single node RAM | Scales across nodes |
| Multi-Key Operations | All keys on same instance | Only within same hash slot |
| Client Complexity | Sentinel-aware client | Cluster-aware client with redirection |
| Minimum Nodes | 3 Sentinels + 1 primary + 1 replica | 6 (3 primaries + 3 replicas) |
| Failover Time | 10-30 seconds | 1-15 seconds |

**Decision drivers:** Dataset size (above or below single-node memory), need for multi-key atomic operations (MULTI/EXEC across keys), client library cluster support, and operational complexity tolerance.

### ADR: Cache vs Primary Datastore

**Context:** Redis is being considered for a workload, and the team must determine whether it serves as a cache layer or the primary system of record.

**Options:**
- **Cache only:** Data always exists in a backing database. TTLs on all keys. Eviction policy (allkeys-lru or volatile-lru) enabled. Cache misses are served from the backing store. Data loss results in increased latency (cache cold start) but no data loss. Simpler operations — can be rebuilt from scratch.
- **Primary datastore:** Redis is the source of truth. No eviction (noeviction policy). Persistence mandatory (AOF + RDB). Backup and restore procedures tested and documented. High availability with automatic failover. Data loss means real data loss. Requires same operational rigor as any production database.
- **Hybrid (same instance):** Some keys are cache (with TTLs), others are primary data (without TTLs). Risk: eviction policies cannot distinguish between cache and primary data unless volatile-* policies are used consistently. Operational ambiguity about which keys are expendable.
- **Hybrid (separate instances):** Dedicated Redis for cache, separate Redis for primary data. Clear operational boundaries. Higher infrastructure cost. Recommended over single-instance hybrid.

**Decision drivers:** Whether a backing datastore exists, durability requirements, acceptable data loss window, operational maturity for managing Redis as a database, and cost of separate instances.

### ADR: Redis vs Valkey

**Context:** Redis re-licensing (SSPL + RSALv2 dual license from Redis 7.4+) requires evaluating whether to continue with Redis or adopt the Valkey fork.

**Options:**
- **Redis (Redis Ltd.):** Original project with Redis Stack modules (Search, JSON, TimeSeries). Dual-licensed — SSPL restricts offering Redis as a managed service. Redis Ltd. continues to add proprietary features. Enterprise support through Redis Ltd.
- **Valkey (Linux Foundation):** Fork of Redis 7.2 under BSD-3 license. Backed by AWS, Google, Oracle. Adopted by Amazon ElastiCache and MemoryDB. Community-driven development. May diverge from Redis in features and APIs over time.
- **KeyDB (Snap):** Multi-threaded Redis fork with higher throughput per node. Less community adoption than Valkey. Different performance characteristics due to multi-threading.

**Decision drivers:** Licensing compliance requirements, managed service provider preference (AWS has migrated to Valkey), need for Redis Stack modules (currently Redis-only), and long-term ecosystem stability preference.

## See Also

- `general/data.md` — General data strategy including caching patterns and data store selection
- `general/database-ha.md` — Database high availability patterns and failover strategies
- `providers/aws/elasticache.md` — AWS ElastiCache and MemoryDB configuration
- `providers/mongodb/database.md` — MongoDB for document storage workloads
- `providers/elasticsearch/search.md` — Elasticsearch for search workloads (alternative to RediSearch)

## Reference Links

- [Redis Documentation](https://redis.io/docs/) -- commands, data types, clustering, persistence, and administration
- [Valkey Documentation](https://valkey.io/docs/) -- Valkey-specific features, migration from Redis, and community roadmap
- [Redis Cluster Specification](https://redis.io/docs/reference/cluster-spec/) -- hash slot distribution, gossip protocol, failover mechanics, and client redirection
- [Amazon MemoryDB Documentation](https://docs.aws.amazon.com/memorydb/) -- durable Redis-compatible database with strong consistency
- [Redis University](https://university.redis.io/) -- free courses on data structures, RediSearch, and Redis Streams
