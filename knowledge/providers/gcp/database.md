# GCP Database

## Scope

Cloud SQL (MySQL, PostgreSQL, SQL Server), Cloud SQL Enterprise Plus, AlloyDB, Cloud Spanner, Firestore (Native and Datastore mode), Bigtable, Memorystore (Redis, Memcached, Valkey), Database Migration Service.

## Checklist

- [ ] [Critical] Is Cloud SQL configured with the appropriate database engine (MySQL 8.0/8.4, PostgreSQL 17, SQL Server 2022), edition (Enterprise or Enterprise Plus for highest performance and availability), machine type, and storage type (SSD vs HDD) for the workload's IOPS and capacity requirements?
- [ ] [Critical] Is Cloud SQL high availability enabled for production instances using regional HA (automatic failover to standby in another zone), with understanding that failover causes 1-2 minutes of downtime?
- [ ] [Recommended] Are Cloud SQL read replicas deployed in the same or cross-region for read-heavy workloads, with IAM database authentication enabled instead of built-in user/password auth?
- [ ] [Critical] Is Cloud Spanner configured with the correct instance configuration (regional for low latency with 99.99% availability SLA, multi-region for 99.999% availability SLA) and node count sized for throughput (10K reads or 2K writes per node)?
- [ ] [Recommended] Are Cloud Spanner schemas designed with interleaved tables for parent-child relationships to co-locate data and avoid hotspots, with primary keys designed to distribute writes evenly (no monotonic keys)?
- [ ] [Recommended] Is AlloyDB evaluated for PostgreSQL workloads requiring high performance, with columnar engine enabled for analytical queries and auto-scaling read pool instances for read-heavy patterns?
- [ ] [Critical] Is Firestore configured in the correct mode? (Native mode for mobile/web with real-time sync and offline support, Datastore mode for server-side workloads with strong consistency)
- [ ] [Recommended] Are Firestore collections and documents designed with shallow hierarchies, composite indexes planned for multi-field queries, and single-field exemptions configured to control index storage costs?
- [ ] [Recommended] Is Bigtable row key designed to avoid hotspots (no timestamp-prefixed keys), with key prefixes that distribute reads/writes evenly across nodes and row key size kept under 4 KB?
- [ ] [Optional] Is Bigtable replication configured with appropriate cluster placement (multi-zone or multi-region) and app profiles routing policies (single-cluster routing for strong consistency, multi-cluster for availability)?
- [ ] [Recommended] Is Memorystore configured with the appropriate engine (Redis for data structures, caching, pub/sub; Memcached for simple key-value caching; Valkey for Redis-compatible open-source alternative) and tier (Basic for dev, Standard for HA with replication)?
- [ ] [Recommended] Are database connections managed via Cloud SQL Auth Proxy or Cloud SQL Connectors (Java, Python, Go, Node.js) for secure, IAM-based connections without exposing public IPs?
- [ ] [Recommended] Are automated backups, point-in-time recovery (PITR), and maintenance windows configured for all managed database instances with retention policies matching RPO requirements?
- [ ] [Optional] Is Database Migration Service (DMS) evaluated for migrations from on-premises or other clouds, with continuous replication configured for minimal-downtime cutover?
- [ ] [Optional] Is Cloud SQL Enterprise Plus evaluated for workloads requiring near-zero downtime maintenance, data cache for improved read performance, and advanced HA with faster failover?

## Why This Matters

GCP offers the broadest range of purpose-built databases among cloud providers, but choosing the wrong one is costly to reverse. Cloud Spanner provides globally consistent transactions at scale but costs 10x more than Cloud SQL per node-hour, making it appropriate only for workloads that genuinely need multi-region strong consistency. Note that Cloud Spanner regional instances provide 99.99% availability SLA (not 99.999% -- the five-nines SLA applies only to multi-region configurations). AlloyDB bridges a gap between Cloud SQL PostgreSQL and Spanner, offering 4x better price-performance than standard PostgreSQL with a columnar engine for mixed OLTP/OLAP. Firestore's mode choice (Native vs Datastore) is permanent per project and cannot be changed, making it a critical up-front decision. Bigtable performance is entirely dependent on row key design -- a poor key design causes hotspotting that no amount of node scaling can fix.

Cloud SQL Enterprise Plus edition provides enhanced performance (data cache backed by local SSD), near-zero downtime maintenance, and faster failover compared to the standard Enterprise edition. Evaluate Enterprise Plus for latency-sensitive production workloads.

Memorystore for Valkey offers a Redis-compatible, open-source in-memory data store as an alternative to Memorystore for Redis, providing cost benefits and avoiding Redis licensing concerns.

## Common Decisions (ADR Triggers)

- **Relational database** -- Cloud SQL (managed MySQL/PostgreSQL, regional) vs AlloyDB (PostgreSQL-compatible, high performance) vs Cloud Spanner (globally consistent, horizontally scalable)
- **Cloud SQL edition** -- Enterprise (standard managed database) vs Enterprise Plus (data cache, near-zero downtime maintenance, faster failover) -- Enterprise Plus for latency-sensitive production workloads
- **NoSQL model** -- Firestore (document, real-time sync) vs Bigtable (wide-column, high throughput) vs Datastore mode (document, server-side)
- **Firestore mode** -- Native mode (mobile/web, real-time listeners, offline) vs Datastore mode (server-side, strong consistency, entity groups) -- irreversible per project
- **Spanner topology** -- regional (single region, 99.99% SLA) vs multi-region (nam-eur, nam3, 99.999% SLA, higher latency for writes)
- **Caching layer** -- Memorystore Redis (data structures, persistence, pub/sub) vs Memorystore Memcached (simple caching, multi-threaded) vs Memorystore Valkey (Redis-compatible, open-source) vs application-level caching
- **Connection security** -- Cloud SQL Auth Proxy (sidecar, auto-cert rotation) vs Private IP (VPC-native, no proxy overhead) vs both, serverless VPC connectors for Cloud Run/Functions
- **Migration strategy** -- Database Migration Service (managed, continuous replication) vs native dump/restore vs third-party tools (Striim, Debezium), homogeneous vs heterogeneous migration
- **Cost model** -- Cloud SQL committed use discounts (1 or 3 year, up to 52% savings) vs on-demand, Spanner autoscaler vs fixed node count, AlloyDB read pool auto-scaling

## Reference Architectures

- [Google Cloud Architecture Center: Databases](https://cloud.google.com/architecture#databases) -- reference architectures for relational, NoSQL, and in-memory database patterns
- [Google Cloud: Cloud SQL best practices](https://cloud.google.com/sql/docs/postgres/best-practices) -- reference patterns for instance sizing, connection management, HA configuration, and backup strategy
- [Google Cloud: Cloud Spanner schema design best practices](https://cloud.google.com/spanner/docs/schema-design) -- reference guide for primary key selection, interleaved tables, and avoiding hotspots in globally distributed schemas
- [Google Cloud: Firestore data model](https://cloud.google.com/firestore/docs/data-model) -- reference design for document and collection hierarchies, subcollections, and denormalization patterns
- [Google Cloud: Bigtable schema design](https://cloud.google.com/bigtable/docs/schema-design) -- reference architecture for row key design, column family organization, and time-series data patterns
