# Elasticsearch

## Scope

This file covers **Elasticsearch** (and OpenSearch) architecture decisions: index design (mappings, shards, replicas), cluster sizing and node roles, Index Lifecycle Management (ILM) policies, observability vs search use cases and their different design patterns, ELK/EFK stack deployment, security configuration (TLS, RBAC, field-level security), cross-cluster replication and search, snapshot and restore strategy, and managed service options (Elastic Cloud, Amazon OpenSearch Service, Azure Cognitive Search). For general observability strategy, see `general/observability.md`. For application search alternatives, see `providers/mongodb/database.md` (Atlas Search) or `providers/redis/database.md` (RediSearch).

## Checklist

- [ ] **[Critical]** Design index mappings explicitly rather than relying on dynamic mapping (define field types, analyzers, and keyword vs text fields at index creation; dynamic mapping creates both text and keyword sub-fields for every string, doubling storage; text fields are analyzed for full-text search while keyword fields support exact match, sorting, and aggregations — incorrect mapping types cannot be changed on existing indexes, requiring reindexing the entire dataset which can take hours on large indexes and requires temporary double storage)
- [ ] **[Critical]** Size shards appropriately for the workload (target 10-50 GB per shard for time-series/logging data; each shard consumes heap memory on the node — oversized clusters with millions of tiny shards cause heap pressure and slow cluster state updates; too few large shards limit search parallelism and make rebalancing slow; for search use cases, fewer larger shards are better than many small ones — the 20-shards-per-GB-of-heap rule of thumb means a node with 30 GB heap should host no more than 600 shards)
- [ ] **[Critical]** Configure node roles to separate concerns in production clusters (dedicated master-eligible nodes (minimum 3) for cluster state management — never combine master and data roles in production; hot data nodes with SSDs for recent/active data; warm/cold nodes with HDDs for older data; coordinating-only nodes for aggregation-heavy queries; ingest nodes for pipeline processing — a cluster where master nodes also serve data risks split-brain or cluster instability when data nodes are under heavy load)
- [ ] **[Critical]** Implement Index Lifecycle Management (ILM) for time-series data (define phases: hot for active indexing, warm for read-only with fewer replicas, cold for infrequent access with searchable snapshots, frozen for archive with minimal resources, delete for automatic purging; configure rollover based on age, size, or document count; use data tiers with appropriate hardware for each phase — without ILM, logging clusters grow unboundedly until disk fills, causing index read-only blocks that cascade into data loss from upstream log shippers that drop messages)
- [ ] **[Critical]** Enable security features from initial deployment (TLS for transport and HTTP layers; native realm or LDAP/SAML/OIDC for authentication; role-based access control for index-level and field-level permissions; audit logging for compliance; API key management for service accounts — Elasticsearch had no security enabled by default before version 8.0; clusters deployed without TLS are vulnerable to data exfiltration and ransomware; multiple publicized incidents of exposed Elasticsearch clusters leaking millions of records have occurred because security was "planned for later")
- [ ] **[Critical]** Plan cluster sizing based on ingest rate, retention period, and query patterns (calculate daily ingest volume including replicas: raw_daily_GB x (1 + replica_count) x 1.1 overhead; multiply by retention days for total storage; size heap at 50% of RAM, maximum 31 GB (compressed OOPs limit); size CPU for ingest pipeline processing and concurrent query load — undersized clusters exhibit cascading failures where slow queries cause thread pool rejection, which causes upstream buffering, which causes further query slowdown)
- [ ] **[Recommended]** Differentiate architecture for observability vs application search (observability/logging: high ingest rate, time-based indexes, ILM with short hot phase, aggregate queries, acceptable query latency in seconds; application search: lower ingest rate, persistent indexes, relevance tuning, custom analyzers, sub-second query latency required — running observability and application search on the same cluster creates resource contention where a log ingestion spike degrades user-facing search latency)
- [ ] **[Recommended]** Evaluate Elasticsearch vs OpenSearch for new deployments (Elasticsearch relicensed to SSPL + Elastic License from 7.11, returned to open-source AGPL from 8.12; OpenSearch is an Apache 2.0 fork maintained by AWS from Elasticsearch 7.10; feature sets are diverging — Elasticsearch has ESQL, ES|QL, and proprietary ML features; OpenSearch has independent security plugin, alerting, and anomaly detection; Amazon OpenSearch Service is AWS's managed offering based on OpenSearch — migration between them becomes harder as versions diverge)
- [ ] **[Recommended]** Configure snapshot and restore for disaster recovery (register a snapshot repository on S3, GCS, Azure Blob, or shared filesystem; schedule automated snapshots with SLM policies; test restore procedures on a separate cluster regularly; for cross-region DR, replicate snapshots to another region's object storage — snapshot restore is the primary disaster recovery mechanism; cross-cluster replication provides lower RPO but requires Enterprise license for Elasticsearch or is available in OpenSearch)
- [ ] **[Recommended]** Deploy the ELK/EFK stack components appropriately (Logstash for complex event processing, enrichment, and multi-destination routing; Beats/Elastic Agent for lightweight log and metrics shipping; Filebeat with modules for common log formats; Fluentd/Fluent Bit as Logstash alternatives in Kubernetes environments; Kibana/OpenSearch Dashboards for visualization — avoid sending logs directly from applications to Elasticsearch; use a buffer like Kafka or Redis between shippers and Elasticsearch to absorb ingest spikes and prevent backpressure from reaching applications)
- [ ] **[Recommended]** Tune indexing and search performance for production (increase refresh_interval from 1s to 30s for logging use cases to reduce segment creation; use bulk API for batch indexing with 5-15 MB request sizes; configure thread pool sizes based on CPU cores; use index sorting for time-series data to improve compression; enable adaptive replica selection for search — default settings optimize for near-real-time search at the expense of indexing throughput, which is the wrong trade-off for observability use cases)
- [ ] **[Optional]** Implement cross-cluster search and replication for multi-region (cross-cluster search (CCS) queries remote clusters without data replication — suitable for federated search across regions; cross-cluster replication (CCR) maintains follower indexes that replicate from leader indexes — suitable for DR and read locality; CCR is eventually consistent with configurable poll interval — CCS adds network latency to queries; CCR requires careful index pattern planning as follower indexes are read-only)
- [ ] **[Optional]** Evaluate Elastic's ML features for anomaly detection and inference (anomaly detection jobs for automated baseline and alert on log rate changes, latency deviations, and unusual user behavior; trained model inference for NLP tasks like classification, NER, and sentiment analysis directly in ingest pipelines; requires ML nodes with appropriate CPU/memory — ML features are included in Elastic's Platinum/Enterprise tier; OpenSearch provides its own anomaly detection plugin with different capabilities)

## Why This Matters

Elasticsearch is the dominant technology for both log analytics and application search, but these two use cases have fundamentally different architectural requirements. Organizations that deploy a single Elasticsearch cluster for both logging and application search invariably encounter problems: a spike in log ingestion from a production incident consumes all indexing capacity, causing user-facing search to slow or fail at the exact moment when observability is most needed. Separating these workloads into different clusters — or at minimum, different node pools with resource isolation — is essential for production reliability.

The most expensive Elasticsearch mistake is shard proliferation. Each index defaults to one shard, but time-based indexing patterns that create daily indexes (e.g., logs-2024.01.15) accumulate thousands of shards over months. Each shard maintains in-memory data structures that consume heap space regardless of the shard's data size. A cluster with 50,000 shards across 200 daily indexes may spend more heap memory on shard metadata than on actual data caching, resulting in frequent garbage collection pauses and eventual cluster instability. ILM with rollover-based indexing (create new index when current reaches a size threshold) prevents this by controlling shard count independently of time granularity.

Security is non-negotiable but historically overlooked. Before Elasticsearch 8.0, security was disabled by default and required explicit configuration. The result was thousands of internet-exposed Elasticsearch clusters containing sensitive data. Even in internal deployments, lack of RBAC means any application that can reach the cluster can read or delete any index. Field-level security prevents applications from accessing PII fields they do not need, which is a common compliance requirement for GDPR, HIPAA, and PCI DSS.

## Common Decisions (ADR Triggers)

### ADR: Elasticsearch vs OpenSearch

**Context:** The organization needs a distributed search and analytics engine and must choose between the two major forks.

**Options:**

| Criterion | Elasticsearch (Elastic) | OpenSearch (AWS) |
|---|---|---|
| License | AGPL (from 8.12) / SSPL+Elastic License (7.11-8.11) | Apache 2.0 |
| Managed Service | Elastic Cloud (multi-cloud) | Amazon OpenSearch Service (AWS) |
| Security Plugin | Built-in (from 8.0) | OpenDistro Security plugin |
| ML Features | Anomaly detection, NLP inference, ESQL | Anomaly detection, k-NN vector search |
| Community | Elastic-led, large ecosystem | AWS-led, Linux Foundation member |
| Migration From Other | Difficult from OpenSearch 2.x+ | Difficult from Elasticsearch 8.x+ |

**Decision drivers:** Licensing requirements (AGPL vs Apache 2.0 implications), cloud provider alignment (AWS favors OpenSearch), feature requirements (ESQL, Elastic ML vs OpenSearch plugins), existing team expertise, and long-term vendor strategy.

### ADR: Observability vs Search Cluster Architecture

**Context:** The organization uses Elasticsearch for both log/metrics observability and user-facing application search.

**Options:**
- **Single cluster with namespace isolation:** Shared infrastructure, index-level RBAC. Lower cost. Risk of resource contention between logging spikes and search queries. Requires careful capacity planning for combined workloads.
- **Separate dedicated clusters:** Independent clusters for observability and search. Complete resource isolation. Higher infrastructure cost. Independent scaling, tuning, and upgrade schedules. Different ILM policies per use case.
- **Hybrid with dedicated node pools:** Single cluster with hot/warm/cold tiers for logging and dedicated search nodes. Partial resource isolation through node allocation awareness. Moderate cost. Complex configuration.

**Decision drivers:** SLA requirements for application search latency, log ingest volume variability, budget for infrastructure, operational team capacity to manage multiple clusters, and whether observability and search have different retention requirements.

### ADR: Log Pipeline Architecture

**Context:** The organization needs to ship logs and metrics from applications and infrastructure to Elasticsearch.

**Options:**
- **Direct shipping (Beats/Agent to Elasticsearch):** Simplest architecture. Beats ship directly to Elasticsearch. No intermediate buffering. Elasticsearch backpressure directly affects log shippers. Risk of data loss during Elasticsearch maintenance or outages.
- **Buffered pipeline (Beats to Kafka to Logstash to Elasticsearch):** Kafka provides durable buffering between shippers and Elasticsearch. Absorbs ingest spikes. Enables replay from Kafka if Elasticsearch is unavailable. Higher infrastructure complexity and cost. Recommended for high-volume production deployments.
- **Kubernetes-native (Fluent Bit to Fluentd to Elasticsearch):** Fluent Bit as lightweight DaemonSet agent on each node. Fluentd as aggregator with buffering and enrichment. Cloud-native with Kubernetes-aware metadata enrichment. Well-suited for containerized environments.

**Decision drivers:** Log volume (below or above 10 GB/day), tolerance for data loss during outages, Kubernetes vs VM-based infrastructure, need for log enrichment and transformation, and team familiarity with each component.

## See Also

- `general/observability.md` — General observability strategy, metrics, logs, and traces
- `general/data.md` — Data strategy including search and analytics engine selection
- `providers/mongodb/database.md` — MongoDB Atlas Search as an alternative for application search
- `providers/redis/database.md` — Redis Stack RediSearch for search backed by in-memory data
- `providers/splunk/observability.md` — Splunk as an alternative log analytics platform
- `providers/datadog/observability.md` — Datadog as a managed observability alternative

## Reference Links

- [Elasticsearch Reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html) -- index management, mappings, queries, aggregations, and cluster administration
- [OpenSearch Documentation](https://opensearch.org/docs/latest/) -- OpenSearch-specific features, plugins, security configuration, and migration guides
- [Elasticsearch Sizing Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/size-your-shards.html) -- shard sizing, heap sizing, and node configuration best practices
- [Elastic Observability Guide](https://www.elastic.co/guide/en/observability/current/index.html) -- ELK stack deployment for logs, metrics, APM, and uptime monitoring
- [OpenSearch Benchmark](https://opensearch.org/docs/latest/benchmark/) -- performance testing and cluster sizing methodology
