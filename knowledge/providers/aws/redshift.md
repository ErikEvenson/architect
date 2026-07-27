# Amazon Redshift

## Scope

Amazon Redshift architecture and design decisions as a cloud data warehouse. Covers the leader/compute-node MPP architecture and slices, node family selection (RG Graviton nodes, RA3, DC2, and the retirement of DS2), Redshift Serverless and RPU-based capacity, Redshift Managed Storage (RMS) as the S3-backed storage tier that decouples storage from compute, physical design (distribution styles, sort keys, column compression encodings, Automatic Table Optimization), maintenance (VACUUM, ANALYZE, and their automatic equivalents), workload management (automatic and manual WLM, query priority, short query acceleration, query monitoring rules) and Concurrency Scaling, data lake query paths (Redshift Spectrum on RA3 vs the integrated data lake query engine on RG), zero-ETL integrations, data sharing, streaming ingestion, materialized views and automatic query rewrite, the `SUPER` type for semi-structured data, the cost model across provisioned and serverless, and Redshift as a migration target from legacy MPP warehouses.

For the warehouse-vs-lake-vs-lakehouse framing and cross-vendor selection, see `general/data-analytics.md`. For migration off Teradata, Netezza, Greenplum, Exadata, or Hadoop onto Redshift, see `patterns/data-warehouse-migration.md`. For S3 as the data lake substrate, see `providers/aws/s3.md`.

## Checklist

### Deployment Model and Node Selection

- [ ] **[Critical]** Is the deployment model chosen deliberately -- provisioned cluster (fixed node count, pause/resume, reserved-node discounts) vs Redshift Serverless (RPU-based auto-scaling, no idle infrastructure)? Serverless suits intermittent, spiky, or unpredictable workloads and dev/test environments; provisioned with reserved nodes is usually cheaper for a steady 24x7 warehouse where the baseline is well understood.
- [ ] **[Critical]** Is the node family chosen on the storage-versus-compute coupling question rather than on raw specs? RG and RA3 nodes use Redshift Managed Storage, so compute is sized for throughput and storage is billed separately per GB. DC2 nodes bundle local NVMe SSD, so growing the dataset forces you to add compute you do not need. AWS recommends DC2 only for datasets under roughly 1 TB compressed, and RG or RA3 otherwise. Dense storage (DS2) node types are no longer available.
- [ ] **[Critical]** Is the RG (Graviton) family evaluated for new clusters? RG nodes are Graviton-based and include an integrated data lake query engine that runs on the cluster's own compute, whereas RA3 clusters use Redshift Spectrum for data lake queries. That difference changes the data lake cost model materially -- Spectrum bills per TB scanned, cluster-resident execution does not.
- [ ] **[Critical]** Is the node count sized against the per-node managed-storage hard limit and the node range, not just against today's data volume? `rg.large` and `ra3.large` cap at 8 TB of managed storage per node (multi-node) with a 2-16 node range; `rg.xlarge`/`ra3.xlplus` cap at 32 TB per node; `rg.4xlarge`, `rg.12xlarge`, `ra3.4xlarge` and `ra3.16xlarge` cap at 128 TB per node. These are hard limits, and the maximum node count you can *create* is lower than the maximum you can reach by elastic resize (for example `ra3.4xlarge` creates up to 32 nodes but elastic-resizes to 64).
- [ ] **[Critical]** Is the slice count known and used when sizing parallel loads? Default slices per node vary by node type (2 for `*.large`/`xlplus`, 4 for `ra3.4xlarge`, 8 for `rg.4xlarge`, 16 for `ra3.16xlarge`/`rg.12xlarge`). Parallel load and CDC thread counts should be a multiple of total cluster slices -- non-multiples produce uneven distribution across slices and extra redistribution overhead.
- [ ] **[Recommended]** For Serverless, is base capacity set consciously rather than left at the default? Base capacity is expressed in RPUs where 1 RPU provides 16 GB of memory, and the default is 128 RPUs. A 128-RPU default on a small workload is a common source of unexpected spend; usage limits (RPU-hours per day) should be configured alongside it.
- [ ] **[Recommended]** Are single-node clusters restricted to development? AWS explicitly does not recommend single-node clusters for production, and resizing a single-node cluster to multi-node requires classic resize (a full data copy with downtime), not elastic resize.
- [ ] **[Optional]** Is cluster pause/resume used for non-production provisioned clusters? Pausing suspends on-demand compute billing and leaves only backup storage charges -- the cheapest way to keep a dev warehouse without deleting it.

### Physical Design: Distribution, Sort, and Compression

- [ ] **[Critical]** Is distribution style chosen per table rather than left uniform? `DISTSTYLE KEY` co-locates rows with matching key values on the same slice and is the only way to get a collocated join; `ALL` replicates the whole table to every node; `EVEN` round-robins; `AUTO` lets Redshift decide and can be promoted to `KEY` once the workload is observed. A fact table has exactly one distribution key, so only one dimension can be collocated with it -- pick the one that is joined most often and largest after filtering.
- [ ] **[Critical]** Is `AUTO` (Automatic Table Optimization) the default for new tables unless there is a specific reason to pin keys? ATO observes query patterns and applies sort and distribution keys automatically, typically within hours of cluster creation once a minimum number of queries have run. Hand-tuned keys that were correct for the original Teradata or Netezza physical design are frequently wrong on Redshift, and ATO is the cheaper path to a good-enough layout.
- [ ] **[Critical]** Is `DISTSTYLE ALL` applied only to genuinely small dimension tables? ALL multiplies storage by the node count and increases load time and maintenance cost on every write. It also disables concurrency-scaling writes on that table. A wide table with many columns and few rows under ALL wastes a striking amount of space because Redshift stores columnar data in 1 MB blocks -- minimum one block per column per slice.
- [ ] **[Critical]** Is a sort key defined (or `SORTKEY AUTO` used) on every large table with range-restricted predicates? Redshift stores min/max metadata per 1 MB block; a sorted table lets the scan skip blocks. AWS's own example is that five years of date-sorted data queried for one month can eliminate up to 98 percent of blocks. An unsorted large fact table is the single most common Redshift performance cliff.
- [ ] **[Recommended]** Is COMPOUND sort used rather than INTERLEAVED unless the access pattern genuinely has no dominant prefix? COMPOUND is the default and is recommended for tables updated regularly with INSERT/UPDATE/DELETE. INTERLEAVED is capped at eight columns, requires `VACUUM REINDEX` which takes significantly longer than `VACUUM FULL`, and interleaved-sorted tables are excluded from concurrency scaling entirely.
- [ ] **[Recommended]** Is column compression left to Redshift (via `COPY` auto-compression or `ANALYZE COMPRESSION`) rather than hand-specified? Note that Redshift does not apply compression to sort and distribution key columns by default -- a deliberate trade to keep zone-map scanning cheap.
- [ ] **[Recommended]** Is `SVV_TABLE_INFO` monitored as the table-health dashboard? It exposes skew, unsorted percentage, and sort keys per table, and is the fastest way to find the handful of tables actually causing the slowdown.
- [ ] **[Optional]** Is the absence of table partitioning understood and designed around? Redshift has no partitioned-table construct. Migration tools emulate source partitioning by creating one table per partition behind a `UNION ALL` view -- which works but multiplies the table count against the per-cluster table quota. Sort keys plus zone maps are the native answer, not partitions.

### Maintenance and Statistics

- [ ] **[Critical]** Are VACUUM and ANALYZE either scheduled or verified to be running automatically? Redshift runs automatic vacuum and automatic analyze, but heavy delete/update workloads still accumulate unsorted regions and ghost rows that show up as "excessive ghost rows" or "very selective filter" alerts in `STL_ALERT_EVENT_LOG`. Missing or stale statistics produce a warning in `EXPLAIN` output and a missing-statistics alert event.
- [ ] **[Critical]** Is query-history retention addressed before it is needed? The `STL_`/`STV_`/`SVL_` system tables retain only a few days of history. Any capacity planning, chargeback, or regression analysis that needs a longer window requires persisting query history to a permanent table or to S3 on a schedule.
- [ ] **[Recommended]** Are the standard diagnostic alerts reviewed rather than only wall-clock query times? `STL_ALERT_EVENT_LOG` surfaces nested loops (usually an accidental cross join), large broadcast or large distribution (a distribution-style problem), and serial execution. `SVL_QUERY_SUMMARY` with `is_diskbased = true` identifies queries that spilled to disk because their WLM slot did not have enough memory.
- [ ] **[Optional]** Is `wlm_query_slot_count` used tactically for known memory-hungry batch jobs? Granting one query several slots gives it the memory of all those slots and is the documented fix for a disk-based query, at the cost of concurrency while it runs.

### Workload Management and Concurrency

- [ ] **[Critical]** Is automatic WLM used rather than hand-tuned manual WLM? Automatic WLM manages concurrency and memory allocation dynamically -- concurrency drops when large hash joins are running and rises for light queries. Clusters on the default parameter group already have it. Manual WLM's fixed slot-and-memory partitioning is the classic source of both disk-based queries and idle capacity, and should be reserved for cases with a hard isolation requirement.
- [ ] **[Critical]** Are WLM queues defined per workload class with explicit priority, and is routing driven by user groups, user roles, or query groups? Automatic WLM allows up to eight user queues (service classes 100-107). Without deliberate routing, an analyst's ad-hoc scan competes on equal terms with the nightly ELT load.
- [ ] **[Critical]** Is Concurrency Scaling enabled on the queues that carry bursty read traffic, and is its billing understood? Free credits accrue at up to one hour per day and accumulate up to 30 hours per active cluster; beyond that it bills per-second at the on-demand rate with a one-minute minimum per burst. For a cluster that bursts predictably every morning this is nearly free; for one that bursts continuously it is a second cluster's worth of spend.
- [ ] **[Critical]** Are the Concurrency Scaling exclusions checked against the actual workload before relying on it? It does not handle queries on interleaved sort keys, temporary tables, system or catalog tables, Python or Lambda UDFs, writes to `DISTSTYLE ALL` targets, or writes to tables with identity columns. Write-path concurrency scaling covers `COPY`, `INSERT`, `UPDATE`, `DELETE`, `CREATE TABLE AS`, `VACUUM`, and manual materialized-view refresh -- but not most DDL, and it is available only on RG and RA3 nodes.
- [ ] **[Recommended]** Are query monitoring rules (QMR) configured to cap runaway queries -- abort or log on excessive execution time, nested loop row counts, or scan volume? A single unbounded ad-hoc query is the usual cause of a stalled morning dashboard refresh.
- [ ] **[Recommended]** Is Short Query Acceleration left on? SQA is evaluated separately from automatic WLM and lets short queries complete while long resource-intensive ones are active.
- [ ] **[Optional]** Is `max_concurrency_scaling_clusters` raised above its default of one where burst concurrency is genuinely high? Each additional cluster multiplies both the burst capacity and the potential spend.

### Data Lake, Ingestion, and Integration

- [ ] **[Critical]** Is the data lake query path costed correctly for the chosen node family? On RA3, Spectrum bills per TB scanned (published at $5/TB, rounded up to the next MB with a 10 MB minimum per query) on top of cluster cost -- so unpartitioned, uncompressed, row-oriented external data is expensive to query repeatedly. On RG, the integrated data lake query engine runs on cluster compute instead.
- [ ] **[Critical]** Is bulk load done with `COPY` from S3 (or `UNLOAD` for extract) rather than row-by-row `INSERT` over JDBC? `COPY` parallelizes across slices; single-row inserts serialize through the leader node and are orders of magnitude slower. Split input files so the count is a multiple of the cluster's slice count.
- [ ] **[Critical]** Are zero-ETL integrations evaluated before building a CDC pipeline for AWS-resident operational sources? Documented sources now include Aurora MySQL and PostgreSQL, RDS for MySQL, PostgreSQL and Oracle, Oracle Database@AWS, DynamoDB, self-managed MySQL/PostgreSQL/SQL Server/Oracle, and application sources including Salesforce, SAP, ServiceNow and Zendesk. Zero-ETL targets require RA3 or Serverless and turn on `enable_case_sensitive_identifier`, which changes identifier semantics for everything else in that warehouse -- verify existing SQL against it.
- [ ] **[Recommended]** Is data sharing used instead of copying data between warehouses for producer/consumer separation, cross-account sharing, or isolating BI read traffic from ELT? Datashares work between provisioned clusters and Serverless workgroups and avoid a second physical copy.
- [ ] **[Recommended]** Is streaming ingestion from Kinesis Data Streams or Amazon MSK used where sub-minute freshness is required? Redshift streaming ingestion lands data into a materialized view, which is a different design shape than a `COPY` batch and needs its own refresh and error-handling plan.
- [ ] **[Recommended]** Are materialized views used for the predictable, repeated dashboard queries, with automatic refresh and automatic query rewrite considered? Automatic rewrite lets existing queries benefit without being edited, but only if the MV is up to date -- so an unrefreshed MV silently stops accelerating anything. AutoMV creates and maintains MVs from observed workload without a DDL change.
- [ ] **[Optional]** Is the `SUPER` type used for semi-structured data rather than pre-flattening JSON in the pipeline? `SUPER` with PartiQL avoids a schema-on-write commitment for nested payloads, at the cost of less predictable query plans.
- [ ] **[Optional]** Is Multi-AZ evaluated for RA3 provisioned clusters where the warehouse is genuinely on the critical path? Multi-AZ is not the default and materially changes the availability story and the cost.

### Security and Cost Control

- [ ] **[Critical]** Is the cluster in a VPC with enhanced VPC routing decided consciously? Enhanced VPC routing forces all `COPY`/`UNLOAD` traffic through the VPC, which is usually what a regulated environment wants -- but it silently breaks `COPY` unless an S3 gateway endpoint or equivalent network path exists. This is a common cause of migration loads failing only after the network team hardens the account.
- [ ] **[Critical]** Are budget and usage guardrails in place -- Serverless RPU-hour usage limits, Spectrum per-TB usage limits, and concurrency-scaling usage limits -- rather than relying on after-the-fact cost review? All three are separately metered and all three can spike without any change to the cluster configuration.
- [ ] **[Recommended]** Are reserved nodes purchased only after the production configuration is validated by real workload, not during migration? AWS's own guidance is to run experiments and proof-of-concepts first. Reserved nodes are committed to a node type, so a reservation bought before the physical design settles frequently ends up on the wrong family.
- [ ] **[Recommended]** Is the Python UDF end-of-support deadline accounted for in any inherited codebase? AWS has announced that Redshift will no longer support Python UDFs after 30 June 2026, enforced in phases. Legacy warehouses that wrapped business logic in Python UDFs -- a very common landing pattern for converted Teradata or Oracle functions -- need a migration plan to SQL UDFs, Lambda UDFs, or stored procedures.
- [ ] **[Optional]** Is column-level and row-level access control implemented in the warehouse rather than through per-consumer views? Redshift supports column-level `GRANT` and row-level security policies; a proliferation of filtered views is harder to audit and drifts from the policy intent.

## Why This Matters

Redshift's cost and performance both hinge on physical design in a way that serverless-first warehouses do not. The default outcome for a migrated schema -- every table `EVEN` distributed with no sort key -- produces a warehouse that scans everything, broadcasts large tables across the interconnect on every join, and spills to disk. The same data and the same queries on a correctly distributed and sorted schema can run an order of magnitude faster on identical hardware. This is why `SORTKEY AUTO` / `DISTSTYLE AUTO` plus Automatic Table Optimization is the right default: it converts a design problem that most teams get wrong into an observation problem that Redshift solves within hours.

The storage-compute coupling decision is the one that ages badly. A DC2 cluster sized for today's 800 GB has no way to absorb data growth except adding compute nodes nobody needed, and there is no in-place path to RA3 without a resize. RG and RA3 with managed storage decouple those axes, and the per-node managed-storage limits are hard ceilings -- a cluster designed at 30 TB on `ra3.xlplus` will hit the 32 TB-per-node wall and require a node-type change, not just more nodes.

Concurrency Scaling and Spectrum are the two features that most often turn a predictable bill into an unpredictable one, because both are metered independently of the cluster and both are triggered by user behavior rather than by an administrator's action. A dashboard rebuilt to refresh every five minutes against Spectrum external tables can add five figures a month without any configuration change. Usage limits on both are the cheapest insurance available.

Redshift's PostgreSQL ancestry sets a trap for teams arriving from Postgres: the wire protocol and much of the dialect are familiar, but the storage engine, the absence of enforced primary and unique keys (they are informational only and the optimizer trusts them), the absence of table partitioning, the 1 MB block granularity, and the leader-node/compute-node split mean that Postgres intuitions about indexes, constraints, and row-at-a-time work are actively misleading. Every migration onto Redshift eventually discovers that duplicate rows exist because nothing enforced the primary key.

Finally, the operational telemetry is short-lived by default. The `STL_`/`SVL_` system tables keep only days of history, so the question "was this slow last quarter too?" is unanswerable unless somebody set up persistence in advance. Teams routinely discover this during their first performance escalation.

## Common Decisions (ADR Triggers)

- **Provisioned vs Serverless** -- provisioned with reserved nodes for a steady, well-characterized 24x7 warehouse (lowest unit cost, pause/resume for non-prod) vs Serverless for spiky, intermittent, or unknown workloads and for dev/test (no idle cost, per-second RPU billing, but no reserved-node discount)
- **Node family: RG vs RA3 vs DC2** -- RG (Graviton, managed storage, integrated data lake query engine) for new clusters vs RA3 (managed storage, Spectrum for data lake) for existing estates and feature parity vs DC2 only for sub-1-TB compressed datasets that will not grow; DS2 is no longer available
- **Managed storage sizing** -- node count driven by compute throughput with storage billed separately (RG/RA3) vs node count driven by storage capacity (DC2); the per-node managed-storage hard limit constrains the former and should be checked against three-year data growth
- **Automatic Table Optimization vs hand-tuned keys** -- `AUTO` sort and distribution keys for most tables (self-tuning, no ongoing DBA effort, correct within hours) vs explicitly pinned `DISTKEY`/`SORTKEY` for a small set of tables where the join and predicate pattern is known and stable and the cost of getting it wrong is high
- **Distribution style per table** -- `KEY` for large fact tables and their most-joined dimension (collocated joins) vs `ALL` for small, stable dimensions (storage multiplied by node count, blocks concurrency-scaling writes) vs `EVEN` as the neutral default for tables with no dominant join key
- **Compound vs interleaved sort key** -- compound for nearly everything, especially write-heavy tables vs interleaved only when predicates genuinely hit arbitrary subsets of up to eight columns, accepting `VACUUM REINDEX` cost and exclusion from concurrency scaling
- **Automatic vs manual WLM** -- automatic WLM as the default (dynamic concurrency and memory, fewer disk-based queries) vs manual WLM only where a hard, statically partitioned resource guarantee is contractually required
- **Concurrency Scaling posture** -- enabled with usage limits for bursty read traffic (near-free within accrued credits) vs disabled where the workload bursts continuously and a larger main cluster is cheaper and more predictable
- **Data lake access path** -- Spectrum external tables on RA3 (per-TB-scanned billing, keeps cold data out of the warehouse) vs RG's integrated data lake query engine (cluster compute, no per-TB charge) vs loading the data into managed storage (fastest, highest storage cost, needs a pipeline)
- **Zero-ETL vs a managed CDC pipeline** -- zero-ETL for supported AWS-resident sources (no pipeline to operate, but forces `enable_case_sensitive_identifier` and gives read-only replicated tables) vs DMS or a streaming pipeline where transformation, filtering, or unsupported sources are involved
- **Data sharing vs copying** -- datashares for producer/consumer isolation and cross-account access without a second copy vs physical copies where the consumer needs to write, reshape, or retain independently
- **Materialized views vs summary tables in the ELT** -- MVs with auto-refresh and automatic query rewrite (transparent to consumers, Redshift manages incrementality) vs explicit aggregate tables built by the pipeline (full control over refresh timing and dependencies, visible in the DAG)
- **Multi-AZ vs single-AZ with snapshots** -- Multi-AZ RA3 for warehouses on the critical path (higher cost, non-default) vs single-AZ with automated snapshots and cross-region copy for the far more common case where hours of RTO are acceptable

## Reference Architectures

### Migration landing zone from a legacy MPP warehouse

- Source schema converted with AWS SCT; all tables created with `DISTSTYLE AUTO` and `SORTKEY AUTO` so Automatic Table Optimization observes the real workload rather than inheriting the source's physical design
- Bulk history extracted to S3 as compressed, split files (file count a multiple of cluster slices) and loaded with `COPY`; incremental deltas via AWS DMS, which stages CSV to S3 and issues `COPY` behind the scenes
- Source partitioning emulated where necessary as per-partition tables behind a `UNION ALL` view, with the table count checked against the per-cluster table quota
- Dual-run period: legacy and Redshift both loaded, with row-count and checksum reconciliation per table and business-metric parity checks on the top reports
- WLM queues separated for the migration load, the dual-run reconciliation queries, and normal BI traffic so reconciliation does not distort the performance comparison
- After cutover, `SVV_TABLE_INFO` reviewed weekly for skew and unsorted percentage; reserved nodes purchased only once the steady-state configuration has held for a full business cycle

### Warehouse plus data lake with tiered retention

- Hot 13 months of fact data in Redshift Managed Storage, sorted on the event-date column so range-restricted dashboard queries skip most blocks
- Colder history in S3 as partitioned, compressed columnar files, queried through Spectrum external tables (RA3) or the integrated data lake query engine (RG)
- A `UNION ALL` view presents hot and cold as one logical table to BI, so report definitions do not change when data ages out
- Spectrum usage limit configured to cap per-TB spend; partition pruning verified with `EXPLAIN` before the view is published
- Monthly job moves the aged partition from managed storage to S3 and re-registers it as an external partition

### Producer/consumer separation with data sharing

- One producer warehouse owns ELT and writes; consumers are separate Serverless workgroups per business unit, each reading through a datashare
- ELT contention is eliminated by construction -- an analyst's runaway query cannot slow the nightly load because it runs on different compute
- Cost is attributed naturally: each consumer workgroup has its own RPU-hour bill and its own usage limit
- The producer runs on provisioned RA3/RG with reserved nodes (steady baseline); consumers run Serverless (bursty, business-hours only)

## Reference Links

- [Amazon Redshift Management Guide](https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html) -- clusters, Serverless, networking, snapshots, and administration
- [Amazon Redshift Database Developer Guide](https://docs.aws.amazon.com/redshift/latest/dg/welcome.html) -- SQL reference, table design, query tuning, and system tables
- [Amazon Redshift provisioned clusters](https://docs.aws.amazon.com/redshift/latest/mgmt/working-with-clusters.html) -- node type specifications, slices per node, managed storage limits, and node ranges
- [Amazon Redshift Serverless feature overview](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-considerations.html) -- base RPU capacity, recovery points, and feature parity with provisioned
- [Billing for Amazon Redshift Serverless](https://docs.aws.amazon.com/redshift/latest/mgmt/serverless-billing.html) -- RPU-hour metering and usage limits
- [Automatic table optimization](https://docs.aws.amazon.com/redshift/latest/dg/t_Creating_tables.html) -- how Redshift chooses and applies sort and distribution keys automatically
- [Choose the best distribution style](https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-best-dist-key.html) -- collocated joins, ALL distribution trade-offs, and cardinality guidance
- [Sort keys](https://docs.aws.amazon.com/redshift/latest/dg/t_Sorting_data.html) -- compound vs interleaved, 1 MB block min/max metadata, and `VACUUM REINDEX` cost
- [Column compression encodings](https://docs.aws.amazon.com/redshift/latest/dg/c_Compression_encodings.html) -- available encodings and why key columns are left uncompressed by default
- [VACUUM](https://docs.aws.amazon.com/redshift/latest/dg/r_VACUUM_command.html) -- SORT ONLY, DELETE ONLY, FULL, and REINDEX variants
- [Query performance improvement](https://docs.aws.amazon.com/redshift/latest/dg/query-performance-improvement-opportunities.html) -- diagnosing missing statistics, nested loops, ghost rows, skew, and disk-based queries
- [SVV_TABLE_INFO](https://docs.aws.amazon.com/redshift/latest/dg/r_SVV_TABLE_INFO.html) -- per-table skew, unsorted percentage, and key configuration
- [Implementing automatic WLM](https://docs.aws.amazon.com/redshift/latest/dg/automatic-wlm.html) -- queues, service classes 100-107, priority, and routing
- [WLM query monitoring rules](https://docs.aws.amazon.com/redshift/latest/dg/cm-c-wlm-query-monitoring-rules.html) -- metric-based abort/log/hop actions
- [Short query acceleration](https://docs.aws.amazon.com/redshift/latest/dg/wlm-short-query-acceleration.html) -- how SQA interacts with automatic WLM
- [Concurrency scaling](https://docs.aws.amazon.com/redshift/latest/dg/concurrency-scaling.html) -- read and write support, eligibility rules, exclusions, and monitoring views
- [Getting started with Amazon Redshift Spectrum](https://docs.aws.amazon.com/redshift/latest/dg/c-getting-started-using-spectrum.html) -- external schemas and querying S3 from Redshift
- [Zero-ETL integrations](https://docs.aws.amazon.com/redshift/latest/mgmt/zero-etl-using.html) -- supported sources, destination databases, history mode, and monitoring
- [Sharing data across clusters](https://docs.aws.amazon.com/redshift/latest/dg/datashare-overview.html) -- producer/consumer datashares, cross-account and cross-region
- [Materialized views](https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-overview.html) -- refresh modes, automatic query rewrite, AutoMV, and MVs on MVs
- [Streaming ingestion to a materialized view](https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-streaming-ingestion.html) -- Kinesis Data Streams and Amazon MSK sources
- [Semi-structured data with SUPER](https://docs.aws.amazon.com/redshift/latest/dg/super-overview.html) -- the `SUPER` type and PartiQL querying
- [Amazon Redshift best practices for loading data](https://docs.aws.amazon.com/redshift/latest/dg/c_loading-data-best-practices.html) -- `COPY` parallelism, file splitting, and slice alignment
- [Reliability in Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/mgmt/managing-cluster-recovery.html) -- Multi-AZ deployments and cluster recovery
- [Quotas and limits in Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/mgmt/amazon-redshift-limits.html) -- per-cluster table quotas, node quotas, and other service limits
- [Amazon Redshift pricing](https://aws.amazon.com/redshift/pricing/) -- on-demand and reserved node rates, Serverless RPU-hour, managed storage, Spectrum, and concurrency-scaling credits
- [Using Amazon Redshift as a DMS target](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Redshift.html) -- S3 staging plus `COPY`, CDC settings, LOB limits, and parallel-apply tuning
- [AWS SCT source databases](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Source.html) -- warehouse sources convertible to Redshift, including Teradata, Netezza, Greenplum, Vertica, and Oracle DW

---

## See Also

- `patterns/data-warehouse-migration.md` -- migrating from Teradata, Netezza, Greenplum, Exadata, or Hadoop onto Redshift or a lakehouse, including dual-run reconciliation
- `providers/teradata/data-warehouse.md` -- the most common migration source, and what its physical design assumptions do not translate to
- `general/data-analytics.md` -- warehouse vs lake vs lakehouse selection and the cross-vendor cloud data warehouse comparison
- `providers/snowflake/data-platform.md` -- the main non-AWS-native alternative for the same workloads
- `providers/databricks/data-platform.md` -- lakehouse alternative; Lakehouse Federation can query Redshift without copying
- `providers/gcp/bigquery.md` -- serverless warehouse comparison point, including the per-TB-scanned pricing contrast
- `providers/aws/s3.md` -- S3 as the data lake tier behind Spectrum and as the staging area for `COPY`
- `providers/aws/migration-services.md` -- DMS and SCT positioning within the wider AWS migration toolset
- `providers/aws/rds-aurora.md` -- the operational databases that feed Redshift via zero-ETL
- `patterns/data-pipeline.md` -- pipeline architecture and sized cost benchmarks that include Redshift components
- `general/cost.md` -- FinOps practices applicable to reserved nodes, RPU limits, and per-TB scan controls
- `providers/aws/vpc.md` -- VPC design including the S3 gateway endpoint that enhanced VPC routing requires
