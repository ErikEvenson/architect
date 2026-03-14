# AWS Lambda & Serverless

## Checklist

- [ ] Choose API Gateway type: REST API (feature-rich, API keys, usage plans, WAF) vs HTTP API (lower cost, simpler, JWT authorizer) vs WebSocket API (real-time bidirectional)
- [ ] Configure Lambda memory (128 MB-10,240 MB) understanding that CPU scales proportionally with memory allocation
- [ ] Set function timeout appropriately (max 15 minutes); use Step Functions for longer workflows
- [ ] Evaluate cold start impact: language runtime choice (Python/Node.js ~200ms vs Java/C# ~1-3s), VPC attachment adds ENI creation time, package size affects init duration
- [ ] Enable provisioned concurrency for latency-sensitive functions that cannot tolerate cold starts (billed per GB-hour even when idle)
- [ ] Configure reserved concurrency to prevent a single function from consuming the entire account-level concurrency limit (default 1,000)
- [ ] Use Lambda layers for shared dependencies (max 5 layers, 250 MB unzipped total); prefer container images (up to 10 GB) for large dependencies
- [ ] Set up dead letter queues (SQS or SNS) for async invocations to capture failed events after retry exhaustion (2 automatic retries)
- [ ] Design idempotent handlers since Lambda may invoke functions more than once; use Powertools for idempotency with DynamoDB
- [ ] Use Lambda@Edge (Node.js/Python, up to 5s at origin, 30s at viewer) or CloudFront Functions (JavaScript, sub-millisecond, viewer events only) for edge compute
- [ ] Choose deployment framework: SAM (CloudFormation-based, Lambda-focused), CDK (imperative, multi-resource), Serverless Framework (plugin ecosystem), or Terraform
- [ ] Design Step Functions workflows using Standard (up to 1 year, exactly-once) vs Express (up to 5 minutes, at-least-once) based on duration and execution guarantees
- [ ] Configure VPC-attached Lambda only when accessing VPC resources (RDS, ElastiCache); uses Hyperplane ENIs with improved cold start since 2019 but still adds latency

## Why This Matters

Serverless architectures eliminate infrastructure management and scale automatically from zero to thousands of concurrent executions. However, poorly designed serverless systems suffer from cold start latency spikes, runaway costs at high throughput, tight vendor coupling, and debugging complexity across distributed event-driven flows. Choosing the right event source, memory configuration, and orchestration pattern directly impacts cost, latency, and reliability.

Lambda pricing is per-request plus per-GB-second of compute. A function using 1,024 MB running for 200ms costs roughly $0.0000033 per invocation. At low-to-moderate scale this is dramatically cheaper than always-on compute, but at sustained high throughput (millions of invocations per hour) containers or EC2 may be more cost-effective.

## Common Decisions (ADR Triggers)

- **Synchronous vs asynchronous invocation model** -- Synchronous (API Gateway, ALB) blocks the caller; asynchronous (S3, SNS, EventBridge) decouples but requires DLQ and idempotency. This shapes error handling, retry logic, and user experience.
- **Monolithic Lambda vs single-purpose functions** -- A single Lambda behind API Gateway handling all routes (Lambda-lith) simplifies deployment but increases cold start size. Single-purpose functions per route optimize cold starts but multiply deployment units.
- **Step Functions vs direct Lambda chaining** -- Step Functions add cost ($0.025 per 1,000 state transitions) but provide built-in retry, error handling, parallel execution, and visual debugging. Direct invocation (Lambda calling Lambda) is cheaper but creates hidden coupling and loses execution history.
- **API Gateway REST vs HTTP API** -- REST API supports AWS WAF, API keys, usage plans, request validation, and caching. HTTP API costs ~70% less, supports JWT authorizers natively, and has lower latency. Choose REST when you need WAF integration or advanced features.
- **Lambda@Edge vs CloudFront Functions** -- Lambda@Edge runs in regional edge caches with network access, larger memory (up to 10 GB), and longer timeout. CloudFront Functions run in every edge location with sub-millisecond execution but no network access and 10 KB code limit. Use CloudFront Functions for header manipulation and simple rewrites; Lambda@Edge for authentication, A/B testing, and origin selection.
- **Provisioned concurrency vs accepting cold starts** -- Provisioned concurrency eliminates cold starts but adds steady-state cost. Use it for customer-facing APIs with strict P99 latency requirements; skip it for async background processing.

## Reference Architectures

### Web API Backend
API Gateway (HTTP API) -> Lambda functions -> DynamoDB. Cognito or JWT authorizer for authentication. CloudWatch Alarms on throttling and error rates. X-Ray tracing enabled across all components. Custom domain with Route 53 alias to API Gateway.

### Event-Driven Processing Pipeline
S3 upload -> S3 Event Notification -> Lambda (validate/transform) -> SQS queue -> Lambda (process) -> DynamoDB (store results). DLQ on both SQS and async Lambda invocations. Step Functions for complex multi-step processing with parallel branches and error handling states.

### Scheduled Data Processing
EventBridge Scheduler -> Step Functions -> parallel Lambda invocations (fan-out via Map state) -> aggregate results -> SNS notification. Use Express Workflows for sub-5-minute jobs; Standard Workflows for long-running ETL with wait states.

### Real-Time WebSocket Application
API Gateway WebSocket API -> Lambda (connect/disconnect/message handlers) -> DynamoDB (connection store) -> Lambda (broadcast via API Gateway Management API). Use $connect route for auth, $default for message routing.
