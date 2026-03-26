# Azure Messaging (Service Bus, Event Hubs, Event Grid)

## Scope

Azure messaging and event streaming services. Covers Service Bus (queues, topics, sessions, tiers), Event Hubs (partitioned streaming, Kafka compatibility, Capture), and Event Grid (reactive event routing, filtering, domains).

## Checklist

- [ ] **[Critical]** Choose messaging service based on pattern: Service Bus for enterprise messaging (queues and topics with transactions, sessions, ordering), Event Hubs for high-throughput event streaming (millions of events/second with partitioned consumption), Event Grid for reactive event-driven routing (push-based delivery with filtering)
- [ ] **[Critical]** Select Service Bus tier: Basic (queues only, no topics, 256 KB messages), Standard (queues and topics, 256 KB messages, shared capacity), Premium (dedicated resources, 100 MB messages, VNet integration, availability zones, geo-DR); Premium is required for production workloads needing predictable performance
- [ ] **[Critical]** Configure Service Bus dead-letter queues (DLQ): automatic dead-lettering on message expiration or max delivery count exceeded (default 10), explicit dead-lettering from application code; monitor DLQ depth with Azure Monitor and set up alerts for investigation and reprocessing
- [ ] **[Recommended]** Enable Service Bus duplicate detection with a configurable time window (default 10 minutes, max 7 days); uses MessageId property for deduplication; required for idempotent message processing in retry scenarios
- [ ] **[Recommended]** Design Service Bus session-aware processing for FIFO ordering: messages with the same SessionId are delivered in order to a single consumer; use sessions for order processing, workflow steps, or entity-scoped processing; session state storage (up to 256 KB) available for checkpointing
- [ ] **[Critical]** Configure Event Hubs partitions at creation time (2-32 for Standard, up to 2000 for Dedicated): partitions determine maximum parallel consumers; partition count cannot be changed after creation; use partition keys for ordering guarantees within a partition
- [ ] **[Recommended]** Enable Event Hubs Capture for automatic archival to Azure Blob Storage or Data Lake Storage Gen2 in Avro format; configure capture window by time (1-15 minutes) and size (10-500 MB); zero-code data lake ingestion pattern
- [ ] **[Optional]** Set up Event Hubs Schema Registry for schema governance: Avro schemas with compatibility enforcement (backward, forward, full), integrated with Kafka Schema Registry API; prevents schema evolution from breaking consumers
- [ ] **[Recommended]** Design Event Grid subscriptions with event filtering: subject filtering (prefix/suffix), advanced filtering (operators on data fields: StringContains, NumberGreaterThan, etc., up to 25 advanced filters per subscription); reduces consumer processing by filtering at the platform level
- [ ] **[Critical]** Configure Event Grid dead-letter destination (Blob Storage container) for undeliverable events with retry policy (max delivery attempts 1-30, default 30; event TTL 1-1440 minutes, default 1440); monitor dead-lettered events for investigation
- [ ] **[Optional]** Plan Event Hubs Kafka protocol compatibility: Event Hubs provides a Kafka-compatible endpoint (Standard tier and above) supporting Kafka producer/consumer APIs, Kafka Streams, and Kafka Connect; enables migration from Apache Kafka without code changes
- [ ] **[Recommended]** Implement Service Bus message ordering guarantees: use sessions for strict FIFO within a session, or single-partition topics/queues; without sessions, Service Bus provides at-most best-effort ordering with no strict guarantee
- [ ] **[Optional]** Configure Event Grid event domains for multi-tenant scenarios: a single event domain can contain up to 100,000 topics for per-tenant event isolation with centralized management, authorization, and throttling

## Why This Matters

Azure provides three distinct messaging services optimized for different patterns. Using the wrong service creates performance bottlenecks, ordering violations, or unnecessary cost. Service Bus handles enterprise integration patterns with transactions, sessions, and guaranteed ordering. Event Hubs handles massive-scale event streaming with partitioned parallel consumption. Event Grid handles reactive event routing with push-based delivery and advanced filtering.

Service Bus Premium costs significantly more than Standard ($677/month per messaging unit vs pay-per-operation) but provides dedicated resources, predictable latency, and features required for production (VNet integration, messages up to 100 MB, geo-disaster recovery). Many teams start on Standard and discover they need Premium only after hitting shared-capacity performance issues in production.

Event Hubs partition count is the most consequential capacity decision because it cannot be changed after namespace creation. Under-provisioning partitions limits future consumer parallelism. Over-provisioning wastes resources if each partition has low throughput. The partition count should be based on expected peak consumer parallelism, not current throughput.

## Common Decisions (ADR Triggers)

- **Service Bus vs Event Hubs vs Event Grid** -- Service Bus for command-style messages requiring transactions, ordering (sessions), and exactly-once processing between specific producers and consumers. Event Hubs for high-throughput telemetry, log, and event streaming where consumers read independently at their own pace with replay capability. Event Grid for reactive event notification where something happened and multiple subscribers may need to react asynchronously. Many architectures combine all three: Event Grid triggers on Azure resource events, routes to Event Hubs for buffering, consumers use Service Bus for reliable downstream command processing.
- **Service Bus queues vs topics** -- Queues provide point-to-point delivery to a single consumer group with competing consumers for load distribution. Topics provide publish/subscribe with multiple subscriptions, each receiving a copy of the message with optional filtering. Use queues for work distribution (task processing, command handling). Use topics for event fan-out (order placed -> inventory service subscription + notification subscription + analytics subscription).
- **Event Hubs Standard vs Dedicated vs Premium** -- Standard provides shared infrastructure with throughput units (1 TU = 1 MB/s ingress, 2 MB/s egress) for moderate workloads. Premium provides isolated single-tenant infrastructure with processing units for predictable performance. Dedicated provides fully isolated clusters for extreme throughput (up to 2000 partitions). Use Standard for development and moderate production. Use Premium for most production workloads needing isolation. Use Dedicated for very high throughput or strict isolation requirements.
- **Event Grid system topics vs custom topics** -- System topics emit events from Azure services automatically (Blob Storage created, Resource Group changed, Key Vault secret expiring). Custom topics emit application-defined events published via the Event Grid SDK. Use system topics for infrastructure automation and reactive operations. Use custom topics for application-level event-driven architecture.
- **Service Bus geo-disaster recovery vs active geo-replication** -- Geo-DR provides metadata replication (queues, topics, subscriptions, rules) with manual failover but does not replicate messages. Active geo-replication (application-level) sends messages to multiple namespaces for true data redundancy but requires application changes. Use geo-DR for metadata protection and namespace failover. Use application-level replication when message data must survive regional outages.
- **Event Hubs Kafka protocol vs native SDK** -- Kafka protocol enables migration from existing Kafka deployments without code changes and supports Kafka ecosystem tools (Connect, Streams, MirrorMaker). Native SDK provides tighter Azure integration, simpler authentication (Entra ID), and Event Hubs-specific features (Capture, Schema Registry AMQP API). Use Kafka protocol for Kafka migrations. Use native SDK for new greenfield applications.

## Reference Architectures

### Order Processing with Guaranteed Delivery
API Management -> Service Bus Premium topic (OrderReceived) -> three subscriptions with SQL filters: (1) PaymentSubscription (filter: OrderTotal > 0) -> Azure Function processes payment, (2) InventorySubscription -> Azure Function reserves inventory, (3) NotificationSubscription -> Logic App sends confirmation email. Sessions enabled on PaymentSubscription with SessionId = OrderId for per-order sequencing. DLQ configured on all subscriptions with maxDeliveryCount 5. Azure Monitor alerts on DLQ message count > 0.

### High-Throughput Event Streaming Pipeline
IoT Hub or application producers -> Event Hubs (32 partitions, Standard tier with auto-inflate to 20 TUs) -> three consumer groups: (1) Stream Analytics for real-time aggregation to Power BI, (2) Azure Functions for alerting on anomalies, (3) Event Hubs Capture to Data Lake Storage Gen2 in Avro format for batch analytics. Schema Registry enforces Avro schemas with backward compatibility. Partition key = deviceId for per-device ordering.

### Reactive Infrastructure Automation
Event Grid system topics: Blob Storage events (BlobCreated) -> Azure Function processes uploaded files; Key Vault events (SecretNearExpiry) -> Logic App notifies security team and triggers rotation; Resource Group events (ResourceWriteSuccess) -> Azure Function enforces tagging policy. Dead-letter container in Blob Storage for failed deliveries. Advanced filters restrict events to specific blob containers and resource types.

### Multi-Tenant Event Architecture
Event Grid domain with per-tenant topics (tenant-001, tenant-002, ... tenant-N). Application publishes tenant-scoped events to domain topics. Per-tenant subscriptions route events to tenant-specific Azure Functions or webhooks. Domain-level RBAC: tenant applications authorized to publish/subscribe only to their own topic. Centralized monitoring across all domain topics via Azure Monitor metrics. Dead-letter per subscription for tenant-level failure isolation.

---

## Reference Links

- [Azure Service Bus documentation](https://learn.microsoft.com/en-us/azure/service-bus-messaging/) -- queues, topics, sessions, dead-letter queues, and geo-disaster recovery
- [Azure Event Hubs documentation](https://learn.microsoft.com/en-us/azure/event-hubs/) -- partitioned streaming, Kafka compatibility, Capture, and Schema Registry
- [Azure Event Grid documentation](https://learn.microsoft.com/en-us/azure/event-grid/) -- reactive event routing, filtering, system topics, and event domains

## See Also

- `general/data.md` -- General data architecture including messaging and event streaming patterns
- `providers/azure/serverless.md` -- Azure Functions as consumers for Service Bus, Event Hubs, and Event Grid
- `providers/azure/observability.md` -- Azure Monitor for messaging service metrics and alerting
