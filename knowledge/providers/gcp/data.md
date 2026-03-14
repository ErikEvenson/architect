# GCP Data Services

## Checklist

- [ ] Is Cloud SQL selected for relational workloads, with the appropriate tier and high availability configuration (regional instance with automatic failover)?
- [ ] Are Cloud SQL instances configured with private IP only (no public IP), using Private Service Connect or private services access?
- [ ] Is Cloud SQL configured with automated backups, point-in-time recovery, and cross-region read replicas for disaster recovery?
- [ ] Is Cloud Spanner evaluated for workloads requiring global strong consistency, horizontal scaling, and 99.999% availability SLA?
- [ ] Is Cloud Spanner node count and processing units right-sized based on read/write throughput, with autoscaler configured?
- [ ] Is Memorystore for Redis configured with the appropriate tier? (Basic for caching without HA, Standard for replication and failover)
- [ ] Is Memorystore deployed with AUTH enabled, in-transit encryption, and private service access (no public IP)?
- [ ] Is Cloud Bigtable evaluated for high-throughput, low-latency NoSQL workloads (time-series, IoT, analytics) with cluster sizing based on storage and throughput needs?
- [ ] Is Firestore selected for serverless document database workloads, with the appropriate mode (Native for mobile/web, Datastore for server-side)?
- [ ] Are database connections using Cloud SQL Auth Proxy or Cloud SQL Connector libraries for secure IAM-based authentication?
- [ ] Is customer-managed encryption (CMEK) enabled for Cloud SQL, Spanner, and Bigtable using Cloud KMS?
- [ ] Are maintenance windows configured for Cloud SQL during low-traffic periods, and is the database flag configuration version-controlled?
- [ ] Is AlloyDB evaluated for PostgreSQL workloads requiring analytical and transactional performance with columnar engine?

## Why This Matters

GCP offers a uniquely broad database portfolio, from globally consistent Spanner to serverless Firestore. Cloud SQL differs from AWS RDS in its use of the Cloud SQL Auth Proxy for connectivity. Spanner's pricing model (per-node plus storage) requires careful capacity planning. Bigtable requires schema design expertise (row key design) to achieve performance. Choosing the wrong database type creates significant migration costs.

## Common Decisions (ADR Triggers)

- **Cloud SQL vs AlloyDB** -- standard managed PostgreSQL/MySQL vs Google's enhanced PostgreSQL with columnar engine
- **Cloud SQL vs Spanner** -- regional relational vs globally distributed strongly consistent, cost implications
- **Firestore mode** -- Native mode (real-time sync, offline) vs Datastore mode (server-side, GQL queries)
- **Bigtable vs Firestore** -- high-throughput wide-column vs serverless document, pricing model differences
- **Memorystore tier** -- Basic (no HA, lower cost) vs Standard (automatic failover), Redis vs Memcached
- **Cloud SQL connectivity** -- Cloud SQL Auth Proxy vs private IP with VPC peering vs Cloud SQL Connector libraries
- **Spanner instance sizing** -- processing units (100-999) vs nodes (1000+ PUs), regional vs multi-regional configuration
