# AWS ElastiCache

## Checklist

- [ ] Is Redis chosen over Memcached when persistence, replication, pub/sub, Lua scripting, or complex data structures are needed?
- [ ] Is cluster mode enabled for Redis workloads that need horizontal scaling beyond a single node's memory limit?
- [ ] Are read replicas configured (up to 5 per shard) for read-heavy workloads, and is the application using the reader endpoint?
- [ ] Is Multi-AZ with automatic failover enabled for all production replication groups?
- [ ] Is encryption at rest enabled with a customer-managed KMS key?
- [ ] Is encryption in transit (TLS) enabled, and are clients configured to connect over TLS?
- [ ] Is Redis AUTH or IAM-based authentication configured to prevent unauthorized access?
- [ ] Is the ElastiCache cluster deployed in private subnets with security groups restricting access to application-tier only?
- [ ] Is the node type right-sized based on memory requirements, connection counts, and network bandwidth? (r7g Graviton nodes for cost efficiency)
- [ ] Are CloudWatch alarms configured for evictions, cache hit ratio, CPU, memory usage, replication lag, and connection count?
- [ ] Is a cache eviction policy (maxmemory-policy) explicitly set? (allkeys-lru for general caching, volatile-lru for mixed key expiry)
- [ ] Is the backup/snapshot retention configured for production clusters to enable point-in-time recovery?
- [ ] Is ElastiCache Serverless evaluated for workloads with unpredictable or spiky cache demand?
- [ ] Are parameter groups version-controlled with tuned settings for timeout, maxclients, and tcp-keepalive?

## Why This Matters

Misconfigured caching layers cause cache stampedes, data loss on failover, and security exposure. Unencrypted Redis clusters transmit data in plaintext within the VPC. Missing eviction policies cause out-of-memory crashes. Single-AZ deployment means a full cache loss during AZ failure, causing a thundering herd against the database.

## Common Decisions (ADR Triggers)

- **Redis vs Memcached** -- feature richness and persistence vs simplicity and multi-threaded performance
- **Cluster mode enabled vs disabled** -- horizontal sharding vs simpler single-shard with replicas
- **ElastiCache Serverless vs provisioned** -- auto-scaling and zero management vs predictable pricing and control
- **Node type selection** -- memory-optimized (r7g) vs general-purpose (m7g), Graviton vs x86
- **Caching strategy** -- cache-aside vs write-through vs write-behind, TTL policies per key pattern
- **High availability model** -- Multi-AZ failover vs application-level fallback to database
- **Data tiering** -- ElastiCache data tiering (SSD + memory) for large datasets with uneven access patterns

## Reference Architectures

- [AWS Architecture Center: Caching strategies](https://aws.amazon.com/architecture/databases/) -- reference architectures for caching layers with ElastiCache in multi-tier applications
- [AWS Well-Architected Labs: Performance Efficiency](https://www.wellarchitectedlabs.com/performance-efficiency/) -- hands-on labs for caching patterns and performance optimization
- [AWS ElastiCache best practices](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/best-practices.html) -- official best practices for Redis cluster design, scaling, and high availability
- [AWS Prescriptive Guidance: Caching patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/caching-strategies/) -- cache-aside, write-through, and session store reference patterns
- [AWS ElastiCache for Redis cluster mode architecture](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/Replication.Redis-RedisCluster.html) -- reference design for horizontally scaled Redis with sharding
