# AWS ElastiCache

## Checklist

- [ ] [Critical] Is **Valkey** selected as the primary engine for new deployments? (AWS adopted Valkey in 2024 — a Linux Foundation fork of Redis, fully compatible, 20-33% lower pricing than Redis OSS on ElastiCache)
- [ ] [Critical] Is the engine choice documented: Valkey (recommended — best price-performance, active open-source development under Linux Foundation), Redis OSS (legacy, still supported), or Memcached (simple key-value, multi-threaded, no persistence)?
- [ ] [Critical] Is cluster mode enabled for Valkey/Redis workloads that need horizontal scaling beyond a single node's memory limit?
- [ ] [Critical] Are read replicas configured (up to 5 per shard) for read-heavy workloads, and is the application using the reader endpoint?
- [ ] [Critical] Is Multi-AZ with automatic failover enabled for all production replication groups?
- [ ] [Critical] Is encryption at rest enabled with a customer-managed KMS key?
- [ ] [Critical] Is encryption in transit (TLS) enabled, and are clients configured to connect over TLS?
- [ ] [Critical] Is AUTH or IAM-based authentication configured to prevent unauthorized access?
- [ ] [Critical] Is the ElastiCache cluster deployed in private subnets with security groups restricting access to application-tier only?
- [ ] [Recommended] Is the node type right-sized based on memory requirements, connection counts, and network bandwidth? (r7g Graviton nodes for cost efficiency)
- [ ] [Recommended] Are CloudWatch alarms configured for evictions, cache hit ratio, CPU, memory usage, replication lag, and connection count?
- [ ] [Recommended] Is a cache eviction policy (maxmemory-policy) explicitly set? (allkeys-lru for general caching, volatile-lru for mixed key expiry)
- [ ] [Recommended] Is the backup/snapshot retention configured for production clusters to enable point-in-time recovery?
- [ ] [Recommended] Is ElastiCache Serverless evaluated for workloads with unpredictable or spiky cache demand?
- [ ] [Optional] Are parameter groups version-controlled with tuned settings for timeout, maxclients, and tcp-keepalive?

## Why This Matters

Misconfigured caching layers cause cache stampedes, data loss on failover, and security exposure. Unencrypted Redis clusters transmit data in plaintext within the VPC. Missing eviction policies cause out-of-memory crashes. Single-AZ deployment means a full cache loss during AZ failure, causing a thundering herd against the database.

## Engine Comparison: Valkey vs Redis OSS vs Memcached

| Feature | Valkey (Recommended) | Redis OSS | Memcached |
|---|---|---|---|
| **Recommendation** | Primary choice for new deployments | Legacy, still supported | Simple caching only |
| **Governance** | Linux Foundation, open-source (BSD license) | Redis Ltd (dual-license since 2024) | Open-source (BSD) |
| **AWS pricing** | 20-33% lower than Redis OSS | Standard ElastiCache pricing | Standard ElastiCache pricing |
| **Persistence** | Yes (RDB + AOF) | Yes (RDB + AOF) | No |
| **Replication** | Yes (primary + up to 5 replicas) | Yes (primary + up to 5 replicas) | No |
| **Cluster mode** | Yes (horizontal sharding) | Yes (horizontal sharding) | Yes (client-side sharding) |
| **Data structures** | Strings, lists, sets, sorted sets, hashes, streams, HyperLogLog, bitmaps | Same as Valkey | Strings only |
| **Pub/Sub** | Yes | Yes | No |
| **Lua scripting** | Yes | Yes | No |
| **Multi-threaded I/O** | Yes (improved over Redis) | Yes (since Redis 6) | Yes (native) |
| **Transactions** | Yes (MULTI/EXEC) | Yes (MULTI/EXEC) | No (CAS only) |
| **Serverless** | Yes (ElastiCache Serverless) | Yes (ElastiCache Serverless) | No |
| **Client compatibility** | Any Redis client works (wire-compatible) | Native | Memcached clients |
| **Max node memory** | Up to 635 GiB (r7g.16xlarge) | Up to 635 GiB (r7g.16xlarge) | Up to 635 GiB (r7g.16xlarge) |

**Why Valkey is recommended:** AWS adopted Valkey in 2024 after Redis Ltd changed to a dual-license model. Valkey is maintained under the Linux Foundation with contributions from AWS, Google, Oracle, and others. It is wire-compatible with Redis (existing Redis clients and applications work without changes). ElastiCache Valkey nodes are 20-33% cheaper than equivalent Redis OSS nodes. For new deployments, there is no technical reason to choose Redis OSS over Valkey.

## ElastiCache Serverless

ElastiCache Serverless eliminates capacity planning and node management. Key characteristics:

- **Automatic scaling:** Scales compute and memory automatically based on workload demand. No need to select node types or manage cluster resizing.
- **Engines supported:** Valkey and Redis OSS (not Memcached).
- **Pricing model:** Pay for data stored (per GB-hour) and ElastiCache Processing Units (ECPUs) consumed. No per-node charges. More cost-effective for variable workloads; can be more expensive than provisioned for steady high-throughput workloads.
- **High availability:** Built-in Multi-AZ with automatic failover. Data is replicated across multiple AZs.
- **Connectivity:** Accessed via a single endpoint (no cluster configuration needed). VPC-based with security group control.
- **Limits:** Supports up to 5 TB of data storage per cache. Scales to millions of requests per second.
- **Use cases:** Unpredictable or spiky traffic patterns, new applications where cache sizing is uncertain, teams wanting zero operational overhead for caching infrastructure.
- **When to use provisioned instead:** Steady-state high-throughput workloads where provisioned pricing is cheaper, workloads needing more than 5 TB, workloads requiring specific node types or configurations, Memcached engine requirement.

## Common Decisions (ADR Triggers)

- **Valkey vs Redis OSS vs Memcached** [Critical] -- Valkey is recommended for all new deployments (lower cost, open governance, wire-compatible with Redis). Redis OSS for existing workloads not yet migrated. Memcached only for simple key-value caching with no persistence, replication, or complex data structure needs.
- **Cluster mode enabled vs disabled** [Recommended] -- horizontal sharding vs simpler single-shard with replicas
- **ElastiCache Serverless vs provisioned** [Critical] -- auto-scaling and zero management vs predictable pricing and control; Serverless supports Valkey and Redis OSS only
- **Node type selection** [Recommended] -- memory-optimized (r7g) vs general-purpose (m7g), Graviton vs x86
- **Caching strategy** [Recommended] -- cache-aside vs write-through vs write-behind, TTL policies per key pattern
- **High availability model** [Critical] -- Multi-AZ failover vs application-level fallback to database
- **Data tiering** [Optional] -- ElastiCache data tiering (SSD + memory) for large datasets with uneven access patterns

## Reference Architectures

- [AWS Architecture Center: Caching strategies](https://aws.amazon.com/architecture/databases/) -- reference architectures for caching layers with ElastiCache in multi-tier applications
- [AWS Well-Architected Labs: Performance Efficiency](https://www.wellarchitectedlabs.com/performance-efficiency/) -- hands-on labs for caching patterns and performance optimization
- [AWS ElastiCache best practices](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/best-practices.html) -- official best practices for Redis cluster design, scaling, and high availability
- [AWS Prescriptive Guidance: Caching patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/) -- cache-aside, write-through, and session store reference patterns
- [AWS ElastiCache for Redis cluster mode architecture](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Replication.Redis-RedisCluster.html) -- reference design for horizontally scaled Redis with sharding
