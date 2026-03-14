# Azure Serverless

## Checklist

- [ ] Is the Azure Functions hosting plan selected based on workload characteristics -- Consumption (pay-per-execution, cold starts) vs Premium (pre-warmed instances, VNet integration) vs Dedicated (App Service plan, predictable cost)?
- [ ] Are Durable Functions used for stateful orchestration patterns -- function chaining, fan-out/fan-in, async HTTP APIs, monitoring, and human interaction workflows?
- [ ] Are Azure Functions bindings and triggers configured to minimize boilerplate -- input/output bindings for Blob Storage, Cosmos DB, Service Bus, and Event Hubs instead of SDK calls?
- [ ] Is Azure Logic Apps (Standard or Consumption) deployed for low-code workflow automation with 400+ managed connectors for SaaS, on-premises, and Azure service integration?
- [ ] Is Azure Event Grid configured as the event backbone with system topics for Azure resource events and custom topics for application-domain events?
- [ ] Is Azure Service Bus deployed for enterprise messaging with queues (point-to-point) and topics/subscriptions (pub/sub) with dead-letter queues, sessions, and duplicate detection enabled?
- [ ] Is Azure Event Hubs configured for high-throughput streaming ingestion with appropriate partition count (cannot be changed after creation) and consumer groups per downstream processor?
- [ ] Is Event Hubs Capture enabled to automatically archive streaming events to Blob Storage or Data Lake Gen2 in Avro format for long-term retention and batch processing?
- [ ] Are retry policies and dead-letter destinations configured for all messaging components -- Event Grid (retry + dead-letter to storage), Service Bus (max delivery count + dead-letter queue), Functions (retry policy)?
- [ ] Is VNet integration enabled for Premium Azure Functions and Logic Apps Standard to access private endpoints and on-premises resources through VNet?
- [ ] Are function app slots configured for production deployments with slot-based deployment swaps and pre-warm verification?
- [ ] Are Event Grid event subscriptions filtered with subject and advanced filters to minimize unnecessary function invocations and reduce cost?
- [ ] Is Service Bus configured with appropriate tier -- Basic (queues only) vs Standard (queues + topics, 256KB messages) vs Premium (dedicated capacity, 100MB messages, VNet integration)?
- [ ] Are idempotency patterns implemented across all event-driven functions, handling at-least-once delivery guarantees from Event Grid, Service Bus, and Event Hubs?

## Why This Matters

Azure's serverless ecosystem is more fragmented than AWS Lambda + EventBridge, requiring architects to combine Azure Functions, Logic Apps, Event Grid, Service Bus, and Event Hubs into a cohesive event-driven architecture. Azure Functions Consumption plan has cold starts of 1-10 seconds (worse for Java and .NET), making the Premium plan necessary for latency-sensitive workloads. Event Grid and Service Bus serve different patterns -- Event Grid is optimized for reactive event distribution (high fan-out, low latency) while Service Bus provides transactional messaging guarantees (sessions, ordering, dead-letter). Event Hubs is purpose-built for streaming ingestion at millions of events per second but requires careful partition planning since partition count is immutable after creation.

## Common Decisions (ADR Triggers)

- **Functions Consumption vs Premium vs Dedicated** -- zero-cost at idle with cold starts vs pre-warmed instances with VNet integration ($0.173/vCPU/hr) vs App Service plan sharing with web apps
- **Event Grid vs Service Bus vs Event Hubs** -- reactive event distribution (fire-and-forget) vs transactional messaging (guaranteed delivery, ordering) vs streaming ingestion (high-throughput, partitioned)
- **Durable Functions vs Logic Apps** -- code-first orchestration in C#/Python/JS with unit testing vs low-code visual designer with managed connectors and no-code transforms
- **Logic Apps Consumption vs Standard** -- pay-per-action serverless vs single-tenant with VNet support, local development, and workflow hosting on App Service Environment
- **Service Bus sessions vs partitions** -- ordered message processing per session ID (FIFO per group) vs throughput scaling across partitions (no ordering guarantee)
- **Event Hubs partition count** -- more partitions enable more parallel consumers but increase cost; 4-32 for most workloads, cannot be changed after creation (Kafka-compatible API available)
- **Function language runtime** -- .NET (fastest cold start, best integration) vs Python/Node.js (faster development) vs Java (slowest cold start on Consumption, use Premium)

## Reference Architectures

- [Azure Architecture Center: Serverless event processing](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/serverless/event-processing) -- reference architecture for event-driven processing with Functions, Event Hubs, and Cosmos DB
- [Azure Architecture Center: Serverless web application](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/serverless/web-app) -- static frontend with Functions backend, API Management, and CDN
- [Azure Architecture Center: Enterprise integration with queues and events](https://learn.microsoft.com/en-us/azure/architecture/example-scenario/integration/queues-events) -- reference design combining Service Bus, Event Grid, and Logic Apps for enterprise workflow automation
- [Azure Well-Architected Framework: Azure Functions](https://learn.microsoft.com/en-us/azure/well-architected/service-guides/azure-functions) -- reliability, security, cost, and performance best practices for Functions deployments
- [Azure Architecture Center: Choosing a messaging service](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/messaging) -- decision matrix for Event Grid vs Service Bus vs Event Hubs based on pattern, throughput, and delivery guarantees
