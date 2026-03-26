# RabbitMQ Messaging

## Scope

Covers RabbitMQ architecture, AMQP 0-9-1 protocol, exchange types, queue types (classic, quorum, streams), clustering, high availability, federation, shovel, management and monitoring, performance tuning, and deployment patterns. Applicable when RabbitMQ is selected as the message broker for inter-service communication, task distribution, or event routing.

## Checklist

- [ ] **[Critical]** What exchange types are used and why? (direct: exact routing key match for point-to-point; fanout: broadcast to all bound queues for pub/sub; topic: wildcard routing key patterns for flexible routing; headers: attribute-based routing independent of routing key)
- [ ] **[Critical]** Are quorum queues used for replicated, durable workloads? (quorum queues replace classic mirrored queues as of RabbitMQ 3.13+, Raft-based consensus for data safety, configurable replication factor, automatic leader election on node failure, mandatory for production data-critical queues)
- [ ] **[Critical]** Is publisher confirms enabled for reliable message delivery? (asynchronous confirms for throughput, synchronous confirms for strict guarantees, batch confirms for balanced approach, handling nack responses with retry logic)
- [ ] **[Critical]** Is consumer acknowledgment configured correctly? (manual ack for reliable processing, automatic ack only for fire-and-forget, reject with requeue for transient failures, reject without requeue to DLQ for permanent failures, prefetch count to limit unacknowledged messages)
- [ ] **[Critical]** Are dead letter exchanges (DLX) configured? (DLX bound to dead letter queues for failed/expired/rejected messages, per-queue DLX configuration, DLQ monitoring and alerting, message headers enriched with rejection reason and original exchange/routing key)
- [ ] **[Critical]** Is the cluster sized appropriately? (minimum 3 nodes for quorum queue fault tolerance, odd number of nodes to avoid split-brain, separate disk and RAM nodes only for classic queues, all nodes should be disk nodes for quorum queues)
- [ ] **[Recommended]** Is consumer prefetch (QoS) tuned? (prefetch count limits unacknowledged messages per consumer, too low underutilizes consumers, too high causes uneven distribution, start with prefetch 10-50 and adjust based on message processing time)
- [ ] **[Recommended]** Are message TTLs and queue TTLs configured? (per-message TTL for time-sensitive operations, per-queue TTL as default expiration, queue auto-delete and expiry for temporary queues, expired messages routed to DLX)
- [ ] **[Recommended]** Is the management plugin enabled with appropriate access controls? (HTTP API for monitoring and administration, separate admin and monitoring users, RBAC with vhost-level permissions, disable guest user in production)
- [ ] **[Recommended]** Are virtual hosts (vhosts) used for logical separation? (separate vhosts per application or environment, independent permissions per vhost, resource limits per vhost in RabbitMQ 3.13+, default "/" vhost should not be used in production)
- [ ] **[Recommended]** Is TLS configured for all connections? (TLS for client connections on port 5671, TLS for inter-node communication, TLS for management plugin, certificate rotation strategy, mutual TLS for service authentication)
- [ ] **[Recommended]** Are RabbitMQ Streams evaluated for log-based workloads? (append-only log structure similar to Kafka, non-destructive consumer reads with offsets, high throughput for fan-out patterns, stream protocol for dedicated client support, useful for replay and audit requirements)
- [ ] **[Recommended]** Is lazy queue mode considered for memory management? (lazy queues store messages to disk as early as possible, reduces memory usage for large backlogs, slightly higher latency for message delivery, appropriate for consumers that fall behind)
- [ ] **[Recommended]** How is the cluster monitored? (queue depth and growth rate, consumer count per queue, message rates per exchange, node memory and disk usage, file descriptor usage, Erlang process count, connection and channel counts, Prometheus endpoint for metrics export)
- [ ] **[Recommended]** Are alarms configured for resource limits? (memory alarm triggers at configurable threshold -- default 40% of system RAM, disk alarm triggers when free space drops below limit, connection blocking when alarms fire, flow control backpressure on publishers)
- [ ] **[Optional]** Is shovel or federation needed for cross-cluster messaging? (shovel for reliable point-to-point message forwarding between clusters, federation for decentralized exchange/queue linking across sites, shovel for WAN-connected datacenters, federation for loosely coupled multi-site deployments)
- [ ] **[Optional]** Are priority queues needed? (up to 255 priority levels, each priority level uses a separate internal queue, high priority count increases memory usage, typically 1-10 priority levels is sufficient)
- [ ] **[Optional]** Is the consistent hash exchange plugin needed? (distributes messages across queues based on routing key hash, useful for sharding workloads across parallel consumers, built-in plugin requires enabling)
- [ ] **[Optional]** Are queue length limits configured? (max-length or max-length-bytes to cap queue size, overflow behavior: drop-head discards oldest, reject-publish blocks producers, reject-publish-dlx routes to DLX, prevents unbounded queue growth)
- [ ] **[Optional]** Is the delayed message exchange plugin needed? (schedule message delivery for future processing, useful for retry delays and scheduled tasks, plugin must be installed separately, alternative: TTL + DLX for fixed delay patterns)

## Why This Matters

RabbitMQ is one of the most widely deployed message brokers, supporting AMQP, MQTT, and STOMP protocols with flexible routing capabilities that exceed most alternatives. Its exchange-binding-queue model provides routing patterns from simple point-to-point to complex content-based routing without application code changes. However, RabbitMQ requires careful configuration to be production-ready.

Using classic mirrored queues instead of quorum queues risks data loss during network partitions and node failures -- quorum queues with Raft consensus are the only safe choice for durable workloads. Missing publisher confirms means messages can be silently lost between the producer and broker. Incorrect prefetch settings cause either consumer starvation or uneven load distribution. Without dead letter exchanges, failed messages disappear with no recovery path. Cluster sizing below three nodes eliminates the fault tolerance that quorum queues provide. Memory and disk alarms, when not monitored, cause connection blocking that cascades to application-level failures.

RabbitMQ Streams, introduced in 3.9, provide Kafka-like log semantics within RabbitMQ, enabling offset-based consumption and replay without deploying a separate streaming platform. This is valuable for teams that need both traditional messaging and streaming patterns in a single broker.

## Common Decisions (ADR Triggers)

- **Quorum queues vs classic queues** -- quorum queues provide Raft-based replication with automatic leader election and are mandatory for data-critical workloads; classic queues have lower latency and resource usage for non-critical, transient workloads; classic mirrored queues are deprecated as of RabbitMQ 3.13
- **Exchange type selection** -- direct for simple routing, topic for flexible pattern matching (e.g., `order.*.created`), fanout for broadcast, headers for attribute-based routing; exchange topology design affects system flexibility and performance
- **RabbitMQ Streams vs traditional queues** -- streams for log-based consumption with offset tracking, replay capability, and high fan-out; traditional queues for competing consumers, per-message routing, and acknowledgment-based processing; streams add Kafka-like capabilities without a separate platform
- **Shovel vs federation for multi-site** -- shovel provides reliable unidirectional or bidirectional message forwarding with exact delivery semantics; federation provides decentralized exchange/queue linking where each site operates independently; shovel for deterministic replication, federation for loosely coupled sites
- **Single cluster vs multi-cluster with federation** -- single cluster simplifies operations but limits geographic distribution; multi-cluster with federation provides site-level independence and WAN tolerance but adds operational complexity and eventual consistency between sites
- **Vhost strategy** -- per-application vhosts for isolation and independent permissions; per-environment vhosts for dev/staging/prod separation on shared clusters; single vhost with naming conventions for simple deployments
- **Connection and channel management** -- one connection per application with multiple channels vs connection pooling; channel-per-thread model for thread safety; connection recovery and topology recovery strategy
- **Message persistence** -- persistent messages (delivery mode 2) with durable queues for guaranteed durability; transient messages for high-throughput non-critical data; persistence impacts throughput significantly on spinning disks

## Reference Links

- [RabbitMQ Documentation](https://www.rabbitmq.com/docs) -- Official documentation covering all features, protocols, and operational guidance
- [RabbitMQ Quorum Queues](https://www.rabbitmq.com/docs/quorum-queues) -- Raft-based replicated queues for data safety and high availability
- [RabbitMQ Streams](https://www.rabbitmq.com/docs/streams) -- Append-only log data structure for high throughput and replay
- [RabbitMQ Clustering Guide](https://www.rabbitmq.com/docs/clustering) -- Cluster formation, node management, and network partition handling
- [RabbitMQ Reliability Guide](https://www.rabbitmq.com/docs/reliability) -- Publisher confirms, consumer acknowledgments, and delivery guarantees
- [RabbitMQ Monitoring Guide](https://www.rabbitmq.com/docs/monitoring) -- Health checks, metrics, Prometheus integration, and alerting
- [RabbitMQ Production Checklist](https://www.rabbitmq.com/docs/production-checklist) -- Official checklist for production deployments covering resource limits, security, and monitoring
- [RabbitMQ Shovel Plugin](https://www.rabbitmq.com/docs/shovel) -- Reliable message forwarding between brokers and clusters
- [RabbitMQ Federation Plugin](https://www.rabbitmq.com/docs/federation) -- Decentralized exchange and queue linking across sites
- [RabbitMQ TLS Guide](https://www.rabbitmq.com/docs/ssl) -- TLS configuration for client, inter-node, and management connections
- [CloudAMQP Blog](https://www.cloudamqp.com/blog/) -- Practical RabbitMQ tutorials, performance tuning, and best practices

## See Also

- `general/messaging-patterns.md` -- General messaging patterns including broker selection, delivery guarantees, saga patterns, and idempotency
- `patterns/event-driven.md` -- Event-driven architecture patterns where RabbitMQ serves as the event backbone
- `patterns/microservices.md` -- Microservices communication patterns using message brokers
- `general/observability.md` -- Monitoring broker health, queue depths, and consumer lag
- `general/disaster-recovery.md` -- Disaster recovery patterns including cross-site message replication
- `general/security.md` -- Security patterns for TLS, authentication, and access control
