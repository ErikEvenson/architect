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

## Key Patterns

- **API Gateway**: single entry point for external traffic
- **Service Mesh**: infrastructure layer for service-to-service communication
- **Circuit Breaker**: prevent cascading failures
- **Saga**: manage distributed transactions
- **CQRS**: separate read and write models
- **Event Sourcing**: append-only event log as source of truth
- **Strangler Fig**: incrementally migrate from monolith
