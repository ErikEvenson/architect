# Azure Cosmos DB

## Scope

Azure Cosmos DB is a globally-distributed, multi-model database service. Covers the API surfaces (NoSQL / SQL, MongoDB, Cassandra, Gremlin, Table, PostgreSQL via Citus), the five **consistency models** and what they cost in latency and availability, **partition key** design and the consequences of getting it wrong, the request unit (RU/s) capacity model (provisioned vs serverless vs autoscale), multi-region writes (multi-master), the change feed for event-driven workloads, **vector search** for AI/ML workloads, indexing policy, conflict resolution in multi-write topologies, and the integration with Synapse Link for HTAP analytics. Does not cover Cosmos DB for PostgreSQL (the Citus-based service) in depth — that is closer to a Postgres deployment than a Cosmos DB deployment.

## Checklist

- [ ] **[Critical]** Choose the **partition key** deliberately and document the choice. The partition key determines how data is physically distributed across partitions, and a bad choice produces hot partitions (throughput throttling), cold partitions (wasted RU/s), or storage limits per logical partition (20 GB hard limit). Common bad choices: timestamp-based keys (all writes hit the latest partition), customer ID with one giant customer, status fields with low cardinality. Common good choices: composite keys that distribute writes evenly while keeping related reads on the same partition.
- [ ] **[Critical]** Choose the **consistency model** based on the application requirement, not by default. Cosmos DB offers five levels (Strong, Bounded Staleness, Session, Consistent Prefix, Eventual). **Session** is the default and is the right answer for most applications (a client sees its own writes). **Strong** is rarely the right answer because it precludes multi-region writes and increases latency. **Eventual** is rarely the right answer because the application has to handle out-of-order reads. Document the choice per workload.
- [ ] **[Critical]** For multi-region deployments, decide between **single-region writes** (one primary region, replicas in other regions) and **multi-region writes / multi-master** (every region accepts writes, with conflict resolution). Multi-master is harder to reason about and requires conflict resolution logic; use it only when the latency benefit of writes-from-anywhere is required and the conflict scenarios are understood.
- [ ] **[Critical]** Use **provisioned throughput with autoscale** instead of standard provisioned for variable workloads. Autoscale provisions a maximum RU/s and automatically scales down to 10% of the maximum during idle periods, cutting cost without manual intervention. Standard provisioned is appropriate only for steady, predictable workloads.
- [ ] **[Critical]** Use **serverless** for development, test, and low-volume production workloads with bursty traffic. Serverless billing is per-RU-consumed with no minimum, which can be much cheaper than provisioned for workloads with low average throughput. Serverless has limits (no global distribution, no autoscale, max 5K RU/s, max 50 GB) — outside those limits, provisioned is required.
- [ ] **[Critical]** Restrict network access via **private endpoints** or **service endpoints with firewall rules**. By default a Cosmos DB account accepts traffic from any public IP. Lock it down to specific VNets or specific source IPs. The "publicly reachable Cosmos DB" finding is one of the most common in any Azure baseline review.
- [ ] **[Critical]** Use **customer-managed keys (CMK)** in Key Vault for any production database holding sensitive data. The default Microsoft-managed key is sufficient for non-regulated workloads only — CMK provides demonstrable customer control of the key and integrates with the broader key lifecycle management.
- [ ] **[Recommended]** Tune the **indexing policy** for the workload. Cosmos DB indexes every property by default, which is convenient but expensive — every index update consumes RU/s. For read-heavy workloads, the default is fine. For write-heavy workloads, exclude paths that are not queried to reduce RU consumption.
- [ ] **[Recommended]** Use the **change feed** for event-driven downstream processing (materialized views, search index updates, analytics pipeline triggers). The change feed is a built-in CDC mechanism that does not consume separate RU/s for the read side and is the supported pattern for "react to writes".
- [ ] **[Recommended]** For analytics on Cosmos DB data, use **Synapse Link** instead of querying the operational store directly. Synapse Link maintains a column-store representation of the Cosmos DB data that can be queried by Synapse without consuming operational RU/s. This is the right pattern for any HTAP workload.
- [ ] **[Recommended]** Configure **continuous backup** with the appropriate retention. Cosmos DB offers periodic backup (default, free, point-in-time recovery within the retention window) and continuous backup (paid, point-in-time recovery to any moment within the last 7 or 30 days). Continuous backup is the right answer for any production database where the recovery point objective is "as recent as possible".
- [ ] **[Optional]** For AI/ML workloads requiring vector similarity search, use **Cosmos DB for NoSQL with vector search** (or Cosmos DB for MongoDB with vector index, depending on the API surface in use). Vector search in Cosmos DB is integrated with the operational store, which avoids the need for a separate vector database for many use cases.
- [ ] **[Optional]** For workloads that need to integrate with Apache Cassandra clients, use the **Cassandra API**. For workloads that need MongoDB driver compatibility, use the **MongoDB API**. The native NoSQL API has the deepest feature support and is the right choice when there is no compatibility requirement.

## Why This Matters

Cosmos DB is one of the easiest databases in Azure to misuse expensively. Three failure modes drive most of the cost surprises and most of the performance complaints:

1. **Bad partition key.** A partition key that creates hot partitions causes throttling errors at low overall RU/s utilization, which the application sees as "the database is slow" even though most of the provisioned throughput is unused. The fix is partition key redesign, which usually requires data migration. Getting the partition key right at the start is much cheaper than fixing it later.
2. **Default indexing on write-heavy workloads.** The default indexing policy indexes every property, which is convenient but means every property update consumes RU/s for the index update. Workloads that write large documents with many properties can spend 80% of their RU consumption on index maintenance rather than on the actual writes. The fix is excluding paths from indexing for properties that are not queried — usually a one-time tuning exercise that cuts RU consumption substantially.
3. **Wrong consistency model.** Strong consistency precludes multi-region writes and adds latency; Eventual makes the application reason about out-of-order reads. Session is the right default for most applications but is not always the chosen one because the documentation discusses all five at equal length. Picking the right model is a per-workload decision and should be documented.

A secondary failure mode is **multi-master without understanding conflict resolution**. Multi-master allows writes in every region but requires the application to handle conflicts when the same document is updated concurrently in two regions. Cosmos DB offers Last-Writer-Wins (the default, with a configurable conflict resolution path) and Custom (a stored procedure that resolves conflicts). Last-Writer-Wins is fine for many applications but is wrong for workloads where the lost updates matter — and the audit consequence is that the application silently loses data when conflicts occur.

## Common Decisions (ADR Triggers)

- **API surface** — NoSQL (the native API) for new workloads with no compatibility requirement. MongoDB API for migrating existing MongoDB workloads. Cassandra / Gremlin / Table for the specific compatibility cases. PostgreSQL is a different service (Cosmos DB for PostgreSQL via Citus) and is closer to a Postgres deployment.
- **Provisioned vs serverless vs autoscale** — autoscale for variable workloads with predictable peaks. Standard provisioned for steady workloads with predictable throughput. Serverless for development, test, and bursty production workloads under the serverless limits.
- **Single-region vs multi-region** — single-region for any workload that does not have an explicit availability or latency requirement justifying the cost. Multi-region (read replicas) for workloads with users in multiple geographies. Multi-master only when writes-from-anywhere is required and conflict scenarios are understood.
- **Consistency model** — Session by default. Strong only when the application cannot tolerate any staleness and the latency cost is acceptable. Bounded Staleness for "Strong, but with a defined staleness window for performance". Eventual for the rare workload where read-your-writes is not required.
- **Customer-managed key vs Microsoft-managed key** — CMK for regulated and sensitive workloads. MMK for everything else. The decision should be made per data classification.
- **Periodic vs continuous backup** — periodic (free) for workloads where the default 30-day point-in-time recovery is sufficient. Continuous (paid) for workloads where the recovery point needs to be "as recent as possible" and where 30-day continuous PITR is required.

## Reference Architectures

### High-throughput global API backed by Cosmos DB

- **Cosmos DB for NoSQL**, autoscale provisioned throughput at the database level
- **Multi-region** distribution: write region in `East US`, read replicas in `West Europe` and `Southeast Asia`
- **Single-region writes** (not multi-master); the API layer routes writes to the primary region via Front Door routing rules
- **Session consistency** (the default)
- **Partition key** is `/tenantId` for a multi-tenant SaaS workload (each tenant gets its own logical partition, scaling per-tenant)
- **Customer-managed key** in Key Vault for the storage encryption
- **Private endpoint** in each region's workload VNet; no public network access
- **Continuous backup** with 30-day PITR
- **Change feed** drives a downstream search index update via Functions

### Event sourcing / CQRS with Cosmos DB

- **Cosmos DB for NoSQL** as the event store (immutable append-only writes)
- **Provisioned autoscale**, partition key is `/aggregateId`
- **Change feed** drives projections to other Cosmos DB containers, to Synapse for analytics, and to Service Bus for downstream consumers
- **Session consistency**
- **Indexing** restricted to the few properties used for "find events for aggregate X" queries; everything else excluded for write performance

### Vector search for retrieval-augmented generation

- **Cosmos DB for NoSQL** with vector search enabled
- **Embeddings** stored as a vector property on each document
- **Index policy** includes a vector index on the embedding property (DiskANN or quantizedFlat depending on document count)
- Query pattern is "find top-K nearest neighbors" with optional filter by other properties
- Used as the retrieval backend for an LLM pipeline; complements but does not replace a dedicated vector database for very large or specialized workloads

---

## Reference Links

- [Azure Cosmos DB documentation](https://learn.microsoft.com/azure/cosmos-db/)
- [Choosing the right consistency level](https://learn.microsoft.com/azure/cosmos-db/consistency-levels)
- [Partitioning and horizontal scaling](https://learn.microsoft.com/azure/cosmos-db/partitioning-overview)
- [Request units in Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/request-units)
- [Change feed in Azure Cosmos DB](https://learn.microsoft.com/azure/cosmos-db/change-feed)
- [Vector search in Cosmos DB for NoSQL](https://learn.microsoft.com/azure/cosmos-db/nosql/vector-search)

## See Also

- `providers/azure/database.md` — broader Azure database service set (SQL, PostgreSQL, MySQL, Cosmos summary)
- `providers/azure/key-vault.md` — CMK storage and rotation
- `providers/azure/networking.md` — private endpoint configuration
- `providers/aws/dynamodb.md` — equivalent globally-distributed NoSQL service in AWS
- `general/data.md` — general data architecture and storage tier selection
- `patterns/cqrs-event-sourcing.md` — event sourcing pattern (when added)
