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
