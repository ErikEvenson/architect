# API Design

## Scope

This file covers **API design decisions** including API style selection, versioning, rate limiting, authentication, error handling, and lifecycle management. For deployment strategies, see `general/deployment.md`. For security controls on APIs, see `general/security.md`.

## Checklist

- [ ] **[Critical]** What API style is used and why? (REST for resource-oriented CRUD, GraphQL for flexible client queries, gRPC for high-performance service-to-service, AsyncAPI for event-driven)
- [ ] **[Recommended]** Is there an API gateway? (Kong, AWS API Gateway, Apigee, Azure APIM — routing, auth, rate limiting, transformation, caching)
- [ ] **[Critical]** What versioning strategy is used? (URL path /v1/ for simplicity, Accept header for purity, query parameter for flexibility — pick one and be consistent)
- [ ] **[Recommended]** How are rate limiting and throttling configured? (per-client limits, tiered plans, burst allowance, 429 response with Retry-After header)
- [ ] **[Critical]** What authentication mechanism secures the API? (OAuth 2.0 authorization code for user-facing, client credentials for service-to-service, API keys for simple integrations, JWT validation)
- [ ] **[Recommended]** Is an OpenAPI/Swagger specification maintained? (contract-first design recommended, auto-generated client SDKs, interactive documentation)
- [ ] **[Recommended]** How is pagination implemented? (cursor-based for large datasets, offset/limit for simple cases, Link headers, total count considerations)
- [ ] **[Recommended]** What error response format is standardized? (RFC 7807 Problem Details, consistent error codes, actionable error messages, request correlation IDs)
- [ ] **[Critical]** Is CORS configured correctly? (allowed origins, methods, headers — avoid wildcard in production, preflight caching)
- [ ] **[Critical]** How is backward compatibility maintained? (additive changes only, deprecation timeline, sunset headers, consumer-driven contract testing)
- [ ] **[Recommended]** What is the API lifecycle process? (design review, alpha/beta/GA stages, deprecation policy, sunset timeline — typically 6-12 months)
- [ ] **[Optional]** How is API documentation generated and maintained? (Swagger UI, Redoc, developer portal, example requests/responses, SDKs)
- [ ] **[Optional]** Is there an API linting/governance tool? (Spectral, Optic — enforcing naming conventions, response formats, security requirements)

## Why This Matters

APIs are contracts. Once published, they are difficult to change without breaking consumers. Poor API design decisions compound over time: inconsistent naming, missing pagination, and no versioning strategy lead to breaking changes, frustrated developers, and eventually a rewrite. Rate limiting protects backend services from abuse and noisy neighbors. Without OpenAPI specs, documentation drifts from implementation and client SDK generation is impossible. Error handling inconsistency forces every consumer to write custom parsing logic. Backward compatibility is the single most important API design principle — breaking changes destroy consumer trust and create coordination nightmares across teams.

## Common Decisions (ADR Triggers)

- **API style selection** — REST vs GraphQL vs gRPC, based on client needs, performance requirements, and team expertise
- **API gateway selection** — managed (AWS API Gateway, Apigee) vs self-hosted (Kong, Tyk), feature requirements, cost model
- **Versioning strategy** — URL path vs header vs query parameter, major version policy, how long to support old versions
- **Authentication model** — OAuth 2.0 flows per use case, API key management, JWT issuer and validation, mTLS for internal APIs
- **Rate limiting policy** — global vs per-endpoint limits, tier definitions, burst allowance, how to communicate limits to consumers
- **Pagination approach** — cursor-based vs offset/limit, maximum page size, inclusion of total count (performance implications)
- **Error format standard** — RFC 7807 adoption, custom error code taxonomy, localization of error messages
- **Breaking change policy** — what constitutes a breaking change, deprecation notice period, consumer notification process
- **Contract testing** — Pact or similar for consumer-driven contracts, schema validation in CI/CD, breaking change detection

## See Also

- [security.md](security.md) -- security controls including API authentication and authorization
- [deployment.md](deployment.md) -- deployment strategies for API services
- [service-mesh.md](service-mesh.md) -- service-to-service communication, mTLS, and traffic management
- [testing-strategy.md](testing-strategy.md) -- contract testing and integration test strategies
- [api-gateway.md](api-gateway.md) -- API gateway architecture, traffic management, and request transformation
