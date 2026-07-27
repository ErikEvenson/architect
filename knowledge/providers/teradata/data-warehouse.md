# Teradata Data Warehouse

## Scope

Teradata as it is actually encountered: the shared-nothing MPP architecture (Parsing Engine, AMPs, BYNET), the primary index as the data-distribution mechanism and skew as the dominant performance concern, spool space, the physical design objects that have no cloud equivalent (partitioned primary indexes, join indexes, secondary indexes, columnar tables), statistics and the cost-based optimizer, workload management, the load and export utility family (BTEQ, FastLoad, MultiLoad, TPump, FastExport, TPT), the dialect surface that breaks on migration, the current cloud products, and what a migration off Teradata actually costs in rewritten SQL.

Teradata is the single most common source system in cloud data-warehouse migration engagements, so this file is written to be useful in two directions: designing and operating a Teradata estate, and getting off one. For the migration process itself -- assessment, dual-run, reconciliation, cutover, decommissioning -- see `patterns/data-warehouse-migration.md`.

**Naming.** Teradata renamed its product line in 2026. The platform formerly called Vantage is now the **Teradata Autonomous Knowledge Platform**; VantageCloud is **Teradata Cloud**; ClearScape Analytics is **Teradata AI Studio**; QueryGrid is **Teradata Fabric**; IntelliFlex is **Teradata Factory**. Older names remain in customer contracts, runbooks, job titles, and on parts of Teradata's own site (the pricing page still uses VantageCloud Enterprise and VantageCloud Lake). Expect both sets to be in use for years, and confirm which product a customer actually holds rather than inferring it from the name they use.

## Checklist

### Architecture and Data Distribution

- [ ] **[Critical]** Is the shared-nothing model understood before any performance conversation? A Parsing Engine handles session control, parsing, optimization, and dispatch; work is distributed across AMPs (Access Module Processors) over the BYNET interconnect; each AMP owns a private slice of storage and processes only its own rows. Every performance characteristic of the platform -- good and bad -- follows from the fact that a query is only as fast as its slowest AMP.
- [ ] **[Critical]** Is it understood that `PRIMARY INDEX` is a data-placement mechanism and not the same thing as a primary key? Teradata hashes the primary index columns, maps the row hash to an AMP, and stores the row there. A Unique Primary Index (UPI) additionally enforces uniqueness; a Non-Unique Primary Index (NUPI) does not enforce anything. Confusing `PRIMARY INDEX` with `PRIMARY KEY` is the single most common conceptual error made by people arriving from other databases, and it propagates directly into bad migration decisions.
- [ ] **[Critical]** Is skew measured rather than assumed? A low-cardinality, heavily-defaulted, or null-heavy primary index concentrates rows on a subset of AMPs. Skew is visible from `DBC.TableSizeV` by comparing `CurrentPerm` across AMPs for a table. A skewed table makes every query touching it run at the speed of one AMP regardless of how many the system has, and skew accumulates silently as data distributions change.
- [ ] **[Critical]** Is spool space understood as a hard failure boundary rather than a performance setting? Intermediate results live in per-user spool. An unoptimized join or an unexpected product join exhausts spool and the query fails outright ("no more spool space") rather than running slowly. This is why Teradata estates tend to contain SQL that has never been made efficient -- the optimizer and the spool limit together enforced a floor that a cloud target will not.
- [ ] **[Recommended]** Are NoPI tables used where they are appropriate -- staging and landing tables that are loaded and immediately consumed, where hash distribution buys nothing and even distribution is what you want?
- [ ] **[Recommended]** Is the physical-versus-logical model documented? A well-run Teradata estate has an integrated logical model in third normal form with semantic views over it, and a physical model tuned separately. Migrations that only capture the physical tables lose the semantics that the views encode.
- [ ] **[Optional]** Is BYNET-level redistribution visible in `EXPLAIN` output being read by whoever is tuning? Redistribution of a large table across AMPs before a join is the equivalent of a broadcast on other MPP systems and is the usual cause of a query that is fast in test and slow in production.

### Physical Design

- [ ] **[Critical]** Is the primary index chosen for the dominant join and access pattern, with the distribution consequence checked? The primary index simultaneously determines distribution, single-AMP retrieval eligibility, and join collocation. All three matter and they can conflict. Any change to it is a full table redistribution.
- [ ] **[Critical]** Are partitioned primary indexes (PPI, including multi-level) inventoried before a migration date is committed? PPI gives partition elimination on top of hash distribution. It is heavily used on large fact tables and has no direct equivalent on several cloud targets -- Amazon Redshift has no partitioned-table construct at all, and conversion tooling emulates the source's partitioning by generating one table per partition behind a `UNION ALL` view.
- [ ] **[Critical]** Are join indexes catalogued as what they are -- materialized, automatically-maintained pre-joins and aggregates that the optimizer substitutes transparently? Reports that depend on a join index for their runtime will not show anything unusual in their SQL. On migration, the join index disappears and the report slows down by an amount nobody predicted, because the dependency was invisible.
- [ ] **[Recommended]** Are secondary indexes (unique and non-unique) and hash indexes reviewed for whether they still earn their maintenance cost? They add write overhead on every load, and estates accumulate indexes created for queries that no longer run.
- [ ] **[Recommended]** Are column-partitioned (columnar) tables identified separately? They behave differently enough on scan-heavy workloads that migration performance testing which ignores them will mislead.
- [ ] **[Recommended]** Is multi-value compression on columns inventoried before extract sizing? Column-level compression can make the on-platform footprint substantially smaller than the extracted size, which changes the transfer and staging plan.
- [ ] **[Optional]** Are `SET` versus `MULTISET` choices deliberate? `SET` is the default in Teradata mode and prohibits duplicate rows, which costs a duplicate-row check on every insert. `MULTISET` permits duplicates and avoids that check. This choice has direct migration consequences -- see the reconciliation item below.

### Statistics and the Optimizer

- [ ] **[Critical]** Is a statistics collection regime in place and actually running? The optimizer is cost-based and unusually dependent on statistics; stale or missing statistics on a large table produce plans that are not merely suboptimal but catastrophically wrong (product joins, wrong join order, spool exhaustion). `COLLECT STATISTICS` on the relevant columns and indexes is not optional maintenance.
- [ ] **[Critical]** Are statistics collected on the columns the optimizer actually needs -- join columns, predicate columns, and index columns -- rather than on everything or on nothing? Collecting on everything is expensive on a large estate; collecting on nothing produces the failure mode above.
- [ ] **[Recommended]** Is `EXPLAIN` output part of the change process for any new or modified production query? Teradata's `EXPLAIN` is unusually readable and reports confidence levels; a "no confidence" step on a large table is the signal that statistics are missing.
- [ ] **[Recommended]** For migration work, are source statistics harvested as *input* to target physical design? Cardinality and skew data from the source tells you which columns are good distribution-key candidates on the target. AWS SCT does this explicitly, using collected statistics and a configurable skew threshold to exclude skewed columns from distribution-key candidacy.
- [ ] **[Optional]** Is query logging (DBQL) enabled at a useful granularity? `DBC.DBQLogTbl`, `DBC.dbqlsqltbl`, and `DBC.QryLogObjectsV` are the workload-profiling substrate for capacity planning, chargeback, and migration assessment. `BEGIN QUERY LOGGING` with SQL and object capture is the standard configuration; note that full SQL text capture has its own storage cost.

### Workload Management

- [ ] **[Critical]** Is workload management configured deliberately rather than left at defaults? Teradata's workload management assigns queries to workloads by classification (user, account, application, estimated cost, object touched), and applies priority, concurrency throttles, and filters. On a mixed estate this is what stops an ad-hoc analyst query from displacing the nightly batch. Note that the available capability varies by platform tier and edition -- confirm what the customer actually has rather than assuming the full Teradata Active System Management feature set.
- [ ] **[Critical]** Is the workload-management configuration treated as a *design artifact* during migration rather than a configuration to translate? It encodes years of accumulated knowledge about which workloads conflict, at what times, and what the business considers important. No cloud target has an equivalent model, so the correct move is to extract the intent -- workload classes, their priorities, their windows -- and design the target's isolation from that.
- [ ] **[Recommended]** Are filters and throttles reviewed periodically against the current workload? A throttle added years ago to protect a batch window that has since moved is a permanent, invisible concurrency cap.
- [ ] **[Recommended]** Is Viewpoint (or the current monitoring portal) actually used for capacity trending, not just for incident response? The question a migration needs answered is "what does a normal week look like," and only trending data answers it.
- [ ] **[Optional]** Is per-user spool limit set deliberately as a guardrail? It is the crudest but most effective protection against a single runaway query.

### Load, Export, and Scripting

- [ ] **[Critical]** Is the utility footprint counted as code, not configuration? BTEQ, FastLoad, MultiLoad, TPump, FastExport, and Teradata Parallel Transporter scripts are the load and extract layer of most Teradata estates, and BTEQ in particular combines SQL with control flow (`.LOGON`, `.EXPORT`, `.IMPORT`, `.RUN FILE`, `.OS`, `.IF ERRORCODE`, `.QUIT`), error handling, and file manipulation. These are programs. They have no equivalent on a cloud target and are rewritten, not converted. Counting them -- and their total line count -- is one of the best available predictors of migration effort.
- [ ] **[Critical]** Is TPT the standard for new work, with the older standalone utilities treated as legacy? Teradata Parallel Transporter consolidates the load/export operators behind one framework. Estates that still run large volumes of standalone FastLoad and MultiLoad scripts carry an extra migration burden and an extra operational one.
- [ ] **[Critical]** For migration extract planning, is a native parallel export path used rather than a JDBC pull? FastExport and TPT's export operator move data at a completely different order of magnitude from a driver-based extract, and the source usually has a bounded window in which extraction can run without harming production.
- [ ] **[Recommended]** Are load utility concurrency limits accounted for in extract scheduling? The number of concurrent load and export jobs a system will accept is bounded, and hitting the limit during a migration extract stalls the schedule in a way that looks like a network problem.
- [ ] **[Optional]** Is backup and archive tooling in scope for the retention obligation after decommissioning? Extracting archival data from a retired Teradata platform is somewhere between very expensive and impossible; the archival extract must be taken while the platform still runs. See `general/legal-hold.md`.

### SQL Dialect and Application Coupling

- [ ] **[Critical]** Has the codebase been grepped for the dialect constructs that will not port? `QUALIFY` (window-function filtering without a subquery), `FORMAT` phrases in DDL and in `CAST`, `SAMPLE`, `TOP`, volatile and global temporary tables, `HELP` and `SHOW` statements, `TRANSLATE`/`TRANSLATE_CHK` with `LATIN_TO_UNICODE`, and Teradata's permissive implicit conversions all appear in real codebases. A single grep across procedures, macros, BTEQ, and report SQL gives a better effort signal than any object count.
- [ ] **[Critical]** Are macros counted separately from stored procedures? Macros are a Teradata-specific parameterised SQL construct with no equivalent on any target. They are typically converted to views, stored procedures, or application code depending on what they actually do, and the decision is per macro.
- [ ] **[Critical]** Are SPL stored procedures scoped as rewrite rather than conversion? Error handling, transaction semantics, cursor behaviour, and dynamic SQL all differ from every target's procedural dialect. Automated conversion produces syntactically valid output that still needs behavioural review and test, so the per-object cost is dominated by review, not by translation.
- [ ] **[Critical]** Is character-set and comparison semantics understood before reconciliation is designed? `LATIN` versus `UNICODE` column definitions, case-specificity settings, and padded/trailing-space comparison behaviour change `GROUP BY` cardinality and string equality on the target. This is the most common cause of "the data is identical but the checksums do not match."
- [ ] **[Critical]** Is the `SET`-table duplicate-row behaviour flagged to the reconciliation workstream in advance? A `SET` table silently rejects duplicate rows on insert. A faithful migration to a target with no such behaviour therefore produces *more* rows than the source, and the source was the one discarding data. AWS SCT provides an explicit option to emulate `SET` semantics in converted `INSERT..SELECT` statements precisely because this is a known trap.
- [ ] **[Recommended]** Are ETL tools checked for pushdown optimization against Teradata? Informatica, DataStage, and Ab Initio jobs configured for pushdown generate Teradata-dialect SQL at runtime. They do not repoint; the pushdown behaviour has to be re-established or the transformation moved out of the tool.
- [ ] **[Recommended]** Is embedded SQL in the BI and semantic layer inventoried as code? MicroStrategy, Cognos, and Business Objects content frequently contains hand-written Teradata SQL. It belongs in the conversion inventory, not in the "repoint the connection string" bucket.
- [ ] **[Optional]** Are numeric precision and rounding differences identified before financial reconciliation begins? `DECIMAL`/`NUMBER` division and rounding semantics differ across platforms and produce differences in the last decimal place that are legitimate and must be registered as such rather than investigated repeatedly.

### Cloud and Current Products

- [ ] **[Critical]** Is the customer's actual product and deployment established, not assumed from the name they use? Teradata Cloud runs on AWS, Azure, and Google Cloud; Teradata Factory covers the on-premises engineered platform. The pricing page still presents the earlier VantageCloud Enterprise and VantageCloud Lake structure, and internal documentation will use whichever name was current when it was written.
- [ ] **[Critical]** Is the compute model understood for cloud deployments? Teradata Cloud separates compute from storage and supports both always-on active compute for mission-critical operations and on-demand elastic compute for training, experimentation, and burst workloads, with elastic compute able to operate directly on open-format tables in object storage. This is architecturally much closer to a modern cloud warehouse than a classic Teradata appliance, and it materially changes the "stay versus leave" calculation.
- [ ] **[Critical]** Is the pricing structure understood before a stay-versus-leave business case is built? As published on Teradata's pricing page and read on 26 July 2026: the Lake tiers start from $4.80, $6.00, and $7.20 per hour for Standard, Lake, and Lake+ respectively; Enterprise tiers start at $9,000 and $10,500 per month; block storage is quoted as low as $1,445/TB per year and object storage as low as $276/TB per year. Teradata states that all Vantage deployment options carry the same price per unit. Verify current rates and the precise unit definition directly with the vendor -- the published unit definition is not mathematically explicit and the numbers change.
- [ ] **[Recommended]** Is a migration *to* Teradata Cloud evaluated alongside migration away from Teradata? For an estate with tens of thousands of lines of SPL and BTEQ and a heavy join workload, moving to Teradata's own cloud offering eliminates the entire dialect and procedural rewrite. It keeps the vendor relationship and the subscription, but it is frequently the cheapest path to exiting a datacentre and is systematically under-considered in engagements framed as "get off Teradata."
- [ ] **[Recommended]** Is Teradata Fabric (formerly QueryGrid) in use for federation to other platforms? An estate already federating to Hadoop, Snowflake, or object storage has a partial coexistence mechanism in place that can be used during a migration.
- [ ] **[Optional]** Is native object-store querying already in use for cold data? Teradata has supported reading and writing data in cloud object storage from SQL for several releases; where it is already in use, the coldest data may already be outside the platform and out of migration scope. Confirm the current feature name and capability against documentation for the deployed version.

### Migrating Off Teradata

- [ ] **[Critical]** Is the effort estimate built from procedural code and utility scripts rather than from table count and data volume? Table count and terabytes are easy to gather and nearly uncorrelated with duration. Stored procedure count, macro count, BTEQ/TPT line count, and dialect-construct frequency are what predict the schedule.
- [ ] **[Critical]** Is the physical design explicitly *not* carried across? Primary indexes, PPI schemes, join indexes, and secondary indexes are answers to questions the target does not ask. Harvest them as evidence about the workload -- which columns are joined, which predicates are selective, which tables are skewed -- and then design the target from the workload profile.
- [ ] **[Critical]** Is DBQL-based workload profiling done over at least 30 days including a period close? This is the input to target sizing, to physical design, to workload isolation design, and to identifying which of the estate's objects are genuinely dead. Every one of those is guesswork without it.
- [ ] **[Critical]** Is the cost model difference understood -- that Teradata was a paid-for fixed asset where queries were effectively free at the margin, and most targets are consumption-priced? A decade of report authors wrote unrestricted scans against the fact table because there was no marginal cost signal. On a per-byte-scanned or per-compute-second target, that same behaviour scales cost with adoption. This is the single largest post-migration cost surprise and it is a design problem, not a tuning problem.
- [ ] **[Recommended]** Is conversion tooling used with realistic expectations? AWS SCT converts Teradata schemas and code objects to Amazon Redshift (optionally in combination with AWS Glue) and offers Teradata-specific options for `SET`-table emulation, partition emulation via `UNION ALL` views, compression encoding, and statistics-driven distribution and sort key selection. The BigQuery Migration Service covers Teradata among its supported source dialects. Both are genuine accelerators for the mechanical layer; neither removes the review-and-test cost on procedural code.
- [ ] **[Recommended]** Is SQL virtualization or emulation considered as a bridge where the codebase is enormous and the timeline is short? Products exist that intercept Teradata-dialect SQL and execute it against a cloud target, deferring the rewrite. This trades a large one-time rewrite for an ongoing dependency on a third party in the query path, and the trade should be made explicitly rather than by default.
- [ ] **[Recommended]** Is the decommissioning date anchored to the support or subscription renewal? The business case is the licence, hardware, and support saving, and it is only realised on decommissioning. See the decommissioning discipline in `patterns/data-warehouse-migration.md`.
- [ ] **[Optional]** Is a partial migration an acceptable outcome? Moving data science, ad-hoc exploration, and semi-structured workloads off Teradata while leaving the core integrated warehouse in place is a legitimate and often cheaper end state than a full exit -- provided somebody owns the resulting two-platform operating model rather than it happening by attrition.

## Why This Matters

Teradata estates are old, load-bearing, and expensive, and that combination produces a specific engagement shape. The platform is usually the system of record for enterprise reporting; it has been tuned continuously for fifteen to thirty years; the people who built it have mostly left; and the annual cost is large enough that somebody senior has asked whether it can be replaced. The technical question is never "can this data be moved" -- it can -- but "how much of what makes it work is written down."

Most of what makes it work is not written down, and it is not in the schema. It is in the primary index choices that make the nightly join collocated, in the join indexes that silently accelerate the reports the executives look at, in the statistics regime that keeps the optimizer from choosing a product join, in the workload-management rules that keep the analysts from displacing the batch, and in thirty thousand lines of BTEQ that encode the actual load process. A migration plan built from a schema extract captures none of that and will produce a target that is slower, more expensive, and produces different numbers.

The primary-index confusion deserves specific attention because it causes real damage. Practitioners arriving from Oracle or SQL Server read `PRIMARY INDEX` as a primary key, translate it into a target primary key or distribution key, and thereby import the source's data-placement decisions into a system with a different execution model. The correct treatment is to read the primary index as *evidence*: it tells you what the design team thought the dominant join was, which is useful input, and nothing more.

The `SET`-table behaviour is the best example of why reconciliation needs its own discipline. A faithful migration off a `SET` table produces more rows on the target than the source has, because the source was silently discarding duplicates on insert. A reconciliation process that treats any row-count difference as a defect will spend weeks chasing this, and a reconciliation process that has not anticipated it will erode confidence in the whole exercise at exactly the wrong moment. The fix is a legitimate-difference register built before reconciliation starts, and the `SET`-table case belongs on it from day one.

Finally, the cost-model inversion is the surprise that lands after the programme is declared successful. Teradata was capital: bought once, sized for peak, and free at the margin. Every cloud target meters something -- bytes scanned, compute-seconds, credits, RPU-hours -- so the query behaviour a Teradata estate has trained into its users for a decade becomes a variable cost that grows with adoption. Organisations that did not redesign the fact tables' physical layout during conversion discover this in the first full billing month after cutover, and by then the migration team has usually been disbanded.

## Common Decisions (ADR Triggers)

- **Stay on Teradata Cloud vs migrate to a different platform** -- Teradata Cloud eliminates the dialect, procedural, and utility rewrite entirely and still exits the datacentre (keeps the vendor relationship and subscription; retains the operating model) vs migrating to a cloud warehouse or lakehouse (removes the subscription, unlocks the wider ecosystem, and costs a full rewrite of SPL, macros, and BTEQ); this option is systematically under-considered in engagements framed as "get off Teradata"
- **Target platform for an exit** -- cloud warehouse (closest analogue, simplest cutover, easiest reconciliation) vs lakehouse (open formats, one storage tier for SQL and ML, more design responsibility) vs a split where BI goes to a warehouse and data science goes to a lake; see `general/data-analytics.md`
- **Physical design on the target** -- re-derive keys and clustering from DBQL workload profiling and source statistics (correct, requires the profiling work) vs delegate to the target's automatic optimization (cheaper, converges within hours to days, correct for most tables) vs translate the source's primary indexes mechanically (fast, wrong, and imports the source's skew)
- **Partitioning emulation** -- accept the conversion tool's per-partition tables behind a `UNION ALL` view (preserves partition elimination semantics, multiplies object count against per-cluster quotas, produces unmaintainable DDL) vs redesign onto the target's native mechanism -- sort keys, clustering, or partition-by (better end state, requires design work during conversion)
- **Procedural code strategy** -- automated conversion with per-object review (lower unit cost, quality varies sharply by construct) vs deliberate rewrite of the high-value procedures with retirement of the rest (higher unit cost, sheds accumulated dead logic, and is usually the only way the estate actually gets smaller)
- **SQL virtualization as a bridge** -- accept an emulation layer so the existing Teradata-dialect codebase runs unchanged against a cloud target (fast cutover, defers the rewrite) vs rewrite up front (no third party in the query path, no ongoing licence, longer programme)
- **`SET` vs `MULTISET` on the target** -- reproduce `SET` deduplication semantics explicitly in the load pipeline (row counts match the source, extra cost on every load) vs allow duplicates and treat the difference as expected (cheaper, requires the legitimate-difference register and business sign-off that the extra rows are correct)
- **Workload isolation design** -- translate the existing workload-management rules (fast, and produces rules that do not fit the target's model) vs extract the intent from DBQL and design target isolation from the profiled workload (correct, requires the profiling work)
- **Extract path** -- native parallel export via TPT/FastExport to object storage (fast, bounded impact on the source, needs load-slot scheduling) vs driver-based extract (simple, orders of magnitude slower, and frequently the reason a migration schedule slips)
- **Partial vs full exit** -- move exploratory, data science, and semi-structured workloads off while retaining the integrated warehouse (lower risk, retains the subscription, needs an owner for the two-platform model) vs full exit and decommission (realises the whole business case, and is the only version that stops the double run rate)

## Reference Architectures

### Migration assessment from a live Teradata estate

- DBQL enabled with SQL and object capture for at least 30 days including a period close; output is the query inventory by frequency and by resource consumption, and the table-access map
- Object inventory from the data dictionary reconciled against the query inventory to identify objects with no reads over a full business cycle -- the archive-and-drop candidate list
- Skew and size profile per table from `DBC.TableSizeV`, with `CurrentPerm` compared across AMPs; feeds both target key selection and the "which tables are already a problem here" list
- Statistics harvested as target design input, not just as a source health check
- Procedural inventory: stored procedures, macros, and views counted and classified; BTEQ, TPT, and standalone utility scripts counted by file and by line
- Dialect grep across every code artifact -- procedures, macros, BTEQ, ETL-generated SQL, BI report SQL -- for `QUALIFY`, `FORMAT`, `SAMPLE`, volatile tables, and the rest
- Consumption inventory including direct ODBC/JDBC connections and scheduled extracts, not just the BI catalogue
- Physical design register: every PPI, join index, hash index, and secondary index, with the query it exists for where that can be established

### Extract pipeline for the history load

- TPT export operator (or FastExport for legacy estates) writing compressed, split files directly to cloud object storage
- File count tuned to a multiple of the target loader's parallelism unit; extract scheduled against the platform's concurrent load-slot limit rather than against wall-clock convenience
- Uncompressed extract size measured on a pilot subject area before the full transfer is scheduled -- multi-value compression makes the on-platform footprint a poor predictor
- Physical transfer appliance used where the volume-over-window arithmetic does not work on the existing link
- Character-set handling pinned explicitly at extract time (`LATIN` versus `UNICODE` columns) so encoding problems surface in the pilot rather than in reconciliation

### Coexistence during an incremental exit

- Teradata remains authoritative for un-migrated subject areas; the target is authoritative for migrated ones, with a single writer per dataset and no dataset maintained independently on both
- Conformed dimensions migrated first and served to both platforms, so the two do not diverge on reference data
- Cross-platform dependencies handled by scheduled extract from the authoritative side rather than by live federation, unless the coexistence period is long enough to justify the extra component -- where Teradata Fabric federation is already in place, it is a legitimate bridge
- Source frozen for schema change from the start of reconciliation for each wave
- Capacity released progressively where the licensing model permits it, so the programme's funding stays visible

## Reference Links

- [Teradata documentation](https://docs.teradata.com/) -- SQL reference, utilities, workload management, and administration; the authoritative source for version-specific behaviour
- [Teradata documentation search](https://docs.teradata.com/search/all?query=primary+index) -- the documentation set is versioned and deep links rot; search from here rather than bookmarking topic URLs
- [Teradata platform](https://www.teradata.com/platform) -- the Autonomous Knowledge Platform and the 2026 product naming
- [Teradata Cloud](https://www.teradata.com/platform/cloud) -- cloud deployment across AWS, Azure, and Google Cloud; active versus elastic compute
- [Teradata pricing](https://www.teradata.com/pricing) -- published tier pricing and storage rates; verify current values directly
- [Teradata Developers](https://developers.teradata.com/) -- developer resources, drivers, and community content
- [Teradata Downloads](https://downloads.teradata.com/) -- Teradata Tools and Utilities including BTEQ, TPT, and the load/export utilities
- [AWS SCT: Teradata source](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Source.Teradata.html) -- conversion to Amazon Redshift, the `SET`-table emulation option, `UNION ALL` partition emulation, statistics collection via BTEQ, and skew-threshold-driven key selection
- [AWS Schema Conversion Tool](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Welcome.html) -- assessment reports and the conversion workflow
- [Teradata to BigQuery migration overview](https://docs.cloud.google.com/bigquery/docs/migration/teradata-overview) -- the documented Google Cloud migration path
- [BigQuery Migration Service](https://docs.cloud.google.com/bigquery/docs/migration-intro) -- assessment, SQL translation, and data transfer, with Teradata among the supported source dialects

---

## See Also

- `patterns/data-warehouse-migration.md` -- the migration process: assessment, dual-run and reconciliation, cutover, and decommissioning
- `providers/aws/redshift.md` -- the most commonly documented conversion target, and the physical design decisions that determine post-migration cost
- `providers/snowflake/data-platform.md` -- alternative migration target where multi-cloud is a requirement
- `providers/databricks/data-platform.md` -- lakehouse migration target, especially where ML workloads are in scope
- `providers/gcp/bigquery.md` -- BigQuery as a target, and the per-TB-scanned cost model that punishes an unmodified Teradata query pattern
- `providers/cloudera/data-platform.md` -- the other dominant legacy data platform; frequently coexists with Teradata in the same estate
- `general/data-analytics.md` -- warehouse vs lake vs lakehouse selection and the cloud data warehouse comparison
- `general/data-migration-tools.md` -- bulk transport tooling and physical transfer appliances for the history load
- `general/legal-hold.md` -- retention obligations that must be satisfied before the platform is decommissioned
- `general/cost-onprem.md` -- total cost framing for an on-premises platform including hardware refresh and specialist staffing
- `patterns/migration-coexistence.md` -- running two platforms during an incremental exit
