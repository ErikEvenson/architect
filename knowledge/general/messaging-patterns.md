# Messaging Patterns

## Scope

Covers messaging architecture patterns for distributed systems including message broker selection, communication models (pub/sub, point-to-point, streaming), delivery guarantees, ordering, dead letter queues, saga patterns, idempotency, and backpressure. Applicable when services communicate asynchronously, when workloads require decoupled processing, or when event-driven architectures need reliable message delivery.

## Checklist

- [ ] **[Critical]** What communication model is required? (point-to-point for task distribution, pub/sub for event fan-out, streaming for ordered log consumption, request-reply for synchronous-over-async)
- [ ] **[Critical]** What delivery guarantee does each message flow require? (at-most-once: fire-and-forget, lowest latency; at-least-once: retry with consumer idempotency; exactly-once: transactional guarantees with higher latency and complexity)
- [ ] **[Critical]** How is consumer idempotency enforced? (idempotency keys in message headers, deduplication tables with TTL, conditional writes, upserts instead of inserts, idempotent operations by design)
- [ ] **[Critical]** Is message ordering required? (strict global ordering via single partition/queue, per-entity ordering via partition keys or message groups, no ordering requirement allows maximum parallelism)
- [ ] **[Critical]** Are dead letter queues (DLQ) configured for every consumer? (maximum retry count before DLQ routing, DLQ monitoring and alerting, manual inspection and replay mechanism, DLQ message enrichment with failure reason)
- [ ] **[Critical]** How are distributed transactions handled? (saga pattern with compensating transactions, choreography-based sagas via events, orchestration-based sagas via a coordinator service like Temporal or Step Functions)
- [ ] **[Critical]** What message broker is selected and why? (RabbitMQ for flexible routing and AMQP, Kafka for high-throughput ordered streaming, cloud-native services like SQS/SNS/EventBridge/Pub/Sub for managed operations, NATS for lightweight low-latency messaging, Redis Streams for simple use cases with existing Redis)
- [ ] **[Recommended]** How is backpressure managed? (consumer-side flow control, queue depth limits with producer blocking or rejection, rate limiting at ingress, auto-scaling consumers based on queue depth or consumer lag, circuit breakers on downstream dependencies)
- [ ] **[Recommended]** What is the message serialization format? (JSON for human readability and debugging, Protobuf for compact binary with schema enforcement, Avro for schema evolution with registry, MessagePack for compact JSON-compatible binary)
- [ ] **[Recommended]** Is there a schema registry for message contracts? (Confluent Schema Registry, AWS Glue Schema Registry, Apicurio -- enforcing backward/forward compatibility, preventing breaking changes)
- [ ] **[Recommended]** What is the message retention policy? (immediate deletion after acknowledgment for queues, time-based retention for streams, indefinite retention for event sourcing, archival to object storage for compliance)
- [ ] **[Recommended]** How are poison messages handled? (messages that repeatedly fail processing, DLQ routing after max retries, structured logging of failure context, alerting on DLQ depth, replay tooling for reprocessing after fix)
- [ ] **[Recommended]** Is the outbox pattern needed for reliable publishing? (transactional outbox to avoid dual-write problems, change data capture from outbox table, polling publisher as simpler alternative, ensures atomicity between database write and message publish)
- [ ] **[Recommended]** How is message routing implemented? (topic-based routing with hierarchical subjects, content-based routing with header or body inspection, consumer groups for load balancing across instances)
- [ ] **[Recommended]** What is the retry strategy? (immediate retry for transient failures, exponential backoff with jitter to prevent thundering herd, maximum retry count before DLQ, separate retry topics/queues for delayed reprocessing)
- [ ] **[Optional]** Is message priority supported? (priority queues for urgent messages, separate high/low priority queues, priority-based consumer allocation)
- [ ] **[Optional]** Is request-reply pattern needed? (correlation IDs for matching responses, dedicated reply queues per consumer or shared reply queue with routing, timeout handling for missing replies)
- [ ] **[Optional]** Are message TTLs configured? (per-message or per-queue expiration, expired message routing to DLQ or silent discard, appropriate TTLs for time-sensitive operations)
- [ ] **[Optional]** Is message batching used for throughput? (producer-side batching to reduce network round trips, consumer-side batch processing for efficiency, batch size and linger time tuning, partial batch failure handling)
- [ ] **[Optional]** Is multi-region messaging required? (cross-region replication for disaster recovery, active-active messaging with conflict resolution, geo-routing for latency-sensitive consumers, federation or mirroring between broker clusters)

## Why This Matters

Messaging patterns are foundational to distributed system reliability. The wrong delivery guarantee leads to data loss (at-most-once) or duplicate processing causing financial errors (at-least-once without idempotency). Missing dead letter queues cause silent message loss with no recovery path. Without backpressure handling, a slow consumer causes unbounded queue growth leading to broker memory exhaustion and cascading failures. Choosing point-to-point when pub/sub is needed forces tight coupling and prevents adding new consumers without modifying producers. The dual-write problem -- writing to a database and publishing a message non-atomically -- is one of the most common sources of data inconsistency in microservices. Saga patterns add significant complexity but are essential for maintaining consistency across service boundaries without distributed transactions.

Broker selection has long-term implications: RabbitMQ excels at flexible routing and traditional messaging but requires careful cluster management; Kafka provides unmatched throughput and replay capability but adds operational complexity and is overkill for simple task queues; cloud-native services minimize operations but create vendor lock-in. The choice should match team expertise, throughput requirements, ordering needs, and operational maturity.

## Common Decisions (ADR Triggers)

- **Message broker selection** -- RabbitMQ vs Kafka vs cloud-native services (SQS/SNS, Pub/Sub, Event Hubs); factors include throughput requirements, ordering guarantees, operational expertise, replay capability, and vendor lock-in tolerance
- **Delivery guarantee per message flow** -- at-most-once vs at-least-once vs exactly-once; determines idempotency requirements, consumer complexity, and performance characteristics
- **Saga pattern approach** -- choreography (event-driven, decentralized) vs orchestration (coordinator-driven, centralized); choreography is simpler for few steps but harder to debug; orchestration provides visibility but adds a single point of failure
- **Outbox pattern adoption** -- transactional outbox with CDC vs direct publish with accept-and-retry; outbox guarantees atomicity but adds infrastructure (CDC tooling like Debezium); direct publish is simpler but risks dual-write inconsistency
- **Schema management strategy** -- schema registry with compatibility enforcement vs schema-less JSON with contract testing; registries prevent breaking changes but add operational overhead
- **Ordering scope** -- strict global ordering (single partition, limits throughput) vs per-entity ordering (partition key, scales horizontally) vs no ordering (maximum parallelism)
- **Backpressure strategy** -- producer-side rate limiting vs consumer auto-scaling vs queue depth limits with rejection; determines system behavior under load and failure cascading
- **Message serialization format** -- JSON vs Protobuf vs Avro; affects message size, schema enforcement, debugging ease, and cross-language compatibility
- **Retry and DLQ strategy** -- immediate retry vs exponential backoff vs separate retry queues; max retries before DLQ; DLQ retention and replay automation
- **Multi-region messaging** -- active-passive replication vs active-active with conflict resolution; broker federation vs application-level routing

## Reference Links

- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/) -- Comprehensive catalog of messaging patterns by Gregor Hohpe and Bobby Woolf
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/) -- Distributed event streaming platform documentation covering producers, consumers, streams, and connect
- [RabbitMQ Documentation](https://www.rabbitmq.com/docs) -- AMQP message broker documentation covering exchanges, queues, clustering, and protocols
- [NATS Documentation](https://docs.nats.io/) -- Lightweight messaging system documentation covering core NATS, JetStream, and key-value store
- [CloudEvents Specification](https://cloudevents.io/) -- CNCF specification for describing event data in a common format across platforms
- [Microservices.io Saga Pattern](https://microservices.io/patterns/data/saga.html) -- Detailed explanation of saga pattern for managing distributed transactions
- [Microservices.io Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html) -- Pattern for reliable message publishing with database atomicity
- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/) -- Schema management for Kafka with compatibility enforcement

## See Also

- `patterns/event-driven.md` -- Event-driven architecture patterns including event sourcing, CQRS, and choreography vs orchestration
- `patterns/microservices.md` -- Microservices architecture where messaging is the primary inter-service communication mechanism
- `patterns/data-pipeline.md` -- Data pipeline architectures using streaming and batch messaging
- `general/data.md` -- Data consistency patterns relevant to distributed messaging and eventual consistency
- `general/observability.md` -- Monitoring message broker health, consumer lag, queue depth, and dead letter queues
- `general/api-design.md` -- API design patterns including async APIs and webhook callbacks
- `providers/aws/messaging.md` -- AWS-specific messaging services (SQS, SNS, EventBridge, Kinesis, MSK)
- `providers/azure/messaging.md` -- Azure-specific messaging services (Service Bus, Event Grid, Event Hubs)
- `providers/gcp/messaging.md` -- GCP-specific messaging services (Pub/Sub, Dataflow)
- `providers/rabbitmq/messaging.md` -- RabbitMQ-specific architecture, AMQP protocol, and deployment patterns
