# Oracle Database

## Scope

This file covers **Oracle Database** architecture decisions: edition selection (Standard Edition 2, Enterprise Edition), Real Application Clusters (RAC), Data Guard (physical and logical standby), Automatic Storage Management (ASM), PGA and SGA memory sizing, RMAN backup strategy, licensing models (processor-based, Named User Plus, options and packs, audit risk), partitioning, Advanced Security (TDE, network encryption), and migration paths to PostgreSQL, AWS RDS for Oracle, or Oracle Autonomous Database. For general database strategy (engine selection, replication patterns, encryption), see `general/data.md`. For migration methodology and cutover planning, see `general/database-migration.md`.

## Checklist

- [ ] **[Critical]** Select the appropriate Oracle edition based on feature requirements and licensing exposure (Enterprise Edition for RAC, Data Guard, partitioning, and Advanced Compression; Standard Edition 2 for single-instance or RAC with 2-socket limit and 16-thread cap; Developer for non-production only — inadvertent use of Enterprise-only features on Standard Edition triggers license compliance violations during audits)
- [ ] **[Critical]** Audit current usage of licensed options and packs before any architecture change (Diagnostics Pack, Tuning Pack, Advanced Security, Advanced Compression, Partitioning, RAC, Active Data Guard, In-Memory, and Multitenant are separately licensed options; enabling a feature even accidentally in a script or OEM console counts as usage; run Oracle LMS scripts or a third-party audit tool to identify all features in use — license non-compliance findings routinely reach seven figures)
- [ ] **[Critical]** Design Data Guard topology for HA and DR (Maximum Protection mode for zero data loss at risk of primary stall if standby is unreachable; Maximum Availability for zero data loss with automatic degradation to async; Maximum Performance for minimal performance impact with seconds of potential data loss — configure Fast-Start Failover with an Observer for automatic failover and test switchover procedures quarterly)
- [ ] **[Critical]** Define RMAN backup strategy with explicit RPO and retention (full backups weekly, incremental level-1 daily, archive log backups every 15-30 minutes for point-in-time recovery; use block change tracking for faster incrementals; store backups in a separate location or cloud object storage via Oracle Database Backup Cloud Service — test RMAN restore and point-in-time recovery monthly)
- [ ] **[Critical]** Determine licensing model and count processors or users accurately (processor licensing counts each physical core multiplied by Oracle's core factor for that CPU architecture; Named User Plus requires a minimum of 25 NUP per processor; virtualization on VMware or cloud instances follows Oracle's partitioning policy, which often does not recognize soft partitioning — incorrect counting is the primary cause of audit shortfalls)
- [ ] **[Critical]** Size SGA and PGA based on workload characteristics (SGA buffer cache sized to achieve 95%+ hit ratio for OLTP; shared pool sized for parsed SQL retention; PGA aggregate target sized for sort and hash join operations; use Automatic Memory Management on single-instance or manual management on RAC — undersized memory causes excessive physical I/O and temp tablespace spilling)
- [ ] **[Recommended]** Configure ASM for storage management and performance (use ASM disk groups with appropriate redundancy — EXTERNAL for hardware RAID, NORMAL for 2-way mirroring, HIGH for 3-way mirroring; separate disk groups for DATA and FRA; size the Flash Recovery Area at 2-3x the database size — ASM simplifies storage management and provides automatic I/O balancing across disks)
- [ ] **[Recommended]** Evaluate migration path for cost reduction or modernization (PostgreSQL for open-source cost elimination with schema and PL/SQL conversion effort; AWS RDS for Oracle for managed infrastructure with license-included or BYOL; Oracle Autonomous Database for fully managed cloud-native with auto-tuning and auto-patching; AWS SCT and Oracle SQL Developer for schema conversion assessment — migration from Oracle requires thorough PL/SQL, stored procedure, and data type compatibility analysis)
- [ ] **[Recommended]** Design partitioning strategy for large tables (range partitioning by date for time-series data with partition pruning; list partitioning for categorical data; hash partitioning for even distribution; composite partitioning for multi-dimensional access patterns — partitioning requires Enterprise Edition and a separate license; consider whether the performance benefit justifies the licensing cost)
- [ ] **[Recommended]** Implement Transparent Data Encryption for data at rest (TDE tablespace encryption for encrypting all data in a tablespace transparently; TDE column encryption for specific sensitive columns; wallet management for encryption keys with auto-login wallets for automated startup — TDE requires Advanced Security option on Enterprise Edition, which is separately licensed)
- [ ] **[Recommended]** Plan RAC architecture for high availability and scalability (RAC provides instance-level failover and horizontal read/write scaling; requires shared storage via ASM and a private interconnect network with low latency; size the interconnect for Cache Fusion traffic; use services for workload routing and connection failover — RAC adds operational complexity and requires Enterprise Edition plus the RAC option license)
- [ ] **[Optional]** Assess Oracle Multitenant architecture for database consolidation (pluggable databases in a container database simplify patching, backup, and cloning; Standard Edition 2 allows 3 PDBs per CDB; Enterprise Edition with Multitenant option allows unlimited PDBs — Multitenant is the strategic direction for Oracle and the default architecture from 21c onward)
- [ ] **[Optional]** Evaluate GoldenGate for zero-downtime migration or real-time data integration (GoldenGate provides heterogeneous replication between Oracle and non-Oracle databases; supports bidirectional replication for active-active topologies; useful for migration cutover with minimal downtime — GoldenGate is separately licensed and adds operational complexity)

## Why This Matters

Oracle Database licensing is the single most expensive software line item in many enterprise environments, and the complexity of Oracle's licensing model creates significant financial and compliance risk. Unlike most software where you pay for what you deploy, Oracle's licensing model can penalize organizations for features they enabled inadvertently, for running on virtualization platforms Oracle does not recognize as "hard partitioned," or for failing to count cores correctly under Oracle's processor core factor table. A single Oracle LMS audit finding can exceed the cost of the entire infrastructure project. Every architecture decision — edition selection, option usage, RAC deployment, virtualization platform, and cloud migration target — has direct licensing implications that must be evaluated before implementation.

On the technical side, Oracle's performance depends heavily on correct memory sizing, storage configuration, and Data Guard topology. An undersized SGA forces excessive disk I/O that no amount of storage speed can fully compensate for, while an oversized PGA on a system with many concurrent sessions can cause memory pressure and OS swapping. Data Guard configuration determines both the data loss exposure and the recovery time during failures — the difference between Maximum Protection and Maximum Performance mode is the difference between guaranteed zero data loss and a small window of potential loss, but the operational implications of each mode are dramatically different. These decisions are difficult and expensive to change once production data is flowing.

## Common Decisions (ADR Triggers)

### ADR: Oracle Edition and Licensing Model

**Context:** The organization must select an Oracle edition and licensing model that meets technical requirements while controlling cost and audit risk.

**Options:**

| Criterion | Enterprise Edition | Standard Edition 2 |
|---|---|---|
| RAC Support | Yes (separately licensed) | Yes (2-socket, 16-thread cap) |
| Data Guard | Full (Active Data Guard separately licensed) | Physical standby only |
| Partitioning | Yes (separately licensed) | No |
| TDE | Yes (Advanced Security option) | No (available from 19c onward in SE2) |
| In-Memory | Yes (separately licensed) | No |
| Max CPU Threads | Unlimited | 16 threads per instance |
| Processor License Cost | ~$47,500 list per processor | ~$17,500 list per socket |

**Decision drivers:** Feature requirements (RAC, partitioning, TDE, Active Data Guard), database size and concurrency needs, total licensing cost including required options, and audit risk tolerance.

### ADR: HA and DR Architecture

**Context:** The database must survive infrastructure failures and meet defined RPO and RTO targets.

**Options:**
- **Data Guard (physical standby):** Byte-for-byte replica of the primary. Supports all three protection modes. Automatic failover with Fast-Start Failover and Observer. RPO=0 in synchronous mode, RTO=seconds-to-minutes. Standard approach for Oracle DR.
- **RAC + Data Guard:** RAC for local HA (instance failover) combined with Data Guard for DR (site failover). Provides both horizontal scaling and geographic redundancy. Highest availability but also highest complexity and licensing cost.
- **RAC only:** Protects against instance failure within a single site. Does not protect against site-level disasters. Appropriate when DR is handled by storage replication or backup/restore.
- **RMAN backup and restore:** Lowest cost DR option. RPO determined by backup frequency. RTO measured in hours depending on database size. Acceptable for non-critical databases or as a tertiary recovery mechanism.

**Decision drivers:** RPO/RTO requirements, number of sites, licensing budget (RAC and Active Data Guard are separately licensed options), and operational team expertise with Oracle clustering.

### ADR: Migration Away from Oracle

**Context:** The organization wants to reduce Oracle licensing costs or modernize by migrating to an alternative database platform.

**Options:**
- **PostgreSQL:** Eliminates Oracle licensing entirely. Requires PL/SQL conversion (Orafce extension helps with partial compatibility), data type mapping, and application query rewriting. Largest cost savings but highest migration effort.
- **AWS RDS for Oracle or Oracle on cloud VM:** Maintains Oracle compatibility, moves infrastructure to cloud. License-included option simplifies licensing; BYOL leverages existing licenses. Moderate migration effort — primarily a platform migration.
- **Oracle Autonomous Database:** Fully managed Oracle cloud service with auto-tuning, auto-patching, and auto-scaling. Full compatibility with existing PL/SQL and features. Shifts cost from infrastructure to consumption-based cloud pricing.

**Decision drivers:** PL/SQL code complexity and conversion feasibility, licensing cost reduction targets, team willingness to adopt a new database platform, and timeline for migration completion.

## See Also

- `general/database-migration.md` — Database migration strategy, schema migration tooling, replication, and cutover planning
- `general/database-ha.md` — Database high availability patterns, replication topologies, and failover strategies
- `providers/postgresql/database.md` — PostgreSQL configuration and HA (common Oracle migration target)
