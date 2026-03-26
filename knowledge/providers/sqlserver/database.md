# SQL Server

## Scope

This file covers **SQL Server** architecture decisions: edition selection (Standard, Enterprise, Developer), Always On Availability Groups (AG), Failover Cluster Instances (FCI), log shipping, TempDB configuration, memory and MAXDOP tuning, backup strategy (full, differential, transaction log), licensing models (per-core, Server+CAL, Software Assurance, Azure Hybrid Benefit), SQL Agent jobs, SSIS/SSRS/SSAS workloads, and migration paths to Azure SQL Database, Azure SQL Managed Instance, or SQL Server on Azure VMs. For general database strategy (engine selection, replication patterns, encryption), see `general/data.md`. For migration methodology and cutover planning, see `general/database-migration.md`.

## Checklist

- [ ] **[Critical]** Select the appropriate SQL Server edition based on feature requirements and licensing budget (Enterprise for AG with readable secondaries, compression, partitioning, and online index operations; Standard for basic AG with database-level failover and 128 GB memory cap; Developer for non-production environments with full Enterprise features at no cost — mismatched editions between dev and prod mask feature-dependent bugs)
- [ ] **[Critical]** Design Always On Availability Group topology for HA and DR (synchronous commit for zero-RPO within a datacenter or region; asynchronous commit for cross-region DR with seconds-to-minutes RPO; automatic failover requires synchronous commit plus a witness; manual failover for DR replicas — test failover quarterly and document runbooks for both planned and unplanned scenarios)
- [ ] **[Critical]** Define backup strategy covering full, differential, and transaction log backups with explicit RPO (full backups weekly or daily depending on database size; differential backups every 4-12 hours to reduce restore time; transaction log backups every 5-15 minutes for point-in-time recovery — store backups off-server and test restores monthly, including tail-log recovery procedures)
- [ ] **[Critical]** Determine licensing model and count cores accurately (per-core licensing requires a minimum of 4 core licenses per physical server; Software Assurance unlocks failover rights, Azure Hybrid Benefit, and version upgrade rights; Azure Hybrid Benefit can reduce cloud VM costs by 40-55% — engage a licensing specialist for complex topologies with AG secondaries and DR replicas to avoid audit exposure)
- [ ] **[Critical]** Configure TempDB with multiple data files equal to the number of logical processors up to 8 (one file per core reduces allocation contention and PFS/GAM/SGAM latch waits; size files equally and enable trace flag 1118 on versions before 2016; place TempDB on the fastest available storage — TempDB contention is the most common preventable performance bottleneck)
- [ ] **[Critical]** Set MAXDOP and cost threshold for parallelism based on workload type (OLTP workloads typically use MAXDOP 1-4 with cost threshold 25-50; data warehouse workloads benefit from higher MAXDOP matching NUMA node core count; set max server memory to leave 4-6 GB for the OS plus memory for other services — default settings cause excessive parallelism and memory pressure)
- [ ] **[Recommended]** Plan SQL Server Agent jobs and maintenance tasks (index rebuild/reorganize schedules based on fragmentation thresholds; statistics updates for non-auto-updated columns; integrity checks via DBCC CHECKDB weekly; cleanup of backup history and job history — schedule maintenance during low-activity windows and monitor job duration trends for early warning of growth issues)
- [ ] **[Recommended]** Evaluate SSIS, SSRS, and SSAS deployment and migration strategy (SSIS packages may need conversion to Azure Data Factory pipelines or SSIS-IR for cloud migration; SSRS reports can migrate to Power BI or SSRS on Azure VM; SSAS tabular models can move to Azure Analysis Services or Power BI Premium — inventory all BI components before planning database migration)
- [ ] **[Recommended]** Assess migration target for cloud modernization (Azure SQL Database for fully managed PaaS with limited surface area; Azure SQL Managed Instance for near-100% compatibility including SQL Agent, cross-database queries, and CLR; SQL Server on Azure VM for full feature parity including SSIS/SSRS/FCI — run Data Migration Assistant and Azure Migrate assessments to identify blockers)
- [ ] **[Recommended]** Design database security with least-privilege access and auditing (use contained database users or Windows/Active Directory authentication over SQL authentication; implement row-level security and dynamic data masking for sensitive columns; enable SQL Server Audit to capture login failures, schema changes, and privileged operations; apply Transparent Data Encryption for at-rest encryption)
- [ ] **[Recommended]** Configure log shipping as a secondary DR mechanism or for reporting offload (log shipping provides a simple, well-understood DR complement to AG; restore with STANDBY mode enables read-only reporting on the secondary; monitor backup/copy/restore job latency to ensure RPO is met — log shipping works across editions and does not require Enterprise)
- [ ] **[Optional]** Evaluate Failover Cluster Instance for instance-level HA (FCI provides automatic instance failover using shared storage via SAN or Storage Spaces Direct; protects against server failure but not storage failure; requires Windows Server Failover Clustering and shared disk — AG is generally preferred for new deployments but FCI remains common in existing environments)
- [ ] **[Optional]** Plan data compression strategy to reduce storage and improve I/O performance (row compression for OLTP tables with frequent updates; page compression for read-heavy and archival tables with 50-80% size reduction; columnstore indexes for analytical queries on large fact tables — compression requires Enterprise edition or Standard edition on SQL Server 2016 SP1+)

## Why This Matters

SQL Server licensing is one of the largest line items in enterprise IT budgets, and incorrect core counting or edition selection can result in audit findings costing hundreds of thousands of dollars. Organizations frequently run Enterprise edition everywhere "just in case," paying 4x the Standard edition price for features they never use, or conversely run Standard edition and discover mid-project that readable secondaries, online index rebuilds, or partitioning require Enterprise. The licensing model also directly affects cloud migration economics — Azure Hybrid Benefit with Software Assurance can cut compute costs nearly in half, but only if the on-premises licenses are eligible and properly documented.

On the technical side, SQL Server's default configuration is optimized for small workloads and backward compatibility, not production performance. A freshly installed SQL Server with default MAXDOP, cost threshold, and single TempDB file will develop performance problems as soon as concurrent load increases. Always On Availability Groups require careful planning around quorum, witness configuration, listener DNS, and failover behavior — a poorly configured AG can cause split-brain scenarios or extended outages when the cluster makes unexpected decisions during network partitions.

## Common Decisions (ADR Triggers)

### ADR: SQL Server Edition Selection

**Context:** The organization must choose an edition that balances feature requirements against licensing cost for each environment.

**Options:**

| Criterion | Enterprise | Standard | Developer |
|---|---|---|---|
| Memory Limit | OS maximum | 128 GB per instance | OS maximum |
| AG Readable Secondaries | Yes | No (basic AG only) | Yes |
| Online Index Operations | Yes | No | Yes |
| Data Compression | Yes | Yes (2016 SP1+) | Yes |
| Partitioning | Yes | Yes (2016 SP1+) | Yes |
| Cost (per 2-core pack) | ~$15,000 list | ~$3,900 list | Free (non-production) |
| Use Case | Production with advanced HA/performance | Production with moderate requirements | Development and testing |

**Decision drivers:** Required HA features, memory ceiling, budget, and whether readable secondaries or online operations are needed for production SLAs.

### ADR: HA and DR Architecture

**Context:** The database must survive infrastructure failures and regional disasters while meeting defined RPO and RTO targets.

**Options:**
- **Always On AG (synchronous + asynchronous):** Synchronous within the primary datacenter for automatic failover (RPO=0, RTO=30-60s); asynchronous to a DR region (RPO=seconds-minutes, RTO=minutes with manual failover). Most common enterprise pattern.
- **Failover Cluster Instance:** Instance-level failover using shared storage. Protects against server failure but not storage failure. Simpler to manage than AG for single-database workloads.
- **Log shipping:** Simple, reliable DR with configurable RPO based on log backup frequency. Works across all editions. No automatic failover — requires manual role change and application reconnection.
- **Azure SQL Managed Instance with auto-failover groups:** Managed HA with automatic geo-replication and failover. Eliminates infrastructure management. Requires migration to Managed Instance compatibility surface area.

**Decision drivers:** RPO/RTO requirements, existing infrastructure (SAN for FCI, network bandwidth for AG), edition licensing, and cloud migration timeline.

### ADR: Cloud Migration Target

**Context:** The organization is migrating SQL Server workloads to the cloud and must select the appropriate target service.

**Options:**
- **Azure SQL Database:** Fully managed PaaS. Lowest operational overhead. Limited compatibility — no SQL Agent, cross-database queries, or CLR. Best for modernized applications.
- **Azure SQL Managed Instance:** Near-complete SQL Server compatibility in a managed service. Supports SQL Agent, linked servers, cross-database queries, and most Enterprise features. Best for lift-and-shift of complex databases.
- **SQL Server on Azure VM:** Full feature parity with on-premises. Customer manages patching, backups, and HA. Best for workloads requiring SSIS, SSRS, FCI, or features not available in Managed Instance.

**Decision drivers:** Application compatibility requirements, BI component dependencies (SSIS/SSRS/SSAS), operational maturity, and total cost of ownership including management overhead.

## See Also

- `general/database-migration.md` — Database migration strategy, schema migration tooling, replication, and cutover planning
- `general/database-ha.md` — Database high availability patterns, replication topologies, and failover strategies
- `providers/azure/database.md` — Azure database services including Azure SQL and Managed Instance
- `providers/aws/rds-aurora.md` — AWS RDS for SQL Server configuration and limitations
