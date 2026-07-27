# Lakehouse Medallion Architecture (Bronze / Silver / Gold)

## Scope

The medallion architecture is the dominant layering convention for lakehouse data platforms: raw data lands in a **bronze** layer, is cleansed and conformed into a **silver** layer, and is aggregated into business-facing **gold** tables. This file covers what actually belongs in each layer, how to make each hop idempotent and re-runnable, how to handle late-arriving data and change data capture, where the schema-on-read boundary sits, what data-quality gates between layers should do, when the pattern is over-applied, and how the layers map onto catalogs and schemas across platforms.

This is a **convention**, not a product feature. Every platform lets you implement it and none of them enforce it. The term originates with Databricks (also called *multi-hop*), but the same three-tier idea appears as raw/staged/curated, landing/conformed/presentation, and in dbt as staging/intermediate/marts.

For the storage formats underneath the layers see `general/open-table-formats.md`. For ingestion, orchestration, and sized cost benchmarks see `patterns/data-pipeline.md`. For the platform-level warehouse-vs-lake-vs-lakehouse decision see `general/data-analytics.md`.

## Overview

Each layer answers a different question and has a different contract:

| | Bronze | Silver | Gold |
|---|---|---|---|
| Question answered | "What did the source send us?" | "What is true about our entities?" | "What does the business need to see?" |
| Schema posture | Schema-on-read, permissive | Schema-on-write, enforced | Schema-on-write, modelled |
| Write pattern | Append-only | `MERGE` / upsert | Full or incremental rebuild |
| Grain | Source record, as delivered | Conformed entity / event | Aggregated, dimensional, or wide |
| Typical consumers | Reprocessing jobs only | Data scientists, downstream pipelines, ad-hoc SQL | BI tools, applications, executives |
| Quality posture | Accept everything, record what arrived | Validate, quarantine, reject | Assume valid input |
| Retention driver | Replay horizon + audit | Business history + SCD needs | Reporting horizon |
| PII posture | As delivered (encrypt, restrict) | Masked, tokenized, or classified | Generally de-identified or aggregated |

The property that makes the pattern worth its cost is that **bronze is a replayable record of what arrived**. If a transformation bug corrupts silver and gold, you rebuild them from bronze without going back to source systems that may have already aged their data out. That single property justifies most of the storage cost. If bronze is not replayable -- if it is mutated in place, or truncated on a shorter horizon than the recovery requirement -- the pattern is being paid for without being received.

## Checklist

### Layer Definition and Contracts

- [ ] **[Critical]** Is the number of layers justified by the actual complexity, rather than adopted because the pattern is well known? Three layers on a 10 GB single-source dataset with one dashboard is over-engineering: it triples storage, triples the number of jobs to schedule and monitor, and adds two hops of latency to serve one report. Two layers (raw + curated) is the correct answer far more often than the literature suggests. Add a layer when a specific, named problem requires it.
- [ ] **[Critical]** Does each layer have a written contract stating what is guaranteed at its boundary -- schema stability, grain, freshness SLA, quality guarantees, and who is allowed to read it? Layers without contracts degrade into "three copies of the same data with slightly different column names," which is the most common way the pattern fails in practice.
- [ ] **[Critical]** Is **bronze append-only and never mutated in place**, preserving exactly what the source delivered? Correcting data in bronze destroys the replay property that justifies the layer existing. Corrections belong in silver, applied deterministically from bronze.
- [ ] **[Critical]** Does every bronze record carry ingestion provenance -- source system, source file or offset, ingestion timestamp, batch or run id, and (where available) a source-side commit identifier or LSN? Without this you cannot reconstruct which run produced which rows, cannot do partial replay, and cannot debug a bad load. Add it at ingest; it cannot be recovered later.
- [ ] **[Critical]** Is silver the layer where **conformance** happens -- consistent keys, consistent types, deduplication, resolved reference data, standardized units and time zones -- so that downstream consumers stop re-solving the same problems independently? If two gold tables each implement their own customer deduplication, silver is not doing its job.
- [ ] **[Recommended]** Is gold modelled around consumption (star schema, wide denormalized tables, or a metrics/semantic layer) rather than being "silver with a `GROUP BY`"? A gold layer that grows one table per dashboard is a symptom that the semantic layer is missing. See the semantic-layer guidance in `general/data-analytics.md`.
- [ ] **[Recommended]** Is there a rule for where a given transformation belongs, so the layers stay meaningful? A usable rule: **type/format/dedup/conform** goes in silver; **business definitions and aggregation** go in gold; **nothing** goes in bronze. Ambiguous logic that lands wherever is convenient is what erodes the layering.
- [ ] **[Optional]** If a fourth layer is proposed (platinum, semantic, feature store), is the specific need documented? A feature store for ML and a metrics layer for BI are legitimate additions; "gold felt too crowded" is not.

### Idempotent Reprocessing

- [ ] **[Critical]** Can every layer transition be re-run over the same input and produce the same output, without duplicates and without needing manual cleanup first? This is the single most important property of the whole pattern, because reprocessing is not an exception case -- it is how you recover from bugs, schema changes, and bad source data. Implement it with `MERGE` on a stable natural or surrogate key, or with deterministic partition-level overwrite (`replaceWhere` / partition overwrite / `INSERT OVERWRITE` scoped to a partition predicate).
- [ ] **[Critical]** Are transformations free of non-deterministic functions in anything that affects the output values or keys? `current_timestamp()`, `rand()`, `uuid()`, and "row number over an unstable ordering" all make a re-run produce different results than the original run. Capture wall-clock time once at ingest into a bronze column and read it from there.
- [ ] **[Critical]** Is the reprocessing scope bounded and parameterizable -- can an operator re-run "just 2026-03-14 through 2026-03-16" rather than only "everything"? Full rebuilds of large tables are expensive enough that teams avoid running them, which means bugs stay in the data. Partition-scoped reprocessing is what makes correction routine.
- [ ] **[Critical]** Is the deduplication key correct and stable, and is deduplication applied at a defined layer rather than defensively everywhere? At-least-once delivery from most streaming and file-based ingestion means bronze *will* contain duplicates. Deduplicating in silver on a source-provided idempotency key is correct; deduplicating on "all columns" is fragile and expensive.
- [ ] **[Recommended]** Are incremental processing checkpoints (stream checkpoints, job bookmarks, high-watermark tables) stored durably and versioned alongside the pipeline code, with a documented procedure for resetting them? A reset that loses the checkpoint but not the output data is how duplicates get created during an incident.
- [ ] **[Recommended]** Do downstream layers read from an explicit change feed rather than recomputing from scratch where volume justifies it -- Delta Change Data Feed, Iceberg incremental reads, or Hudi incremental queries? This is the main lever that makes a medallion pipeline cost-proportional to change volume instead of table size.
- [ ] **[Optional]** Is there a periodic full-rebuild test (against a copy, in a lower environment) proving that bronze can actually regenerate silver and gold? Replayability that has never been exercised is usually broken -- schemas drift, code depends on state, and a bronze retention policy quietly aged out the range you need.

### Late-Arriving and Out-of-Order Data

- [ ] **[Critical]** Are event time and processing time distinguished everywhere, and is partitioning based on **event time** for tables that will be corrected? Partitioning by ingestion date makes late-arriving records land in the wrong partition and makes "reprocess last Tuesday" impossible to express.
- [ ] **[Critical]** Is there a defined **restatement window** -- how far back the pipeline will accept and merge corrections -- and is it enforced rather than implicit? Without a bound, every run must consider the entire history; with a bound, each run rewrites a fixed number of partitions and cost stays flat. Anything arriving outside the window needs an explicit exception path, not silent acceptance or silent loss.
- [ ] **[Critical]** For streaming pipelines, is the watermark configured deliberately, with the trade-off understood? A long watermark holds more state and adds latency; a short one drops late events. Whatever is dropped by the stream must still be recoverable from bronze by a batch backfill, or the data is simply lost.
- [ ] **[Recommended]** Are dropped or quarantined late records observable -- counted, sampled, and alertable -- rather than silently discarded? "Numbers are slightly low on Mondays" is a very expensive way to discover that a watermark is too tight.
- [ ] **[Recommended]** Do gold aggregates get recomputed for any partition whose silver inputs changed, rather than being append-only? An append-only gold layer over a mutable silver layer produces figures that never converge with the underlying data, and the discrepancy is usually found by a stakeholder rather than by a test.

### Change Data Capture

- [ ] **[Critical]** Does bronze store the CDC **change stream** append-only (insert/update/delete events with their operation type and ordering token) rather than the current state? Collapsing to current state at ingest destroys the ability to rebuild history or fix an incorrect merge rule. See `patterns/data-pipeline.md` and `providers/confluent/kafka.md` for the transport side.
- [ ] **[Critical]** Is ordering established by a **source-side monotonic token** -- LSN, SCN, binlog position, transaction id, commit timestamp -- and never by arrival time or file modification time? Kafka partitioning, retries, and parallel writers all reorder events; using arrival order to decide which update wins produces silently wrong current-state tables.
- [ ] **[Critical]** Are deletes handled explicitly, with a decision recorded about soft vs hard delete propagation? Debezium-style tombstones, `op = 'd'` records, and truncate events each need a defined behaviour in silver. A pipeline that ignores delete events accumulates rows that no longer exist in the source, which is both a correctness problem and, for personal data, a compliance one.
- [ ] **[Critical]** Is the initial snapshot plus incremental stream handoff designed so that no records are lost or double-applied at the boundary? This is the single most error-prone part of a CDC pipeline: the snapshot must be taken at a known position in the change log, and the incremental stream must start from exactly that position.
- [ ] **[Recommended]** Is the silver representation chosen deliberately -- current-state (Type 1) via `MERGE`, or full history (Type 2 slowly changing dimension) with validity ranges? Type 2 is materially more expensive to build and maintain and should be driven by a stated requirement to query "as of" a past date, not adopted by default.
- [ ] **[Recommended]** Is the table format's mutation mode matched to CDC write frequency? A CDC target receiving frequent small merges is the canonical case for merge-on-read with scheduled compaction; leaving it on a copy-on-write default rewrites whole files for a handful of changed rows. See `general/open-table-formats.md`.
- [ ] **[Optional]** Are source schema changes (added column, dropped column, re-typed column) detected and surfaced by the CDC path rather than discovered when a downstream job fails? A schema registry with compatibility enforcement is the standard mechanism.

### Schema Boundaries and Evolution

- [ ] **[Critical]** Is the schema-on-read / schema-on-write boundary placed at the **bronze-to-silver** hop, and is it enforced there? Bronze accepts what arrives, including records it cannot parse. Silver enforces types, nullability, and referential expectations. Pushing enforcement earlier makes ingestion fragile (a malformed record blocks a whole load); pushing it later means every gold consumer re-implements it.
- [ ] **[Critical]** Are unparseable or schema-violating records **captured**, not dropped? A rescued-data column, a `_corrupt_record` column, or a dedicated quarantine table is what turns "we lost 3% of yesterday's events" into a debuggable dataset. Dropping on parse failure is the most common silent-data-loss mechanism in lakehouse pipelines.
- [ ] **[Recommended]** Is schema evolution explicit in the write path (`mergeSchema` and equivalents set intentionally, not globally on) so that an upstream change is a reviewed event rather than an automatic one? An added nullable column is usually safe to absorb; a re-typed or removed column is not.
- [ ] **[Recommended]** Is there a data contract between the producing system and bronze -- expected schema, semantics, freshness, and a change-notification obligation -- for sources that are internally owned? Contracts are how you stop a well-meaning upstream deploy from breaking twelve downstream tables.

### Data Quality Gates

- [ ] **[Critical]** Are quality checks placed **at layer boundaries** and given an explicit failure action -- warn, quarantine the offending rows, or fail the run and stop propagation? A check with no defined action is a dashboard nobody reads. The bronze-to-silver gate is where most value is: it is the last point where bad data can be stopped cheaply.
- [ ] **[Critical]** Is there a distinction between checks that must **block** propagation (primary key uniqueness, referential integrity on a join key, a null rate in a required column) and checks that should only **alert** (distribution drift, row-count variance against a trailing baseline)? Blocking on a soft signal causes teams to disable the gate entirely.
- [ ] **[Recommended]** Are quarantined rows retained, counted, and routed somewhere with an owner, rather than written to a table nobody reads? A quarantine table with a growing row count and no consumer is an outage in slow motion.
- [ ] **[Recommended]** Is the quality framework chosen and standardized rather than hand-rolled per pipeline -- declarative expectations in the pipeline framework, or a dedicated tool (Great Expectations, Soda, Glue Data Quality, Dataplex data quality, dbt tests)? Per-pipeline bespoke assertions do not aggregate into a platform-level quality signal.
- [ ] **[Recommended]** Are freshness and completeness monitored per layer as first-class metrics, so that "the gold table is stale" is detected before a stakeholder notices? Row counts, max event timestamp, and time-since-last-successful-run per table cover most real incidents.
- [ ] **[Optional]** Are quality results themselves stored as data (a table of check runs, outcomes, and row counts) so trends are analyzable and SLA reporting is possible?

### Physical Layout, Governance, and Cost

- [ ] **[Critical]** Is the layer boundary expressed in the platform's own namespace hierarchy so that access control can be granted per layer? The common patterns are **catalog per environment, schema per layer** (`prod.bronze.orders`) or **catalog per layer** (`bronze.sales.orders`). Whichever is chosen, most users should have no access to bronze at all -- bronze holds raw PII, source quirks, and duplicates, and is the layer most likely to be misread.
- [ ] **[Critical]** Is PII handling defined per layer -- encrypted and access-restricted in bronze, masked or tokenized in silver, generally aggregated or de-identified in gold -- and is the erasure path across all three layers documented? A GDPR erasure request that only removes from gold is not compliance. See `general/data-classification.md`.
- [ ] **[Critical]** Is bronze retention set from the **replay horizon plus audit requirement**, and priced? Bronze is usually the largest layer and grows fastest, and it is the layer with the least visible value, which makes it the one most likely to be either kept forever by inertia or truncated in a cost panic. Both are failures. Set it from the recovery requirement and apply storage tiering below that.
- [ ] **[Recommended]** Is the roughly 2-3x storage multiplication of the pattern acknowledged in the cost model, along with the compute cost of each hop? Storage is usually the cheap part; the recurring compute for hop transformations and the table maintenance on three sets of tables is what actually shows up on the bill.
- [ ] **[Recommended]** Are cold bronze partitions tiered to cheaper storage classes, given they are read only during reprocessing? This is one of the highest-ratio cost optimizations available in the pattern. See `providers/aws/s3.md` and the equivalent lifecycle controls on other clouds.
- [ ] **[Recommended]** Is lineage captured across the hops so that impact analysis ("what breaks if this source column changes?") is mechanical rather than archaeological? Most modern catalogs derive this automatically from query history when the transformations run through governed compute.
- [ ] **[Optional]** Are gold tables that no longer have consumers detected and retired? Gold layers accrete abandoned tables faster than any other layer because creating one is cheap and nobody owns deletion.

## Why This Matters

The medallion pattern earns its cost in exactly one situation: when something goes wrong. A transformation bug, a source system that started sending a field in a different unit, a deduplication rule that was subtly incorrect for six months -- in a platform with a genuine bronze layer, each of these is a bounded reprocessing job. In a platform where transformations were applied at ingest and the raw data was never kept, each of them is a negotiation with the source system about whether they still have the data, followed by an admission that some of the history is now unrecoverable. Teams that have lived through the second version never build the first way again.

The pattern fails in two opposite directions, and both are common. **Under-applied**: the pipeline writes transformed data straight into a serving table, so there is no replay path and no audit trail of what the source actually sent. **Over-applied**: three layers, three sets of tables, three sets of maintenance jobs, and three sets of monitoring for a dataset small enough to fit in memory, where silver is bronze with renamed columns and gold is silver with a `GROUP BY`. The second failure is more common in organizations that adopted the pattern from a conference talk. It burns engineering time and cloud spend continuously, and because it looks like best practice, nobody challenges it.

Idempotency is where the pattern most often breaks in practice, and the break is invisible until the first reprocess. A pipeline that appends rather than merges will double every row on a re-run. A transformation that stamps `current_timestamp()` into a business column produces different data on the second run than the first. A job whose "incremental" logic depends on the checkpoint being in sync with the output table will duplicate or skip data when the two are reset independently during an incident. Every one of these is discovered at the worst possible time -- during recovery from an unrelated problem -- and each turns a one-hour fix into a multi-day cleanup.

Late-arriving data is the second reliable source of quiet wrongness. If the pipeline partitions by ingestion date, corrections land in today's partition rather than the day they belong to, and no amount of reprocessing that day will fix last week's numbers. If the streaming watermark is tighter than the real tail of the source's delivery distribution, records are dropped every day at a low rate, and nothing alerts because dropping is the designed behaviour. Both produce reports that are consistently slightly wrong, which is worse than reports that are obviously broken, because they get trusted.

CDC amplifies all of this. Change streams are ordered by a source-side token that is not the order the events arrive in, and the ordering matters because the last update wins. Pipelines that merge by arrival order are correct almost all of the time -- which means the incorrect rows are rare, scattered, and effectively impossible to find without a full comparison against the source. The correct designs (order by LSN, keep the raw change stream in bronze, make the merge deterministic) cost very little more to build and remove the entire failure class.

## Common Mistakes

- **Bronze that is not actually raw** -- filters, type casts, column renames, or "just dropping the obviously bad rows" applied during ingestion. Any of these means bronze cannot reproduce what the source sent.
- **Silver that is bronze with renamed columns** -- the layer exists structurally but adds no conformance, so downstream consumers still each solve deduplication and key resolution independently.
- **Gold as a dashboard dumping ground** -- one table per report, no shared dimensions, no metric definitions, and conflicting numbers between dashboards that supposedly measure the same thing.
- **Append-only silver over a mutable source** -- produces a table whose row count grows forever and whose "current state" query requires a window function that gets slower every month.
- **Partitioning bronze by ingestion date** -- makes event-time reprocessing and late-data correction impossible to express.
- **Non-idempotent hops** -- append instead of merge, non-deterministic functions in output columns, or reprocessing that requires a manual delete first.
- **Quality checks with no failure action** -- a metrics dashboard of data-quality scores that nothing consumes and no run ever blocks on.
- **Silently dropping malformed records** -- parse failures discarded rather than routed to a quarantine table, which is invisible data loss.
- **One bronze table per source *file layout* rather than per source entity** -- a schema change upstream spawns a second table, and downstream logic accumulates unions.
- **No table maintenance** -- three layers of Iceberg or Delta tables with no scheduled compaction, snapshot expiry, or orphan cleanup. See `general/open-table-formats.md`.
- **Copying the pattern's *names* without its *contracts*** -- schemas called bronze/silver/gold with no stated guarantee at any boundary.

## Key Patterns

- **Multi-hop / medallion** -- the base pattern: append-only raw, conformed entity, aggregated serving.
- **Write-audit-publish (WAP)** -- write to a branch or staging snapshot, run quality checks against it, publish atomically only if it passes. Iceberg branches and Delta staging tables both support this, and it is the strongest form of a blocking quality gate because bad data is never visible even briefly.
- **Quarantine and reprocess** -- rows failing a gate are written to a quarantine table with the failed expectation recorded, then re-driven through the same transformation once the rule or the data is fixed.
- **Slowly changing dimension (Type 1 / Type 2)** -- current-state overwrite vs history-preserving validity ranges in silver. Type 2 is the expensive one; require a stated "as of" query need before choosing it.
- **Snapshot plus incremental** -- bootstrap from a full source snapshot at a known change-log position, then apply the incremental stream from exactly that position.
- **Restatement window** -- a fixed lookback (for example, 7 or 30 days) over which each run rewrites affected partitions, bounding reprocessing cost.
- **Change feed propagation** -- downstream layers consume a change feed rather than recomputing, so cost tracks change volume rather than table size.
- **Semantic/metric layer above gold** -- centralized metric definitions consumed by every BI tool, in place of a proliferating set of per-dashboard gold tables.

## Common Decisions (ADR Triggers)

- **Number of layers** -- two (raw + curated) for single-source, low-complexity, small-volume platforms vs three (bronze/silver/gold) for multi-source platforms with distinct engineering and analytics consumers vs four when a feature store or semantic layer is genuinely separate. Default to fewer; the burden of proof is on adding a layer.
- **Bronze retention and role** -- bronze as the authoritative replay source (long retention, higher storage cost, full recovery independence) vs the source system as the replay source (short bronze retention, cheaper, dependent on the source's own retention and on re-extraction capacity). This decision determines whether bronze cost is justified.
- **Silver modelling style** -- normalized conformed entities vs wide denormalized tables vs Data Vault. Data Vault buys auditability and source-agnostic loading at a substantial complexity cost and is rarely justified below enterprise scale with many overlapping sources.
- **Gold modelling style** -- dimensional star schema (portable, BI-tool-native, well understood) vs one-big-table denormalization (simplest for a single consumer, duplicates logic across tables) vs a virtual gold layer of views over silver with a semantic layer carrying the metrics (least storage, highest query cost).
- **CDC representation in silver** -- Type 1 current state (cheap, sufficient for most operational reporting) vs Type 2 history (required for point-in-time and regulatory "as of" queries, materially more expensive to build, test, and maintain).
- **Quality-gate failure policy** -- fail-fast and stop the pipeline (strongest guarantee, causes freshness outages on transient source problems) vs quarantine and continue (keeps the platform fresh, requires an owned quarantine workflow) vs warn only (lowest friction, weakest guarantee). Usually differs per check severity rather than being one global policy.
- **Batch vs streaming per hop** -- streaming bronze with batch silver/gold is a very common and defensible hybrid; full streaming through to gold buys latency at a large operational-complexity cost and should be tied to a stated business latency requirement.
- **Physical isolation of layers** -- catalog per environment with schema per layer (simpler cross-layer lineage and joins, permissions by schema) vs catalog per layer (stronger blast-radius and permission isolation, more cross-catalog friction) vs separate storage accounts/buckets per layer (strongest isolation, most operational overhead).
- **Gold materialization** -- materialized tables (fast, predictable BI performance, storage and refresh cost, staleness risk) vs views over silver (always fresh, no extra storage, query cost paid per read) vs materialized views where the platform maintains them incrementally.
- **Table format mutation mode per layer** -- append-only bronze, merge-on-read silver with scheduled compaction for CDC targets, copy-on-write gold for read-latency-sensitive serving tables. Encode this in table-creation templates rather than leaving it to each pipeline author.

## Reference Architectures

### Databricks medallion with Unity Catalog

Cloud object storage -> Auto Loader ingests files into append-only bronze Delta tables with `_metadata` provenance columns -> Delta Live Tables (or Workflows) apply expectations and `MERGE` into silver -> gold aggregates built from silver, with liquid clustering rather than partitioning. Unity Catalog gives `catalog.schema.table` where the catalog is the environment and the schema is the layer; grants are issued per schema so bronze is restricted. Change Data Feed drives incremental silver-to-gold propagation. Predictive optimization handles maintenance on managed tables. See `providers/databricks/data-platform.md`.

### AWS medallion on S3 with Iceberg

S3 prefixes `bronze/`, `silver/`, `gold/` (or separate buckets for stronger isolation) holding Iceberg tables registered in the Glue Data Catalog as three Glue databases -> Glue ETL or EMR Spark performs the hops -> Glue Data Quality rules gate bronze-to-silver -> Athena serves ad-hoc SQL over silver and gold -> Lake Formation grants per database, with bronze restricted to the data-engineering role and column-level filters applied on silver. Glue table optimizers run compaction and snapshot expiry on the mutable silver tables. Lifecycle policies tier bronze partitions older than the restatement window. See `providers/aws/glue.md`, `providers/aws/athena.md`, `providers/aws/lake-formation.md`, `providers/aws/s3.md`.

### BigQuery medallion

GCS landing -> BigQuery datasets `bronze`, `silver`, `gold` in one project (or a project per layer for stronger IAM isolation) -> scheduled queries or dbt perform the hops, with `MERGE` on the natural key for silver -> partitioned by event date and clustered on the common filter columns -> gold as materialized views or scheduled aggregate tables -> Dataplex handles discovery, profiling, and quality scans, and column-level policy tags enforce PII masking. See `providers/gcp/bigquery.md` and `providers/gcp/dataplex.md`.

### Streaming CDC medallion

Debezium captures changes from operational databases -> Kafka topics keyed by primary key -> a streaming job appends the raw change events (with operation type and LSN) to bronze -> a second job applies ordered `MERGE` into merge-on-read silver tables, emitting Type 1 current state and, where required, Type 2 history -> scheduled compaction keeps read amplification bounded -> gold aggregates refresh on a batch cadence rather than per event, because most business metrics do not need sub-minute freshness. See `patterns/event-driven.md` and `providers/confluent/kafka.md`.

### The two-layer counter-example

A single source, tens of gigabytes, one analytics consumer: land raw files in an immutable `raw/` prefix with date partitioning and lifecycle tiering, and build one curated table set with quality checks at the single hop. No silver. This is the right architecture far more often than a three-layer diagram, and it can be extended to three layers later at low cost -- the raw layer is already the bronze layer.

## Reference Links

- [Databricks Medallion Architecture](https://www.databricks.com/blog/what-is-medallion-architecture) -- the origin of the bronze/silver/gold terminology and its intended layer semantics
- [dbt: How We Structure Our Projects](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview) -- the staging/intermediate/marts equivalent of the same layering, with modelling conventions
- [Delta Lake Change Data Feed](https://docs.delta.io/delta-change-data-feed/) -- row-level change propagation between layers without full recomputation
- [Apache Iceberg Branching and Tagging](https://iceberg.apache.org/docs/latest/branching/) -- the mechanism behind write-audit-publish quality gates
- [Debezium](https://debezium.io/documentation/reference/stable/index.html) -- CDC connectors, snapshot-plus-incremental semantics, tombstone and delete event handling
- [Great Expectations](https://greatexpectations.io/) -- declarative data-quality expectations with validation results as data
- [Soda](https://www.soda.io/) -- SQL-based data quality checks and monitoring
- [AWS Glue Data Quality](https://docs.aws.amazon.com/glue/latest/dg/glue-data-quality.html) -- DQDL rules evaluated inside Glue jobs and on catalog tables
- [Kimball Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) -- star schemas, conformed dimensions, and slowly changing dimension types for the gold layer
- [Apache Spark Structured Streaming Programming Guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html) -- event time, watermarks, and late-data semantics

## See Also

- `general/open-table-formats.md` -- Iceberg/Delta/Hudi mechanics underneath the layers, including merge-on-read and table maintenance
- `patterns/data-pipeline.md` -- ingestion, orchestration, dead-letter handling, and sized cost benchmarks per cloud
- `general/data-analytics.md` -- warehouse vs lake vs lakehouse selection, ETL vs ELT, semantic layers, and data mesh
- `general/query-engines.md` -- the compute layer that serves silver and gold
- `patterns/event-driven.md` -- streaming ingestion, ordering, and replay semantics feeding bronze
- `general/data-classification.md` -- classification and PII handling policy applied per layer
- `general/database-migration.md` -- source-side extraction and CDC bootstrap considerations
- `providers/databricks/data-platform.md` -- Delta Live Tables, Auto Loader, Unity Catalog namespace mapping
- `providers/snowflake/data-platform.md` -- database/schema layering and streams-and-tasks equivalents
- `providers/aws/glue.md` -- Glue databases as layer boundaries, ETL jobs, and Data Quality
- `providers/aws/lake-formation.md` -- per-layer and per-column permissions over catalog-registered tables
- `providers/gcp/dataplex.md` -- lake/zone modelling, discovery, and data-quality scans on GCP
- `general/observability.md` -- freshness, lag, and pipeline health monitoring per layer
