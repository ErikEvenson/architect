# API Gateway

## Scope

This file covers **API gateway architecture decisions** including gateway selection, authentication enforcement, traffic management, request transformation, and API lifecycle concerns at the gateway layer. API gateways handle north-south traffic (external clients to internal services) and optionally east-west traffic between internal services. For API design conventions (versioning, pagination, error formats), see `general/api-design.md`. For service-to-service communication and mTLS via sidecar proxies, see `general/service-mesh.md`. For deployment strategies, see `general/deployment.md`.

## Checklist

- [ ] **[Critical]** Is an API gateway justified, and is the boundary between gateway, load balancer, and service mesh clearly defined? (Load balancers handle L4/L7 traffic distribution without application logic; API gateways add authentication, rate limiting, transformation, and routing at L7; service meshes handle east-west service-to-service concerns. Overlap between these layers is the most common source of confusion and misconfiguration)
- [ ] **[Critical]** Which gateway platform is selected, and does the cost model match the expected traffic volume? (Managed: AWS API Gateway REST/HTTP/WebSocket, Azure API Management, GCP API Gateway, Apigee -- per-request pricing can become expensive at high volumes; self-hosted: Kong, Traefik, APISIX, Envoy Gateway, Tyk -- operational cost in staff time and infrastructure but predictable at scale)
- [ ] **[Critical]** What authentication and authorization is enforced at the gateway? (API key validation for simple integrations, OAuth 2.0 token introspection or JWT validation for user-facing APIs, mTLS for service-to-service -- decide what the gateway validates vs. what is delegated to backend services. Gateway should handle identity verification; backends should handle fine-grained authorization)
- [ ] **[Critical]** How is rate limiting configured, and what are the limits per client, per endpoint, and globally? (Fixed window is simplest but allows bursts at window boundaries; sliding window is smoother but more complex; token bucket allows controlled bursts. Define limits per API key or OAuth client, set different limits per endpoint based on cost, return 429 with Retry-After header, and decide on local vs. distributed rate limiting for multi-instance gateways)
- [ ] **[Recommended]** How is API versioning handled at the gateway? (URL path /v1/resource is most common and simplest to route; Accept header with media type versioning is RESTful but harder to test in browsers; query parameter ?version=1 is less common. The gateway must route different versions to different backend deployments without cross-contamination)
- [ ] **[Recommended]** What request and response transformations does the gateway perform? (Header injection, request validation against OpenAPI schemas, response filtering to strip internal fields, protocol translation such as REST-to-gRPC. Keep transformations minimal -- complex logic in the gateway becomes an untestable bottleneck)
- [ ] **[Recommended]** Is the Backend for Frontend pattern implemented through the gateway? (Separate gateway configurations or dedicated gateway instances per client type -- mobile, web, third-party -- allowing tailored response shapes, aggregation of multiple backend calls, and client-specific rate limits without polluting a shared API surface)
- [ ] **[Recommended]** How are canary releases and traffic splitting handled at the gateway? (Weighted routing to direct a percentage of traffic to new backend versions, header-based routing for internal testing, cookie-based routing for session affinity during canary -- coordinate with deployment strategy to avoid conflicts between gateway-level and service-mesh-level traffic splitting)
- [ ] **[Recommended]** In Kubernetes, is the Gateway API standard adopted instead of legacy Ingress? (Gateway API provides richer routing, cross-namespace references, traffic splitting, and header-based matching natively; supported by Kong, Traefik, APISIX, Envoy Gateway, Istio, and Cilium. Legacy Ingress is functional but frozen and requires annotations for advanced features)
- [ ] **[Recommended]** How is the gateway monitored and what SLOs are defined? (Track request latency at p50/p95/p99, error rates by status code, rate limit hit counts, authentication failure rates. The gateway is a single point of failure for all API traffic -- its availability SLO must match or exceed the strictest backend SLO)
- [ ] **[Optional]** Is a GraphQL gateway needed, and how does it integrate with REST backends? (Apollo Gateway or Apollo Federation for multi-service GraphQL; schema stitching vs. federation -- federation gives teams ownership of their subgraphs. Consider query complexity limits, depth limits, and cost analysis to prevent expensive queries from overwhelming backends)
- [ ] **[Optional]** Are WebSocket or streaming APIs routed through the gateway? (AWS API Gateway supports WebSocket APIs natively; Kong and Traefik support WebSocket proxying; ensure connection limits, idle timeouts, and authentication for long-lived connections are configured. Managed gateways often charge per connection-minute for WebSockets)
- [ ] **[Optional]** Is response caching configured at the gateway? (Cache GET responses by path and query parameters, set TTLs per endpoint, invalidate on write operations. Gateway-level caching reduces backend load but adds cache coherence complexity -- suitable for read-heavy, infrequently changing data)

## Why This Matters

The API gateway is the front door to every service in the architecture. Every external request passes through it, making it simultaneously the most critical infrastructure component and the most attractive target for misconfiguration. A gateway that fails to enforce authentication exposes every backend service. A gateway without rate limiting allows a single client to overwhelm the entire platform. A gateway with excessive transformation logic becomes an opaque bottleneck that is difficult to test and debug.

Cost is a frequently underestimated concern. Managed API gateways such as AWS API Gateway charge per request -- at $3.50 per million requests, an API handling 100 million requests per month costs $350 in gateway fees alone, before accounting for data transfer and caching. At higher volumes, self-hosted gateways such as Kong or APISIX running on existing Kubernetes infrastructure become significantly cheaper in direct costs, though they require operational investment in upgrades, monitoring, and scaling. The cost model decision should be made early because migrating between gateway platforms requires rewriting routing rules, authentication integration, and transformation logic.

The boundary between API gateway, load balancer, and service mesh is the most important architectural clarity to establish. Without clear responsibility boundaries, teams duplicate rate limiting in the gateway and the mesh, apply authentication inconsistently across layers, and debug routing issues across three different configuration systems. The general principle is: the API gateway handles external-facing concerns (client authentication, rate limiting, API versioning, request validation), the service mesh handles internal service-to-service concerns (mTLS, retries, circuit breaking), and the load balancer handles raw traffic distribution. When a team cannot articulate which layer handles which concern, incidents are longer and harder to diagnose.

## Common Decisions (ADR Triggers)

- **Managed vs. self-hosted gateway** -- managed gateways (AWS API Gateway, Azure APIM, Apigee) reduce operational burden but introduce per-request costs and vendor lock-in for routing configuration; self-hosted gateways (Kong, Traefik, APISIX, Envoy Gateway) offer full control and predictable costs but require operational capacity for upgrades, scaling, and high availability
- **Gateway authentication strategy** -- gateway-terminated JWT validation vs. token passthrough to backends, API key management approach, whether to use OAuth 2.0 introspection (real-time but adds latency) or local JWT validation (fast but cannot revoke tokens until expiry)
- **Rate limiting architecture** -- local rate limiting (per-instance counters, simple but inaccurate with multiple gateway instances) vs. distributed rate limiting (Redis or similar shared counter, accurate but adds latency and external dependency); fixed window vs. sliding window vs. token bucket algorithm
- **API versioning strategy at the gateway** -- URL path versioning with separate route rules per version vs. header-based versioning with content negotiation; how to sunset old versions and redirect clients
- **Gateway per team vs. shared gateway** -- single shared gateway simplifies operations but creates a bottleneck for configuration changes; per-team or per-domain gateways give autonomy but multiply operational overhead and complicate cross-cutting concerns like authentication
- **BFF pattern adoption** -- dedicated gateway configuration per client type vs. single unified API; BFF reduces payload sizes and call counts for mobile clients but multiplies the number of API surfaces to maintain
- **Kubernetes Ingress vs. Gateway API** -- legacy Ingress with controller-specific annotations vs. Gateway API standard with richer native routing; Gateway API is the future standard but may have less mature tooling for specific controllers
- **GraphQL gateway adoption** -- Apollo Federation vs. schema stitching vs. single GraphQL server; federation gives service teams ownership but adds complexity in schema composition, error handling, and query planning across subgraphs

## Reference Links

- [Kong Gateway](https://docs.konghq.com/)
- [Apache APISIX](https://apisix.apache.org/)
- [Traefik Proxy](https://doc.traefik.io/traefik/)
- [Envoy Gateway](https://gateway.envoyproxy.io/)
- [AWS API Gateway](https://docs.aws.amazon.com/apigateway/)
- [Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/)
- [Google Cloud API Gateway](https://cloud.google.com/api-gateway/docs)
- [Apigee](https://cloud.google.com/apigee/docs)
- [Kubernetes Gateway API](https://gateway-api.sigs.k8s.io/)
- [Apollo Federation](https://www.apollographql.com/docs/federation/)

## See Also

- [api-design.md](api-design.md) -- API style selection, versioning conventions, pagination, error formats
- [service-mesh.md](service-mesh.md) -- service-to-service communication, mTLS, traffic management
- [security.md](security.md) -- authentication, authorization, zero-trust networking
- [deployment.md](deployment.md) -- canary releases, blue-green deployments, CI/CD pipelines
- [networking.md](networking.md) -- Kubernetes networking, CNI, NetworkPolicy
- [tls-certificates.md](tls-certificates.md) -- certificate management and rotation
- [observability.md](observability.md) -- metrics, tracing, and logging for gateway monitoring
- `patterns/microservices.md` -- microservices decomposition, inter-service communication, and service mesh patterns
