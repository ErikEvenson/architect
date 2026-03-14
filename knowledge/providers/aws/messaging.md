# AWS Messaging (SQS, SNS, EventBridge, Kinesis, MSK)

## Checklist

- [ ] Choose SQS queue type: Standard (nearly unlimited throughput, at-least-once delivery, best-effort ordering) vs FIFO (300 TPS without batching / 3,000 with batching, exactly-once processing, strict ordering per message group)
- [ ] Configure SQS visibility timeout to exceed the maximum processing time of consumers; default is 30 seconds, maximum is 12 hours; use `ChangeMessageVisibility` for dynamic extension
- [ ] Enable SQS long polling (WaitTimeSeconds 1-20 seconds) to reduce empty responses and API costs; short polling returns immediately and may miss messages distributed across servers
- [ ] Set up SQS dead letter queues (DLQ) with a redrive policy (maxReceiveCount typically 3-5); configure DLQ redrive to move failed messages back to source queue after investigation
- [ ] Configure SNS message filtering policies on subscriptions to route messages by attributes, reducing consumer processing and Lambda invocations by up to 90% compared to filtering in application code
- [ ] Design EventBridge event buses with schemas: default bus for AWS service events, custom bus for application events; use schema registry and discovery for event contract management
- [ ] Configure EventBridge archive and replay for debugging and reprocessing; archive specific events with filtering rules; replay events to the same or different bus within the retention period
- [ ] Choose Kinesis Data Streams shard count based on throughput: each shard supports 1 MB/s write (1,000 records/s) and 2 MB/s read; use on-demand capacity mode for unpredictable workloads
- [ ] Configure Kinesis Data Firehose for zero-administration delivery to S3, Redshift, OpenSearch, or HTTP endpoints with automatic batching, compression (GZIP/Snappy), and format conversion (Parquet/ORC)
- [ ] Evaluate MSK (Managed Streaming for Apache Kafka) vs Kinesis: MSK for Kafka ecosystem compatibility and existing Kafka expertise; Kinesis for simpler operations and tighter AWS integration
- [ ] Set appropriate message retention: SQS (1 minute to 14 days, default 4 days), Kinesis (24 hours to 365 days), EventBridge archive (indefinite), MSK (configurable, broker storage-based)
- [ ] Implement message deduplication: SQS FIFO uses content-based or explicit deduplication IDs (5-minute window); EventBridge and SNS provide at-least-once delivery requiring consumer-side idempotency
- [ ] Design fan-out patterns: SNS -> multiple SQS queues for parallel processing, EventBridge rules -> multiple targets (up to 5 per rule, use multiple rules for more), Kinesis enhanced fan-out for dedicated 2 MB/s per consumer

## Why This Matters

Messaging services decouple producers from consumers, enabling independent scaling, fault isolation, and asynchronous processing. The choice of messaging service determines throughput limits, ordering guarantees, delivery semantics, and operational complexity. Using the wrong service leads to message loss, duplicate processing, ordering violations, or unnecessary cost.

SQS is the simplest and most cost-effective for point-to-point workload decoupling. SNS enables pub/sub fan-out. EventBridge provides content-based routing with deep AWS service integration. Kinesis handles high-throughput ordered streaming. MSK provides Kafka compatibility for teams with existing Kafka investment. Many architectures combine multiple services -- for example, EventBridge for routing events to SNS for fan-out to SQS queues consumed by Lambda.

## Common Decisions (ADR Triggers)

- **SQS vs EventBridge for event-driven processing** -- SQS is point-to-point with pull-based consumption, message-level retention, and no content-based routing. EventBridge is publish/subscribe with push-based delivery, content-based filtering via rules, and native integration with 35+ AWS services as sources. Use SQS when you need buffering and backpressure; use EventBridge when you need routing and multiple consumers for different event types.
- **SQS Standard vs FIFO** -- Standard queues provide nearly unlimited throughput with at-least-once delivery and best-effort ordering. FIFO queues guarantee exactly-once processing and strict ordering within message groups but are limited to 3,000 messages/second with batching. Use FIFO for financial transactions, command ordering, or anywhere duplicate processing causes harm. Use Standard for high-throughput workloads tolerant of occasional duplicates.
- **Kinesis Data Streams vs SQS for high-throughput ingestion** -- Kinesis preserves ordering per shard, supports multiple consumers reading the same data independently, retains data up to 365 days, and supports replay. SQS deletes messages after consumption, is simpler to operate, and scales automatically. Use Kinesis for real-time analytics, log/event aggregation where ordering matters, and multiple consumers. Use SQS for task queues and work distribution.
- **Kinesis vs MSK (Kafka)** -- Kinesis is serverless (on-demand mode), integrates natively with AWS services, and requires minimal operations. MSK provides full Kafka API compatibility, supports the Kafka ecosystem (Connect, Streams, Schema Registry), and suits teams migrating from self-managed Kafka. MSK requires capacity planning (broker sizing, storage) and costs more at low throughput but can be cheaper at very high throughput with MSK Serverless.
- **SNS + SQS fan-out vs EventBridge fan-out** -- SNS + SQS is proven, simple, and supports very high throughput. EventBridge provides richer filtering (content-based on nested JSON fields), direct integration with more targets (Step Functions, API Gateway, third-party SaaS), and built-in archive/replay. EventBridge has a limit of 5 targets per rule (use multiple rules) and lower throughput limits (10,000 PutEvents/second soft limit per region per account).
- **Synchronous vs asynchronous communication** -- Synchronous (API calls) is simpler to reason about and debug but creates tight coupling and cascading failures. Asynchronous (messaging) decouples services, enables retry/DLQ patterns, and absorbs traffic spikes, but adds latency and complexity (eventual consistency, message ordering). Default to async for inter-service communication; use sync for user-facing request/response paths.

## Reference Architectures

### Order Processing Pipeline
API Gateway -> Lambda (validate order) -> EventBridge (OrderPlaced event) -> rules route to: (1) SQS queue -> Lambda (payment processing), (2) SQS queue -> Lambda (inventory reservation), (3) SNS (notification). DLQ on each SQS queue. Step Functions for saga orchestration across payment, inventory, and shipping services with compensating transactions on failure.

### Real-Time Analytics Ingestion
Application/IoT devices -> Kinesis Data Streams (on-demand mode) -> Kinesis Data Analytics (Apache Flink) for real-time aggregation -> Kinesis Data Firehose -> S3 (Parquet format, partitioned by date). Lambda consumer for real-time alerting on anomalies. Enhanced fan-out for the analytics consumer to get dedicated throughput independent of Firehose.

### Event-Driven Microservices (Event Bus)
Custom EventBridge bus -> schema registry for event contracts. Each microservice publishes domain events to the bus. EventBridge rules route events to target services via SQS queues (buffering) or directly to Lambda (simple transforms). Archive enabled for all events with 90-day retention for replay and debugging. CloudWatch metrics on FailedInvocations and DLQ depth for alerting.

### Reliable Message Processing with Exactly-Once
SQS FIFO queue with content-based deduplication. Message group ID based on entity ID (e.g., customer ID) for per-entity ordering. Lambda event source mapping with batch size 10, maximum batching window 5 seconds. DLQ with maxReceiveCount 3. CloudWatch alarm on ApproximateAgeOfOldestMessage for processing delay detection. Redrive policy for manual DLQ inspection and replay.
