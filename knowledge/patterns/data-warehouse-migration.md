# Data Warehouse Migration

## Scope

Migrating a legacy enterprise data warehouse -- Teradata, Netezza, Greenplum, Oracle/Exadata, or a Hadoop/Hive estate -- onto a cloud warehouse or lakehouse. Covers assessment and workload profiling, what actually drives effort (procedural code, proprietary SQL dialects, load utilities and scripting, ETL-tool coupling), schema conversion versus deliberate redesign, ELT rewrite, **dual-run and reconciliation** as the mechanism that makes cutover trustable, incremental versus big-bang cutover, repointing the BI and semantic layer, and decommissioning timed against licence and support renewal.

This pattern is the substance of most enterprise cloud data engagements. It is distinct from `general/database-migration.md` (OLTP database migration, where the schema usually moves unchanged) and from `general/data-migration-tools.md` (bulk transport mechanics). The defining characteristic of a warehouse migration is that the *physical design assumptions do not transfer*: the source's distribution keys, partitioning, indexes, statistics, and workload-management configuration encode decades of tuning for an architecture the target does not have.

## Overview

A warehouse migration has five workstreams that proceed at different speeds and are frequently mis-sequenced:

1. **Schema and data** -- tables, types, and history. Mechanical, tool-assisted, and the part everyone estimates.
2. **Procedural and transformation code** -- stored procedures, macros, UDFs, load scripts, ETL jobs. Manual, and typically 60-80 percent of the real effort.
3. **Consumption** -- reports, dashboards, semantic layers, extracts, and the long tail of spreadsheets with an ODBC connection. Discovered late and owned by nobody.
4. **Reconciliation** -- proving the target produces the same answers as the source. The workstream that determines whether the business will accept cutover.
5. **Decommissioning** -- retiring the source and recovering the licence. The workstream that funds the programme and is the first thing dropped when the schedule slips.

The programme is finished when workstream 5 completes, not when workstream 1 does. Migrations that stall almost always stall with the target in production, the source still running, and two platforms being paid for.

## Checklist

### Assessment and Workload Profiling

- [ ] **[Critical]** Has the workload been profiled from the source's own query log rather than from what people say they run? Every serious MPP warehouse logs queries -- Teradata's DBQL tables (`DBC.DBQLogTbl`, `DBC.QryLogObjectsV`), Netezza's history database, Greenplum and Oracle via their own instrumentation, Hadoop via YARN and Ranger audit. Profile at least 30 days including a month-end close. The output you need is: which tables are actually read, by which consumers, at what frequency, and what the top-N queries by frequency and by resource consumption look like.
- [ ] **[Critical]** Is the object inventory reconciled against the query log to identify what is genuinely dead? Mature warehouses carry a large fraction of tables and jobs that produce output nobody consumes. Migrating them faithfully is the most expensive possible way to discover they were unused. Anything unread over a full business cycle is a candidate for archive-and-drop rather than migration.
- [ ] **[Critical]** Has the procedural code been counted and classified, not just noted? Count stored procedures, macros, UDFs, triggers, load scripts, and orchestration definitions separately, and classify each as (a) mechanically convertible, (b) convertible with review, or (c) requiring rewrite. This count is the single best predictor of programme duration, and it is the number most often not gathered before a date is committed.
- [ ] **[Critical]** Is the ETL tooling in scope, and does it push transformation down into the source database? Informatica, DataStage, Ab Initio, and SSIS jobs configured for pushdown optimization generate source-dialect SQL at runtime. Those jobs do not "just repoint" -- the generated SQL is dialect-specific and the pushdown behaviour has to be re-established or the transformation moved out of the tool entirely.
- [ ] **[Critical]** Is the consumption layer inventoried, including the parts IT does not own? The report catalogue in the BI tool is the easy half. The other half is: direct ODBC/JDBC connections from desktop tools, scheduled extracts to file shares, application code with embedded SQL, and data feeds to downstream systems. Every one of these is a cutover dependency, and the ones nobody knew about are what cause the rollback.
- [ ] **[Recommended]** Is data volume measured as compressed source footprint, uncompressed extract size, and target storage separately? These three numbers differ by large factors. Exadata Hybrid Columnar Compression and Teradata multi-value compression can make the extract several times the on-platform footprint, which changes both the transfer plan and the staging cost.
- [ ] **[Recommended]** Are the source's SLAs and batch window documented as they actually are, not as the runbook claims? The target has to meet the real batch window, and the real one is usually tighter than the documented one because it has been quietly eroded.
- [ ] **[Optional]** Is a vendor assessment tool used to accelerate the inventory -- AWS SCT's assessment report, the BigQuery migration assessment, or an equivalent? These produce a useful first-pass conversion-complexity breakdown by object type. Treat the output as a scoping input, not as an effort estimate: the "manual conversion required" bucket is where the schedule lives, and its per-object cost varies by an order of magnitude.

### What Actually Drives Effort

- [ ] **[Critical]** Are stored procedures and macros scoped as rewrite rather than conversion? Procedural dialects (Teradata SPL, Oracle PL/SQL, Netezza NZPLSQL, Greenplum PL/pgSQL, Hive/Spark procedural wrappers) differ in error handling, transaction semantics, cursor behaviour, and dynamic SQL. Conversion tools produce syntactically valid output that needs behavioural review anyway. Assume review-and-test cost per procedure regardless of tool coverage.
- [ ] **[Critical]** Is the volume of load-utility scripting counted? Teradata estates in particular carry large volumes of BTEQ, FastLoad, MultiLoad, TPump, FastExport, and TPT scripts that combine data movement with conditional logic, error handling, and control flow. These are programs, not configuration. They map onto a completely different target model (object-storage staging plus a bulk-load command plus an orchestrator), so they are rewritten, not translated.
- [ ] **[Critical]** Are dialect-specific SQL constructs enumerated across the whole codebase, including inside reports? Teradata's `QUALIFY`, `FORMAT` phrases in DDL and casts, `SAMPLE`, `SET`-table semantics and volatile tables; Oracle's `CONNECT BY`, `DECODE`, `ROWNUM`, and analytic extensions; Netezza's `ORGANIZE ON` and NZPLSQL; Greenplum's `DISTRIBUTED BY` and append-optimized DDL; HiveQL's lateral views and SerDe declarations. A single grep across the codebase for these constructs gives a better effort signal than any headline object count.
- [ ] **[Critical]** Are UDFs classified by implementation language? SQL UDFs usually port. C, Java, and Python UDFs may not have a target equivalent at all, or may have one with a deprecation horizon -- Amazon Redshift, for example, has announced end of support for Python UDFs after 30 June 2026, which removes a landing spot that migration teams have historically used for exactly this code.
- [ ] **[Critical]** Is the semantic layer coupling understood? MicroStrategy, Cognos, Business Objects, and older Power BI/Tableau content frequently contain hand-written source-dialect SQL, database-specific functions, and assumptions about join behaviour and null ordering. This is where "the migration is done" collides with "the numbers on my report changed."
- [ ] **[Recommended]** Is workload management treated as a design gap rather than a configuration to copy? Teradata TASM and equivalents encode years of priority, throttle, and filter tuning. The target's model (Redshift WLM queues and priorities, Snowflake warehouses, BigQuery reservations, Databricks SQL warehouses and pools) is structurally different. Design the target's isolation from the profiled workload, not by translating rules.
- [ ] **[Recommended]** Are the source's physical-design objects catalogued explicitly so their absence on the target is a decision rather than an omission? Join indexes, hash indexes, secondary indexes, materialized views, partitioned primary indexes, and zone maps do not have direct equivalents. Each one exists because a query was slow; each one needs a target-side answer.
- [ ] **[Optional]** Is a small representative slice converted end to end before the estimate is finalised? Converting five procedures, ten tables, and three reports produces a measured per-object cost. Every estimate built without one is a guess.

### Schema Conversion Versus Redesign

- [ ] **[Critical]** Is the schema-conversion posture decided explicitly -- like-for-like conversion, or redesign? Like-for-like is faster to cut over, keeps reconciliation simple (the same tables produce the same rows), and preserves consumer contracts. Redesign produces a better platform but makes reconciliation much harder, because you can no longer compare table to table. Doing both at once is the most common cause of a migration that never reaches parity.
- [ ] **[Critical]** Is the recommended default "convert now, redesign after cutover" understood and defended? The business case for the migration is almost always licence and infrastructure recovery, which requires decommissioning, which requires cutover. Redesign delays cutover, and the redesign work is not lost -- it is simply done later, against a target platform the team now understands, without the source running in parallel.
- [ ] **[Critical]** Are the source's distribution and partitioning constructs deliberately *not* carried across? A Teradata primary index, a Netezza distribution key, or a Greenplum `DISTRIBUTED BY` clause is a data-placement decision for a specific architecture. On the target it should be re-derived from the profiled workload, or delegated to the platform's automatic optimization where one exists. Carrying it across mechanically is how you inherit skew that took years to develop.
- [ ] **[Critical]** Is the absence of table partitioning on some targets accounted for in the design? Amazon Redshift has no partitioned-table construct; conversion tooling emulates source partitioning by generating one table per partition behind a `UNION ALL` view (AWS SCT defaults to a cap of 368 target tables per source table). That works, but it multiplies object counts against the per-cluster table quota and produces DDL nobody wants to maintain. Sort keys, clustering, or partition-by on the target are the native answer.
- [ ] **[Critical]** Are data-type conversions reviewed for precision, not just for name? Numeric precision and scale, `NUMBER` versus `DECIMAL` versus floating point, date-versus-timestamp, timestamp-with-timezone handling, and maximum string length all differ. Redshift, for instance, does not support `VARCHAR` larger than 64 KB, so source LOB columns cannot land as-is. A silent precision downgrade is invisible until a financial total is wrong in the fourth decimal place.
- [ ] **[Recommended]** Are character-set and collation semantics checked before reconciliation is designed? Trailing-space handling, case sensitivity, and sort order differ between platforms. Teradata's `LATIN` versus `UNICODE` character sets and its padded-comparison semantics are a classic source of "the data is identical but the checksums do not match."
- [ ] **[Recommended]** Are constraints understood as informational on most warehouse targets? Redshift, Snowflake, and BigQuery do not enforce primary key or uniqueness constraints -- the optimizer trusts them, but nothing prevents duplicates. Any deduplication the source was doing implicitly has to be done explicitly in the pipeline.
- [ ] **[Optional]** Is an open table format adopted for new tables where the target supports it, so the next migration is cheaper? See `general/data-analytics.md` for the format selection discussion.

### Data Movement and Initial Load

- [ ] **[Critical]** Is the extract path chosen against the source's native parallel export capability rather than a JDBC pull? Teradata TPT/FastExport, Netezza `nzsql`/external tables, Greenplum `gpfdist`, Oracle Data Pump or external tables, and Hadoop DistCp all move data far faster than a row-at-a-time driver, and the source usually has a finite window in which extraction can run without harming production.
- [ ] **[Critical]** Is file layout on the staging tier designed for the target's parallel loader? Split, compressed, columnar or delimited files with a count that is a multiple of the target's parallelism unit (Redshift slices, Snowflake warehouse threads, Spark partitions) load dramatically faster than one large file or thousands of tiny ones.
- [ ] **[Critical]** Is history load separated from ongoing change capture, with an explicit handover point? The standard shape is bulk history extract to object storage, then CDC or scheduled delta loads to close the gap, then a defined cut where the source stops being written. Getting the handover wrong produces duplicated or missing rows in exactly the window nobody is testing.
- [ ] **[Critical]** Is network transfer capacity checked against the actual volume and window? Multi-hundred-terabyte extracts over a shared corporate link are a schedule risk that is trivially avoidable with physical transfer appliances. Establish the achievable sustained throughput empirically before committing to a date.
- [ ] **[Recommended]** Are compressed source footprints translated into realistic extract sizes before sizing the staging tier? Exadata HCC and Teradata multi-value compression can expand several-fold on extract.
- [ ] **[Recommended]** Is CDC feasibility confirmed per source rather than assumed? Legacy MPP warehouses are frequently poor CDC sources -- there may be no log-based capture path at all, and the practical option is a timestamp- or sequence-based delta extract, which requires that every table actually has a reliable change column. Verify this table by table before designing around it.
- [ ] **[Optional]** Is a bounded pilot dataset defined -- one subject area, full history -- to shake out the pipeline before the full load? The pilot's value is that it surfaces type, encoding, and null-handling problems at a scale where they can be diagnosed.

### ELT and Transformation Rewrite

- [ ] **[Critical]** Is the transformation model chosen deliberately rather than inherited? Most legacy estates are ETL: a tool transforms data outside the warehouse and loads the result. Most cloud targets favour ELT: land raw, transform in the warehouse with SQL under version control. That is a better end state, but it is a rewrite and a change of ownership (engineers to analytics engineers), not a migration.
- [ ] **[Critical]** Is transformation logic put under version control with tests as part of the rewrite, rather than after? The migration is the only moment when every transformation is being touched anyway. A migration that reproduces undocumented, untested logic in a new dialect has spent the budget and bought nothing but a platform change.
- [ ] **[Critical]** Are the orchestration semantics rebuilt rather than translated? Oozie XML, BTEQ control flow, and ETL-tool schedulers encode dependencies, retries, and failure handling. There is no high-quality automated converter to a modern orchestrator. Rebuild the DAG from the dependency graph the profiling produced.
- [ ] **[Recommended]** Is idempotency established for every rewritten job? Cloud pipelines get re-run -- for backfill, after failure, during reconciliation. A job that was safe to run once a night on the source because a human watched it is not safe in the target's operating model.
- [ ] **[Recommended]** Is the batch window re-validated against the target's actual concurrency model early? A sequence of jobs that fitted the source's window because the workload manager prioritised them may not fit the target's, where concurrency is bought rather than scheduled.
- [ ] **[Optional]** Is data quality validation added at the ingestion boundary as part of the rewrite? The migration is the cheapest time to introduce it; see `general/data-analytics.md`.

### Dual-Run and Reconciliation

- [ ] **[Critical]** Is a dual-run period planned where both platforms are loaded from the same sources and produce comparable output? This is the mechanism that makes cutover trustable. Without it, cutover is a leap of faith and the business will correctly refuse to take it. Budget for it explicitly -- it is a period of paying for both platforms *and* running a reconciliation workload, and it is the line item most often cut.
- [ ] **[Critical]** Is reconciliation layered: row counts, then column checksums, then business-metric parity? Row counts catch load failures and filter errors. Column-level aggregate checksums (sum, min, max, count-distinct, and a hash aggregate over the row) catch type and encoding problems. Business-metric parity -- the actual numbers on the actual reports -- catches the semantic differences the first two layers cannot see. All three are necessary and only the third is sufficient.
- [ ] **[Critical]** Are checksums designed to be *comparable* across the two dialects rather than merely computable on each? Hash functions differ between platforms, so the usual approach is to normalise first (cast to a canonical string form with explicit format, trim, and apply a defined null token) and then aggregate. Floating-point columns cannot be checksummed reliably at all because summation order differs; compare them with a tolerance instead.
- [ ] **[Critical]** Is a legitimate-difference register maintained, so expected differences are not re-investigated every cycle? Real examples: Teradata `SET` tables silently reject duplicate rows on insert, so a faithful migration to a target with no such behaviour produces *higher* row counts and the source was the one losing data; trailing-space comparison differences change `GROUP BY` cardinality; different rounding on `DECIMAL` division changes totals in the last decimal place; null ordering in `ORDER BY` differs, changing which row a "top 1" query returns. Each of these must be diagnosed once, documented, and then excluded from the delta report.
- [ ] **[Critical]** Does reconciliation cover a complete business cycle including month-end or period-close? Daily reconciliation over three weeks proves nothing about the period-close logic, which is where the complicated, high-value, least-documented code lives.
- [ ] **[Recommended]** Is reconciliation automated and reported on a schedule, with a signed-off tolerance policy per metric? "Investigate every difference" is not a policy; it produces a backlog that never converges. Materiality thresholds should be agreed with the business owner in advance, per metric, in writing.
- [ ] **[Recommended]** Is the reconciliation workload isolated from the performance comparison? Running heavy full-table checksums on the target while also measuring whether it meets the SLA produces two wrong answers.
- [ ] **[Recommended]** Is performance parity assessed on the profiled top-N queries rather than on a synthetic benchmark? The question the business is asking is "will my report still return in eight seconds," and the answer comes from the real query mix.
- [ ] **[Optional]** Is a reconciliation harness built to be reusable across subject areas rather than hand-written per table? Migrations run reconciliation hundreds of times; the harness pays for itself in the first month.

### Cutover

- [ ] **[Critical]** Is cutover incremental by subject area or consumer group rather than big-bang, unless there is a specific reason otherwise? Incremental cutover reduces blast radius, lets the team learn, and produces early licence savings if source capacity can be released progressively. Its cost is a longer coexistence period with cross-platform joins or duplicated reference data.
- [ ] **[Critical]** Is a rollback path defined and tested, with a decision deadline, for each cutover wave? "Keep the source running" is not a rollback plan unless the source is still being loaded and someone has confirmed the reports still point at it and still work.
- [ ] **[Critical]** Is the freeze period on the source defined and communicated -- no new objects, no schema changes -- from the start of reconciliation? A moving source is the most reliable way to make reconciliation never converge.
- [ ] **[Recommended]** Is the batch chain cut over as a unit within a subject area? Splitting a dependency chain across two platforms produces cross-platform orchestration and cross-platform data dependencies, which is the most expensive coexistence shape.
- [ ] **[Recommended]** Is there a hypercare period with the migration team on call and the source still available? The failures that matter surface at the first period-close after cutover, not in the first week.
- [ ] **[Optional]** Is a query-federation or virtualization layer used to smooth coexistence during a long incremental cutover? It reduces consumer churn during the transition at the cost of an extra component that then has to be removed.

### BI Layer and Consumption Repoint

- [ ] **[Critical]** Is every consumer's connection path enumerated and owned, including the ones outside the BI tool? Connection strings, gateway configurations, service accounts, drivers, and firewall rules all change. Driver differences alone (ODBC/JDBC version, TLS requirements, authentication mode) account for a meaningful fraction of cutover-day incidents.
- [ ] **[Critical]** Is embedded source-dialect SQL inside reports found and fixed before cutover, not after? Any report with a hand-written query, a custom SQL dataset, or a database-specific function is a code object, and it belongs in the conversion inventory rather than in the "repoint the connection" bucket.
- [ ] **[Critical]** Is report-level output parity tested for the top reports as part of business-metric reconciliation? Running the same report against both platforms and diffing the output is the check that the business actually believes.
- [ ] **[Recommended]** Is the authentication and authorization model for consumers designed on the target rather than translated? Source-side grants, roles, and row-level restrictions rarely map cleanly. Translating them mechanically tends to fail permissively, which is invisible until an audit.
- [ ] **[Recommended]** Is extract-and-cache behaviour in the BI tool reviewed? Tools that cache or extract data can mask a broken connection for days and can also multiply cost on a per-byte-scanned target if the extract refresh is aggressive.
- [ ] **[Optional]** Is the opportunity taken to retire unused reports? The consumption inventory usually shows that a large share of reports have not been opened in a year.

### Decommissioning and Licence Recovery

- [ ] **[Critical]** Is the decommissioning date the anchor for the schedule, tied to the source's support or subscription renewal? The business case is the licence, hardware, and support saving. If the programme is not sequenced so that the source is retired before the renewal, the saving is deferred by a full term and the business case is materially worse than the one that was approved.
- [ ] **[Critical]** Is there a funded, scheduled decommissioning workstream with a named owner, rather than an assumption that it happens after cutover? Decommissioning is the workstream most often unfunded, and an un-decommissioned source is a permanent double run rate plus a permanent second copy of regulated data.
- [ ] **[Critical]** Is the retention and legal-hold requirement for the source's data settled before the platform is switched off? Retrieving data from a decommissioned MPP appliance is somewhere between very expensive and impossible. Take the archival extract while the platform is still running, in an open format, and verify it is readable independently of the source. See `general/legal-hold.md`.
- [ ] **[Recommended]** Is capacity released progressively where the source's licensing permits it? Some models allow node reduction, which converts an incremental cutover into incremental savings and keeps the programme's funding visible.
- [ ] **[Recommended]** Are downstream integrations confirmed dead before the source is switched off, by monitoring connections rather than by asking? Turning the source off and waiting for complaints is a real technique, but it should be a deliberate, communicated "lights-off" test with a rapid restore path, not an accident.
- [ ] **[Optional]** Is the hardware disposition path planned for on-premises appliances, including data destruction certification? See `general/hardware-asset-disposition.md`.

## Source Platform Notes

What each common source makes hard. Verify version-specific details against current vendor documentation.

### Teradata

The most common cloud-warehouse migration source. Its architecture is shared-nothing: a Parsing Engine handles session control, parsing, optimization, and dispatch, and work is distributed across AMPs (Access Module Processors) over the BYNET interconnect, each AMP owning a slice of every table.

- **The primary index is a distribution mechanism, not a constraint.** `PRIMARY INDEX` determines which AMP a row lands on via a row hash. It is not the same thing as a primary key. Teams migrating off Teradata routinely mistranslate it into a target primary key or a distribution key without re-deriving it from the workload, and inherit the source's skew.
- **Skew is the dominant performance concern**, and it is measurable on the source (`DBC.TableSizeV` `CurrentPerm` per AMP). A low-cardinality or heavily-defaulted primary index concentrates rows on a few AMPs. Skew analysis on the source is directly useful input for target key selection -- AWS SCT, for example, excludes columns above a configurable skew threshold from distribution-key candidacy.
- **`SET` tables are the default in Teradata mode and silently reject duplicate rows on insert.** This is the single most under-appreciated reconciliation trap: a faithful migration produces *more* rows than the source, and the difference is real data the source was discarding. AWS SCT exposes an explicit "emulate the behavior of SET tables" conversion option precisely because of this.
- **Load and scripting utilities are programs.** BTEQ, FastLoad, MultiLoad, TPump, FastExport, and TPT scripts combine data movement with conditional logic and error handling. There is no target equivalent; they are rewritten.
- **Dialect surface is wide.** `QUALIFY`, `FORMAT` phrases in DDL and casts, `SAMPLE`, volatile and global temporary tables, macros, SPL stored procedures, multi-value column compression, and `LATIN`/`UNICODE` character-set semantics all appear in real codebases.
- **Physical design objects have no target equivalent**: partitioned primary indexes (including multi-level), join indexes, hash indexes, and secondary indexes each exist because a query was slow, and each needs a target-side answer.
- **The optimizer is unusually strong on large joins**, and it is statistics-dependent (`COLLECT STATISTICS`). Queries written against it assume that big joins are cheap. On a target priced per byte scanned, the same query can be dramatically more expensive even when it is faster.
- **Spool space limits** mean that unoptimized queries fail on the source rather than running slowly. Migrated SQL that never had to be efficient because Teradata's optimizer rescued it is a real category.
- **Naming note:** Teradata renamed its product line in 2026 -- the platform formerly called Vantage is now the Teradata Autonomous Knowledge Platform, VantageCloud is Teradata Cloud, ClearScape Analytics is Teradata AI Studio, QueryGrid is Teradata Fabric, and IntelliFlex is Teradata Factory. Both naming sets will appear in customer documentation and contracts for years. See `providers/teradata/data-warehouse.md`.

### Netezza (IBM)

An FPGA-accelerated MPP appliance, now continued as IBM Netezza Performance Server.

- **The appliance model is the point**: performance came from purpose-built hardware doing early filtering close to the disk. That hardware advantage does not exist on the target, so query patterns that relied on brute-force scanning need review.
- **Distribution (`DISTRIBUTE ON`) and organization (`ORGANIZE ON`) clauses** are physical design decisions equivalent in role to Teradata's primary index; the same "re-derive, do not translate" rule applies. Zone maps provided the block-skipping that a target's clustering or sort keys must now provide.
- **NZPLSQL stored procedures** are a Postgres-derived procedural dialect and are the main manual-conversion burden.
- **Change capture is awkward.** AWS SCT's documented approach for ongoing replication requires creating a Netezza history database and configuring history logging, then running data extraction agents -- which is more setup than a log-based CDC source and needs to be planned rather than assumed.

### Greenplum

A PostgreSQL-derived MPP with a coordinator and segment architecture.

- **The Postgres lineage cuts both ways.** PL/pgSQL and much standard SQL port well to Postgres-derived targets, which makes the conversion look easy. The MPP-specific surface -- `DISTRIBUTED BY` / `DISTRIBUTED RANDOMLY`, append-optimized and column-oriented table options, resource queues, and `gpfdist` external tables for parallel load -- does not port, and that is where the effort is.
- **Commercial ownership has moved** (VMware, then Broadcom), which for many estates is itself the migration trigger. Confirm the current support and licensing position directly with the vendor rather than from secondary sources; the situation has changed more than once.

### Oracle / Exadata

Usually an Oracle data warehouse running on Exadata engineered systems rather than a distinct product.

- **PL/SQL is the effort.** Warehouses on Oracle accumulate very large PL/SQL package bodies containing business logic. This is the largest manual-rewrite category of any source on this list.
- **Hybrid Columnar Compression is Exadata-dependent.** Data compressed with HCC expands substantially on extract, which changes the transfer and staging plan. Measure the uncompressed size before sizing anything.
- **Smart Scan, storage indexes, and flash cache** are storage-tier offload features. Queries tuned to exploit them have performance characteristics that will not reproduce, and the tuning work has to be redone against the target's mechanisms.
- **Partitioning is heavily used** and is genuinely good on Oracle. Targets without a partitioning construct force a redesign onto sort keys or clustering rather than a translation.
- **Oracle-specific SQL** (`CONNECT BY` hierarchical queries, `DECODE`, `ROWNUM`, `MERGE` variants, and Oracle's analytic extensions) appears throughout both procedures and reports.

### Hadoop / Hive

Frequently a Cloudera estate; see `providers/cloudera/data-platform.md` for the platform-specific detail.

- **The Hive Metastore is the asset.** Table definitions, storage locations, partition lists, and statistics live there, and they cannot be reconstructed from the data files alone. Migrating DDL by hand loses partition metadata and statistics, and the target optimizer then behaves nothing like the source.
- **Hive ACID (transactional) tables are ORC-backed and compaction-dependent**, and most external readers cannot interpret their delta directories. Inventory them before committing to a date.
- **Small files are a first-class problem.** A file count in the hundreds of millions is an operational constraint on the source and will be a cost and performance constraint on the target too. Compaction is part of the migration, not a follow-up.
- **HDFS semantics differ from object storage.** Rename is not atomic and listing is not free; jobs relying on rename-based commit protocols or per-task directory listings behave differently and sometimes incorrectly.
- **Oozie workflows** encode scheduling, dependencies, and business logic in XML with no high-quality automated path to a modern orchestrator. This is manual rewrite work and it is consistently underestimated.
- **Authorization is Ranger-shaped**, and Ranger's per-service resource and tag policies do not map onto cloud IAM or warehouse RBAC. Translation defaults to permissive unless someone reviews it.

## Why This Matters

The failure mode that defines this pattern is the migration that reaches production and never reaches decommissioning. The target is live, the reports work, and the source is still running because three feeds nobody documented still point at it and nobody owns switching them off. The organisation now pays for two warehouses instead of one, has two copies of regulated data, and has consumed the budget that was justified by a licence saving it never realised. Every element of this pattern -- consumption inventory, dual-run, decommissioning as a funded workstream with a named owner -- exists to prevent that specific outcome.

The second failure is estimating from the schema. Table counts and data volumes are easy to gather and are almost uncorrelated with effort. A 200-table warehouse with 3,000 stored procedures and 40,000 lines of BTEQ is a multi-year programme; a 4,000-table warehouse that is loaded by a handful of parameterised jobs and read by a governed semantic layer can move in months. The procedural-code count, the dialect-construct grep, and the consumption inventory are the three numbers that predict the schedule, and all three take real work to obtain, which is why they usually are not obtained before a date is committed.

The third failure is the one this pattern's title gestures at: **lift-and-shifting a star schema onto a platform priced per byte scanned.** On the source, the fact table was expensive to buy once and then free to query, so a decade of report authors wrote `SELECT ... FROM fact JOIN dim ... WHERE` with no partition predicate, and the workload manager kept them from hurting each other. Move that unchanged onto BigQuery, Athena, Redshift Spectrum, or Snowflake without partitioning, clustering, or sort keys, and every dashboard refresh full-scans the fact table. The cost is now proportional to query count and concurrency, so it grows with adoption rather than with data. Organisations discover this in the first full month after cutover, and the fix -- partitioning, clustering, materialized aggregates, and consumer-side query hygiene -- is design work that should have happened during conversion. The physical design is not an optimization to defer; on a consumption-priced platform it *is* the cost model.

Reconciliation deserves more respect than it usually gets because it is the only thing standing between the programme and a loss of business confidence. The differences it surfaces are frequently *legitimate* -- `SET`-table deduplication, collation, rounding, null ordering -- and a team that has not built a legitimate-difference register will chase the same four explanations every cycle and will eventually start waving differences through. Once the business sees one wrong number after cutover, the migration acquires a credibility problem that costs more to fix than the technical work did.

Finally, the physical design assumptions are the real payload. A warehouse's schema is portable; its tuning is not. Primary indexes, distribution keys, partitioning schemes, join indexes, zone maps, statistics, and workload-management rules are all answers to questions the target does not ask, phrased in terms it does not have. Treating them as things to translate rather than as evidence about the workload is the single most reliable way to produce a target that is slower and more expensive than the platform it replaced.

## Common Decisions (ADR Triggers)

- **Convert then redesign vs redesign during migration** -- like-for-like conversion first (fast cutover, tractable reconciliation, preserved consumer contracts, earlier licence recovery) vs redesign in flight (better end state, much harder reconciliation because table-to-table comparison no longer holds, and a materially later decommissioning date)
- **Target platform class** -- cloud warehouse (closest operational analogue to the source, simplest cutover, per-warehouse cost model) vs lakehouse (open formats, one storage tier for SQL and ML, more design freedom, more design responsibility) vs a hybrid where the warehouse serves BI and the lake serves data science; see `general/data-analytics.md`
- **Big-bang vs incremental cutover** -- big-bang for small or tightly-coupled estates (one reconciliation, one rollback decision, one coexistence period) vs incremental by subject area (lower blast radius, progressive licence recovery, but a long coexistence with cross-platform dependencies and duplicated reference data)
- **Dual-run duration and scope** -- a short dual run on a sampled subset (cheap, faster, weaker evidence) vs a full-cycle dual run across a period close on the complete workload (expensive, slower, and the only version the business will actually sign off on)
- **Reconciliation tolerance policy** -- exact match required (defensible, but guarantees a long tail of legitimate-difference investigations) vs agreed per-metric materiality thresholds signed off by the business owner in advance (converges, but requires the business to engage before cutover rather than after)
- **ETL retained vs rewritten as ELT** -- keep the existing ETL tool and repoint it (fastest path, preserves the operating model, keeps pushdown-optimization coupling and licence cost) vs rewrite as in-warehouse ELT under version control (better long-term platform, changes who owns transformation logic, and is a rewrite programme in its own right)
- **Procedural-code strategy** -- automated conversion with review (cheaper per object, output quality varies sharply by construct) vs deliberate rewrite of the high-value procedures and retirement of the rest (higher unit cost, much better end state, and usually the only way to shed the accumulated dead logic)
- **CDC vs delta extract for the coexistence period** -- log-based CDC where the source supports it (lower latency, lower source impact) vs timestamp or sequence-based delta extract (works everywhere, but requires that every table has a reliable change column, which has to be verified table by table)
- **Physical design on the target** -- delegate to the platform's automatic optimization (Redshift Automatic Table Optimization, Snowflake automatic clustering, BigQuery's defaults) for most tables vs hand-designed keys and partitioning for the small set of large tables where the access pattern is known and the cost of getting it wrong is high
- **Decommissioning trigger** -- decommission at the end of each incremental wave where licensing permits capacity release (visible progressive saving, more coordination) vs a single decommissioning after full cutover (simpler, but defers the entire business case to the end and is the version most likely to slip past a renewal)
- **Archive strategy for the retired source** -- full archival extract in an open format verified independently readable (highest confidence, real storage cost) vs retaining a minimal source environment for a defined retention period (lower effort, ongoing licence and support exposure, and the environment tends to become permanent)

## Reference Architectures

### Staging-and-load pipeline for the initial history migration

- Source-native parallel export (Teradata TPT/FastExport, Netezza external tables, Greenplum `gpfdist`, Oracle Data Pump, HDFS DistCp) writing compressed, split files to cloud object storage
- File count tuned to a multiple of the target's parallelism unit; file size in the tens to low hundreds of megabytes compressed
- Target-native bulk load from object storage (`COPY`, `COPY INTO`, `LOAD DATA`, or a Spark write), never row-by-row over a driver
- Physical or high-bandwidth transfer appliance where the volume-over-window arithmetic does not work on the existing link
- Load results validated per file batch, with a manifest so a partial failure can be resumed rather than restarted
- Statistics collected on the target immediately after load, before any performance comparison is attempted

### Dual-run reconciliation harness

- Both platforms loaded from the same upstream sources for the dual-run period; the source is frozen for schema changes
- Layer 1 -- row counts per table per load cycle, reported automatically, with any non-zero delta triaged the same day
- Layer 2 -- per-column aggregates on a canonical normalisation: cast to string with an explicit format, trim, substitute a defined null token, then `SUM`/`MIN`/`MAX`/`COUNT DISTINCT` and a hash aggregate. Floating-point columns compared with a tolerance rather than hashed
- Layer 3 -- business-metric parity: the top reports executed against both platforms and diffed, including the period-close reports
- A legitimate-difference register holding each diagnosed expected difference (SET-table deduplication, collation, rounding, null ordering) with its cause and its exclusion rule, so it is investigated once
- A signed-off tolerance policy per metric, agreed with the business owner before reconciliation starts
- Reconciliation queries run in an isolated compute pool or WLM queue so they do not distort the performance comparison running alongside

### Incremental cutover by subject area

- Subject areas ordered by (a) low inbound dependency, (b) a small, identifiable consumer group, and (c) presence of a business owner who will sign off
- Each wave: convert schema, migrate history, rewrite the batch chain as a unit, dual-run to parity across a full cycle, repoint consumers, hypercare, then release source capacity where licensing permits
- Reference and conformed dimension data either migrated first and served to both platforms, or duplicated with a single authoritative writer -- never independently maintained on both
- Cross-platform dependencies during coexistence handled by scheduled extract from the authoritative side rather than by live federation, unless the coexistence period is long enough to justify the extra component
- A wave is not complete until its source objects are dropped or its capacity is released; "cutover complete, decommissioning to follow" is the state this pattern exists to prevent

## Reference Links

- [AWS Schema Conversion Tool](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Welcome.html) -- assessment reports, schema and code conversion, and the extension pack
- [AWS SCT source databases](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Source.html) -- the full source list including Teradata, Netezza, Greenplum, Vertica, Oracle DW, SQL Server DW, and Hadoop/Oozie
- [AWS SCT: Teradata source](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Source.Teradata.html) -- statistics collection via BTEQ, the SET-table emulation option, `UNION ALL` view partitioning, and skew-threshold-driven key selection
- [AWS SCT: Netezza source](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Source.Netezza.html) -- history-database setup for ongoing change capture and extraction-agent configuration
- [AWS SCT: Greenplum source](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Source.Greenplum.html) -- conversion and optimization settings for Greenplum to Redshift
- [AWS SCT: Oracle data warehouse source](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Source.OracleDW.html) -- Oracle DW conversion settings
- [AWS SCT: Apache Hadoop source](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Source.Hadoop.html) -- Hadoop and Hive estate conversion
- [AWS SCT data extraction agents](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/agents.html) -- distributed extraction to S3 and ongoing replication tasks
- [AWS Database Migration Service](https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html) -- full load and CDC; see the Redshift target page for S3-staging and `COPY` mechanics
- [BigQuery Migration Service](https://docs.cloud.google.com/bigquery/docs/migration-intro) -- assessment, SQL translation, data transfer, and metadata migration
- [BigQuery migration assessment](https://docs.cloud.google.com/bigquery/docs/migration-assessment) -- workload profiling and conversion-complexity reporting
- [BigQuery batch SQL translator](https://docs.cloud.google.com/bigquery/docs/batch-sql-translator) -- bulk dialect translation
- [BigQuery interactive SQL translator](https://docs.cloud.google.com/bigquery/docs/interactive-sql-translator) -- single-statement translation for iterative work
- [Teradata to BigQuery migration overview](https://docs.cloud.google.com/bigquery/docs/migration/teradata-overview) -- documented phases and the migration agent
- [Amazon Redshift to BigQuery migration overview](https://docs.cloud.google.com/bigquery/docs/migration/redshift-overview) -- the same pattern in the opposite direction
- [Hive to BigQuery migration overview](https://docs.cloud.google.com/bigquery/docs/migration/hive-overview) -- Hadoop estate migration guidance
- [Snowflake SnowConvert](https://www.snowflake.com/en/migrate-to-the-cloud/snowconvert/) -- Snowflake's source-code conversion tooling; confirm current source-platform coverage directly
- [AWS Prescriptive Guidance patterns](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/welcome.html) -- reference migration patterns including warehouse migrations
- [Teradata platform](https://www.teradata.com/platform) -- current product naming after the 2026 rename
- [Teradata documentation](https://docs.teradata.com/) -- SQL reference, utilities, and workload management
- [IBM Netezza documentation](https://www.ibm.com/docs/en/netezza) -- Netezza SQL, distribution, and administration
- [IBM Netezza Performance Server](https://www.ibm.com/products/netezza-performance-server) -- the current Netezza product
- [Oracle Exadata](https://www.oracle.com/engineered-systems/exadata/) -- Smart Scan, Hybrid Columnar Compression, and storage indexes
- [dbt](https://www.getdbt.com/) -- the common landing point for rewritten in-warehouse ELT logic under version control
- [Great Expectations](https://greatexpectations.io/) -- data quality assertions usable as part of a reconciliation harness

---

## See Also

- `providers/teradata/data-warehouse.md` -- the most common source platform, its architecture, and what its physical design does not translate to
- `providers/cloudera/data-platform.md` -- Hadoop/Hive estates as a migration source, including Hive Metastore and Ranger policy translation
- `providers/aws/redshift.md` -- Redshift as a migration target, including the physical design decisions that determine post-migration cost
- `providers/snowflake/data-platform.md` -- Snowflake as a migration target
- `providers/databricks/data-platform.md` -- lakehouse as a migration target, especially for Spark and mixed SQL/ML workloads
- `providers/gcp/bigquery.md` -- BigQuery as a migration target, and the per-TB-scanned cost model that punishes an unmodified star schema
- `general/data-analytics.md` -- warehouse vs lake vs lakehouse selection, ETL vs ELT, and open table format choice
- `general/database-migration.md` -- OLTP database migration, where the schema usually does move unchanged
- `general/data-migration-tools.md` -- bulk transport tooling and physical transfer appliances
- `patterns/migration-cutover.md` -- generic cutover mechanics, rollback planning, and hypercare
- `patterns/migration-coexistence.md` -- running two platforms during an incremental cutover
- `patterns/data-pipeline.md` -- target-side pipeline architecture and sized cost benchmarks
- `general/legal-hold.md` -- retention obligations that must be settled before the source is decommissioned
- `general/hardware-asset-disposition.md` -- physical disposal of decommissioned appliances
- `general/workload-migration.md` -- broader workload migration planning and wave sequencing
- `general/cost.md` -- FinOps controls for a consumption-priced target
