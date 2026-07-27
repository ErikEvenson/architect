# dbt Transformation Layer

## Scope

dbt as the SQL transformation layer in an ELT architecture. Covers the deployment models (dbt Core as the open-source runtime, the dbt platform as the commercial product, and the Rust-based Fusion engine), project structure and the `ref`/`source` DAG, the built-in materialisations (view, table, incremental, ephemeral, materialized view) and when each is appropriate, incremental models and the strategy choice (append, merge, delete+insert, insert_overwrite, microbatch) with its platform dependence, snapshots as the Type 2 slowly changing dimension mechanism and their inherent limits, data tests and unit tests, model contracts, versions, access modifiers and groups for cross-team governance, exposures, the MetricFlow-based Semantic Layer, CI patterns including state-based selection and deferral, warehouse cost behaviour, and -- explicitly -- the workloads for which dbt is the wrong tool.

For where dbt sits among ETL/ELT options and semantic layer alternatives see `general/data-analytics.md`. For the models dbt should be building see `general/data-modelling.md`. For getting data into the warehouse in the first place see `general/data-ingestion.md`. dbt does not extract or load; it requires an ingestion layer alongside it.

## Checklist

### Deployment Model and Versioning

- [ ] **[Critical]** Is the split between the open-source runtime and the commercial platform understood before the tooling decision is made? dbt Core is the Apache 2.0 runtime and is fully capable of building, testing, and documenting models from any orchestrator. The dbt platform (formerly dbt Cloud) adds hosted scheduling, a development environment, the Semantic Layer, cross-project references, and role-based access. Several capabilities teams assume are "dbt" are platform-only -- the Semantic Layer is documented as requiring a paid platform tier -- and discovering that after the model layer is built is an unpleasant re-plan.
- [ ] **[Critical]** Is the project's engine and release strategy explicit? dbt Labs has shipped a new execution engine, **Fusion**, written in Rust, which the documentation now describes as the default experience on install and which builds on the Apache 2.0 runtime released as dbt Core 2.0. Platform projects consume this through **release tracks** (Fusion Nightly / Stable / Extended / Fallback, and the older dbt Core tracks) rather than by pinning a discrete minor version. This area has moved quickly; verify current naming, track availability, and adapter support against the documentation at the time of the decision rather than relying on any summary, including this one.
- [ ] **[Recommended]** Has the vendor-consolidation position been considered in the tooling ADR? Fivetran and dbt Labs have merged, which puts the ingestion connector platform and the transformation framework under one commercial roof. The open-source runtime remains Apache 2.0 and adapters remain community and vendor maintained, but a procurement or concentration-risk review will reasonably ask about it, and the answer should be prepared rather than improvised.
- [ ] **[Recommended]** Is the adapter for the target platform first-party or community maintained, and is its support for the features the design depends on verified? Incremental strategy availability, `materialized_view` support, microbatch support, and contract enforcement all vary by adapter. Design decisions that assume a strategy the adapter does not implement fail at the first build, which is the good case; the bad case is an adapter that silently falls back.
- [ ] **[Optional]** Is dbt Core in CI pinned to a specific runtime version even where the platform uses release tracks, so that a scheduled upstream change cannot alter a pull-request result?

### Project Structure and the DAG

- [ ] **[Critical]** Does every model reference upstream models with `ref()` and raw tables with `source()`, with **no hardcoded schema-qualified table names anywhere**? This is not a style preference: `ref` and `source` are what construct the DAG, and the DAG is what gives dbt execution order, lineage, environment swapping, state-based selection, and impact analysis. A single hardcoded reference removes that edge from the graph, and the model will then build in the wrong order intermittently -- which presents as a flaky pipeline rather than as a wiring error.
- [ ] **[Critical]** Are sources declared with `freshness` thresholds and checked on a schedule? `dbt source freshness` gives a staleness alarm that is independent of the ingestion tool's own monitoring, which matters precisely when the ingestion tool believes it is healthy. It is the cheapest cross-check available between the two layers.
- [ ] **[Critical]** Is there a layered structure with one model per source table at the staging layer -- renaming, casting, and light cleaning only -- and business logic confined to later layers? The value is that the same source table is interpreted once. Without a staging convention, three downstream models each apply their own casting and null handling to the same column and diverge slowly.
- [ ] **[Recommended]** Are model, column, and test definitions in YAML kept alongside the SQL rather than centralised into a small number of large files? Reviewability in a pull request is the whole point; a single 4,000-line schema file is where documentation goes to stop being updated.
- [ ] **[Recommended]** Are naming conventions enforced (staging / intermediate / marts prefixes, and a consistent grain suffix such as `fct_` and `dim_`)? Naming is how a new joiner infers grain without reading the SQL, and it is what makes selectors like `--select marts.*` meaningful.
- [ ] **[Optional]** Are macros used for genuinely repeated logic rather than for abstraction its author enjoys? Heavy Jinja abstraction makes the compiled SQL unreadable at exactly the moment somebody is debugging a wrong number, which is the moment readability matters most.

### Materialisations

- [ ] **[Critical]** Does each model use the simplest materialisation that meets its requirement -- **view** by default, **table** when query cost or downstream fan-out justifies persisting it, **incremental** only when full rebuild time is genuinely a problem? Incremental models are where the correctness bugs live; adopting them pre-emptively buys a class of defect in exchange for run time nobody was waiting on.
- [ ] **[Critical]** Are **ephemeral** models used sparingly and with their limitations understood? Ephemeral models are inlined as CTEs into their consumers: they cannot be selected from directly, do not exist in the warehouse for debugging, are not supported by model contracts, and are duplicated into every downstream consumer's compiled SQL. They suit very light, single-consumer logic early in the DAG and nothing else.
- [ ] **[Recommended]** Where a **materialized view** materialisation is used, is it understood that refresh is delegated to the platform and that the platform's implementation varies (Snowflake, for instance, maps this concept to Dynamic Tables)? The benefit is that the warehouse manages incrementality; the cost is fewer configuration options and platform-specific refresh and cost behaviour that dbt does not abstract away.
- [ ] **[Recommended]** Are large `table` models that nothing consumes identified and removed? Every scheduled rebuild of an unconsumed table is pure warehouse spend, and these accumulate silently as dashboards are retired without their upstream models being retired with them. Exposures (below) are what make this detectable.
- [ ] **[Optional]** Are Python models used only where SQL genuinely cannot express the transformation? They are supported on a subset of adapters, are limited to `table` and `incremental` materialisations, and execute in the warehouse's Python runtime with its library and resource constraints -- so they are a targeted escape hatch, not a general-purpose alternative.

### Incremental Models

- [ ] **[Critical]** Is the incremental strategy chosen for the platform rather than copied from another project? The strategies are `append`, `merge`, `delete+insert`, `insert_overwrite`, and `microbatch`, and both availability *and the default* differ by adapter -- merge-capable warehouses typically default to `merge` while others default to `append`, so the strategy you get by saying nothing is not the same everywhere. Check the adapter's own documentation rather than assuming; a model that silently appends where the author assumed a merge accumulates duplicates from the first re-run. `merge` requires a genuinely unique `unique_key` -- a duplicate in the key silently produces a non-deterministic or failing merge. `insert_overwrite` replaces whole partitions and is natural on partition-oriented engines but destroys anything else in the partition, including late-arriving rows from an earlier load.
- [ ] **[Critical]** Does the `is_incremental()` filter include a **lookback**, rather than filtering on exactly the maximum timestamp already loaded? An exact-max predicate loses every row that arrives late and re-processes nothing on a retry. Size the lookback from measured source arrival delay (see `general/data-ingestion.md`) and reconcile the full period on a schedule.
- [ ] **[Critical]** Is `on_schema_change` set deliberately rather than left at its default? The options are `ignore`, `fail`, `append_new_columns`, and `sync_all_columns`. `ignore` means a new upstream column simply never appears in the incremental table, which is a silent divergence that survives until someone asks why a column is missing months later.
- [ ] **[Recommended]** Is `microbatch` evaluated for large time-series models? It is available from dbt Core v1.9 on the major adapters and turns time-partitioned incremental processing into configuration: `event_time`, `begin`, and `batch_size` are required, `lookback` (default 1) handles late arrivals, each batch is an independent idempotent unit, `dbt retry` reruns only the failed batches, and `--event-time-start` / `--event-time-end` make backfills first-class rather than bespoke. The caveats matter: upstream models need `event_time` configured or dbt cannot filter them and every batch full-scans them; all times are treated as UTC; and you do not use `is_incremental()` inside a microbatch model because each batch is a complete run of its own window.
- [ ] **[Recommended]** Is `full_refresh: false` set on models where a rebuild is unaffordable or would destroy information the source no longer holds? A `--full-refresh` issued against a model whose source has a shorter retention than the model's history deletes history that cannot be recovered. This configuration is a guardrail against a single mistyped flag.
- [ ] **[Recommended]** Where `merge` is used, are `merge_update_columns` or `merge_exclude_columns` applied so that immutable columns (created timestamps, first-touch attribution) are not overwritten on every update? Silently resetting a `created_at` to the latest load time is a common and hard-to-notice defect.
- [ ] **[Optional]** Is there a scheduled full rebuild (or a full-period reconciliation query) for critical incremental models, so that accumulated drift from partial failures and late data is detected rather than compounding indefinitely?

### Snapshots and History

- [ ] **[Critical]** Is it understood that a dbt snapshot is **batch-sampled history, not change data capture**? Snapshots implement Type 2 slowly changing dimensions by comparing the source's current state against the stored history at each run. Any change that occurs and is superseded between two runs is lost permanently. Where regulatory reconstruction requires every intermediate state, the history must originate from log-based CDC and dbt should model it, not manufacture it -- see `general/data-ingestion.md`.
- [ ] **[Critical]** Is the snapshot's target treated as **irreplaceable state**? Snapshots are the one dbt resource that cannot be rebuilt from source: the history exists only in the snapshot table. It must be backed up, must never be dropped or `--full-refresh`ed, and should sit in a schema whose permissions reflect that. A snapshot table lost in an environment rebuild is history lost outright.
- [ ] **[Critical]** Is `hard_deletes` configured where source rows can be deleted? Without it, a row deleted at source remains open-ended and current in the snapshot forever -- the history actively asserts something false. Setting `hard_deletes: new_record` (available from dbt Core 1.9) records the deletion as a new row and adds a `dbt_is_deleted` column. This is the audit-relevant default that is not the default.
- [ ] **[Recommended]** Is the `timestamp` strategy preferred over `check`? The timestamp strategy tracks a single `updated_at` column and is robust to columns being added or removed at source; the check strategy compares an enumerated `check_cols` list and needs maintenance whenever the source shape changes. Use `check` only when the source has no trustworthy modification timestamp -- and note that if the source's `updated_at` is unreliable, the snapshot inherits that unreliability silently.
- [ ] **[Recommended]** Are the snapshot metadata columns and their semantics documented for consumers -- `dbt_valid_from`, `dbt_valid_to` (NULL for the current record unless `dbt_valid_to_current` is configured to a sentinel such as `9999-12-31`), `dbt_scd_id`, `dbt_updated_at`, and `dbt_is_deleted`? Downstream point-in-time joins depend on the interval convention, and a consumer that assumes a closed-closed interval against a NULL-terminated one produces a gap at every version boundary.
- [ ] **[Recommended]** Do snapshots run against source data on their own reliable schedule, ahead of the models that depend on them, and are they monitored separately? A snapshot that silently stops running does not fail anything -- downstream models keep building against a history that has quietly stopped advancing.
- [ ] **[Optional]** Is the `unique_key` on each snapshot backed by an explicit uniqueness test on the source? A non-unique snapshot key matches the wrong rows and corrupts the history in a way that is very hard to unwind afterwards.

### Tests, Contracts, and Governance

- [ ] **[Critical]** Are `not_null` and `unique` tests applied to every model's primary key, and `relationships` tests applied to every foreign key? Most cloud analytical engines do not enforce primary or foreign key constraints even when they accept the declaration, so the `relationships` test is the *only* referential integrity the estate has. Its absence is how orphaned fact rows reach reports.
- [ ] **[Critical]** Is test severity used deliberately -- `error` for anything that must stop the build, `warn` for signals that need triage but should not block? A project where everything is an error trains the team to rerun with tests disabled, which is worse than having no tests. A project where everything is a warning has no tests.
- [ ] **[Recommended]** Is `store_failures` enabled for tests whose failures need investigation? Knowing that 412 rows failed a uniqueness test is not actionable; having the 412 rows in a table is.
- [ ] **[Recommended]** Are **unit tests** used for models with non-trivial logic, distinct from data tests? Data tests assert properties of the actual data; unit tests assert that given fixed input rows the model produces expected output rows, and they catch logic regressions in a pull request rather than after a load. Window functions, incremental filters, and business-rule CASE expressions are the natural targets.
- [ ] **[Recommended]** Are **model contracts** (`contract: {enforced: true}` with declared columns and data types) applied to models that other teams, projects, or BI tools consume? A contract turns a breaking shape change into a build failure in the producer's pull request instead of a broken dashboard in someone else's team. Combine with `versions` when a breaking change genuinely must ship, so consumers can migrate on their own schedule.
- [ ] **[Recommended]** Are `access` modifiers (private / protected / public) and `groups` used to make the intended consumption boundary explicit? Without them, every model is effectively public and every internal intermediate model becomes someone's dependency, at which point it can no longer be refactored.
- [ ] **[Recommended]** Are **exposures** declared for dashboards, reports, and applications that consume dbt models? They extend lineage past the warehouse boundary, make `--select +exposure:name` a real impact-analysis tool, and are what allows the "which models feed nothing" question to be answered. They are cheap and consistently under-used.
- [ ] **[Optional]** Are test packages (dbt-utils, dbt-expectations) used for the common assertions -- accepted ranges, expression checks, recency, cardinality -- rather than reimplemented as singular tests per project?

### Semantic Layer and Metric Definitions

- [ ] **[Recommended]** Has the question of where metric definitions live been settled deliberately -- in dbt models, in the dbt Semantic Layer, in the BI tool, or in a separate headless layer? Defining them in the BI tool means every additional tool redefines them; defining them in models means every metric is a materialised table; the Semantic Layer defines them once and serves them to multiple consumers.
- [ ] **[Recommended]** If the dbt Semantic Layer is chosen, is the commercial dependency accepted? It is powered by MetricFlow (itself Apache 2.0 licensed) but is documented as available on paid dbt platform tiers, so it is a platform commitment and not merely a modelling convention. Vendor-neutral alternatives exist and are discussed in `general/data-analytics.md`.
- [ ] **[Optional]** Are metric definitions reviewed by the people who own the business definition, not only by the people who write the SQL? The purpose of a semantic layer is to make a contested definition explicit and singular; that value is only realised if the contest happens during review.

### CI/CD and Environments

- [ ] **[Critical]** Does CI build only the models a pull request changed, plus their children, deferring everything unchanged to production? `dbt build --select state:modified+ --defer --state <production manifest>` is the standard pattern and it is the difference between a pull-request check measured in minutes and one measured in hours. It requires a stored production `manifest.json` artefact, which is the piece teams usually have to add.
- [ ] **[Critical]** Does each pull request and each developer build into an isolated schema rather than a shared development schema? Shared development schemas produce cross-contamination that presents as intermittent test failures and consumes far more time to diagnose than the isolation costs to set up.
- [ ] **[Critical]** Is production deployment orchestrated with an explicit dependency on the ingestion layer having completed, rather than on a clock? A transformation scheduled at 06:00 against a load that finished at 06:15 produces yesterday's numbers with today's timestamp, and does so silently. Either the orchestrator sequences them, or `source freshness` gates the run.
- [ ] **[Recommended]** Are dbt artefacts (`manifest.json`, `run_results.json`) retained per run? They are the basis of state-based selection, model timing analysis, and after-the-fact answers to "what actually ran and how long did it take" -- and they cannot be reconstructed later.
- [ ] **[Recommended]** Is the orchestration boundary explicit -- dbt for the transformation DAG, an external orchestrator (Airflow, Dagster, Prefect, or the platform's own scheduler) for anything crossing systems? dbt has no cross-system dependency handling and no general backfill state machine beyond microbatch; attempting to make it the enterprise scheduler is a recurring and expensive mistake.
- [ ] **[Optional]** Are generated docs and the DAG published somewhere consumers actually look? Documentation that requires running a CLI command to view has the readership that implies.

### Cost and Performance

- [ ] **[Critical]** Is warehouse spend attributed to dbt runs and reviewed? Every model run is warehouse compute, and the common runaways are consistent: large tables materialised hourly because the schedule was copied from a smaller model, `dbt build` over the entire project in CI, and full-project runs retained after state-based selection was introduced.
- [ ] **[Recommended]** Are expensive tests scoped rather than run over full history? A `unique` test on a billion-row table is a full-table aggregation on every run. Restricting the test to a recent window with a `where` config, or sampling, keeps the signal at a fraction of the cost.
- [ ] **[Recommended]** Is model timing reviewed from run artefacts to find the handful of models that dominate the run? The distribution is almost always extremely skewed, and two or three models typically account for most of the wall clock and most of the cost.
- [ ] **[Optional]** Is the target warehouse sized separately for dbt runs versus interactive BI, so that a heavy transformation run does not degrade dashboards and so that the two workloads' costs are separable?

### Where dbt Is the Wrong Tool

- [ ] **[Critical]** Is dbt being kept out of workloads it does not fit? It is a batch SQL transformation framework, and the recurring poor fits are: **streaming and sub-minute latency** (use stream processing); **ingestion** (dbt neither extracts nor loads, so an EL layer is mandatory alongside it); **complete change history** (snapshots sample state between runs and cannot see intermediate changes -- that must come from CDC); **ML feature pipelines** requiring point-in-time correct joins, feature versioning, and online serving (dbt can build offline features but is not a feature store); **row-by-row imperative logic** (Python models help on some adapters but run under warehouse runtime constraints); **very high-frequency micro-batches** (per-run overhead and warehouse concurrency costs dominate below a few minutes); **cross-system orchestration**; and **governance as a product** -- dbt provides tests, contracts, and lineage, not a catalogue, classification, retention, or access control.
- [ ] **[Recommended]** Where a poor fit is unavoidable in the short term, is it recorded as a known compromise with a review trigger, rather than absorbed as normal? "We run this model every two minutes" tends to become permanent load, and the eventual cost review has no record of why.

## Why This Matters

dbt's central contribution is not that it runs SQL -- every warehouse does that -- but that it makes a transformation layer into reviewable, testable, version-controlled software with a dependency graph. That is why the `ref` discipline is the load-bearing convention: everything else dbt provides (execution order, lineage, environment swapping, state-based CI, impact analysis) is derived from the graph, and every hardcoded table reference removes an edge from it. Projects that treat `ref` as a style preference lose the properties they adopted dbt to get, and they lose them silently -- the pipeline still runs, just occasionally in the wrong order.

Incremental models are where correctness goes wrong, and they are adopted earlier than they need to be. The failure modes are consistent across organisations: an exact-max timestamp filter that permanently drops late-arriving rows; `on_schema_change` left at a default that silently ignores new columns; a `merge` on a `unique_key` that is not actually unique; `insert_overwrite` replacing a partition and taking previously loaded late rows with it. All of these produce plausible tables. None of them fail. They are discovered by a reconciliation nobody had scheduled, typically months later, and the remediation is a rebuild of a table whose source no longer holds the history.

Snapshots deserve more caution than they usually receive because they hold state that exists nowhere else. Everything else in a dbt project is a pure function of sources and code, and can be rebuilt; a snapshot's history is accumulated observation and cannot. A dropped snapshot table in an environment rebuild, or a `--full-refresh` issued by muscle memory, destroys history permanently. The related and less obvious limit is that snapshots sample state at run time: two changes between runs record as one. Where the requirement is "we must be able to reconstruct what was true at any moment", a snapshot cannot satisfy it, and the gap has to be closed at the ingestion layer rather than papered over downstream -- see `general/data-ingestion.md` and `general/data-modelling.md`.

Because most warehouses accept key constraints without enforcing them, dbt's `relationships`, `unique`, and `not_null` tests are frequently the only referential integrity the analytical estate has. That reframes them from hygiene to control: they are the mechanism, and where they are absent there is no other. In a regulated context this is worth stating plainly in the control documentation, alongside model contracts (which convert a breaking schema change into a producer-side build failure) and exposures (which extend lineage from the source table to the named report a regulator asks about).

Finally, cost. dbt makes it very easy to add models and very hard to notice the ones nobody uses, because an unconsumed table is indistinguishable at run time from a critical one. Combined with schedules that get copied from model to model, this produces a spend profile that grows monotonically with project age and has no natural corrective. Exposures plus run-artefact timing analysis are the two cheap instruments that make the waste visible.

## Common Decisions (ADR Triggers)

### ADR: dbt Core vs the dbt Platform

**Context:** The team is adopting dbt and must decide how to run it.

**Options:** dbt Core executed by an existing orchestrator (no licence cost, uses orchestration already in place, no Semantic Layer, self-managed development environments and secrets) vs the dbt platform (hosted scheduling and IDE, Semantic Layer, cross-project references, governance features, per-seat and consumption cost) vs a hybrid where CI runs Core and production runs on the platform.

**Decision drivers:** Whether the Semantic Layer or cross-project references are required (both are platform features); existing orchestration maturity; number of developers; data residency and whether a hosted control plane is acceptable; and post-merger vendor concentration if the ingestion platform is from the same supplier.

### ADR: Incremental Strategy per Model

**Context:** A model's full rebuild time or cost has become unacceptable.

**Options:** `append` (fastest, no deduplication, correct only for immutable event streams) vs `merge` (handles updates, requires a truly unique key) vs `delete+insert` (equivalent outcome on engines without an efficient merge, two statements) vs `insert_overwrite` (partition replacement, very efficient on partitioned engines, destroys anything else in the partition) vs `microbatch` (declarative time windows, first-class backfill and retry, requires `event_time` on upstreams).

**Decision drivers:** Whether source rows are ever updated; whether the key is genuinely unique; the engine's partitioning model and merge efficiency; measured late-arrival behaviour; and whether backfills are frequent enough to justify microbatch's configuration overhead.

### ADR: History Mechanism -- dbt Snapshots vs Log-Based CDC

**Context:** A mutable source must be given history for Type 2 modelling.

**Options:** dbt snapshots (in-project, no additional infrastructure, resolution limited to the run interval, intermediate changes lost, and the snapshot table becomes irreplaceable state) vs log-based CDC landing every change (complete, supports reconstruction, requires source log access and ingestion infrastructure) vs source-side application history (complete and authoritative, requires application change nobody has scheduled).

**Decision drivers:** Whether reconstruction obligations require every intermediate state or only the state at reporting boundaries; whether log access is obtainable from the source owner; and how much history loss is tolerable if the snapshot table is lost or corrupted.

### ADR: Where Metric Definitions Live

**Context:** Business metrics must be defined once and consumed by several tools.

**Options:** dbt Semantic Layer / MetricFlow (definitions with the models, platform-tier dependency) vs materialised metric tables in dbt (no extra tooling, combinatorial explosion of aggregates, definitions still duplicated in filters) vs BI-tool semantic model (best integration with one tool, redefinition in every other) vs an independent headless semantic layer (tool-neutral, another system to operate).

**Decision drivers:** Number of distinct consuming tools, willingness to take a platform-tier dependency, and whether metric definitions are genuinely contested across teams -- which is the condition that makes a semantic layer worth its overhead.

### ADR: CI Strategy

**Context:** Pull-request feedback time is degrading as the project grows.

**Options:** Full builds on every pull request (simplest, cost and duration grow with project size) vs state-based selection with deferral (`state:modified+ --defer`, fast and cheap, requires production artefact management and correct base-manifest handling) vs sampled or limited-data CI environments (fastest, weakest signal, misses data-dependent failures).

**Decision drivers:** Project size, warehouse cost per CI run, tolerance for a pull request that passes CI and fails in production, and whether the team can operate manifest artefact storage reliably.

### ADR: Transformation Framework Selection

**Context:** The organisation needs a transformation layer and dbt is the assumed default.

**Options:** dbt (SQL-first, large ecosystem, strong testing and lineage, batch only) vs platform-native transformation tooling (fewer moving parts, tighter coupling, weaker portability) vs a general-purpose data processing framework (arbitrary logic, streaming capable, more engineering) vs a pushdown ELT tool that generates warehouse SQL (visual development, overlaps dbt directly -- pick one).

**Decision drivers:** Whether the workload is genuinely batch SQL; team skill distribution between analysts and engineers; portability requirements across warehouses; and whether an existing ingestion tool already includes transformation capability that would otherwise be duplicated.

## Reference Architectures

- **Layered ELT project** -- sources (declared with freshness) → staging (one view per source table; rename, cast, no business logic) → intermediate (joins, business rules, conformance; often ephemeral or table) → marts (dimensional models materialised as tables or incrementals) → exposures declaring the dashboards and applications downstream. Tests at every layer boundary, contracts on anything consumed outside the project.
- **CDC landing plus dbt modelling** -- log-based CDC lands an append-only change log; dbt models deduplicate to current state with a merge-style incremental keyed on primary key and log position, and build Type 2 dimensions from the change log directly rather than via snapshots. The strongest arrangement where reconstruction obligations exist, because the complete history lives in the landing layer and dbt remains a pure function of it.
- **Snapshot-based history where CDC is unavailable** -- dbt snapshots run on a fixed schedule against source tables, ahead of dependent models, in a separately permissioned and separately backed-up schema, with `hard_deletes` configured and the sampling limitation documented wherever the derived history is consumed.
- **Microbatch time-series pipeline** -- event-time-partitioned source models with `event_time` declared throughout the upstream chain, microbatch incrementals for the heavy aggregations, `dbt retry` for partial failures, and `--event-time-start` / `--event-time-end` as the standard backfill procedure rather than a bespoke script per incident.
- **Slim CI** -- production job publishes `manifest.json` to artefact storage on every successful run; pull-request job builds `state:modified+` with `--defer` against that manifest into a per-pull-request schema; the schema is dropped on merge. Full builds run on a schedule rather than per pull request.

## Reference Links

- [dbt documentation: About models](https://docs.getdbt.com/docs/build/models) -- models, `ref`, and the project DAG
- [dbt documentation: Sources](https://docs.getdbt.com/docs/build/sources) -- `source()` declarations and freshness checks
- [dbt documentation: Materializations](https://docs.getdbt.com/docs/build/materializations) -- view, table, incremental, ephemeral, and materialized view, with the trade-offs of each
- [dbt documentation: Incremental models](https://docs.getdbt.com/docs/build/incremental-models) -- `is_incremental()`, `unique_key`, and `on_schema_change`
- [dbt documentation: Incremental strategies](https://docs.getdbt.com/docs/build/incremental-strategy) -- append, merge, delete+insert, insert_overwrite, microbatch and the adapter support matrix
- [dbt documentation: Microbatch incremental strategy](https://docs.getdbt.com/docs/build/incremental-microbatch) -- `event_time`, `begin`, `batch_size`, `lookback`, backfills, and the upstream `event_time` caveat
- [dbt documentation: Snapshots](https://docs.getdbt.com/docs/build/snapshots) -- Type 2 SCD implementation, timestamp and check strategies, metadata columns, and `hard_deletes`
- [dbt documentation: Data tests](https://docs.getdbt.com/docs/build/data-tests) -- generic and singular tests, severity, and `store_failures`
- [dbt documentation: Unit tests](https://docs.getdbt.com/docs/build/unit-tests) -- fixture-based logic testing distinct from data assertions
- [dbt documentation: Model contracts](https://docs.getdbt.com/docs/mesh/govern/model-contracts) -- enforced column lists and types at the producer boundary
- [dbt documentation: Model versions](https://docs.getdbt.com/docs/mesh/govern/model-versions) and [model access](https://docs.getdbt.com/docs/mesh/govern/model-access) -- migrating consumers through breaking changes, and private/protected/public boundaries
- [dbt documentation: Exposures](https://docs.getdbt.com/docs/build/exposures) -- extending lineage to dashboards and applications
- [dbt documentation: About MetricFlow](https://docs.getdbt.com/docs/build/about-metricflow) -- semantic models, dimensions, and metric definitions
- [dbt documentation: dbt Semantic Layer](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl) -- architecture, consumption APIs, and the platform tiers required
- [dbt documentation: About the dbt Fusion engine](https://docs.getdbt.com/docs/fusion/about-fusion) -- the Rust engine, its relationship to dbt Core 2.0, and installation posture
- [dbt documentation: Release tracks](https://docs.getdbt.com/docs/dbt-versions/dbt-release-tracks) -- Fusion and Core tracks, cadences, and plan availability
- [dbt documentation: Install dbt](https://docs.getdbt.com/docs/local/install-dbt) -- local installation paths and version selection
- [dbt documentation: Node selection syntax](https://docs.getdbt.com/reference/node-selection/syntax) and [defer](https://docs.getdbt.com/reference/node-selection/defer) -- `state:modified+`, deferral, and slim CI mechanics
- [dbt documentation: Continuous integration](https://docs.getdbt.com/docs/deploy/continuous-integration) -- CI job configuration and per-pull-request schemas
- [dbt documentation: Python models](https://docs.getdbt.com/docs/build/python-models) -- adapter support and materialisation limits
- [dbt best practice guides: how we structure our projects](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview) -- staging / intermediate / marts layering conventions
- [dbt best practice workflows](https://docs.getdbt.com/best-practices/best-practice-workflows) -- naming, testing, and project hygiene
- [dbt-core on GitHub](https://github.com/dbt-labs/dbt-core) -- the Apache 2.0 runtime, issues, and release history
- [MetricFlow on GitHub](https://github.com/dbt-labs/metricflow) -- the semantic layer engine and its licence
- [dbt-utils package](https://github.com/dbt-labs/dbt-utils) and [dbt-expectations package](https://github.com/calogica/dbt-expectations) -- the standard generic-test and macro libraries

## See Also

- `general/data-modelling.md` -- the dimensional, vault, and history models dbt should be implementing, including SCD types and grain
- `general/data-ingestion.md` -- the EL layer dbt requires, and why capture method bounds what history dbt can model
- `general/data-analytics.md` -- ETL versus ELT positioning, semantic layer alternatives, and data quality tooling
- `patterns/data-pipeline.md` -- orchestration, scheduling, and pipeline cost benchmarks
- `general/ci-cd.md` -- general CI/CD practice that the dbt-specific patterns above sit inside
- `general/testing-strategy.md` -- testing strategy in the wider engineering sense
- `general/cost.md` -- warehouse cost management and FinOps practice for the compute dbt consumes
- `providers/databricks/data-platform.md` -- a common dbt target platform, including its incremental and merge behaviour
- `providers/snowflake/data-platform.md` -- a common dbt target platform, including dynamic tables and warehouse sizing for transformation workloads
- `general/governance.md` -- governance operating models that contracts, access modifiers, and exposures support but do not replace
