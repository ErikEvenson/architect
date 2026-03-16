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

## Why This Matters

Microservices enable independent deployment, scaling, and team ownership, but they introduce significant distributed systems complexity. Too many services too early creates operational overhead without proportional benefit -- start with a modular monolith. Shared databases between services create tight coupling that defeats the purpose of decomposition. Synchronous chains across many services compound latency and fragility. Missing circuit breakers allow cascading failures to propagate across the system. Without distributed tracing, debugging cross-service issues becomes impossible. Inconsistent API contracts cause breaking changes that ripple through consumers.

## Common Decisions (ADR Triggers)

- **Service decomposition strategy** — domain-driven design bounded contexts, team topology alignment, granularity level
- **Communication pattern** — synchronous (REST/gRPC) vs asynchronous (messaging), when to use each
- **API gateway selection** — managed (AWS API Gateway, Apigee) vs self-hosted (Kong, Envoy), feature requirements
- **Service mesh adoption** — Istio vs Linkerd vs Cilium, when the complexity is justified
- **Database per service** — strict isolation vs shared database with schema separation, data consistency approach
- **Distributed transaction strategy** — saga pattern (choreography vs orchestration), eventual consistency model
- **Message broker selection** — Kafka vs SQS/SNS vs RabbitMQ, ordering and delivery guarantees
- **Observability stack** — commercial (Datadog, New Relic) vs open source (Prometheus, Grafana, Jaeger), cost at scale

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

### Azure Estimates

> **Disclaimer:** Azure prices are approximate, based on East US region pricing as of early 2025. Actual costs vary by region, commitment tier, and usage patterns. Always verify with the Azure Pricing Calculator.

#### Small (5 Services)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Container Platform | Azure Container Apps (5 services, 0.5 vCPU / 1 GB each) | $130 |
| API Gateway | Azure API Management (Consumption tier, 5M requests) | $20 |
| Service Mesh | None (direct service-to-service) | $0 |
| Databases | 3x Azure SQL S1 + 2x Cosmos DB (serverless) | $230 |
| Messaging | Service Bus (1M messages, Basic) | $1 |
| Observability | Azure Monitor + Application Insights basic | $55 |
| Load Balancer | Application Gateway v2 | $25 |
| Networking | NAT Gateway (1 AZ) | $40 |
| **Total** | | **~$500/mo** |

#### Medium (15 Services)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Container Platform | AKS (6x D2s_v5 worker nodes) | $720 |
| API Gateway | Azure API Management (Standard tier, 50M requests) | $700 |
| Service Mesh | Istio on AKS (included in cluster compute) | $0 |
| Databases | 5x Azure SQL S3/P1 + 5x Cosmos DB + 2x Azure Cache for Redis | $2,400 |
| Messaging | Service Bus (Standard, 50M messages) + Event Hubs (3 TUs) | $750 |
| Observability | Azure Monitor + Application Insights + Log Analytics | $700 |
| Load Balancers | 2x Application Gateway (external + internal) | $60 |
| Networking | NAT Gateway (2 AZs, 500 GB) | $85 |
| **Total** | | **~$5,415/mo** |

#### Large (50 Services)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Container Platform | AKS (20x D4s_v5 worker nodes) | $4,300 |
| API Gateway | Azure API Management (Premium tier) or Kong on AKS | $2,800 |
| Service Mesh | Istio on AKS (dedicated proxy sidecar resources) | $850 |
| Databases | 15x Azure SQL various tiers + 10x Cosmos DB + 5x Azure Cache for Redis | $9,200 |
| Messaging | Event Hubs (Dedicated 1 CU) + Service Bus (Premium) | $3,500 |
| Observability | Datadog or Grafana Cloud (50 services, APM + logs) | $3,200 |
| Load Balancers | 3x Application Gateway + Internal LB for gRPC | $160 |
| Networking | NAT Gateway (3 AZs, 2 TB) + Private Endpoints | $380 |
| **Total** | | **~$24,390/mo** |

### GCP Estimates

> **Disclaimer:** GCP prices are approximate, based on us-central1 region pricing as of early 2025. Actual costs vary by region, commitment tier, and usage patterns. Always verify with the GCP Pricing Calculator.

#### Small (5 Services)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Container Platform | Cloud Run (5 services, 0.5 vCPU / 1 GB each) | $120 |
| API Gateway | Apigee X (Pay-as-you-go, 5M requests) | $25 |
| Service Mesh | None (direct service-to-service) | $0 |
| Databases | 3x Cloud SQL db.custom-1-3840 + 2x Firestore | $180 |
| Messaging | Pub/Sub (1M messages) | $1 |
| Observability | Cloud Monitoring + Cloud Trace basic | $40 |
| Load Balancer | External HTTP(S) LB | $20 |
| Networking | Cloud NAT (1 region) | $35 |
| **Total** | | **~$420/mo** |

#### Medium (15 Services)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Container Platform | GKE Autopilot (equivalent of 6x n2-standard-2) | $650 |
| API Gateway | Apigee X (Standard, 50M requests) | $180 |
| Service Mesh | Anthos Service Mesh on GKE (included) | $0 |
| Databases | 5x Cloud SQL db.custom-4-16384 + 5x Firestore + 2x Memorystore | $2,000 |
| Messaging | Pub/Sub (50M messages) + Confluent Kafka on GKE | $700 |
| Observability | Cloud Monitoring + Cloud Trace + Cloud Logging | $550 |
| Load Balancers | 2x HTTP(S) LB (external + internal) | $50 |
| Networking | Cloud NAT (2 regions, 500 GB) | $70 |
| **Total** | | **~$4,200/mo** |

#### Large (50 Services)

| Component | Service | Monthly Estimate |
|-----------|---------|-----------------|
| Container Platform | GKE Standard (20x n2-standard-4 worker nodes) | $3,900 |
| API Gateway | Apigee X (Enterprise) or Kong on GKE | $1,600 |
| Service Mesh | Anthos Service Mesh (dedicated proxy sidecar resources) | $700 |
| Databases | 15x Cloud SQL various sizes + 10x Firestore + 5x Memorystore | $7,800 |
| Messaging | Confluent Kafka on GKE (6-broker n2-standard-8) + Pub/Sub | $2,900 |
| Observability | Datadog or Grafana Cloud (50 services, APM + logs) | $3,000 |
| Load Balancers | 3x HTTP(S) LB + Internal LB for gRPC | $130 |
| Networking | Cloud NAT (3 regions, 2 TB) + Private Service Connect | $300 |
| **Total** | | **~$20,330/mo** |

### Provider Comparison

> **Disclaimer:** All prices are approximate monthly estimates as of early 2025. Actual costs vary significantly based on region, commitment discounts, negotiated contracts, and usage patterns. Always verify with each provider's pricing calculator.

| Scale | AWS | Azure | GCP |
|-------|-----|-------|-----|
| Small (5 Services) | ~$490/mo | ~$500/mo | ~$420/mo |
| Medium (15 Services) | ~$4,725/mo | ~$5,415/mo | ~$4,200/mo |
| Large (50 Services) | ~$22,250/mo | ~$24,390/mo | ~$20,330/mo |

**Notes:**
- GCP tends to be more cost-effective for container workloads due to GKE Autopilot's efficient bin-packing and free cluster management fees (Autopilot).
- Azure API Management at Standard/Premium tier is significantly more expensive than AWS API Gateway; consider Kong or Envoy on AKS for cost savings.
- All three providers offer Kubernetes-based platforms, but managed service costs (databases, messaging) vary significantly.

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
