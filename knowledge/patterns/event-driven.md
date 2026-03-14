# Event-Driven Architecture

## Overview

Event-driven architecture uses events as the primary mechanism for communication between services. Systems produce, detect, consume, and react to events, enabling loose coupling, scalability, and real-time responsiveness. Core patterns include event sourcing, CQRS, pub/sub messaging, and choreography-based workflows.

## Checklist

- [ ] What is the event backbone? (Kafka, EventBridge, Pub/Sub, SNS/SQS, Event Hubs)
- [ ] Is event sourcing used? (append-only event log as source of truth vs traditional state storage)
- [ ] Is CQRS applied? (separate read/write models, independent scaling of query and command sides)
- [ ] Choreography or orchestration? (decentralized event reactions vs centralized workflow engine like Step Functions or Temporal)
- [ ] Is there an event schema registry? (Confluent Schema Registry, AWS Glue, Apicurio — enforcing contracts)
- [ ] What is the event versioning strategy? (schema evolution, backward/forward compatibility, Avro vs Protobuf vs JSON Schema)
- [ ] What delivery guarantee is required? (exactly-once, at-least-once, at-most-once — and idempotency strategy for at-least-once)
- [ ] How is event ordering preserved? (partition keys, sequence numbers, single-partition topics for strict ordering)
- [ ] Is there a dead letter queue for failed event processing? (DLQ monitoring, alerting, replay mechanism)
- [ ] How are distributed transactions handled? (saga pattern — compensating transactions, orchestrated vs choreographed sagas)
- [ ] Is event replay supported? (rebuilding state from event log, retention policies, compaction)
- [ ] How is backpressure managed? (consumer throttling, queue depth monitoring, auto-scaling consumers)
- [ ] What is the event retention policy? (hours, days, indefinite — cost vs replay capability tradeoff)
- [ ] How are event consumers monitored? (consumer lag, processing latency, error rates, partition assignment)

## Why This Matters

Event-driven architectures enable systems to react in real time, scale independently, and evolve without tight coupling between producers and consumers. However, they introduce complexity in debugging, ordering guarantees, and consistency. Choosing the wrong delivery guarantee leads to data loss (at-most-once) or duplicate processing (at-least-once without idempotency). Missing dead letter queues cause silent data loss. Without schema governance, event contracts drift and break consumers. The saga pattern is essential for maintaining data consistency across services but adds significant complexity compared to traditional transactions.

## Cost Benchmarks

> **Disclaimer:** Prices are rough estimates based on AWS us-east-1 pricing as of early 2025. Actual costs vary by region, reserved instance commitments, and usage patterns. Prices change over time — always verify with the provider's pricing calculator.

### Small (100K events/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Functions | Lambda (3M invocations, 256 MB, 200ms avg) | $2 |
| Event Bus | EventBridge (3M events) | $3 |
| Message Queue | SQS (3M messages) | $1 |
| Event Store | DynamoDB on-demand (3M writes, 10M reads) | $10 |
| Monitoring | CloudWatch Logs + basic metrics | $10 |
| **Total** | | **~$26/mo** |

### Medium (10M events/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Functions | Lambda (300M invocations, 512 MB, 200ms avg) | $200 |
| Event Bus | EventBridge (300M events) | $300 |
| Message Broker | SQS (300M messages) + SNS fan-out (50M) | $150 |
| Event Store | DynamoDB provisioned (write-heavy, 5K WCU) | $350 |
| Dead Letter Queue | SQS DLQ + Lambda reprocessor | $5 |
| Monitoring | CloudWatch + X-Ray (sampled) | $100 |
| **Total** | | **~$1,105/mo** |

### Large (1B events/day)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Functions | Lambda (10B invocations — may hit concurrency limits) | $6,000 |
| Streaming | MSK (6-broker kafka.m5.2xlarge) | $4,500 |
| Event Bus | EventBridge (for routing subset, 1B events) | $1,000 |
| Message Queue | SQS (5B messages) + SNS | $2,200 |
| Event Store | DynamoDB (50K WCU) or S3 event archive | $3,500 |
| Consumers | ECS Fargate (20 consumer tasks, 1 vCPU/2 GB) | $1,200 |
| Dead Letter Queue | SQS DLQ + reprocessing pipeline | $50 |
| Observability | Datadog or self-hosted (OpenSearch + Grafana) | $2,000 |
| **Total** | | **~$20,450/mo** |

### Biggest Cost Drivers

1. **Lambda at high volume** — Lambda is cheap at low scale but at 1B+ events/day, container-based consumers on ECS/EKS are significantly cheaper. Lambda costs scale linearly with invocations; containers amortize compute cost.
2. **EventBridge pricing** — $1 per million events adds up at scale. At 1B events/day ($30K/mo), consider Kafka or direct SQS/SNS.
3. **Message broker (Kafka/MSK)** — MSK clusters run 24/7 regardless of throughput. Right-size brokers and consider serverless MSK for variable workloads.
4. **Observability** — tracing every event is expensive. Use sampling (1-10%) for high-volume event streams.

### Optimization Tips

- Use **Lambda** for low-to-medium volume (<50M events/day) — zero idle cost, pay-per-invocation.
- Switch to **ECS/EKS consumers** at high volume — container-based processing is 3-5x cheaper than Lambda above 100M events/day.
- Use **SQS** instead of EventBridge for point-to-point messaging — SQS is ~3x cheaper per message.
- Use **EventBridge** for routing and fan-out where its rules engine adds value; use SNS for simpler fan-out.
- Enable **SQS long polling** (20s) to reduce empty receives and cost.
- Use **S3** for event archival instead of keeping events in DynamoDB/Kafka indefinitely.
- Consider **MSK Serverless** for variable throughput — avoids paying for idle broker capacity.
- Use **Lambda Provisioned Concurrency** sparingly — it eliminates cold starts but adds idle cost.

## Common Decisions (ADR Triggers)

- **Event backbone selection** — Kafka vs managed services (EventBridge, Pub/Sub), throughput vs operational overhead
- **Event sourcing adoption** — full event sourcing vs event notification pattern, implications for storage and query complexity
- **CQRS boundary** — which domains benefit from separate read/write models vs unnecessary complexity
- **Choreography vs orchestration** — decoupled event reactions vs explicit workflow visibility and error handling
- **Schema management** — registry enforcement, compatibility mode (backward, forward, full), serialization format
- **Delivery guarantee** — exactly-once processing cost vs at-least-once with idempotency keys
- **Saga strategy** — orchestrated sagas (centralized coordinator) vs choreographed sagas (event-driven compensation)
- **Retention and replay** — how long to retain events, compaction strategy, cold storage for historical events
- **Backpressure strategy** — consumer auto-scaling thresholds, queue depth limits, producer rate limiting
