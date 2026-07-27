# Data Ingestion and Change Data Capture

## Scope

How data gets from source systems into an analytical platform, with emphasis on the mechanics that determine correctness rather than the tooling that hides them. Covers change data capture method selection (log-based, query-based, trigger-based) and what each can and cannot detect; per-engine log mechanics for PostgreSQL, MySQL, SQL Server, Oracle, and MongoDB; the initial-snapshot-to-stream handover problem and chunked incremental snapshots; delivery semantics (at-least-once versus exactly-once) and idempotent sink design; ordering, late-arriving and out-of-order data, and watermarking; schema drift detection and propagation policy; backfill and replay strategy and the retention arithmetic that bounds it; managed connectors (Fivetran, Airbyte, Matillion, Apache NiFi, cloud-native services) and the build-versus-buy calculus; reverse ETL / operational activation; and the completeness evidence that makes CDC usable as an audit input.

For pipeline orchestration, cost benchmarks, and the batch/streaming architecture decision see `patterns/data-pipeline.md`. For what to do with the data once it lands see `general/data-modelling.md` and `providers/dbt/transformation.md`. For streaming platform selection see `general/messaging-patterns.md` and `providers/confluent/kafka.md`. For one-off migration (as opposed to continuous replication) see `general/database-migration.md`.

## Checklist

### Capture Method Selection

- [ ] **[Critical]** Has the capture method been chosen against what the downstream model actually needs, rather than by what is easiest to configure? The three families differ in what they can *detect at all*, and no downstream cleverness recovers a change that was never captured.

  | | Log-based | Query-based (high watermark) | Trigger-based |
  |---|---|---|---|
  | Detects hard deletes | Yes | **No** | Yes |
  | Detects intermediate states between reads | Yes | **No** | Yes |
  | Detects changes that bypass the app's `updated_at` logic | Yes | **No** | Yes |
  | Load on the source | Low (reads the log) | Moderate to high (repeated scans) | High (write amplification on every DML) |
  | Privileges required | Replication / log-reading, often DBA-level | Ordinary SELECT | DDL to create triggers and shadow tables |
  | Typical latency | Seconds | Poll interval | Seconds |
  | Main operational risk | Log retention and slot/job stalls fill source storage | Silent data loss | OLTP write latency and shadow-table growth |
  | Works on locked-down managed sources | Sometimes (needs vendor support) | Almost always | Needs DDL rights |

- [ ] **[Critical]** If query-based incremental extraction is used, is the **long-transaction skip** understood and mitigated? Reading `WHERE updated_at > :watermark` and then advancing the watermark to the maximum value seen permanently loses any row whose transaction was still open when the query ran but whose `updated_at` was set earlier -- it commits into the past, behind a watermark that has already moved on. Mitigations: lag the watermark behind wall-clock by more than the longest observed transaction; use overlapping windows with an idempotent merge; or order by a commit-ordered column rather than an application-set timestamp. This defect produces small, permanent, silent gaps and is almost never found by row counts.
- [ ] **[Critical]** If query-based extraction is used against a mutable source, is it accepted in writing that **hard deletes are invisible** and that the downstream model will assert deleted entities are still live indefinitely? The workarounds are a periodic full-key reconciliation (expensive but real) or a source-side soft-delete convention (requires application change). Doing neither is a decision, and it should be a recorded one.
- [ ] **[Recommended]** Where log-based CDC is not permitted by the source owner, has trigger-based capture been evaluated before falling back to query-based? Triggers are unfashionable and they cost write latency, but they are transactionally consistent with the source write and they see deletes and intermediate states. On a low-write reference table, that trade is often obviously correct.
- [ ] **[Optional]** For SaaS and API sources with no log at all, is the API's own change feed (updated-since endpoints, webhooks, audit logs) evaluated for completeness guarantees before being trusted as a change stream? Many "updated since" endpoints exclude deletes, exclude changes made by other integrations, or paginate non-deterministically under concurrent writes.

### Log-Based CDC: Per-Engine Mechanics

- [ ] **[Critical]** **PostgreSQL** -- is the replication slot's retention risk actively monitored? Logical decoding requires a replication slot per consumer, and the slot pins WAL until the consumer confirms it. A stalled, paused, or forgotten consumer accumulates WAL until the source volume fills, taking the database down. Monitor `restart_lsn` and `confirmed_flush_lsn` in `pg_replication_slots` and alert on lag in bytes, not just on connector health. Slots are also the single most common cause of "we deleted the dev connector and prod went read-only".
- [ ] **[Critical]** **PostgreSQL** -- if the captured tables live in a low-traffic database on an instance that also hosts a high-traffic one, is a heartbeat configured? Replication slots are per-database while the WAL is shared across the instance, so the connector cannot confirm progress until an event occurs in *its* database -- and WAL accrues in the meantime. Debezium's `heartbeat.interval.ms` with a heartbeat table added to the publication is the standard fix, and the heartbeat table must actually be in the publication or the mechanism does nothing.
- [ ] **[Critical]** **PostgreSQL** -- is `REPLICA IDENTITY` set appropriately per captured table? `DEFAULT` puts only the primary key in the before-image, so UPDATE and DELETE events carry no prior values for non-key columns; `FULL` carries every column and materially increases WAL volume. Tables without a primary key need `FULL` or `USING INDEX` to produce a usable event key at all. Additionally, unchanged **TOASTed** values (roughly, values over ~8 KB) are omitted from the replication message entirely; Debezium substitutes the string configured in `unavailable.value.placeholder`, and a sink that writes that placeholder as if it were the value silently corrupts the column. Filter or re-fetch, never store.
- [ ] **[Recommended]** **PostgreSQL** -- is the output plugin choice deliberate? `pgoutput` is built into PostgreSQL 10+, is what native logical replication uses, and requires no server-side installation; `decoderbufs` is a community Protobuf plugin requiring installation. On managed services `pgoutput` is usually the only option. Check the engine version's behaviour for replication slots across a failover to a physical standby -- historically slot state did not follow the failover, and support for synchronising slots to standbys is a relatively recent addition; verify for your version rather than assuming.
- [ ] **[Critical]** **MySQL** -- are `binlog_format=ROW` and `binlog_row_image=FULL` confirmed on the actual instance? Both are the documented defaults in MySQL 8.4, but managed-service parameter groups and inherited legacy configurations frequently set `MIXED` or `MINIMAL`, which strips the before-image and produces events that cannot support upserts or Type 2 history. Note also that `binlog_format` is deprecated in 8.4 and subject to removal, with row-based logging the intended future.
- [ ] **[Critical]** **MySQL** -- does binlog retention exceed the maximum tolerable consumer outage? `binlog_expire_logs_seconds` defaults to 2,592,000 seconds (30 days) in MySQL 8.4, but instances are routinely tuned down to hours for disk reasons. Retention is the hard bound on how long a connector can be down before the only recovery is a full re-snapshot -- which on a large table is an outage of its own. Size retention against the recovery objective, not against disk convenience.
- [ ] **[Recommended]** **MySQL on managed services** -- is binary logging actually on? On Amazon RDS, binary logging only occurs if automated backups are enabled for the instance, regardless of the parameter settings; a connector configured correctly against an instance without backups simply sees nothing. Managed instances also do not permit the global read lock, so the initial snapshot falls back to table-level locks, which changes the blocking profile of the snapshot considerably.
- [ ] **[Recommended]** **MySQL** -- are GTIDs enabled where failover to a replica must not require re-snapshotting? Position-based binlog coordinates are per-server; GTIDs are what let a connector resume against a different server in the topology.
- [ ] **[Critical]** **SQL Server** -- is the cleanup-job retention aligned with the consumer's maximum outage? SQL Server CDC reads the transaction log via `sp_replcmds` under a SQL Server Agent capture job and lands changes in `_CT` change tables; a separate cleanup job runs daily at 02:00 and retains **4,320 minutes (3 days)** by default. Beyond that window the changes are gone. The redeeming behaviour is that the validity-interval check makes the `fn_cdc_get_all_changes_*` functions **fail** rather than silently return partial data -- a loud failure, but a failure nonetheless.
- [ ] **[Critical]** **SQL Server** -- is it understood that with CDC enabled, the **log truncation point does not advance until the capture job has harvested the changes, even under SIMPLE recovery**? A stopped or failing capture job grows the transaction log without bound, and issuing CHECKPOINT does not help. This is the exact structural analogue of the PostgreSQL replication-slot risk, and it is the reason CDC on SQL Server needs SQL Server Agent monitoring, not just connector monitoring.
- [ ] **[Recommended]** **SQL Server** -- is the two-capture-instance limit used deliberately for schema-change cutovers? A maximum of two capture instances may be associated with one source table concurrently, which is precisely the mechanism for running an old and a new column shape in parallel while consumers migrate. Note also that the capture instance has a **fixed** column shape: columns added after enablement are ignored, dropped tracked columns return NULL, and only type changes propagate. Those divergences are silent, so column-set reconciliation has to be an explicit test.
- [ ] **[Critical]** **Oracle** -- has the licensing consequence of the mining adapter been established before design? Debezium's Oracle connector supports LogMiner (no additional Oracle licence), OpenLogReplicator (open-source, reads redo and archive logs directly), and XStream -- and **XStream is a commercial component of Oracle GoldenGate**, so choosing it introduces a licence cost that frequently exceeds the entire rest of the pipeline. Establish this before the architecture assumes XStream's throughput.
- [ ] **[Critical]** **Oracle** -- is supplemental logging enabled at the right scope, with the redo-volume consequence accepted? `ALTER TABLE ... ADD SUPPLEMENTAL LOG DATA (ALL) COLUMNS` is what makes before-images available, and it materially increases redo generation -- which propagates into archive log storage, backup windows, and Data Guard bandwidth. Enable per captured table rather than database-wide unless the whole database is captured.
- [ ] **[Recommended]** **Oracle** -- is `UNDO_RETENTION` sized for the initial snapshot? The snapshot of a large table can easily exceed the default 15-minute undo retention, and the snapshot then fails partway through. Size undo (and confirm the undo tablespace can grow) before the first run rather than after the third failed attempt.
- [ ] **[Recommended]** **MongoDB** -- are change streams used with persisted resume tokens, and is the oplog window treated as the retention bound? Change streams are the supported mechanism; the resume token is what makes restart possible; and an oplog that wraps past the last processed token forces a re-snapshot, exactly as with binlog or WAL expiry.

### Snapshot and Stream Handover

- [ ] **[Critical]** Is the handover between the initial snapshot and the ongoing stream provably lossless and duplicate-tolerant? The correct pattern is to record the log position **before** the snapshot begins and start streaming from that position afterwards, accepting that the overlap replays changes already present in the snapshot -- which is harmless if and only if the sink applies changes idempotently. A snapshot taken without recording a position has no safe resume point at all.
- [ ] **[Critical]** For large tables, is a **chunked incremental snapshot** used in preference to a locking full snapshot? Debezium's incremental snapshots (based on the Netflix DBLog watermark approach) split the table by primary key into chunks -- 1,024 rows by default -- and use watermarks in the change stream to reconcile chunk reads against concurrent writes. The operational properties are what matter: streaming continues throughout, the snapshot is resumable after interruption without restarting the table, and it can be triggered on demand through a signalling table to add a newly included table without re-snapshotting everything else.
- [ ] **[Recommended]** Is there a documented, rehearsed procedure for adding a table to an existing pipeline? The naive approach (stop the connector, change the include list, restart) triggers a full re-snapshot of everything on some configurations and produces a gap on others. The signal-driven incremental snapshot is designed for exactly this and should be the standard runbook step.
- [ ] **[Recommended]** Is initial-load volume separated from steady-state volume in the cost model? Some managed connectors exclude the initial historical load from billing and some do not, and the first month's bill is where that difference surfaces.
- [ ] **[Optional]** For sources where a consistent snapshot requires locking, has the snapshot's blocking profile been agreed with the source system owner in advance, including the fallback to table-level locks on managed instances?

### Delivery Semantics and Idempotency

- [ ] **[Critical]** Is the pipeline designed for **at-least-once delivery with an idempotent sink**, rather than assuming exactly-once? End-to-end exactly-once across a source database, a log reader, a broker, and a warehouse requires transactional coordination that most stacks do not have. The practical and robust equivalent is a MERGE keyed on the primary key with a monotonic version guard -- apply only when the incoming log position is greater than the stored one -- so that replays, retries, and out-of-order redelivery are all no-ops.
- [ ] **[Critical]** Is the version/ordering column a **log position** (LSN, SCN, binlog file and offset, resume token) rather than an event timestamp? Timestamps collide, skew between hosts, and are sometimes application-set; the log position is a total order per source and is the only field that reliably answers "which of these two versions of the row is later".
- [ ] **[Critical]** Are deletes handled explicitly at the sink, with a decided policy? Log-based CDC emits delete events and, in Kafka-shaped pipelines, tombstone records. Applying them as physical deletes in the landing layer destroys the ability to answer "what did this row look like last month"; the usual correct treatment is a soft delete (`is_deleted`, `deleted_at`) in the raw landing layer, with physical deletion reserved for erasure obligations. Whatever is chosen, the downstream model has to know which it is -- see `general/data-modelling.md` on hard deletes in Type 2 dimensions.
- [ ] **[Recommended]** Is per-key ordering preserved by partitioning on the primary key, and is it understood that global ordering is neither provided nor usually needed? Two updates to the same row must be applied in order; two updates to different rows need not be. Partitioning on anything other than the key breaks the guarantee that matters and provides one that does not.
- [ ] **[Recommended]** Is there a dead-letter path for events that cannot be parsed or applied, with enough context (source, position, raw payload) to replay them after a fix? A pipeline that halts on one bad record and a pipeline that silently drops it are both wrong; the DLQ is the third option.
- [ ] **[Optional]** Where the sink genuinely supports transactional writes, has exactly-once been evaluated against the throughput cost? It is achievable in specific stacks and it is rarely free.

### Ordering, Lateness, and Watermarks

- [ ] **[Critical]** Has the actual arrival-delay distribution been **measured** for each source before a lateness policy is set? Allowed-lateness windows are routinely set to a round number that nobody validated, and the p99 arrival delay of a mobile client, a batch-exported SaaS source, and a database CDC stream differ by orders of magnitude. Measure event time against processing time in production, then set the window.
- [ ] **[Critical]** Is there a defined behaviour for data arriving after the lateness window closes -- dropped, routed to a side output for reconciliation, or triggering a period restatement? Silently dropping late data is the default in most stream frameworks and it is the reason streaming totals and batch totals disagree.
- [ ] **[Recommended]** In stream processing, is watermark stalling on idle partitions accounted for? A watermark advances with the slowest partition, so a single quiet partition holds the whole job's watermark back and windows never close -- which presents as "the pipeline is running and producing nothing". Idle-source detection is a configuration item, not a default in every framework.
- [ ] **[Recommended]** In warehouse/batch transformation, is a **lookback window** applied on incremental loads rather than filtering on exactly the maximum previously loaded timestamp? An exact-max filter loses every row that arrives late and re-processes nothing on retry. Size the lookback from the measured arrival delay and reconcile the full period periodically (see `providers/dbt/transformation.md` on the microbatch `lookback` config).
- [ ] **[Optional]** Where both a streaming and a batch path exist over the same data, is there a scheduled reconciliation between them, and is one of them designated authoritative for reporting? Two paths that are never compared will differ, and the difference will be discovered by a consumer.

### Schema Drift

- [ ] **[Critical]** Is there an explicit policy for each class of source schema change -- additive columns (propagate automatically), column drops (fail loudly, never silently null), type widening (propagate), type narrowing or incompatible change (fail and require human decision), and column renames (indistinguishable from a drop plus an add, so they need a manual mapping)? Connectors default to different behaviours for each and the defaults are rarely what a governed pipeline wants.
- [ ] **[Critical]** Is drift detected by **reconciling column sets against the source**, rather than by trusting the connector to report it? SQL Server capture instances silently ignore columns added after enablement, and query-based extraction with `SELECT *` silently adds them; both are silent divergences in opposite directions. A scheduled comparison of source information-schema against landing-table shape is cheap and catches both.
- [ ] **[Recommended]** Where a schema registry is in use, is the compatibility mode set deliberately and understood by producers? Backward compatibility (the default in common registry implementations) permits deleting fields and adding optional ones -- which is *not* the same guarantee as "consumers will not break", since a consumer reading a deleted field breaks regardless. Choose the mode from the actual consumer contract.
- [ ] **[Recommended]** Are schema change events captured and retained as a first-class stream? Debezium publishes DDL changes to a dedicated schema-change topic and maintains a schema history so that old events can be interpreted with the schema in force when they were written -- a property that matters enormously when replaying a month-old log through a table that has since been altered.
- [ ] **[Optional]** Are data contracts asserted at the ingestion boundary (expected columns, types, nullability, key uniqueness) so that drift fails at the edge rather than in a downstream model three layers away? See `general/data-analytics.md` on data contracts.

### Backfill and Replay

- [ ] **[Critical]** Is the raw landing layer immutable, append-only, and partitioned such that any window can be reprocessed independently? Replayability is what turns a transformation bug from a data-loss incident into a rerun. A landing layer that is overwritten in place has no replay story.
- [ ] **[Critical]** Has the replay horizon been calculated as the **minimum** of source log retention and landing-zone retention, and is that number known to the people who set recovery objectives? The pipeline can only be rebuilt as far back as the shorter of the two, and this is usually a much smaller number than anyone assumes.
- [ ] **[Critical]** Are backfills idempotent and convergent -- rerunning any window produces the same result as the first run and does not duplicate rows? This follows from the MERGE-with-version-guard design above, and it is worth testing explicitly by running a window twice in a non-production environment and comparing counts.
- [ ] **[Recommended]** Is log compaction understood *not* to be an archive? A compacted topic retains the latest value per key and deliberately discards intermediate history -- which is correct for a state cache and destructive for an audit record. If intermediate states matter, retain the uncompacted log or land every event.
- [ ] **[Recommended]** Is there a runbook for the specific case of "the connector was down longer than source log retention"? The answer is a re-snapshot, and the runbook should cover how to re-snapshot without a gap (incremental snapshot with streaming continuing), how long it takes on the largest table, and what the downstream models do in the meantime.
- [ ] **[Optional]** Are backfills into history-bearing models (Type 2 dimensions, snapshots) handled by a documented procedure rather than by rerunning the normal load? Replaying old changes through a snapshot process that stamps them with today's date corrupts the history it was built to protect.

### Managed Connectors and Build vs Buy

- [ ] **[Critical]** Is the build-versus-buy decision framed as **per-row connector cost against fully-loaded engineering cost including ongoing operation**, rather than against zero? The recurring cost of a self-built SaaS integration is not the initial development; it is pagination changes, OAuth token rotation, undocumented rate limits, silent schema changes, and the on-call rotation that covers forty of them. Buy for the long tail of SaaS APIs, where the catalogue *is* the product. Consider building only for a small number of high-volume databases where the log mechanics are well understood and consumption-based pricing scales badly. A hybrid -- bought connectors for SaaS, built or cloud-native CDC for the big databases -- is the common end state.
- [ ] **[Critical]** For consumption-priced connectors, has the **change-volume** profile of each source been examined rather than its size? Fivetran prices on monthly active rows (MAR): inserts, updates, and deletes to distinct rows in a calendar month, with unchanged rows on re-syncs and the initial historical load excluded. A modest table whose rows are touched by a `last_seen_at` update on every page view can therefore cost more than a table a hundred times its size that changes daily. The remedy is source-side (stop touching the row, or exclude the column from capture where the connector supports it), not connector-side.
- [ ] **[Recommended]** Are connector tiers priced against the sync frequency actually required? Sync-interval floors are a common tier differentiator -- for example Fivetran's Standard tier documents 15-minute syncs with 1-minute syncs on Enterprise -- so a "we need near-real-time" requirement that nobody validated can move the whole contract up a tier.
- [ ] **[Recommended]** If Airbyte is selected, is the connector's maturity assessed individually rather than by the platform's reputation? The catalogue spans vendor-maintained and community connectors of varying quality; pin connector versions, test schema handling explicitly, and know which of your connectors are community-maintained. Commercially, self-managed deployment is free, with Cloud priced by volume on the lower tiers and by dedicated capacity ("Data Workers") on the top tier -- which changes the shape of the cost curve for spiky workloads.
- [ ] **[Recommended]** If Matillion is selected, is the overlap with the transformation layer resolved rather than duplicated? Matillion covers ingestion *and* pushdown ELT that generates warehouse SQL, so it competes with, rather than complements, a SQL transformation framework. Running both without a boundary produces business logic in two places, which is the expensive failure mode. Note also that the product naming has moved: the cloud product previously documented as Data Productivity Cloud is now branded Maia with its own documentation site, while the earlier self-hosted Matillion ETL retains separate docs -- confirm which product a quoted price or feature actually refers to.
- [ ] **[Recommended]** If Apache NiFi is selected, is it being chosen for the properties it is genuinely strong at -- on-premises and edge collection, heterogeneous protocol handling, backpressure between processors, and its **data provenance** repository, which records the lineage of individual flowfiles and is unusually good evidence for audit? It is not an ELT modelling tool and it carries real operational weight (a cluster to run, flows that are configuration rather than reviewable code unless deliberately managed as such).
- [ ] **[Optional]** Have cloud-native replication services been evaluated where the source and target are already in one cloud? They typically undercut third-party connectors on database CDC and have far narrower SaaS catalogues -- which is exactly the split the hybrid strategy above exploits.

### Reverse ETL and Activation

- [ ] **[Critical]** Is field-level ownership defined before any warehouse-to-operational-system sync is built -- which system is authoritative for each field? Without it, two systems overwrite each other on every cycle and the loop is discovered by a sales team watching a field change twice a day.
- [ ] **[Critical]** Is reverse ETL treated as a **data egress path with the same classification and access controls as any other export**? It is the mechanism by which derived, joined, and often sensitive warehouse attributes leave the governed estate for a CRM or an advertising platform, and it is routinely built by an analytics team without the review an equivalent extract would receive.
- [ ] **[Recommended]** Are syncs driven by field-level change detection rather than full-record rewrites? Destination APIs are rate-limited and often metered; rewriting unchanged records burns quota, generates spurious modification events in the destination, and triggers downstream automations that fire on "record updated".
- [ ] **[Recommended]** Are upserts keyed on a stable external identifier stored in the warehouse, with a documented behaviour for records that do not match (create, skip, or error)? Matching on email or name is the standard route to duplicate contact records.
- [ ] **[Optional]** Is there a kill switch and a dry-run mode for activation syncs? The blast radius of a bad reverse ETL run is other people's operational systems, which is a different class of incident from a bad table in the warehouse.

### Operability and Audit Evidence

- [ ] **[Critical]** Is freshness measured **end to end** -- source commit time to availability in the target -- rather than as connector uptime? A connector can be healthy, consuming, and thirty hours behind. The source event timestamp travels in the change event precisely so this can be computed.
- [ ] **[Critical]** Does monitoring distinguish "no changes" from "not advancing"? A stalled log position and a genuinely quiet source look identical on a throughput graph. Alert on the log position not advancing while the source's own log position does -- the two-sided check is the only reliable one, and it is the same signal that protects against the WAL and transaction-log growth risks above.
- [ ] **[Critical]** Where CDC output feeds regulated reporting, is **completeness** demonstrable rather than assumed? The practical evidence set is: continuity of log positions with no gaps, periodic full-table row-count and checksum reconciliation against the source, and proof that source log retention exceeded the maximum consumer outage over the period. If you cannot show that every committed change was captured, a reconstructed balance is an estimate, and it should be described as one.
- [ ] **[Recommended]** Are reconciliation counts run on a schedule against the source and their results retained? Reconciliation is worth as much as its history: a passing check today says little, a year of passing checks with the failures explained is evidence.
- [ ] **[Recommended]** Are connector credentials, replication users, and their privileges reviewed as part of normal access review? Replication privileges are broad by nature and are frequently granted once during a project and never revisited.
- [ ] **[Optional]** Is connector configuration held in version control and deployed as code rather than configured in a UI? The UI-configured pipeline is unreviewable, unreproducible across environments, and undiffable after an incident.

## Why This Matters

Ingestion defects are the hardest class of data defect to detect because they are usually absences. A transformation bug produces a wrong number that somebody eventually notices; a query-based extraction that never saw a delete produces a plausible number that is quietly too high, forever, and reconciles against nothing because the source of truth was never compared. The choice of capture method is therefore not an implementation detail delegated to whoever configures the connector -- it determines the outer bound of what the analytical estate can ever know, and it is chosen once.

The engine-level operational risks are severe and structurally similar across products, which is the useful thing to know about them. A PostgreSQL replication slot with a stalled consumer pins WAL until the volume fills and the database stops accepting writes. A SQL Server database with CDC enabled will not advance its log truncation point while the capture job is down -- under SIMPLE recovery, where operators specifically do not expect log growth. In both cases a pipeline component that is *merely down* escalates into a source-system outage, and in both cases the monitoring that would catch it (slot lag in bytes, capture-job health) is not part of the default connector dashboard. Teams learn this once per organisation.

Cost surprises in this layer come from change volume rather than data volume, and the two are uncorrelated. Consumption pricing based on monthly active rows means an application pattern that touches a row on every request -- a session heartbeat, a last-seen timestamp, an access counter -- can dominate the bill from a table nobody considers large. This is discoverable in advance by profiling update rates per table before signing, and it is discovered otherwise in month two.

The auditability consequences are technically real and are usually raised late. Point-in-time reconstruction downstream depends on capture completeness upstream: a Type 2 dimension can only record the versions it was told about, so if the capture mechanism cannot see intermediate states, the history is a sample and every reconstruction built on it is an approximation. Whether that is acceptable is a business judgement, but it has to be made with the limitation stated, and the limitation originates here -- in the choice between log-based and query-based capture, and in whether the source log retained enough history to prove nothing was missed.

## Common Decisions (ADR Triggers)

### ADR: Change Data Capture Method

**Context:** A source database must feed the analytical platform continuously.

**Options:** Log-based (complete, low source load, high privilege and operational care) vs query-based high-watermark (trivially portable, misses deletes and intermediate states, risks the long-transaction skip) vs trigger-based (complete and transactionally consistent, costs OLTP write latency and DDL rights) vs full periodic reload (simple, correct, only viable at small volume).

**Decision drivers:** Whether deletes and intermediate states are analytically required; the source owner's willingness to grant replication privileges; the source's tolerance for write amplification; and whether the downstream model claims to reconstruct history (which effectively rules out query-based).

### ADR: Self-Hosted CDC vs Managed Connector Platform

**Context:** The organisation must move data from a mix of databases and SaaS applications.

**Options:** Self-hosted open-source CDC (Debezium on Kafka Connect, Debezium Server, or embedded) vs a managed connector platform priced per row or per capacity vs cloud-native replication services vs a hybrid.

**Decision drivers:** The ratio of database sources to SaaS sources (SaaS long tails favour buying decisively); measured change volume per table against consumption pricing; team capacity for Kafka Connect operations; data residency and whether the connector platform may see the data at all; and the licence cost of the source engine's mining adapter, which for Oracle can dominate the entire decision.

### ADR: Delivery Semantics and Sink Design

**Context:** Change events must be applied to the target without loss or duplication.

**Options:** At-least-once with idempotent MERGE and a log-position version guard (robust, simple, the default recommendation) vs transactional exactly-once where the stack genuinely supports it (stronger, lower throughput, more coupling) vs append-only landing with deduplication deferred to the transformation layer (simplest ingestion, moves the problem downstream where it is cheap to fix and easy to forget).

**Decision drivers:** Sink capabilities, throughput requirements, whether the raw landing layer is intended to be an audit record (which favours append-only), and the team's appetite for operating transactional coordination.

### ADR: Snapshot Strategy for Large Tables

**Context:** A multi-terabyte table must be brought into the platform without an unacceptable source outage.

**Options:** Locking consistent snapshot (simplest, blocks writes) vs snapshot-at-recorded-position with idempotent overlap replay (no lock, needs idempotent sink) vs chunked incremental snapshot concurrent with streaming (no lock, resumable, on-demand, most moving parts) vs backfill from an existing backup or replica (offloads the primary entirely, adds a consistency-point problem).

**Decision drivers:** Table size, the source's write-blocking tolerance, whether the sink is idempotent, and whether tables will need to be added to the pipeline later -- which strongly favours the incremental-snapshot mechanism being in place from the start.

### ADR: Lateness Policy per Source

**Context:** Events arrive out of order and some arrive after their period has been reported.

**Options:** Drop after a fixed window (simple, silently loses data) vs route late data to a reconciliation side output (preserves it, requires a consumer) vs restate the affected period (correct, requires downstream restatement semantics) vs an as-of model where late data lands in the current period (auditable, does not match naive expectations of period totals).

**Decision drivers:** Measured arrival-delay distribution, whether periods are ever reported externally (which makes silent restatement unacceptable), and whether the downstream model is bi-temporal -- see `general/data-modelling.md`.

### ADR: Deletes in the Landing Layer

**Context:** The source emits hard deletes and the landing layer must represent them.

**Options:** Soft delete with flag and timestamp (preserves history, simplest downstream) vs physical delete (matches the source exactly, destroys reproducibility) vs both (soft in landing, physical in a downstream serving layer where erasure applies).

**Decision drivers:** Erasure obligations, whether historical reproducibility is required, and whether downstream models distinguish "deleted" from "never existed" -- they must, and they cannot if the row is simply gone.

## Reference Architectures

- **Log-based CDC into an immutable landing layer** -- source database → log reader (Debezium via Kafka Connect, Debezium Server, or a managed equivalent) → durable log or object-storage landing, append-only and partitioned by arrival date → idempotent MERGE into current-state tables → transformation layer. The landing layer is the replay boundary and the audit record; everything downstream of it is rebuildable.
- **Bought SaaS, built database** -- managed connectors for the long tail of SaaS APIs (where the catalogue is the value and change volume is small), self-hosted or cloud-native CDC for the handful of large operational databases (where consumption pricing scales badly and log mechanics are well understood). The most common economically rational end state, and the one that needs a single consistent landing convention so the two halves do not diverge.
- **Snapshot-only for constrained sources** -- where no log access is obtainable, a scheduled full or key-range extract landed as a dated, immutable snapshot, with history derived downstream by comparison. Correctness is bounded by the snapshot interval and deletes are detectable only by key-set difference; both limitations must be documented wherever the derived history is consumed.
- **Streaming with a reconciling batch path** -- a low-latency stream for operational dashboards plus a periodic batch reconciliation over the same landing data that is designated authoritative for reporting. The reconciliation is what stops the two paths silently disagreeing, and one of them must be named as the number of record.
- **Warehouse-to-operations activation loop** -- transformation layer → activation models (explicitly modelled, with external ids and field ownership declared) → reverse ETL tool → operational systems, with sync results landed back into the warehouse so that delivery is itself observable data.

## Reference Links

- [Debezium documentation](https://debezium.io/documentation/reference/stable/index.html) -- the reference implementation for open-source log-based CDC across engines
- [Debezium PostgreSQL connector](https://debezium.io/documentation/reference/stable/connectors/postgresql.html) -- logical decoding plugins, replica identity, TOAST placeholder behaviour, and WAL disk-space consumption
- [Debezium MySQL connector](https://debezium.io/documentation/reference/stable/connectors/mysql.html) -- binlog configuration, GTIDs, managed-instance snapshot locking, and the schema history topic
- [Debezium SQL Server connector](https://debezium.io/documentation/reference/stable/connectors/sqlserver.html) -- capture instance handling and schema change events
- [Debezium Oracle connector](https://debezium.io/documentation/reference/stable/connectors/oracle.html) -- LogMiner, OpenLogReplicator, and XStream adapter modes and their prerequisites
- [Debezium incremental snapshots](https://debezium.io/blog/2021/10/07/incremental-snapshots/) -- chunked, resumable, concurrent snapshotting and the watermarking mechanism
- [Debezium signalling](https://debezium.io/documentation/reference/stable/configuration/signalling.html) -- triggering ad hoc and incremental snapshots without restarting a connector
- [Debezium Server](https://debezium.io/documentation/reference/stable/operations/debezium-server.html) and [Debezium Engine](https://debezium.io/documentation/reference/stable/development/engine.html) -- running CDC without a full Kafka Connect cluster
- [DBLog: A Watermark Based Change-Data-Capture Framework (arXiv)](https://arxiv.org/abs/2010.12597) -- the Netflix paper behind concurrent snapshot-and-stream watermarking
- [PostgreSQL: Logical Replication](https://www.postgresql.org/docs/current/logical-replication.html) and [Logical Decoding](https://www.postgresql.org/docs/current/logicaldecoding-explanation.html) -- the server-side mechanism underneath every PostgreSQL CDC tool
- [PostgreSQL: pg_replication_slots](https://www.postgresql.org/docs/current/view-pg-replication-slots.html) -- `restart_lsn` and `confirmed_flush_lsn`, the columns to monitor for WAL retention risk
- [SQL Server: What is change data capture?](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server) -- capture and cleanup job defaults, validity intervals, and log truncation behaviour
- [SQL Server: Enable and disable change data capture](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/enable-and-disable-change-data-capture-sql-server) -- enablement, capture instances, and permissions
- [SQL Server: Track data changes](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/track-data-changes-sql-server) -- change data capture compared with change tracking
- [MySQL: Binary logging options and variables](https://dev.mysql.com/doc/refman/8.4/en/replication-options-binary-log.html) -- `binlog_format`, `binlog_row_image`, and `binlog_expire_logs_seconds` defaults
- [Oracle LogMiner utility](https://docs.oracle.com/en/database/oracle/oracle-database/19/sutil/oracle-logminer-utility.html) -- redo log mining prerequisites and supplemental logging
- [MongoDB change streams](https://www.mongodb.com/docs/manual/changestreams/) -- resume tokens and oplog window constraints
- [Apache Kafka Connect](https://kafka.apache.org/documentation/#connect) -- the connector runtime most open-source CDC deployments use
- [Confluent Schema Registry: schema evolution and compatibility](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html) -- compatibility modes and what each actually guarantees
- [Fivetran pricing](https://www.fivetran.com/pricing) -- monthly active rows definition, tier sync frequencies, and what is excluded from MAR
- [Airbyte pricing](https://airbyte.com/pricing) and [Airbyte documentation](https://docs.airbyte.com/) -- self-managed versus Cloud editions, volume and capacity pricing
- [Matillion](https://www.matillion.com/), [Maia documentation](https://docs.maia.ai/) (the current cloud product, formerly Data Productivity Cloud), and [Matillion ETL documentation](https://docs.matillion.com/metl/) (the earlier self-hosted product) -- pushdown ELT and ingestion
- [Apache NiFi](https://nifi.apache.org/) and [NiFi documentation](https://nifi.apache.org/documentation/) -- flow-based collection, backpressure, and the data provenance repository
- [AWS DMS: change data capture tasks](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Task.CDC.html) -- cloud-native database replication with CDC
- [Google Cloud Datastream overview](https://docs.cloud.google.com/datastream/docs/overview) -- serverless CDC for supported source engines
- [Azure Data Factory connector overview](https://learn.microsoft.com/en-us/azure/data-factory/connector-overview) -- the connector catalogue for Azure-native ingestion
- [Apache Flink: event time and watermarks](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/time/) -- watermark semantics, allowed lateness, and idle-source handling
- [Spark Structured Streaming programming guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html) -- `withWatermark`, output modes, and late-data handling
- [Hightouch documentation](https://hightouch.com/docs) -- reverse ETL sync modes, matching, and change detection

## See Also

- `general/data-modelling.md` -- what the captured changes are modelled into, and why capture completeness bounds what history can be reconstructed
- `providers/dbt/transformation.md` -- the transformation layer downstream of landing, including incremental lookback and snapshot-based history
- `patterns/data-pipeline.md` -- pipeline architecture, orchestration choices, and sized cost benchmarks per cloud
- `general/data-analytics.md` -- ETL versus ELT, data contracts, data quality frameworks, and governance tooling
- `general/messaging-patterns.md` -- delivery semantics, ordering, and dead-letter patterns in the messaging layer
- `providers/confluent/kafka.md` -- Kafka as the transport for CDC events, including Connect, retention, and compaction
- `general/database-migration.md` -- one-off migration and cutover, which uses the same CDC mechanisms for a different purpose
- `general/data-migration-tools.md` -- bulk transfer and migration tooling
- `general/observability.md` -- monitoring pipeline lag, freshness, and the not-advancing signal
- `general/data-classification.md` -- classification driving what may be replicated and activated outward
