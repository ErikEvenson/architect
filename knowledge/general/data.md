# Data

## Scope

This file covers **what** data management decisions need to be made. For provider-specific **how**, see the provider data files.

## Checklist

- [ ] **[Critical]** What type of database is needed? (relational, document, key-value, graph, time-series)
- [ ] **[Recommended]** What is the expected data volume? Growth rate?
- [ ] **[Recommended]** Is the workload read-heavy, write-heavy, or balanced?
- [ ] **[Critical]** What replication strategy? (synchronous, asynchronous, multi-region)
- [ ] **[Critical]** What is the backup strategy? Frequency? Retention period?
- [ ] **[Recommended]** Is point-in-time recovery needed?
- [ ] **[Critical]** Is data encryption at rest required? What key management?
- [ ] **[Critical]** Is data encryption in transit required?
- [ ] **[Critical]** Are there data residency requirements? (data must stay in specific regions)
- [ ] **[Recommended]** Is a caching layer needed? What caching strategy? (read-through, write-behind, aside)
- [ ] **[Recommended]** What is the connection pooling strategy?
- [ ] **[Critical]** Is database failover automatic or manual?
- [ ] **[Recommended]** Are there schema migration requirements?
- [ ] **[Optional]** Is there a data archival strategy for old data?
- [ ] **[Critical]** Are there compliance requirements for data handling? (PCI, HIPAA, GDPR)

## Why This Matters

Data loss is often unrecoverable. Poor replication strategy leads to data inconsistency. Missing encryption violates compliance requirements. No backup strategy means disaster recovery is impossible.

## Common Decisions (ADR Triggers)

- **Database engine selection** — managed vs self-hosted, SQL vs NoSQL
- **Replication model** — single-region multi-AZ vs multi-region
- **Backup and retention policy** — frequency, retention, cross-region copies
- **Caching strategy** — Redis, Memcached, application-level
- **Encryption approach** — provider-managed keys vs customer-managed keys

## See Also

- `providers/aws/rds-aurora.md` — AWS RDS and Aurora database configuration
- `providers/aws/dynamodb.md` — AWS DynamoDB NoSQL database
- `providers/azure/data.md` — Azure database and data services
- `providers/gcp/data.md` — GCP database and data services
