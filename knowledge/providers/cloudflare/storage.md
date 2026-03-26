# Cloudflare Storage

## Scope

Covers Cloudflare R2 (including Super Slurper and Sippy), KV, Durable Objects, D1, Queues, and Hyperdrive. Use alongside `providers/cloudflare/workers.md` for compute bindings to these storage primitives and `providers/cloudflare/cdn-dns.md` for caching strategies in front of R2.

## Checklist

- [ ] [Critical] Evaluate R2 for S3-compatible object storage with zero egress fees; plan bucket structure, lifecycle rules, and multi-part upload configuration
- [ ] [Recommended] Assess KV for globally distributed key-value data (eventually consistent, up to 25MB values, 512-byte keys); identify read-heavy, write-infrequent use cases
- [ ] [Recommended] Determine Durable Objects requirements for strongly consistent, single-threaded stateful compute (WebSocket coordination, counters, collaborative editing)
- [ ] [Optional] Evaluate D1 for SQLite-based edge database workloads (read replicas at edge, single primary writer, 10GB max database size per database)
- [ ] [Recommended] Plan Queues architecture for guaranteed message delivery between Workers (at-least-once, batched consumption, dead-letter handling)
- [ ] [Recommended] Configure Hyperdrive for connection pooling to existing PostgreSQL and MySQL databases (reduces connection overhead from Workers)
- [ ] [Recommended] Design data residency strategy: R2 storage locations (automatic vs jurisdiction-restricted), KV jurisdictions, Durable Object location hints
- [ ] [Recommended] Plan R2 event notifications (object created/deleted) for triggering Workers on storage events
- [ ] [Recommended] Assess R2 pricing model vs S3: R2 has zero egress but per-operation costs (Class A/B); model costs based on actual access patterns
- [ ] [Recommended] Design cache invalidation strategy when using KV as a cache layer (KV has no built-in TTL expiration guarantees beyond "best effort")
- [ ] [Optional] Evaluate Durable Objects hibernation API for WebSocket-heavy workloads to reduce costs during idle periods
- [ ] [Recommended] Plan migration path from external databases to D1 or from S3 to R2 using Workers + bulk migration tooling
- [ ] [Optional] Evaluate R2 Super Slurper for bulk migration of data from existing S3-compatible or Google Cloud Storage buckets into R2; supports incremental and one-time migrations
- [ ] [Optional] Evaluate R2 Sippy for incremental, lazy migration from S3 to R2; Sippy proxies cache misses back to the source S3 bucket, gradually populating R2 without upfront bulk copy

## Why This Matters

Cloudflare's storage primitives are designed for edge-first architectures where data locality directly impacts latency. Each product occupies a distinct consistency-performance tradeoff: KV is globally replicated and eventually consistent (optimized for reads), Durable Objects provide strong consistency with single-point-of-coordination semantics, D1 offers relational queries at the edge with read replicas, and R2 provides bulk object storage without egress penalties. Choosing the wrong primitive for a workload results in either consistency violations (using KV where strong consistency is needed) or unnecessary cost and latency (using Durable Objects for read-heavy cacheable data). Hyperdrive and Queues solve connectivity problems that arise when edge compute needs to interact with centralized databases and asynchronous workflows.

## Common Decisions (ADR Triggers)

- **R2 vs S3 (or GCS/Azure Blob)**: R2 wins on egress cost (zero) and Cloudflare ecosystem integration. S3 wins on feature maturity (S3 Object Lock, S3 Select, broader lifecycle rule support, cross-region replication). Use R2 for egress-heavy workloads (media serving, CDN origin) and S3 for compliance-heavy workloads requiring Object Lock or complex lifecycle policies.
- **KV vs Durable Objects vs D1**: KV for read-heavy, eventually-consistent data (configuration, feature flags, cached API responses). Durable Objects for coordination requiring strong consistency (rate limiters, counters, WebSocket state, collaborative cursors). D1 for relational queries with moderate write volumes. Never use KV for data requiring read-after-write consistency.
- **Durable Objects vs external database**: Durable Objects are single-threaded and co-located with their state, giving sub-millisecond reads. But they are limited in storage size, lack SQL queries, and cannot be accessed outside Workers. Use external databases (via Hyperdrive) when workloads require complex queries, joins, or access from non-Cloudflare compute.
- **Queues vs external message broker (SQS, Pub/Sub, Kafka)**: Cloudflare Queues integrate natively with Workers and avoid egress/ingress costs. But they lack features like FIFO ordering guarantees, fan-out topics, and message filtering. Use Queues for simple async pipelines within Cloudflare; use external brokers for complex event-driven architectures.
- **Hyperdrive vs direct database connection**: Always use Hyperdrive when connecting Workers to PostgreSQL/MySQL. Direct connections from Workers incur TCP+TLS handshake overhead on every invocation (Workers are stateless). Hyperdrive maintains persistent connection pools, reducing query latency by 2-10x.

## Reference Architectures

### Media Storage and Serving
```
[Upload API (Worker)] --> [R2 Bucket (origin)] --> [Cloudflare CDN Cache]
        |                         |                        |
   [Presigned URLs]          [Lifecycle Rules]        [Cache Rules]
   [Multipart Upload]       [Event Notifications]    [Image Resizing]
                                  |
                            [Processing Worker]
                            [Thumbnail Generation]
```
Workers generate presigned URLs for direct client-to-R2 uploads (bypassing Worker egress limits). R2 event notifications trigger a processing Worker for thumbnail generation or transcoding. Cloudflare CDN caches R2 objects at the edge with cache rules controlling TTL. Image Resizing transforms on-the-fly without storing variants. Zero egress fees make R2 ideal as a CDN origin.

### Real-Time Collaboration (Durable Objects)
```
[Client A (WebSocket)] --\
                          --> [Durable Object Instance (room-123)]
[Client B (WebSocket)] --/           |
                               [In-memory State]
                               [Transactional Storage API]
                               [Hibernation when idle]
                                     |
                               [Periodic Snapshot to R2]
```
Each collaboration room maps to a single Durable Object. WebSocket connections are managed by the DO, which maintains authoritative in-memory state. The DO's transactional storage API persists state changes durably. Hibernation API allows the DO to sleep during idle periods (WebSocket connections are preserved) to reduce costs. Periodic snapshots to R2 provide backup and enable analytics on historical state.

### Edge Application with Mixed Storage
```
[Client Request] --> [Worker (Router)]
                          |
        +-----------------+-----------------+
        |                 |                 |
   [KV Lookup]     [D1 Query]        [Durable Object]
   (config, flags)  (user data,       (rate limiter,
   (cached content)  product catalog)  session state)
        |                 |                 |
        +--------+--------+---------+-------+
                 |                   |
           [Hyperdrive]         [R2 Storage]
           (legacy PostgreSQL)  (file attachments)
```
Workers route requests to the appropriate storage backend based on data characteristics. KV serves configuration and cached content (sub-millisecond reads). D1 handles relational queries for structured data. Durable Objects manage per-user rate limiting and session state. Hyperdrive connects to existing PostgreSQL databases during migration. R2 stores file attachments with zero egress.

## Reference Links

- [Cloudflare R2 Documentation](https://developers.cloudflare.com/r2/) -- S3-compatible object storage, pricing, lifecycle rules, and event notifications
- [Cloudflare KV Documentation](https://developers.cloudflare.com/kv/) -- globally distributed key-value store, consistency model, and API reference
- [Cloudflare D1 Documentation](https://developers.cloudflare.com/d1/) -- edge SQLite database, migrations, query API, and read replication

## See Also

- `general/data.md` -- general data architecture patterns
- `providers/cloudflare/workers.md` -- compute bindings for storage primitives
- `providers/cloudflare/cdn-dns.md` -- caching strategies in front of R2
