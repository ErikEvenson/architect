# Cloudflare Workers and Edge Compute Platform

## Scope

Covers Cloudflare Workers runtime, Pages, edge storage bindings (KV, Durable Objects, D1, R2, Queues), Hyperdrive, Workers AI, Vectorize, Workflows, and Service Bindings. Use alongside `providers/cloudflare/cdn-dns.md` for caching and `providers/cloudflare/security.md` for WAF/bot management in front of Workers.

## Checklist

- [ ] [Critical] Workers are deployed with appropriate routes or custom domains; route patterns use wildcards correctly (`example.com/api/*` matches subpaths, `*.example.com/*` matches subdomains)
- [ ] [Critical] Worker size is within the limits: 1 MB after compression (free), 10 MB (paid); large dependencies are avoided or replaced with lighter alternatives
- [ ] [Critical] CPU time limits are understood: 10 ms (free), 30 s (paid Standard); long-running tasks use scheduled events or Queues rather than blocking request handlers
- [ ] [Critical] KV is used only for read-heavy, eventually-consistent data (configuration, feature flags, translated strings); writes propagate globally within 60 seconds but may take longer under load
- [ ] [Critical] Durable Objects are used when strong consistency, coordination, or single-point-of-serialization is required (collaborative editing, rate counters, WebSocket rooms, distributed locks)
- [ ] [Recommended] Durable Object location hints are set to co-locate with the primary data source or user base when latency matters
- [ ] [Recommended] R2 buckets have appropriate CORS policies, lifecycle rules for object expiration, and public access is only enabled intentionally via r2.dev or custom domain
- [ ] [Recommended] D1 database schema migrations are managed through Wrangler and tested locally; D1 has a 10 GB database size limit and is best for read-heavy workloads at the edge
- [ ] [Recommended] Queues are used for background processing, retry logic, and decoupling write paths; consumers are configured with appropriate batch sizes (max 100) and retry policies
- [ ] [Recommended] Hyperdrive is configured for connection pooling to centralized databases (PostgreSQL and MySQL); connection strings are stored as secrets, not in wrangler.toml
- [ ] [Recommended] Pages projects have build configuration, environment variables, and preview/production branch mappings correctly set; Functions (Pages + Workers) use the `/functions` directory convention
- [ ] [Critical] Wrangler CLI is pinned to a specific version in CI/CD; `wrangler deploy` is used (not deprecated `wrangler publish`); secrets are set via `wrangler secret put`, not in config files
- [ ] [Recommended] Service bindings are used for Worker-to-Worker communication instead of HTTP fetch to avoid egress costs and reduce latency
- [ ] [Optional] Workers AI is evaluated for running inference at the edge (LLMs, image classification, embeddings, text-to-image) without managing GPU infrastructure
- [ ] [Optional] Vectorize is configured for vector search use cases (RAG, semantic search, recommendations); indexes are bound to Workers and populated via Workers AI embeddings or external pipelines
- [ ] [Optional] Workflows are used for durable execution of multi-step, long-running tasks with automatic retries, state persistence, and step-level error handling

## Why This Matters

Workers run on Cloudflare's edge network in 300+ locations, executing within V8 isolates rather than containers. This gives sub-millisecond cold starts but imposes a fundamentally different programming model than traditional servers. Choosing the wrong storage primitive (KV when you need consistency, Durable Objects when you need global reads) creates subtle bugs that only manifest under load or geographic distribution. R2's zero-egress pricing can save significant money compared to S3 but requires understanding its consistency model and API compatibility gaps. D1 is SQLite-based and excellent for read-heavy edge workloads but unsuitable as a primary transactional database for write-heavy applications.

## Common Decisions (ADR Triggers)

- **KV vs Durable Objects vs D1 for state**: KV is eventually consistent, optimized for reads (< 1 ms globally), and cheap. Durable Objects provide strong consistency but serialize all access through a single instance (located in one region). D1 gives relational queries at the edge but is read-optimized with SQLite limitations. This is the most consequential storage decision on the platform.
- **R2 vs external object storage (S3, GCS)**: R2 is S3-compatible with zero egress fees but lacks some S3 features (object lock, certain lifecycle transitions, S3 Select). If the application primarily serves objects through Cloudflare or Workers, R2 eliminates egress costs. If objects are consumed by AWS services, S3 may be simpler.
- **Workers vs Pages Functions**: Pages Functions are Workers that are co-deployed with a static site. Use Pages when the project is primarily a frontend with API routes. Use standalone Workers when the compute is an independent service, middleware layer, or has no associated static assets.
- **Queues vs external message brokers**: Cloudflare Queues integrate natively with Workers but have limited features compared to SQS, Pub/Sub, or Kafka (no FIFO ordering, max 100 messages per batch, limited retention). Use Queues for simple background jobs; use external brokers for complex event-driven architectures.
- **Hyperdrive vs direct database connections**: Hyperdrive pools and caches connections to PostgreSQL and MySQL databases, dramatically reducing connection overhead from Workers. Essential when connecting to a centralized database from Workers (which would otherwise open a new connection per request).
- **Monolithic Worker vs Service Bindings**: A single large Worker is simpler to deploy but harder to maintain and test. Service Bindings allow breaking functionality into separate Workers that call each other without HTTP overhead. Decide based on team structure and deployment independence needs.
- **Edge vs origin rendering**: Workers can do full SSR at the edge, eliminating origin round-trips but adding complexity to the deployment pipeline. Frameworks like Remix, Next.js (via @cloudflare/next-on-pages), SvelteKit, and Astro have Cloudflare adapters. Decide based on latency requirements and framework maturity on the platform.

## Reference Architectures

### Full-Stack Edge Application

```
Users
  |
  v
Cloudflare Edge
  |
  +-- Pages (static assets: HTML, CSS, JS, images)
  |     Built from Git repo (GitHub/GitLab)
  |     Preview deployments per PR
  |
  +-- Pages Functions (/functions directory)
  |     |-- /api/auth/* -> Auth logic
  |     |-- /api/data/* -> CRUD operations
  |     |
  |     +-- Bindings:
  |           D1: user data, application state
  |           KV: session tokens, feature flags
  |           R2: user uploads, generated assets
  |           Queue: email sending, webhooks
  |
  +-- Queue Consumer Worker
        Processes background jobs
        Retries with exponential backoff
```

### API Gateway with Centralized Database

```
API Clients
  |
  v
Worker (API Gateway)
  |-- Route: api.example.com/*
  |-- Auth validation (JWT from KV-cached JWKS)
  |-- Rate limiting (Durable Object per API key)
  |-- Request transformation and routing
  |
  +-- Service Binding --> Worker (Users Service)
  |     +-- Hyperdrive -> PostgreSQL (us-east-1)
  |
  +-- Service Binding --> Worker (Orders Service)
  |     +-- Hyperdrive -> PostgreSQL (us-east-1)
  |
  +-- Service Binding --> Worker (Search Service)
        +-- Fetch -> Elasticsearch (external)

KV Namespace: config
  |-- JWKS keys (cached, 1hr TTL)
  |-- Feature flags
  |-- API key metadata
```

### Real-Time Collaboration with Durable Objects

```
Users (WebSocket connections)
  |
  v
Worker (WebSocket handler)
  |-- Upgrades HTTP to WebSocket
  |-- Routes to Durable Object by room ID
  |
  v
Durable Object: Room
  |-- Single-threaded, strongly consistent
  |-- Maintains list of connected WebSocket clients
  |-- Applies operational transforms / CRDTs
  |-- Persists state to Durable Object storage (SQLite-backed)
  |-- Location hint: "enam" (Eastern North America)
  |
  +-- Alarm: auto-hibernate after 30 min idle
  +-- Queue: broadcast change events for analytics

R2: document snapshots and version history
D1: document metadata, user permissions, search index
```

## See Also

- `providers/cloudflare/storage.md` -- KV, Durable Objects, D1, R2 storage bindings
- `providers/cloudflare/cdn-dns.md` -- caching and CDN integration
- `providers/cloudflare/security.md` -- WAF and bot management in front of Workers
