# GCP Serverless

## Scope

Cloud Run (services, jobs), Cloud Run functions (formerly Cloud Functions -- rebranded August 2024; 1st gen legacy, 2nd gen built on Cloud Run), Eventarc, Pub/Sub, Cloud Tasks, Workflows, Cloud Scheduler, serverless compute patterns.

## Checklist

- [ ] [Recommended] Are Cloud Run functions (formerly Cloud Functions 2nd gen, built on Cloud Run) used instead of 1st gen for new deployments, providing concurrency support, longer timeouts (60 min), larger instances (32 GB RAM, 8 vCPU), and traffic splitting?
- [ ] [Recommended] Are Eventarc triggers configured for event-driven Cloud Run functions and Cloud Run services, replacing direct Pub/Sub and Cloud Storage triggers for unified event routing from 130+ Google Cloud sources?
- [ ] [Recommended] Is Pub/Sub configured with appropriate subscription types (pull vs push vs BigQuery), acknowledgement deadlines, and dead-letter topics with max delivery attempt thresholds?
- [ ] [Optional] Are Pub/Sub ordering keys configured for message ordering requirements, understanding that ordering is per-key and limits throughput to 1 MB/s per ordering key per region?
- [ ] [Optional] Is Pub/Sub exactly-once delivery enabled on pull subscriptions where duplicate processing is unacceptable, understanding the throughput reduction and regional availability constraints?
- [ ] [Recommended] Is Cloud Tasks used for task queuing with rate limiting (max dispatches per second), retry configuration (min/max backoff, max attempts, max doublings), and routing to Cloud Run or HTTP targets?
- [ ] [Optional] Is Workflows configured for multi-step service orchestration with error handling (try/retry/except), parallel step execution, and connector shortcuts for Google Cloud APIs?
- [ ] [Optional] Is Cloud Scheduler configured for recurring jobs with appropriate retry settings, targeting Pub/Sub, HTTP endpoints, or App Engine with cron schedule expressions?
- [ ] [Recommended] Are Cloud Run services configured with appropriate request timeouts (max 3600s), maximum concurrent requests per container, and startup/liveness probes for health checking?
- [ ] [Recommended] Is Cloud Run configured with VPC connectors or Direct VPC Egress for accessing private resources (Cloud SQL, Memorystore, internal services) from serverless environments?
- [ ] [Recommended] Are minimum instances set on latency-sensitive Cloud Run functions and Cloud Run services, with cost implications understood (minimum instances are billed at idle rate)?
- [ ] [Critical] Is the appropriate execution model selected? (Cloud Run functions for single-purpose event handlers, Cloud Run services for containerized services with custom runtimes, Cloud Run Jobs for batch workloads, Workflows for orchestration)
- [ ] [Optional] Are Pub/Sub message schemas (Avro or Protocol Buffers) configured for topics requiring message validation and schema evolution?
- [ ] [Optional] Is the Cloud Run functions concurrency setting tuned (default 1, max 1000), with thread-safe code verified before increasing concurrency?

## Why This Matters

GCP's serverless portfolio is more fragmented than AWS Lambda but offers finer-grained choices. Cloud Functions was officially rebranded as Cloud Run functions in August 2024 to reflect that 2nd gen functions are built on Cloud Run, making Cloud Run the foundational serverless compute layer. The Cloud Functions API remains supported for backward compatibility. The decision between Cloud Run functions and Cloud Run services often comes down to developer experience: Cloud Run functions abstracts the container entirely while Cloud Run services require a Dockerfile but support any language/runtime, gRPC, WebSockets, and streaming. Eventarc unifies event routing that was previously scattered across service-specific triggers, providing a single event bus model. Pub/Sub is the central nervous system for async communication but has nuanced ordering and exactly-once semantics that must be understood: ordering keys partition throughput, and exactly-once only works with pull subscriptions.

## Common Decisions (ADR Triggers)

- **Compute model** -- Cloud Run functions (event handlers, simple HTTP) vs Cloud Run services (containerized services, custom runtimes) vs Cloud Run Jobs (batch workloads) vs App Engine (legacy, automatic scaling)
- **Event routing** -- Eventarc (unified, audit-log-based) vs direct Pub/Sub triggers vs Cloud Storage notifications, event schema management
- **Message queue** -- Pub/Sub (high throughput, at-least-once default, serverless) vs Cloud Tasks (task queue with rate limiting) vs Managed Kafka (Kafka protocol compatibility)
- **Orchestration** -- Workflows (lightweight, Google-native) vs Cloud Composer/Airflow (complex DAGs, data pipelines) vs custom orchestration on Cloud Run
- **Pub/Sub delivery** -- pull (consumer-controlled, batching) vs push (HTTP endpoint delivery, automatic scaling) vs BigQuery subscription (direct analytics)
- **Cold start mitigation** -- minimum instances (cost) vs always-on CPU allocation vs startup CPU boost (Cloud Run), code optimization strategies
- **Concurrency model** -- single concurrent request (stateful, legacy) vs multi-concurrency (efficient, requires thread-safe code), impact on billing
- **Scheduling** -- Cloud Scheduler (managed cron) vs Cloud Tasks (programmatic scheduling) vs GKE CronJobs, at-least-once vs exactly-once guarantees

## Reference Architectures

- [Google Cloud Architecture Center: Serverless](https://cloud.google.com/architecture#serverless) -- reference architectures for event-driven systems, API backends, and data processing pipelines
- [Google Cloud: Event-driven architectures with Eventarc](https://cloud.google.com/eventarc/docs/overview) -- reference design for unified event routing across Google Cloud services with Cloud Audit Logs integration
- [Google Cloud: Asynchronous processing with Pub/Sub and Cloud Run](https://cloud.google.com/run/docs/tutorials/pubsub) -- reference pattern for decoupled, scalable event processing with push subscriptions
- [Google Cloud: Orchestrating microservices with Workflows](https://cloud.google.com/workflows/docs/overview) -- reference architecture for service orchestration with error handling, parallel execution, and API connectors
- [Google Cloud: Choosing a serverless option](https://cloud.google.com/serverless-options) -- decision guide comparing Cloud Run functions, Cloud Run services, and App Engine for different workload patterns

## See Also

- `providers/gcp/containers.md` -- GKE and Cloud Run container platform
- `providers/gcp/messaging.md` -- Pub/Sub and event-driven triggers
- `providers/gcp/networking.md` -- load balancing and VPC connectors for serverless
