# Data

## Checklist

- [ ] What type of database is needed? (relational, document, key-value, graph, time-series)
- [ ] What is the expected data volume? Growth rate?
- [ ] Is the workload read-heavy, write-heavy, or balanced?
- [ ] What replication strategy? (synchronous, asynchronous, multi-region)
- [ ] What is the backup strategy? Frequency? Retention period?
- [ ] Is point-in-time recovery needed?
- [ ] Is data encryption at rest required? What key management?
- [ ] Is data encryption in transit required?
- [ ] Are there data residency requirements? (data must stay in specific regions)
- [ ] Is a caching layer needed? What caching strategy? (read-through, write-behind, aside)
- [ ] What is the connection pooling strategy?
- [ ] Is database failover automatic or manual?
- [ ] Are there schema migration requirements?
- [ ] Is there a data archival strategy for old data?
- [ ] Are there compliance requirements for data handling? (PCI, HIPAA, GDPR)

## Why This Matters

Data loss is often unrecoverable. Poor replication strategy leads to data inconsistency. Missing encryption violates compliance requirements. No backup strategy means disaster recovery is impossible.

## Common Decisions (ADR Triggers)

- **Database engine selection** — managed vs self-hosted, SQL vs NoSQL
- **Replication model** — single-region multi-AZ vs multi-region
- **Backup and retention policy** — frequency, retention, cross-region copies
- **Caching strategy** — Redis, Memcached, application-level
- **Encryption approach** — provider-managed keys vs customer-managed keys
