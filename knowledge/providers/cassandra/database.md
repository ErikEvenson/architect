# Apache Cassandra

## Scope

This file covers **Apache Cassandra** (and DataStax) architecture decisions: partition key and clustering column design, data modeling from query patterns, compaction strategy selection (STCS, LCS, TWCS), replication factor and consistency level tuning, multi-datacenter replication, cluster sizing and topology, DataStax Astra (managed Cassandra-as-a-Service), DataStax Enterprise (DSE) features, anti-patterns to avoid, and operational procedures (repair, compaction, upgrades). For general database strategy (engine selection, replication patterns, encryption), see `general/data.md`. For migration methodology and cutover planning, see `general/database-migration.md`.

## Checklist

- [ ] **[Critical]** Design partition keys to distribute data evenly and keep partitions under 100 MB (the partition key determines which node owns the data; a partition key with low cardinality like "country" or "status" creates hotspots where a few nodes handle disproportionate load; a partition key with extremely high cardinality like a UUID creates ideal distribution but may prevent efficient range queries; composite partition keys combine multiple columns for controlled distribution — oversized partitions cause GC pressure, slow reads, and compaction bottlenecks; Cassandra will warn at 100 MB partitions and may fail reads on multi-GB partitions)
- [ ] **[Critical]** Model tables from query patterns, not from entity relationships (Cassandra requires one table per query pattern — denormalization is the norm, not the exception; define your queries first, then design tables to serve each query with a single partition read; use clustering columns to define sort order within a partition; avoid secondary indexes on high-cardinality columns as they create a hidden distributed query — relational data modeling applied to Cassandra is the most common cause of poor performance, as multi-partition queries and secondary index scans defeat the purpose of Cassandra's distributed architecture)
- [ ] **[Critical]** Set replication factor and consistency levels to match durability and latency requirements (replication factor 3 is the standard for production; LOCAL_QUORUM for both reads and writes provides strong consistency within a datacenter while tolerating one node failure; ONE provides lowest latency but risks reading stale data; EACH_QUORUM for cross-DC strong consistency at the cost of latency — the formula R + W > RF must hold for strong consistency, where R is read consistency, W is write consistency, and RF is replication factor; LOCAL_QUORUM + LOCAL_QUORUM with RF=3 satisfies this within each DC)
- [ ] **[Critical]** Select compaction strategy based on workload pattern (SizeTieredCompactionStrategy (STCS) is the default, suitable for write-heavy workloads but causes temporary 50% space amplification during major compactions; LeveledCompactionStrategy (LCS) provides more predictable read performance and lower space amplification but higher write amplification — suitable for read-heavy workloads; TimeWindowCompactionStrategy (TWCS) is optimal for time-series data where rows are never updated after initial write — TWCS with TTL provides the best storage efficiency for time-series; choosing the wrong compaction strategy for the workload causes either disk space exhaustion or read latency spikes)
- [ ] **[Critical]** Plan multi-datacenter replication topology for DR and locality (Cassandra supports active-active multi-DC replication natively using NetworkTopologyStrategy; each DC has an independent replication factor; writes to one DC asynchronously replicate to others; use LOCAL_QUORUM to avoid cross-DC latency for most operations; EACH_QUORUM only when cross-DC consistency is required — during a DC failure, clients should failover to the surviving DC; ensure the surviving DC has sufficient capacity to handle full load, not just its normal share)
- [ ] **[Critical]** Configure repair strategy to maintain data consistency (Cassandra is an eventually consistent system that requires periodic repair to reconcile data across replicas; run full repair within gc_grace_seconds interval, which defaults to 10 days — if repair does not complete within this window, deleted data can reappear as "zombie" data because tombstones are garbage-collected before all replicas learn about the deletion; use incremental repair or subrange repair to reduce repair impact on large clusters; Reaper is the standard tool for scheduling and managing repairs across the cluster)
- [ ] **[Recommended]** Size clusters based on data volume, throughput, and operational headroom (each node should hold no more than 1-2 TB of data for manageable repair and streaming times; plan for 50% disk headroom for compaction operations with STCS; provision enough nodes to keep CPU utilization below 50% to handle compaction background I/O alongside query traffic; use a minimum of 3 nodes per datacenter — streaming a new node into a cluster with multi-TB nodes takes hours and impacts performance during the process)
- [ ] **[Recommended]** Evaluate DataStax Astra for managed Cassandra deployment (Astra DB provides serverless Cassandra-as-a-Service on AWS, GCP, and Azure; eliminates operational overhead of repair, compaction tuning, and cluster management; Astra uses Stargate API gateway providing REST, GraphQL, and gRPC interfaces alongside CQL; pricing is based on read/write operations and storage rather than node count — Astra limits certain CQL features like user-defined functions and some configuration tunables; evaluate operational cost savings against reduced configurability)
- [ ] **[Recommended]** Design TTL and tombstone management strategy (TTLs in Cassandra create tombstones that accumulate until compaction removes them after gc_grace_seconds; heavy use of TTLs with short gc_grace_seconds can cause tombstone accumulation that degrades read performance — reads must scan through tombstones to find live data; use TWCS for time-series data with TTLs to ensure entire SSTables expire together without individual tombstone overhead; monitor tombstone counts per read using tracing — queries scanning more than 100,000 tombstones will fail by default)
- [ ] **[Recommended]** Plan upgrade and schema change procedures (rolling upgrades allow zero-downtime upgrades one node at a time; always upgrade sstable format after all nodes are on the new version; schema changes propagate through gossip and can temporarily create schema disagreement — never apply schema changes during high-throughput operations; adding a column is safe; removing a column requires ensuring no application is still writing to it; changing partition key requires creating a new table and migrating data)
- [ ] **[Optional]** Evaluate DataStax Enterprise features for advanced use cases (DSE Search integrates Solr for full-text search on Cassandra data; DSE Graph provides graph database capabilities on Cassandra storage; DSE Analytics integrates Apache Spark for analytics queries; DSE Advanced Replication provides fine-grained replication control between datacenters — DSE features add operational complexity and licensing cost; evaluate whether each feature provides sufficient value over standalone alternatives like Elasticsearch or a separate graph database)
- [ ] **[Optional]** Implement lightweight transactions (LWT) judiciously for conditional operations (IF NOT EXISTS and IF conditions provide linearizable consistency for conditional inserts and updates; LWTs use Paxos consensus requiring 4 round trips between nodes instead of 1 — LWT throughput is 10-20x lower than normal writes; use LWTs sparingly for operations that truly require compare-and-set semantics like unique constraint enforcement; batch normal writes separately from LWT writes as mixing them forces the entire batch through the Paxos path)

## Why This Matters

Apache Cassandra provides linear horizontal scalability and multi-datacenter replication that few other databases match, but achieving these capabilities requires a fundamentally different approach to data modeling than relational databases. The most common Cassandra failure is not hardware — it is data model design that treats Cassandra like a relational database with flexible querying. In Cassandra, the data model must be designed from the query patterns backward: if you need data by user and by date, you create two tables with different partition keys, each denormalized to serve its specific query. Organizations that attempt to normalize data and use secondary indexes or ALLOW FILTERING discover that their "scalable" database performs worse than the single-node relational database it replaced.

Partition design drives everything in Cassandra. A partition that grows unboundedly — like storing all events for a user in a single partition — eventually causes garbage collection pauses, read timeouts, and compaction failures as the partition exceeds hundreds of megabytes. The Bucket pattern (adding a time bucket to the partition key, like user_id + month) distributes data across multiple partitions while preserving query locality. Getting partition design wrong requires table recreation and full data migration, as partition keys cannot be modified on existing tables.

Operational disciplines that are optional in other databases are mandatory in Cassandra. Repair must run regularly to prevent data resurrection from tombstone garbage collection. Compaction must be monitored to prevent disk exhaustion. JVM garbage collection must be tuned because Cassandra runs as a long-lived JVM process where GC pauses directly impact request latency. Organizations that deploy Cassandra without dedicated operational expertise inevitably encounter one of these issues in production, and the remediation is often significantly more disruptive than prevention.

## Common Decisions (ADR Triggers)

### ADR: Cassandra vs Other Distributed Databases

**Context:** The organization needs a horizontally scalable database and must evaluate Cassandra against alternatives.

**Options:**

| Criterion | Apache Cassandra | Amazon DynamoDB | Google Cloud Spanner | CockroachDB |
|---|---|---|---|---|
| Consistency Model | Tunable (eventual to strong) | Strong (per-item) | Strong (global) | Strong (serializable) |
| Multi-Region | Native active-active | Global Tables | Native multi-region | Native multi-region |
| Data Model | Wide-column (CQL) | Key-value / document | Relational (SQL) | Relational (SQL) |
| Operational Overhead | High (self-hosted) | None (serverless) | None (managed) | Moderate (self-hosted) |
| Query Flexibility | Low (query-driven design) | Low (key-based access) | High (SQL joins) | High (SQL joins) |
| Cost Model | Infrastructure + ops | Per-request + storage | Per-node + storage | Infrastructure + ops |

**Decision drivers:** Consistency requirements (strong vs eventual), data model complexity (relational joins needed vs key-based access), multi-region replication needs, operational team expertise, cloud provider commitment, and total cost of ownership.

### ADR: DataStax Astra vs Self-Hosted Cassandra

**Context:** The organization has chosen Cassandra and must decide between managed (Astra) and self-hosted deployment.

**Options:**
- **DataStax Astra:** Serverless pricing based on operations and storage. Zero operational overhead for repair, compaction, and upgrades. Multi-cloud availability. Stargate API layer for REST/GraphQL access. Limited CQL feature set. Higher per-operation cost at large scale.
- **Self-hosted (VM):** Full control over configuration, compaction tuning, and version. Requires DBA expertise for repair scheduling, capacity planning, and upgrades. Lower per-GB cost at scale. Can use any Cassandra version or fork. Operational cost often exceeds infrastructure cost.
- **Self-hosted (Kubernetes with K8ssandra):** K8ssandra operator provides automated deployment, repair (Reaper), and monitoring (Medusa for backups). Reduces operational burden vs raw VM deployment. Adds Kubernetes complexity. Requires understanding of StatefulSet behavior and persistent volume management.
- **DataStax Enterprise (DSE):** Commercial distribution with added features (Search, Graph, Analytics). Includes management tools and support. Higher licensing cost. Features may justify cost if DSE Search or Graph replaces standalone components.

**Decision drivers:** Operational team Cassandra expertise, scale (small clusters favor Astra, large clusters favor self-hosted for cost), need for DSE-specific features, Kubernetes maturity, and support requirements.

### ADR: Compaction Strategy Selection

**Context:** Each Cassandra table must use a compaction strategy that matches its read/write pattern.

**Options:**
- **SizeTieredCompactionStrategy (STCS):** Default strategy. Groups similarly-sized SSTables for compaction. Best for write-heavy workloads. Requires 50% free disk for major compactions. Read amplification increases between compactions as data spreads across many SSTables. Worst-case temporary space usage is the highest of all strategies.
- **LeveledCompactionStrategy (LCS):** Organizes SSTables into levels with guaranteed non-overlapping key ranges per level. Read amplification is low (typically 1-2 SSTables per read). Write amplification is higher (each write may be compacted multiple times across levels). Requires only 10% free disk. Best for read-heavy workloads or workloads with frequent updates.
- **TimeWindowCompactionStrategy (TWCS):** Creates SSTables per time window (e.g., 1 hour). SSTables within the same window are compacted together. Never compacts across time windows. Optimal for time-series data with TTLs where data is never updated after insertion. Entire windows expire simultaneously, avoiding tombstone overhead.

**Decision drivers:** Read vs write ratio, data mutation frequency (updates vs append-only), TTL usage pattern, available disk space, and latency sensitivity for reads.

## See Also

- `general/data.md` — General data strategy, engine selection, and distributed database patterns
- `general/database-migration.md` — Migration methodology and cutover planning
- `general/database-ha.md` — Database high availability patterns and failover strategies
- `providers/mongodb/database.md` — MongoDB for document storage with flexible schema
- `providers/aws/dynamodb.md` — AWS DynamoDB for serverless wide-column workloads

## Reference Links

- [Apache Cassandra Documentation](https://cassandra.apache.org/doc/latest/) -- architecture, CQL, configuration, and operational procedures
- [DataStax Cassandra Documentation](https://docs.datastax.com/) -- DataStax Enterprise features, Astra DB, drivers, and best practices
- [Cassandra Data Modeling Guide](https://cassandra.apache.org/doc/latest/cassandra/data_modeling/index.html) -- query-driven data modeling, partition design, and denormalization patterns
- [K8ssandra Documentation](https://docs.k8ssandra.io/) -- Kubernetes operator for Cassandra with Reaper, Medusa, and Stargate
- [The Last Pickle - Cassandra Blog](https://thelastpickle.com/blog/) -- advanced Cassandra operations, repair strategies, and performance tuning
