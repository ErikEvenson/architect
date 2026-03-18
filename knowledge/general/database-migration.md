# Database Migration

## Scope

This file covers **database migration strategy and execution** including migration approaches, schema migration tooling, replication, cutover planning, and rollback. For general workload migration, see `general/workload-migration.md`. For database design decisions, see `general/data.md`.

## Checklist

- [ ] **[Critical]** What migration strategy is chosen? (lift-and-shift for speed, re-platform for managed service benefits, re-architect for schema redesign or engine change)
- [ ] **[Critical]** What schema migration tool manages DDL changes? (Flyway for JVM, Alembic for Python, Liquibase for multi-DB, Prisma Migrate, Atlas — version-controlled, repeatable)
- [ ] **[Recommended]** Is a dual-write pattern needed during transition? (write to both old and new databases, reconciliation process, eventual cutover — complex but enables zero-downtime)
- [ ] **[Recommended]** Is change data capture (CDC) used for replication? (Debezium, AWS DMS, GCP Datastream — streaming changes from source to target during migration)
- [ ] **[Critical]** What is the cutover strategy? (blue-green database switch, progressive traffic shifting, read cutover first then write cutover)
- [ ] **[Critical]** How is data validated post-migration? (row count comparison, checksum validation, application-level spot checks, reconciliation reports)
- [ ] **[Recommended]** Are performance benchmarks established before and after? (query latency p50/p95/p99, throughput, index efficiency, connection pool behavior)
- [ ] **[Critical]** What is the rollback strategy? (reverse replication, dual-write rollback, point-in-time restore, maximum rollback window)
- [ ] **[Recommended]** How is downtime estimated and communicated? (maintenance window calculation, customer notification, SLA impact assessment)
- [ ] **[Recommended]** How are large tables migrated? (partitioned migration, parallel data copy, online schema change tools like pt-online-schema-change or gh-ost)
- [ ] **[Recommended]** What happens to application code during migration? (database abstraction layer, feature flags for query routing, ORM compatibility testing)
- [ ] **[Recommended]** How are stored procedures, triggers, and views handled? (inventory, rewrite or eliminate, testing parity)
- [ ] **[Critical]** Is the migration rehearsed in a staging environment? (full dress rehearsal with production-scale data, timing measurements, runbook validation)

## Why This Matters

Database migrations are among the highest-risk infrastructure operations. Data loss during migration is often unrecoverable. Downtime estimates are frequently wrong because large table migrations take longer than expected, replication lag is underestimated, and application compatibility issues surface late. Dual-write patterns add consistency risk if not carefully implemented. Without rehearsal on production-scale data, teams discover performance problems during the actual migration window. CDC-based migrations reduce downtime but add operational complexity and require monitoring of replication lag. Every database migration needs a tested rollback plan with a clearly defined point-of-no-return.

## Common Decisions (ADR Triggers)

- **Migration strategy** — lift-and-shift (same engine, new host) vs re-platform (new managed service, same schema) vs re-architect (new engine, new schema)
- **Schema migration tooling** — Flyway vs Liquibase vs Alembic, migration file format (SQL vs declarative), versioning scheme
- **Replication approach** — CDC with Debezium/DMS vs application-level dual-write vs dump-and-restore, lag tolerance
- **Cutover method** — big-bang cutover with maintenance window vs blue-green with instant switch vs progressive traffic migration
- **Downtime budget** — zero-downtime requirement drives architecture (CDC + dual-write), acceptable window simplifies approach
- **Data validation scope** — full row-by-row comparison vs statistical sampling vs application-level smoke tests, automated vs manual
- **Large table strategy** — partitioned copy, parallel workers, online DDL tools, pre-seeding with catch-up replication
- **Rollback point-of-no-return** — when rollback becomes impossible (e.g., after writes to new schema), contingency plan beyond that point
- **Engine change implications** — SQL dialect differences, transaction isolation behavior, index types, JSON/array support, vendor-specific features

## See Also

- [data-migration-tools.md](data-migration-tools.md) -- specific tools for data transfer (rclone, pg_dump, AWS DMS)
- [data.md](data.md) -- database design decisions, storage engines, and data modeling
- [workload-migration.md](workload-migration.md) -- overall migration planning including application and infrastructure migration
- [disaster-recovery.md](disaster-recovery.md) -- rollback strategies and recovery procedures relevant to migration cutover
