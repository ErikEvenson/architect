# Confluent / Apache Kafka

## Scope

Apache Kafka event streaming platform and Confluent Platform/Cloud. Covers broker architecture (ZooKeeper and KRaft), topic design (partitions, replication, retention), Schema Registry, ksqlDB, Kafka Connect, Kafka Streams, consumer groups, cluster sizing, security (SASL, ACLs, mTLS, encryption), Confluent Cloud (Basic/Standard/Dedicated clusters), and self-managed deployment patterns.

## Checklist

### Cluster Architecture

- [ ] **[Critical]** Choose cluster coordination mode: ZooKeeper-based (legacy, requires separate ZooKeeper ensemble of 3 or 5 nodes) vs KRaft (Kafka Raft, production-ready since Kafka 3.3 / Confluent Platform 7.4, eliminates ZooKeeper dependency, supports up to 1 million partitions per cluster vs ~200,000 with ZooKeeper)
- [ ] **[Critical]** Size broker count based on throughput, storage, and replication: each broker handles ~100 MB/s aggregate throughput in production (depends on disk, network, replication factor); plan for N+2 brokers minimum so the cluster survives one planned and one unplanned outage simultaneously
- [ ] **[Critical]** Choose deployment model: Confluent Cloud (fully managed, pay-per-use, cluster types Basic/Standard/Dedicated) vs Confluent Platform (self-managed on VMs or Kubernetes) vs open-source Apache Kafka (no Schema Registry, no RBAC, no Tiered Storage, community support only)
- [ ] **[Recommended]** Separate controller nodes from broker nodes in KRaft mode for production clusters with more than 6 brokers; use 3 dedicated controllers for clusters up to ~50 brokers, 5 controllers for larger deployments
- [ ] **[Recommended]** Deploy brokers across 3 or more availability zones / fault domains with `broker.rack` configured; use `min.insync.replicas` with rack-aware replication to guarantee writes survive an AZ failure
- [ ] **[Recommended]** Use dedicated disks for Kafka log directories (not shared with OS); prefer multiple SSD or NVMe volumes per broker with JBOD configuration (`log.dirs=/data/kafka-logs1,/data/kafka-logs2`) for throughput parallelism
- [ ] **[Optional]** Enable Tiered Storage (Confluent Platform 7.0+ / Confluent Cloud Dedicated) to offload cold data to object storage (S3, GCS, Azure Blob), reducing broker disk requirements by 60-80% for long-retention topics

### Topic Design

- [ ] **[Critical]** Set partition count based on target throughput: each partition handles ~10 MB/s write throughput (single producer); total topic throughput = partitions x per-partition throughput; partitions cannot be decreased after creation -- overpartitioning wastes resources, underpartitioning limits parallelism
- [ ] **[Critical]** Configure replication factor of 3 for production topics (tolerates 1 broker failure with `min.insync.replicas=2`); never use replication factor 1 in production; replication factor 2 with `min.insync.replicas=2` blocks all writes on any single broker failure
- [ ] **[Critical]** Set `min.insync.replicas=2` for production topics (with replication factor 3) and use `acks=all` on producers; this combination ensures no acknowledged write is lost even if one broker fails
- [ ] **[Critical]** Design partition key strategy carefully: keys determine ordering guarantees and partition assignment; null keys round-robin across partitions (no ordering); choose keys that distribute evenly (avoid hot partitions) while grouping related events (e.g., customer ID, order ID)
- [ ] **[Recommended]** Configure retention policy per topic based on consumer requirements: `retention.ms` for time-based (default 7 days), `retention.bytes` for size-based, or both (whichever limit is reached first); use `cleanup.policy=compact` for changelog/state topics where only the latest value per key matters
- [ ] **[Recommended]** Use topic naming conventions consistently: `<domain>.<entity>.<event-type>` (e.g., `orders.payments.completed`) or `<environment>.<team>.<dataset>` -- establish and enforce conventions via Confluent Platform Topic Governance or naming validation in CI/CD
- [ ] **[Recommended]** Plan for partition rebalancing: adding partitions to existing topics breaks key-based ordering for in-flight data; prefer creating new topics with the desired partition count and migrating consumers when major throughput changes are needed
- [ ] **[Optional]** Enable idempotent producer (`enable.idempotence=true`, default since Kafka 3.0) to prevent duplicate messages on retries without additional application logic

### Schema Registry

- [ ] **[Critical]** Deploy Schema Registry for all non-trivial Kafka deployments; enforce schema registration before producing (configure producers with `auto.register.schemas=false` in production) to prevent schema drift and breaking changes
- [ ] **[Critical]** Choose schema compatibility mode per subject: BACKWARD (default, new schema can read old data -- safe for consumer upgrades), FORWARD (old schema can read new data -- safe for producer upgrades), FULL (both directions), or NONE (no compatibility checks -- dangerous in production)
- [ ] **[Recommended]** Use Avro, Protobuf, or JSON Schema serialization via Confluent serializers; Avro is most common in Kafka ecosystems due to compact binary format and strong Schema Registry integration; Protobuf preferred for polyglot environments with existing gRPC usage
- [ ] **[Recommended]** Configure Schema Registry in high-availability mode: 2+ instances behind a load balancer, with one elected leader handling writes; uses a Kafka topic (`_schemas`) as its backing store, so HA follows Kafka cluster availability
- [ ] **[Optional]** Implement schema migration strategy for breaking changes: create new topic with new schema, dual-write during transition, migrate consumers, then decommission old topic; avoid NONE compatibility mode as a shortcut

### Kafka Connect

- [ ] **[Critical]** Deploy Kafka Connect in distributed mode for production (not standalone); size Connect worker cluster based on connector count and throughput -- each worker handles ~50-100 tasks depending on complexity; scale horizontally by adding workers
- [ ] **[Recommended]** Use Confluent Hub connectors where available (400+ pre-built connectors) before writing custom connectors; key connectors include JDBC Source/Sink, Debezium CDC (MySQL, PostgreSQL, MongoDB, SQL Server, Oracle), S3 Sink, Elasticsearch Sink, BigQuery Sink
- [ ] **[Recommended]** Configure dead letter queues for sink connectors (`errors.tolerance=all`, `errors.deadletterqueue.topic.name=<dlq-topic>`) to prevent single bad records from blocking entire connector pipelines
- [ ] **[Recommended]** Use Single Message Transforms (SMTs) for lightweight transformations (field renaming, timestamp routing, masking) in Connect; move complex transformations to Kafka Streams or ksqlDB -- Connect is for integration, not business logic
- [ ] **[Optional]** Deploy Debezium for change data capture (CDC) instead of polling-based JDBC connectors; Debezium reads database transaction logs with minimal impact on source database performance and captures deletes (which JDBC source cannot)

### ksqlDB and Kafka Streams

- [ ] **[Recommended]** Choose between ksqlDB (SQL interface, managed processing) and Kafka Streams (Java/Scala library, embedded in applications): ksqlDB for ad-hoc queries, materialized views, and teams preferring SQL; Kafka Streams for complex processing embedded in microservices with full programming language control
- [ ] **[Recommended]** Size ksqlDB clusters based on query complexity and throughput; each persistent query consumes resources proportional to input topic throughput; use `EXPLAIN <query>` to understand processing topology before deploying
- [ ] **[Recommended]** Configure state store management for stateful operations (aggregations, joins, windowed operations): use RocksDB (default) with sufficient local SSD storage; state stores rebuild from changelog topics on restart -- plan for recovery time proportional to state size
- [ ] **[Optional]** Use interactive queries (Kafka Streams) or pull queries (ksqlDB) to expose stream processing state via REST APIs, avoiding the need for a separate database for serving real-time aggregations

### Consumer Groups and Processing

- [ ] **[Critical]** Size consumer groups appropriately: maximum useful consumers in a group equals the number of partitions in the topic -- additional consumers sit idle; too few consumers means each handles more partitions and may fall behind
- [ ] **[Critical]** Configure consumer `session.timeout.ms` (default 45s) and `heartbeat.interval.ms` (default 3s) to balance failure detection speed against false rebalance triggers; set `max.poll.interval.ms` (default 5 minutes) based on maximum per-batch processing time to avoid unnecessary rebalances
- [ ] **[Recommended]** Use static group membership (`group.instance.id`) for containerized/Kubernetes consumers to prevent rebalances during rolling deployments; consumers rejoin with the same assignment if they restart within `session.timeout.ms`
- [ ] **[Recommended]** Implement cooperative sticky partition assignment (`partition.assignment.strategy=cooperative-sticky`) to minimize partition shuffling during rebalances -- only reassigns partitions that need to move, reducing stop-the-world rebalance impact
- [ ] **[Recommended]** Design consumer error handling: implement per-record retry with backoff, dead letter topic for poison pills, and consumer lag alerting; never silently skip or drop failed records without logging and alerting

### Security

- [ ] **[Critical]** Enable encryption in transit: configure TLS/SSL for all broker-to-broker, client-to-broker, and inter-component communication; use separate listeners for internal (SASL_PLAINTEXT acceptable on trusted networks) and external (SASL_SSL mandatory) traffic
- [ ] **[Critical]** Choose authentication mechanism: SASL/SCRAM-SHA-512 (username/password, stored in ZooKeeper/KRaft), SASL/OAUTHBEARER (OAuth 2.0/OIDC, recommended for Confluent Platform with MDS or external IdP), mTLS (certificate-based, strong but complex certificate management), or SASL/GSSAPI (Kerberos, enterprise AD integration)
- [ ] **[Critical]** Enable authorization: Kafka ACLs (open-source, per-resource allow/deny rules) or Confluent RBAC (role-based, integrates with LDAP/AD via Metadata Service -- MDS); define least-privilege ACLs per service account -- never share credentials across applications
- [ ] **[Recommended]** Enable audit logging (Confluent Platform) to track who accessed which topics, produced/consumed messages, and modified configurations; required for compliance (PCI DSS, HIPAA, SOX) and incident investigation
- [ ] **[Recommended]** Encrypt data at rest using filesystem-level encryption (dm-crypt/LUKS, BitLocker) or cloud-provider volume encryption (EBS encryption, Azure Disk Encryption); Kafka does not provide native at-rest encryption
- [ ] **[Optional]** Implement client-side field-level encryption for sensitive data fields (PII, PCI) using Confluent Schema Registry encryption or application-level encryption, allowing different consumers to decrypt only the fields they are authorized to access

### Confluent Cloud Specifics

- [ ] **[Critical]** Choose Confluent Cloud cluster type based on requirements: Basic (shared multi-tenant, 100 MB/s, limited features, dev/test only), Standard (shared multi-tenant, 100 MB/s, Schema Registry, Connectors), Dedicated (single-tenant, up to 20 Gbps, private networking, custom configs, BYOK encryption, commitment discounts)
- [ ] **[Critical]** Configure private networking for Dedicated clusters: AWS PrivateLink, Azure Private Link, or GCP Private Service Connect; public endpoints expose clusters to internet-based attacks even with authentication
- [ ] **[Recommended]** Use Confluent Cloud service accounts with API keys scoped to specific clusters and resources (topic-level ACLs); avoid using organization admin credentials for application access
- [ ] **[Recommended]** Monitor Confluent Cloud Cluster Linking for hybrid architectures: replicate topics between Confluent Cloud and self-managed clusters or across cloud regions with no consumer lag, preserving offsets and topic configuration
- [ ] **[Recommended]** Plan for Confluent Cloud cost management: charges are based on ingress/egress throughput (per GB), partition count, connector task hours, ksqlDB CSU hours, and Schema Registry schemas; Dedicated clusters have base hourly charges regardless of usage

### Observability

- [ ] **[Critical]** Monitor key broker metrics via JMX: `UnderReplicatedPartitions` (>0 indicates broker or disk failure), `ActiveControllerCount` (exactly 1 across cluster), `OfflinePartitionsCount` (>0 means data unavailable), `RequestHandlerAvgIdlePercent` (<0.3 indicates overloaded broker)
- [ ] **[Critical]** Monitor consumer lag per consumer group: `records-lag-max` and `records-lead-min` metrics; use Confluent Control Center, Burrow, or Kafka Exporter for Prometheus; alert when lag exceeds a threshold proportional to acceptable data freshness SLA
- [ ] **[Recommended]** Track producer metrics: `record-send-rate`, `record-error-rate`, `request-latency-avg`; alert on error rate increases which indicate broker issues, authorization failures, or network problems
- [ ] **[Recommended]** Monitor disk usage per broker and partition: set alerts at 70% disk utilization; when a broker disk fills, it stops accepting writes for all partitions on that disk -- cascading to under-replication and potential data loss if multiple brokers fill simultaneously
- [ ] **[Recommended]** Use Confluent Control Center (self-managed) or Confluent Cloud Console for end-to-end stream monitoring, data lineage, consumer group management, and topic inspection; integrate with Prometheus/Grafana via JMX Exporter for infrastructure-level metrics

## Why This Matters

Apache Kafka is the de facto standard for event streaming, powering real-time data pipelines, event-driven architectures, and stream processing at scale. However, Kafka's operational complexity is significantly higher than managed message queues. Incorrect topic design (wrong partition count, replication factor, or retention) leads to data loss, ordering violations, or unrecoverable performance bottlenecks. Consumer group misconfiguration causes cascading rebalances that halt processing for minutes. Security misconfigurations expose sensitive event streams to unauthorized access.

The choice between Confluent Cloud, Confluent Platform, and open-source Kafka determines operational burden, feature availability, and cost trajectory. Confluent Cloud eliminates infrastructure management but introduces vendor lock-in and throughput-based pricing that can escalate quickly. Self-managed deployments provide full control but require dedicated expertise for upgrades, rebalancing, security patching, and capacity planning. Many organizations underestimate Kafka operations -- a 3-broker dev cluster is simple, but a production cluster handling 1 GB/s with 50 consumer groups, Schema Registry, Connect, and ksqlDB requires a dedicated platform team.

## Common Decisions (ADR Triggers)

- **Confluent Cloud vs self-managed Kafka** -- Confluent Cloud eliminates broker management, patching, and capacity planning. Self-managed provides full configuration control, no per-GB throughput charges, and works in air-gapped environments. Use Confluent Cloud when the team lacks dedicated Kafka expertise or when time-to-production matters more than per-GB cost. Use self-managed when running in regulated environments requiring on-premises data residency, when throughput costs exceed infrastructure costs, or when custom broker plugins are needed.
- **KRaft vs ZooKeeper** -- KRaft (Kafka Raft) eliminates the ZooKeeper dependency, simplifies deployment, and supports higher partition counts (1 million+ vs ~200,000). ZooKeeper mode is deprecated as of Kafka 3.5 and will be removed in Kafka 4.0. Use KRaft for all new deployments. Plan ZooKeeper-to-KRaft migration for existing clusters before Kafka 4.0 (target 2025).
- **Avro vs Protobuf vs JSON Schema** -- Avro provides compact binary serialization with the tightest Schema Registry integration and is the Kafka ecosystem default. Protobuf suits polyglot environments already using gRPC and offers better cross-language code generation. JSON Schema is human-readable but larger on the wire and slower to serialize. Use Avro unless there is an existing organizational investment in Protobuf.
- **Kafka Connect vs custom producers/consumers for integration** -- Kafka Connect provides fault-tolerant, scalable, configuration-driven integration with 400+ pre-built connectors, automatic offset management, and dead letter queues. Custom code provides full control but requires implementing offset tracking, error handling, retry logic, and scaling. Use Connect for standard integrations (database CDC, S3 sink, Elasticsearch); use custom code for complex business logic or unsupported systems.
- **ksqlDB vs Kafka Streams vs Flink** -- ksqlDB provides SQL-based stream processing with minimal code, ideal for filtering, aggregation, and joins by teams comfortable with SQL. Kafka Streams is a Java/Scala library embedded in applications, suitable for complex event processing with full programming language capabilities. Apache Flink (available via Confluent Cloud) handles the highest throughput with exactly-once semantics and advanced windowing. Use ksqlDB for team-accessible real-time transformations, Kafka Streams for microservice-embedded processing, and Flink for large-scale stateful stream processing.
- **Topic-per-event-type vs topic-per-entity vs single topic** -- Topic-per-event-type provides clear separation, independent retention, and simple consumer logic but creates many topics. Topic-per-entity (all events for an entity in one topic) preserves entity-level ordering but mixes schemas. Single topic simplifies infrastructure but limits parallelism and mixes unrelated consumers. Default to topic-per-event-type with Schema Registry subject naming strategies; use topic-per-entity when strict entity-level event ordering is required.
- **Exactly-once semantics (EOS) vs at-least-once** -- EOS (idempotent producers + transactional API + `read_committed` consumers) guarantees no duplicates across produce-consume-produce chains but adds 10-20% latency overhead and requires careful transaction timeout tuning. At-least-once with consumer-side idempotency is simpler and sufficient for most workloads. Use EOS for financial transactions, inventory systems, and anywhere duplicates cause monetary impact. Use at-least-once with idempotent consumers for analytics, logging, and event notification.

## Reference Links

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/) -- official Kafka docs covering broker configuration, producer/consumer APIs, and operations
- [Confluent Platform Documentation](https://docs.confluent.io/platform/current/overview.html) -- Confluent Platform installation, configuration, Schema Registry, Connect, ksqlDB, and security
- [Confluent Cloud Documentation](https://docs.confluent.io/cloud/current/overview.html) -- Confluent Cloud cluster management, networking, API keys, and billing
- [Confluent Developer](https://developer.confluent.io/) -- tutorials, courses, and design patterns for Kafka application development
- [KRaft Migration Guide](https://docs.confluent.io/platform/current/installation/migrate-zk-kraft.html) -- step-by-step guide for migrating from ZooKeeper to KRaft mode
- [Schema Registry Documentation](https://docs.confluent.io/platform/current/schema-registry/index.html) -- schema management, compatibility modes, and serializer configuration
- [Kafka Connect Documentation](https://docs.confluent.io/platform/current/connect/index.html) -- connector deployment, configuration, transforms, and monitoring
- [Confluent Hub](https://www.confluent.io/hub/) -- catalog of pre-built Kafka Connect connectors
- [Kafka Broker Configuration Reference](https://kafka.apache.org/documentation/#brokerconfigs) -- complete broker configuration parameter reference
- [Confluent Cloud Cluster Types](https://docs.confluent.io/cloud/current/clusters/cluster-types.html) -- comparison of Basic, Standard, and Dedicated cluster features and limits

## See Also

- `general/data.md` -- General data architecture including event streaming patterns and data pipeline design
- `patterns/event-driven.md` -- Event-driven architecture patterns using Kafka as the backbone
- `patterns/data-pipeline.md` -- Data pipeline patterns including Kafka-based streaming ETL
- `providers/aws/messaging.md` -- AWS MSK (Managed Streaming for Apache Kafka) and alternative AWS messaging services
- `general/security.md` -- General security patterns including encryption, authentication, and authorization
- `general/observability.md` -- Monitoring and alerting strategies applicable to Kafka cluster operations
