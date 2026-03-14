# Microservices Architecture

## Overview

Microservices decompose an application into small, independently deployable services. Each service owns its data and communicates via APIs or messaging.

## Checklist

- [ ] What is the service decomposition strategy? (by business domain, bounded contexts)
- [ ] How do services communicate? (synchronous REST/gRPC vs asynchronous messaging)
- [ ] Is there an API gateway for external traffic? (routing, auth, rate limiting)
- [ ] Is there a service mesh for internal traffic? (mTLS, observability, traffic management)
- [ ] Does each service have its own database? (database per service pattern)
- [ ] How is distributed tracing implemented? (correlation IDs across service boundaries)
- [ ] How are cross-service transactions handled? (saga pattern, eventual consistency)
- [ ] Is there a circuit breaker pattern for inter-service calls?
- [ ] How is service discovery implemented? (DNS, service registry, mesh)
- [ ] What is the deployment strategy per service? (independent deploys recommended)
- [ ] Is there a centralized logging and log aggregation system?
- [ ] How are API contracts managed? (OpenAPI specs, schema registry, contract testing)
- [ ] Is there a message broker for async communication? (SQS, Kafka, RabbitMQ)
- [ ] How are shared libraries and common code managed? (shared packages vs duplication)

## Common Mistakes

- Too many services too early (start with a modular monolith)
- Shared databases between services (tight coupling)
- Synchronous chains across many services (latency, fragility)
- No circuit breakers (cascading failures)
- Missing distributed tracing (impossible to debug cross-service issues)
- Inconsistent API contracts (breaking changes without versioning)
- No centralized logging (debugging across services is impossible)

## Cost Benchmarks

> **Disclaimer:** Prices are rough estimates based on AWS us-east-1 pricing as of early 2025. Actual costs vary by region, reserved instance commitments, and usage patterns. Prices change over time — always verify with the provider's pricing calculator.

### Small (5 Services)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Container Platform | ECS Fargate (5 services, 0.5 vCPU / 1 GB each) | $150 |
| API Gateway | API Gateway (5M requests) | $20 |
| Service Mesh | None (direct service-to-service) | $0 |
| Databases | 3x RDS db.t3.small + 2x DynamoDB on-demand | $200 |
| Messaging | SQS (1M messages) | $1 |
| Observability | CloudWatch + X-Ray basic | $50 |
| Load Balancer | 1x ALB with path-based routing | $25 |
| Networking | NAT Gateway (1 AZ) | $45 |
| **Total** | | **~$490/mo** |

### Medium (15 Services)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Container Platform | EKS + EC2 (6x m6i.large worker nodes) | $750 |
| API Gateway | API Gateway (50M requests) | $175 |
| Service Mesh | App Mesh or Istio (included in cluster compute) | $0 |
| Databases | 5x RDS db.r6g.large + 5x DynamoDB + 2x ElastiCache | $2,200 |
| Messaging | SQS + SNS (50M messages) + MSK (3-broker kafka.m5.large) | $800 |
| Observability | CloudWatch + X-Ray + OpenSearch (2x r6g.large) | $650 |
| Load Balancers | 2x ALB (external + internal) | $60 |
| Networking | NAT Gateway (2 AZs, 500 GB) | $90 |
| **Total** | | **~$4,725/mo** |

### Large (50 Services)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Container Platform | EKS + EC2 (20x m6i.xlarge worker nodes) | $4,500 |
| API Gateway | API Gateway (500M requests) or Kong/Envoy on EKS | $1,750 |
| Service Mesh | Istio on EKS (dedicated proxy sidecar resources) | $800 |
| Databases | 15x RDS various sizes + 10x DynamoDB + 5x ElastiCache | $8,500 |
| Messaging | MSK (6-broker kafka.m5.2xlarge) + SQS/SNS | $3,200 |
| Observability | Datadog or Grafana Cloud (50 services, APM + logs) | $3,000 |
| Load Balancers | 3x ALB + NLB for gRPC | $150 |
| Networking | NAT Gateway (3 AZs, 2 TB) + VPC endpoints | $350 |
| **Total** | | **~$22,250/mo** |

### Biggest Cost Drivers

1. **Databases** — each service owning its database multiplies database costs. Typically 35-45% of total spend.
2. **Observability** — distributed tracing, centralized logging, and metrics across many services grow significantly. Third-party tools (Datadog, New Relic) charge per host/service.
3. **Messaging/Streaming** — Kafka (MSK) clusters are expensive at scale. SQS is cheap per-message but costs grow with volume.
4. **Container platform overhead** — EKS control plane ($74/mo) plus sidecar proxies for service mesh add 10-15% compute overhead.

### Optimization Tips

- Start with **ECS Fargate** for small deployments — no cluster management, pay-per-task.
- Use **DynamoDB on-demand** for unpredictable workloads, **provisioned capacity** with auto-scaling for steady workloads.
- Consider **self-hosted observability** (Grafana + Prometheus + Loki on EKS) vs commercial tools to reduce cost at scale.
- Use **SQS/SNS** instead of Kafka (MSK) unless you need replay, ordering, or high-throughput streaming.
- Consolidate small, low-traffic services to reduce per-service overhead (avoid nano-services).
- Use **Spot Instances** for non-critical worker nodes (30-70% savings).

## Key Patterns

- **API Gateway**: single entry point for external traffic
- **Service Mesh**: infrastructure layer for service-to-service communication
- **Circuit Breaker**: prevent cascading failures
- **Saga**: manage distributed transactions
- **CQRS**: separate read and write models
- **Event Sourcing**: append-only event log as source of truth
- **Strangler Fig**: incrementally migrate from monolith
