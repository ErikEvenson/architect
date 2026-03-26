# MySQL and MariaDB

## Scope

This file covers **MySQL and MariaDB** architecture decisions: InnoDB configuration and tuning, Group Replication and InnoDB Cluster, MySQL Router for connection routing, ProxySQL for advanced query routing and connection pooling, buffer pool sizing and performance tuning, backup strategies (mysqldump, mysqlpump, Percona XtraBackup, MariaDB Backup), MySQL vs MariaDB feature and compatibility divergence, and migration paths to Amazon Aurora, Google Cloud SQL, and Azure Database for MySQL. For general database strategy (engine selection, replication patterns, encryption), see `general/data.md`. For migration methodology and cutover planning, see `general/database-migration.md`.

## Checklist

- [ ] **[Critical]** Select between MySQL and MariaDB and understand the divergence implications (MySQL and MariaDB diverged significantly after MariaDB 10.x; replication compatibility is not guaranteed across forks; MariaDB offers features like system-versioned tables and columnar storage via ColumnStore that MySQL lacks; MySQL offers Group Replication and InnoDB Cluster that MariaDB does not support — switching between forks mid-project requires thorough compatibility testing of SQL syntax, authentication plugins, and replication protocols)
- [ ] **[Critical]** Size the InnoDB buffer pool to maximize in-memory data access (set innodb_buffer_pool_size to 70-80% of available RAM on dedicated database servers; enable multiple buffer pool instances for concurrency on servers with large buffer pools; monitor buffer pool hit ratio and aim for 99%+ for OLTP workloads — an undersized buffer pool forces excessive disk reads and is the most common cause of MySQL performance problems)
- [ ] **[Critical]** Design replication topology for HA and read scaling (MySQL Group Replication with InnoDB Cluster for multi-primary or single-primary automatic failover; traditional asynchronous replication for read replicas and cross-region DR; semi-synchronous replication for reduced data loss risk; MariaDB Galera Cluster for synchronous multi-primary — choose single-primary mode unless the application is designed for multi-primary conflict resolution)
- [ ] **[Critical]** Define backup strategy with explicit RPO and tested restore procedures (Percona XtraBackup or MariaDB Backup for hot physical backups without locking; mysqldump or mysqlpump for logical backups suitable for smaller databases or cross-version migrations; binary log backup for point-in-time recovery between physical backups — full backup daily, binary log backup every 5-15 minutes, and test restores monthly including point-in-time recovery to a specific transaction)
- [ ] **[Critical]** Deploy a connection proxy for routing, pooling, and failover (MySQL Router with InnoDB Cluster for integrated routing and automatic failover detection; ProxySQL for advanced query routing, connection multiplexing, query caching, and read/write splitting; MaxScale for MariaDB environments — direct application connections to the database without a proxy layer create tight coupling and make topology changes disruptive)
- [ ] **[Critical]** Configure InnoDB redo log and flush settings for durability and performance (innodb_flush_log_at_trx_commit=1 for full ACID compliance with every transaction flushed to disk; setting to 2 for better performance with up to 1 second of data loss risk on OS crash; innodb_log_file_size large enough to hold 1-2 hours of write activity to reduce checkpoint frequency — changing durability settings is a deliberate trade-off between performance and data safety that must be documented)
- [ ] **[Recommended]** Tune InnoDB for the workload profile (innodb_io_capacity and innodb_io_capacity_max matched to actual storage IOPS; innodb_read_io_threads and innodb_write_io_threads scaled for concurrent I/O; innodb_flush_method=O_DIRECT on Linux to bypass OS cache double-buffering; innodb_file_per_table enabled for manageable tablespace sizing — default InnoDB settings assume slow storage and conservative concurrency)
- [ ] **[Recommended]** Plan schema design around InnoDB clustering and indexing behavior (InnoDB tables are clustered on the primary key; use auto-increment integers or ordered UUIDs for primary keys to avoid page splits; avoid random UUIDs as primary keys which cause severe write amplification; design secondary indexes knowing they include the primary key — poor primary key choice degrades both write performance and storage efficiency)
- [ ] **[Recommended]** Assess managed MySQL options for operational simplicity (Amazon Aurora MySQL for high throughput with storage auto-scaling and up to 15 read replicas; Amazon RDS MySQL for standard managed MySQL; Google Cloud SQL for MySQL with automatic HA and backups; Azure Database for MySQL Flexible Server — Aurora's storage layer provides 6-way replication and faster failover than standard MySQL replication)
- [ ] **[Recommended]** Implement monitoring for replication lag, slow queries, and InnoDB metrics (monitor Seconds_Behind_Master or Group Replication applier queue for replication health; enable slow query log with appropriate thresholds; track InnoDB buffer pool hit ratio, row lock waits, and history list length; alert on growing undo log or long-running transactions — InnoDB performance degradation is typically gradual and detectable before it becomes an outage)
- [ ] **[Recommended]** Design encryption at rest and in transit (InnoDB tablespace encryption using keyring plugin for at-rest encryption; require TLS for all client connections with minimum TLS 1.2; use the enterprise audit plugin or MariaDB audit plugin for access logging — encryption configuration differs between MySQL and MariaDB and between Community and Enterprise editions)
- [ ] **[Optional]** Evaluate MySQL Enterprise vs Community edition (Enterprise includes Thread Pool for high-concurrency connection handling, Enterprise Audit, Enterprise Firewall, Enterprise Encryption, and Enterprise Monitor; Percona Server for MySQL provides many Enterprise-equivalent features as open source including thread pool and audit logging — assess whether Enterprise features justify the Oracle licensing cost or whether Percona Server meets requirements)
- [ ] **[Optional]** Plan migration to Aurora or cloud-managed MySQL (Aurora MySQL is wire-compatible with MySQL 5.7 and 8.0; test application compatibility with Aurora's distributed storage model, which behaves differently for large transactions and temp table usage; evaluate Aurora Serverless v2 for variable workloads; consider Aurora Global Database for cross-region DR — Aurora's storage architecture changes some MySQL assumptions about disk I/O patterns and crash recovery)

## Why This Matters

MySQL is the most widely deployed open-source relational database, powering applications from small web services to large-scale internet platforms. However, MySQL's apparent simplicity masks configuration decisions that dramatically affect reliability and performance. The single most impactful setting — innodb_buffer_pool_size — is often left at its default of 128 MB, which forces a database with even a few gigabytes of data to perform constant disk reads. Similarly, InnoDB's default durability settings and redo log size are conservative, and tuning them to match actual storage capabilities and durability requirements can improve write throughput by an order of magnitude.

The MySQL and MariaDB ecosystem split creates a strategic decision that many organizations underestimate. While the forks were compatible through MariaDB 10.2, subsequent releases have diverged in replication protocols, optimizer behavior, authentication mechanisms, and feature sets. Organizations that assumed MariaDB was a drop-in replacement for MySQL (or vice versa) have encountered compatibility issues during version upgrades, replication setup, and cloud migration. Cloud managed services universally support MySQL (not MariaDB), making the fork choice a factor in cloud migration planning. Group Replication and InnoDB Cluster provide MySQL with integrated HA capabilities that reduce reliance on external tools, but they require MySQL 8.0+ and InnoDB-only schemas, which may require application changes for workloads still using MyISAM tables or older MySQL versions.

## Common Decisions (ADR Triggers)

### ADR: MySQL vs MariaDB

**Context:** The organization must choose between MySQL and MariaDB for a new deployment or standardize across existing environments.

**Options:**

| Criterion | MySQL (Oracle) | MariaDB | Percona Server for MySQL |
|---|---|---|---|
| Cloud Managed Options | Aurora, RDS, Cloud SQL, Azure | SkySQL (MariaDB), limited cloud options | Not available as managed service |
| Group Replication / InnoDB Cluster | Yes | No (uses Galera Cluster instead) | Yes (MySQL-compatible) |
| System-Versioned Tables | No | Yes (temporal queries built-in) | No |
| Thread Pool | Enterprise only | Built-in (Community) | Built-in (free) |
| Audit Plugin | Enterprise only | Built-in (Community) | Built-in (free) |
| Oracle Licensing Required | Community free; Enterprise paid | Fully open source (GPLv2/BSL) | Fully open source (GPLv2) |
| Replication Compatibility | Standard MySQL replication | Diverging from MySQL protocol | MySQL-compatible |

**Decision drivers:** Cloud migration plans (Aurora/RDS require MySQL compatibility), need for Enterprise features without Oracle licensing (favors Percona), specific MariaDB features (system-versioned tables, ColumnStore), and existing team expertise.

### ADR: HA and Failover Architecture

**Context:** The MySQL/MariaDB deployment must survive failures and meet defined RPO and RTO targets.

**Options:**
- **InnoDB Cluster (Group Replication + MySQL Router + MySQL Shell):** Integrated HA solution for MySQL 8.0+. Single-primary mode with automatic failover. Built-in conflict detection for multi-primary mode. Requires minimum 3 nodes. RPO=0 in single-primary, RTO=seconds.
- **Galera Cluster (MariaDB or Percona XtraDB Cluster):** Synchronous multi-primary replication. All nodes accept writes. Automatic node provisioning and conflict detection. Requires minimum 3 nodes. Higher write latency due to certification-based replication. RPO=0, RTO=seconds.
- **Semi-synchronous replication with ProxySQL:** At least one replica acknowledges each transaction before commit returns. ProxySQL handles routing and failover detection. Simpler than Group Replication but slower failover. RPO=0 (when semi-sync is active), RTO=seconds-to-minutes depending on proxy configuration.
- **Asynchronous replication with manual failover:** Standard MySQL replication. Simplest to operate. RPO=seconds of replication lag. RTO=minutes for manual promotion. Acceptable for non-critical databases.

**Decision drivers:** RPO/RTO requirements, MySQL vs MariaDB fork choice, multi-primary write requirement, operational complexity tolerance, and number of available nodes.

### ADR: Connection Proxy Selection

**Context:** A proxy layer is needed for connection management, query routing, and failover handling.

**Options:**
- **MySQL Router:** Lightweight proxy bundled with InnoDB Cluster. Automatic topology awareness via Group Replication metadata. Limited query-level routing. Best for InnoDB Cluster deployments where simplicity is preferred.
- **ProxySQL:** Feature-rich proxy with query-level routing rules, connection multiplexing, query caching, and mirroring. Supports read/write splitting based on query patterns or hints. Steeper learning curve but more flexible. Works with both MySQL and MariaDB.
- **MaxScale (MariaDB):** Full-featured proxy for MariaDB environments. Supports read/write splitting, query filtering, and connection pooling. BSL-licensed (source-available, free for fewer than 3 servers, paid beyond). Best for MariaDB-specific deployments.
- **HAProxy / Application-level routing:** HAProxy for TCP-level load balancing with health checks. Application-level routing for read/write splitting in code. Lower operational complexity but no query-level intelligence.

**Decision drivers:** MySQL vs MariaDB fork, need for query-level routing and caching, InnoDB Cluster integration requirement, licensing constraints (MaxScale BSL), and operational simplicity preference.

## See Also

- `general/database-migration.md` — Database migration strategy, schema migration tooling, replication, and cutover planning
- `general/database-ha.md` — Database high availability patterns, replication topologies, and failover strategies
- `providers/aws/rds-aurora.md` — AWS RDS and Aurora MySQL configuration and migration

## Reference Links

- [MySQL Reference Manual](https://dev.mysql.com/doc/refman/8.4/en/) -- InnoDB, replication, performance schema, and server configuration
- [MySQL InnoDB Cluster](https://dev.mysql.com/doc/mysql-shell/8.4/en/mysql-innodb-cluster.html) -- Group Replication, MySQL Router, and MySQL Shell for HA deployments
- [MariaDB Server Documentation](https://mariadb.com/kb/en/documentation/) -- MariaDB-specific features, Galera Cluster, and compatibility with MySQL
