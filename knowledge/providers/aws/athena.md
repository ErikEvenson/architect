# Amazon Athena

## Scope

Amazon Athena is serverless interactive SQL over data in S3 (and, through connectors, over other sources). There is no cluster to provision: you point Athena at tables in the AWS Glue Data Catalog and pay for the data each query scans. This file covers engine versions, the per-TB-scanned cost model and why partition pruning dominates it, workgroups and cost controls, partition management including partition projection, CTAS and `INSERT INTO`, federated queries, Iceberg DML support and its constraints, provisioned capacity, Athena for Apache Spark, and the service quotas that shape designs.

Athena is referenced across the library as the ad-hoc query surface for S3 data lakes but had no page of its own. For the catalog it queries see `providers/aws/glue.md`; for fine-grained access control over that catalog see `providers/aws/lake-formation.md`; for the storage layer see `providers/aws/s3.md`; for how Athena compares to Trino, Spark SQL, and warehouse engines see `general/query-engines.md`.

> Pricing, engine versions, and provisioned-capacity minimums change. Verify current published rates and limits against AWS documentation before using them in an estimate.

## Checklist

### Cost Model

- [ ] **[Critical]** Is it understood that Athena bills on **bytes scanned**, not on query time or result size, so cost is a function of data layout rather than of query complexity? A `SELECT COUNT(*)` over an unpartitioned uncompressed CSV lake is expensive; a complex multi-join over well-partitioned Parquet is cheap. Every optimization below is really the same optimization: read fewer bytes.
- [ ] **[Critical]** Is the data stored in a **columnar format** (Parquet or ORC) with compression, rather than CSV or JSON? This is the single largest cost lever available and typically reduces scanned bytes by an order of magnitude, because Athena reads only the columns the query references and skips row groups whose statistics exclude them. Converting a lake from JSON to Parquet routinely cuts the Athena bill by 80-95%.
- [ ] **[Critical]** Is the data **partitioned on the columns that queries actually filter on**, most commonly event date? Partition pruning is what turns a full-lake scan into a few directories. Unpartitioned tables are the most common cause of surprise Athena bills, because the cost of a careless query scales with the entire dataset rather than the relevant slice.
- [ ] **[Critical]** Are per-query and per-workgroup **data usage controls** configured before analysts are given access? Without a limit, one `SELECT *` against a petabyte-scale table produces a five-figure charge in minutes, and nothing in the default configuration prevents it. This is a guardrail, not an optimization, and it belongs in the initial rollout.
- [ ] **[Critical]** Is `SELECT *` discouraged in favour of explicit column lists, and is the team aware that `LIMIT` does **not** bound the scan on a full-table query? `LIMIT` restricts rows returned, not data read; it provides essentially no cost protection. Column projection and partition predicates are what reduce the bill.
- [ ] **[Recommended]** Are small files consolidated, and is the per-query minimum charge understood? Athena applies a small minimum billed scan per query, so a workload of very many tiny queries over very many tiny files pays disproportionately relative to the data involved -- and small files also slow query planning. See the small-file discussion in `general/open-table-formats.md`.
- [ ] **[Recommended]** Are query costs attributed per team or per workload through separate workgroups with cost allocation tags, so that optimization effort can be aimed at the workloads that actually cost money? Athena spend is almost always concentrated in a handful of queries and dashboards.
- [ ] **[Recommended]** Are recurring dashboard queries served from pre-aggregated gold tables rather than re-scanning detail tables on every refresh? A dashboard that refreshes every five minutes against a raw table is a standing charge; the same numbers from a small aggregate table are nearly free. See `patterns/lakehouse-medallion.md`.
- [ ] **[Recommended]** Has `EXPLAIN` or the query-statistics output been used on the expensive queries to confirm that partition pruning and predicate pushdown are actually happening? Assumed pruning that is not occurring (because the predicate is on a non-partition column, or wrapped in a function that defeats it) is invisible except in the bytes-scanned figure.
- [ ] **[Optional]** Has **provisioned capacity** been evaluated for workloads with sustained, predictable, high-volume scanning? Provisioned capacity bills for compute units over time instead of per byte scanned, which inverts the cost model and can be cheaper for heavy steady usage while also giving predictable concurrency. Confirm the current minimum capacity units and minimum commitment period before modelling it -- these have changed since launch.

### Workgroups and Governance

- [ ] **[Critical]** Are separate workgroups used per team, environment, or workload class rather than everything running in the `primary` workgroup? A workgroup is the unit of query isolation, result location, engine version pinning, cost control, metrics, and tagging. Retrofitting workgroups after adoption means changing every client configuration at once.
- [ ] **[Critical]** Is the **query result location** set per workgroup, on a bucket with a lifecycle policy that expires old results? Every Athena query writes its result set to S3, and result buckets grow indefinitely and silently. They also contain query output -- meaning they inherit the sensitivity of the underlying data while usually not inheriting its access controls.
- [ ] **[Critical]** Is workgroup configuration **enforced** (client settings overridden by the workgroup) rather than merely suggested, so users cannot redirect results to an unmanaged bucket or bypass the configured limits?
- [ ] **[Recommended]** Is the engine version **pinned** per workgroup, with a deliberate upgrade process and a test workgroup running the newer engine? Automatic engine upgrades change SQL semantics, function behaviour, and occasionally query plans. Pinning turns an unplanned breakage into a scheduled migration.
- [ ] **[Recommended]** Are the per-workgroup CloudWatch metrics (data scanned, query execution time, queued queries, failed queries) alarmed, so cost and performance regressions are detected rather than discovered on the bill?
- [ ] **[Recommended]** Are workgroup-level IAM policies restricting which principals can use which workgroup, so cost controls cannot be evaded by switching workgroups?
- [ ] **[Optional]** Is query result reuse enabled where the workload tolerates slightly stale answers? Reusing a recent identical query's result skips the scan entirely and is close to free, which is well suited to dashboards that many users load independently.

### Partition Management

- [ ] **[Critical]** Is a partition management strategy chosen deliberately -- Glue crawler, explicit `ALTER TABLE ADD PARTITION` from the pipeline, `MSCK REPAIR TABLE`, or **partition projection**? Doing nothing means new data is invisible to queries, which presents as "the table is missing yesterday's data" rather than as an error.
- [ ] **[Critical]** For tables with a large or ever-growing number of partitions, is **partition projection** used instead of catalog-registered partitions? Partition projection computes partition locations from table properties at query time rather than listing them from the Glue Data Catalog. It removes the catalog partition-listing step from query planning, eliminates the need to run crawlers or `MSCK REPAIR` as data arrives, and avoids catalog partition storage cost. For high-cardinality time-partitioned tables it is usually the correct default.
- [ ] **[Critical]** When using partition projection, are the projection types and ranges configured correctly, and is the failure mode understood? Projection supports enumerated values, integer ranges, date ranges, and injected values. An over-broad range makes Athena generate an enormous set of candidate locations and slows planning; a too-narrow range makes data silently unqueryable because the partition is never projected. Injected columns require an equality predicate in the query, so a query without one fails rather than scanning everything.
- [ ] **[Critical]** Is `MSCK REPAIR TABLE` understood as a bootstrap tool rather than an operational one? It scans the table's S3 prefix to discover partitions, which is slow on large tables, and it only *adds* partitions -- it does not remove partitions whose data is gone. Pipelines should add partitions explicitly as they write.
- [ ] **[Recommended]** Where catalog partitions are used on tables with many partitions, are **Glue partition indexes** created on the commonly filtered partition keys? Without an index, partition filtering requires the catalog to evaluate all partitions; with one, the filter is served from the index. The number of indexes per table is small and limited, so choose the keys that queries actually filter on.
- [ ] **[Recommended]** Is the partition scheme sized so partitions hold a meaningful amount of data? Over-partitioning is as damaging in Athena as anywhere else: many tiny partitions mean many tiny files, slow planning, higher catalog cost, and worse compression. See `general/open-table-formats.md`.
- [ ] **[Recommended]** Is Hive-style partitioning (`key=value` path segments) used so partition discovery and projection work naturally, rather than an ad-hoc path layout requiring explicit location mapping per partition?
- [ ] **[Optional]** For tables in an open table format, is partition management delegated to the format instead? Iceberg tracks its own partitions in table metadata, so crawlers, `MSCK REPAIR`, and projection are all unnecessary -- one of the better practical reasons to adopt Iceberg for tables with painful partition management.

### SQL, CTAS, and Table Formats

- [ ] **[Critical]** Is the **engine version** in use known, and are its SQL semantics the ones the team is writing against? Athena's SQL engine derives from the Presto/Trino lineage, and successive engine versions have changed function behaviour, type coercion, and reserved words. "It worked last month" after an engine upgrade is a real and recurring class of incident.
- [ ] **[Critical]** Is `CREATE TABLE AS SELECT` used to convert raw text data into partitioned, compressed columnar tables as a standard step, rather than querying raw CSV or JSON repeatedly? CTAS is the cheapest available path from an expensive layout to a cheap one, and the conversion pays for itself quickly on any table queried more than a few times.
- [ ] **[Critical]** Is the documented **partition limit for a single CTAS or `INSERT INTO`** accounted for in conversion jobs? Athena limits how many partitions one write statement can create, so a full historical backfill must be executed in batches (for example, a year at a time) rather than as a single statement. Discovering this mid-backfill is common; designing for it is cheap.
- [ ] **[Recommended]** Are bucketing and sort order used on large tables where queries filter on a high-cardinality non-partition column? Bucketing distributes rows across a fixed number of files by hash, letting Athena skip files for equality predicates that partitioning cannot express economically.
- [ ] **[Recommended]** For mutable tables, is **Iceberg** used rather than attempting to emulate updates with partition overwrites? Athena supports `INSERT`, `UPDATE`, `DELETE`, and `MERGE` on Iceberg tables, along with time travel and table maintenance statements. This is the supported path for row-level mutation in Athena.
- [ ] **[Critical]** If Iceberg tables are written by more than one engine, has Athena's delete-encoding behaviour been checked against the table's configured mutation mode? Athena's documented behaviour is to use merge-on-read with positional deletes, and it does not honour copy-on-write table properties -- queries do not fail, the properties are simply ignored. A cross-engine standard on `write.delete.mode` / `write.update.mode` / `write.merge.mode` therefore does not hold for Athena. See `general/open-table-formats.md`.
- [ ] **[Recommended]** Are Iceberg table maintenance operations (`OPTIMIZE`, `VACUUM`) scheduled for tables Athena mutates, or delegated to Glue table optimizers? Athena can issue them, but nothing runs them automatically, and an unmaintained merge-on-read table accumulates delete files until queries slow materially.
- [ ] **[Recommended]** Are views used to present a stable, governed interface over physical tables that may be reorganized? Athena views are catalog objects and are the natural place to hide partition-layout changes from consumers.
- [ ] **[Optional]** Is `UNLOAD` used when the goal is to produce files rather than a result set, avoiding a second pass over the query results?

### Federated Queries and Connectors

- [ ] **[Recommended]** Is federated query understood as **Lambda-based connectors**, with the cost and performance implications that follow? Each federated source is served by a Lambda function that Athena invokes; you pay for Lambda invocation and duration, for Athena bytes scanned, and for S3 spill when intermediate results exceed the Lambda response size. Throughput is bounded by Lambda concurrency, not by the source.
- [ ] **[Critical]** Has pushdown been validated for the specific connector and query shape before federation is designed into a production path? When predicates and projections push down, federation is efficient; when they do not, the connector pulls the source data across into Athena and filters there -- turning a selective query into a full extract, repeatedly, at both cost and load on the operational source.
- [ ] **[Recommended]** Is federation reserved for exploratory joins, low-volume lookups, and one-off analysis rather than for production pipelines? A recurring federated join against an operational database is an ingestion pipeline written in the least efficient available form; the durable answer is to land the data in the lake. See `patterns/data-pipeline.md`.
- [ ] **[Optional]** Is the connector's spill bucket configured with a lifecycle policy and appropriate encryption? Spill data is intermediate query data in S3 with the same sensitivity as the source.

### Security and Operations

- [ ] **[Critical]** Are query results encrypted and the result bucket access-controlled to at least the same standard as the source data? Result sets are a complete, unfiltered copy of whatever the query returned, in a bucket that is frequently overlooked in access reviews.
- [ ] **[Critical]** Where fine-grained access control is required, is Lake Formation used rather than attempting to express column and row restrictions through IAM on S3 prefixes? IAM cannot express column masking or row filtering; only the catalog-level authorization layer can. See `providers/aws/lake-formation.md`.
- [ ] **[Recommended]** Are the relevant service quotas known before designing a workload -- concurrent query limits per account and region, and the DML and DDL query timeouts? A batch process firing hundreds of concurrent Athena queries will queue and eventually throttle; a long-running conversion query can hit the timeout and lose its work.
- [ ] **[Recommended]** Is CloudTrail capturing Athena API activity, and are query histories retained beyond the console's window where audit requirements demand it?
- [ ] **[Optional]** Is **Athena for Apache Spark** considered where the work is genuinely procedural rather than SQL -- notebook-driven exploration, Python transformations, ML feature work? It is a separate, session-based, DPU-billed surface, not a variant of the SQL engine, and for scheduled production ETL a Glue or EMR job is usually the better fit. See `providers/aws/glue.md`.
- [ ] **[Optional]** Are JDBC/ODBC driver users routed through workgroups with the same controls as console users? BI tools connecting over JDBC are frequently the largest source of scanned bytes and the least visible.

## Why This Matters

Athena's cost model concentrates almost all financial risk in decisions made before any query runs. Because billing is per byte scanned and there is no cluster to size, the platform gives no natural feedback signal: a badly laid out lake and a well laid out lake feel identical to use and differ by one to two orders of magnitude on the invoice. Teams that adopt Athena "because it is serverless and cheap" and land raw JSON in S3 without partitioning routinely see bills that would have paid for a provisioned warehouse several times over. The fix -- Parquet, compression, partitioning on the filter column, aggregate tables for dashboards -- is well understood and almost never applied before the first surprising bill.

The absence of a cluster also means the absence of a natural blast-radius limit. In a provisioned system, a careless query is slow and annoys colleagues. In Athena, it silently scans everything and generates a charge proportional to the size of the lake. Data usage controls at the workgroup level are the only mechanism that bounds this, they are not on by default, and they are frequently added only after the incident that justified them. Any Athena rollout to a population of analysts should configure per-query and per-workgroup limits before granting access.

Partition management is the second recurring failure. The default mental model -- run a crawler, get partitions -- breaks down as partition counts grow: crawlers get slow and expensive, `MSCK REPAIR` gets slower still, and query planning spends increasing time listing partitions from the catalog before reading any data. Partition projection resolves this by computing partitions from table properties instead of storing them, and it is the correct default for high-cardinality time-partitioned tables. It is also easy to misconfigure in a way that fails silently: a projection range that does not cover the data makes rows unqueryable while the table looks perfectly healthy.

Engine version changes deserve more respect than they usually get. Athena's SQL comes from the Presto/Trino lineage and successive versions have changed function semantics and type handling. Workgroups can pin the engine version, which converts an uncontrolled change into a scheduled one with a test path. Teams that leave engine selection on automatic discover the differences when a scheduled report starts producing different numbers.

Finally, Athena is frequently deployed as though it were the whole analytics platform rather than one surface onto it. It is excellent for ad-hoc exploration, moderate-volume reporting, and occasional large scans. It is a poor fit for high-concurrency interactive dashboards with strict latency targets, for sustained heavy scanning where the per-byte model becomes expensive relative to provisioned compute, and for workloads needing tight control over caching and warm-up. Recognizing where that boundary sits -- and moving those workloads to provisioned capacity, a warehouse, or a dedicated engine -- is the difference between Athena being cheap and Athena being the largest line on the analytics bill. See `general/query-engines.md`.

## Common Decisions (ADR Triggers)

- **Athena vs Redshift vs a dedicated query engine** -- Athena for ad-hoc, spiky, low-to-moderate-volume SQL over S3 with no infrastructure to run vs Redshift for sustained high-concurrency BI with predictable workloads and tight latency targets vs self-managed Trino or a commercial engine for heavy federated or multi-format workloads where cluster-hour billing beats per-byte. The crossover is driven by monthly bytes scanned and by concurrency requirements, and should be computed rather than assumed.
- **On-demand per-TB vs provisioned capacity** -- per-TB scanning for variable and unpredictable workloads (no commitment, cost tracks usage, unbounded worst case) vs provisioned capacity for sustained heavy scanning and predictable concurrency (fixed cost, isolates workloads from each other, requires a minimum commitment). Verify current minimums before modelling.
- **Partition projection vs catalog partitions** -- projection for high-cardinality, regularly-shaped, time-partitioned tables (no crawler, no partition metadata, fast planning; requires correct range configuration and a predictable layout) vs catalog partitions with partition indexes for irregular layouts and tables where partitions are genuinely enumerable.
- **Crawler vs pipeline-managed partitions** -- crawlers for discovery of unfamiliar or externally-produced data vs explicit `ALTER TABLE ADD PARTITION` from the writing pipeline for data you produce. Pipeline-managed is cheaper, faster, deterministic, and does not risk a crawler re-typing a column. See `providers/aws/glue.md`.
- **Table format for mutable data** -- Iceberg for row-level `UPDATE`/`DELETE`/`MERGE`, time travel, and self-managing partitions vs Hive-style partitioned Parquet with partition-overwrite emulation for append-mostly data where the operational simplicity is worth losing mutation. Note Athena's merge-on-read-only behaviour when planning cross-engine writes.
- **Federation vs ingestion** -- federated query for exploratory access and low-volume lookups against operational sources vs landing the data in the lake for anything recurring. The decision hinges on whether pushdown holds for the query shapes involved.
- **Workgroup topology** -- one workgroup per team for cost attribution and independent limits vs one per workload class (BI, ad-hoc, ETL) for engine and limit tuning vs both dimensions where the organization is large enough to need it.
- **Where fine-grained access control lives** -- Lake Formation filters for centralized, catalog-level enforcement vs materialized masked tables in the gold layer for portability across engines and simpler pipeline behaviour. See `providers/aws/lake-formation.md`.

## Reference Architectures

### Ad-hoc analytics over an S3 data lake

S3 lake with Hive-partitioned Parquet -> Glue Data Catalog holds table definitions, with partition projection configured on the large time-series tables -> Athena workgroups per team, each with a per-query data limit, an enforced result location on a lifecycle-managed bucket, and a pinned engine version -> Lake Formation grants column- and row-level access, with analyst roles holding no direct S3 access -> CloudWatch alarms on per-workgroup bytes scanned. See `providers/aws/lake-formation.md`.

### Raw-to-optimized conversion

Raw JSON or CSV lands in `raw/` -> a scheduled CTAS (or Glue ETL job) writes partitioned, Snappy-compressed Parquet into `curated/`, batched to stay within the per-statement partition limit -> analysts query only the curated tables, and the raw prefix is restricted to the pipeline role and tiered to colder storage. This single conversion is typically the largest cost reduction available on a young Athena deployment.

### Iceberg lakehouse queried by Athena

Iceberg tables in S3 registered in the Glue Data Catalog -> Spark or Glue ETL as the writer of record -> Athena serves interactive SQL and performs occasional row-level corrections via `MERGE` -> Glue table optimizers run compaction, snapshot expiry, and orphan-file removal -> partition management is handled by Iceberg itself, so no crawlers or `MSCK REPAIR` are needed. Verify Athena's supported Iceberg spec version against what the writer produces. See `general/open-table-formats.md`.

### BI dashboards on aggregate tables

Detail tables in silver -> scheduled CTAS or Glue jobs materialize small gold aggregate tables shaped for the dashboards -> QuickSight or a third-party BI tool queries only the aggregates through a dedicated workgroup with a low per-query limit -> result reuse absorbs repeated identical dashboard loads. This keeps BI cost roughly constant regardless of how large the underlying detail data grows. See `patterns/lakehouse-medallion.md`.

## Reference Links

- [Amazon Athena User Guide](https://docs.aws.amazon.com/athena/latest/ug/what-is.html) -- service overview, supported data sources, and getting started
- [Athena Engine Versions](https://docs.aws.amazon.com/athena/latest/ug/engine-versions.html) -- available engine versions, upgrade behaviour, and per-version SQL changes
- [Amazon Athena Pricing](https://aws.amazon.com/athena/pricing/) -- per-TB-scanned rates, minimum per-query charge, provisioned capacity, and Athena for Spark rates
- [Workgroup Data Usage Controls](https://docs.aws.amazon.com/athena/latest/ug/workgroups-setting-control-limits-cloudwatch.html) -- per-query and per-workgroup scan limits, CloudWatch metrics, and alarm configuration
- [Partition Projection](https://docs.aws.amazon.com/athena/latest/ug/partition-projection.html) -- projection types, table properties, location templates, and constraints
- [Partitioning Data in Athena](https://docs.aws.amazon.com/athena/latest/ug/partitions.html) -- Hive-style partitions, `MSCK REPAIR TABLE`, and `ALTER TABLE ADD PARTITION`
- [Glue Partition Indexes with Athena](https://docs.aws.amazon.com/athena/latest/ug/glue-best-practices-partition-index.html) -- partition indexing and its effect on partition filtering
- [Creating a Table from Query Results (CTAS)](https://docs.aws.amazon.com/athena/latest/ug/ctas.html) -- formats, compression, bucketing, and partition-count considerations
- [Querying Apache Iceberg Tables](https://docs.aws.amazon.com/athena/latest/ug/querying-iceberg.html) -- supported DML, time travel, `OPTIMIZE`, `VACUUM`, and documented limitations
- [Connecting to Data Sources](https://docs.aws.amazon.com/athena/latest/ug/connect-to-a-data-source.html) -- federated query, Lambda-based connectors, and the data source registry
- [Performance Tuning: Data Optimization Techniques](https://docs.aws.amazon.com/athena/latest/ug/performance-tuning-data-optimization-techniques.html) -- columnar formats, compression, partitioning, and file sizing guidance
- [Athena Provisioned Capacity](https://docs.aws.amazon.com/athena/latest/ug/capacity-management.html) -- capacity reservations, minimums, and workgroup assignment
- [Athena for Apache Spark](https://docs.aws.amazon.com/athena/latest/ug/notebooks-spark.html) -- notebook sessions, DPU billing, and when to use it over SQL
- [Athena Service Quotas](https://docs.aws.amazon.com/athena/latest/ug/service-limits.html) -- concurrent query limits, timeouts, and adjustable quotas

## See Also

- `providers/aws/glue.md` -- the Glue Data Catalog Athena queries, crawlers, ETL jobs, and Iceberg table optimizers
- `providers/aws/lake-formation.md` -- column-, row-, and cell-level access control enforced on Athena queries
- `providers/aws/s3.md` -- the storage layer, storage classes, lifecycle policies for result buckets, and S3 Tables
- `general/query-engines.md` -- Athena's per-byte model compared with Trino cluster-hours, BigQuery slots, and warehouse credits
- `general/open-table-formats.md` -- Iceberg mechanics, the merge-on-read constraint Athena imposes, and table maintenance
- `patterns/lakehouse-medallion.md` -- serving aggregate gold tables to BI instead of re-scanning detail tables
- `patterns/data-pipeline.md` -- ingestion and conversion pipelines that produce Athena-friendly layouts, with sized cost benchmarks
- `general/data-analytics.md` -- warehouse vs lake vs lakehouse selection and the analytics cost-management checklist
- `general/cost.md` -- broader cloud cost management and FinOps practice
- `providers/aws/iam.md` -- IAM policies for workgroup access, result buckets, and catalog permissions
