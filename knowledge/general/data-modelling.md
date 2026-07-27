# Data Modelling for Analytics

## Scope

How to model data for analytical consumption, independent of which platform stores it. Covers Kimball dimensional modelling (the four-step design process, fact table grain, transaction / periodic snapshot / accumulating snapshot fact types, factless fact tables, conformed dimensions and the bus matrix, degenerate / junk / role-playing / mini-dimensions, bridge tables for multi-valued dimensions), star versus snowflake, slowly changing dimensions Types 0 through 7 and when each is actually warranted, surrogate versus natural versus hash keys, Inmon's normalised Corporate Information Factory, Data Vault 2.0 (hubs, links, satellites, raw versus business vault, PIT and bridge structures) and the conditions under which its insert-only auditability earns its join cost, One Big Table and wide denormalised serving tables on columnar engines, bi-temporal history and point-in-time reconstruction, and the question of whether schema-on-read plus cheap compute makes modelling optional.

For platform selection (warehouse vs lake vs lakehouse) and governance tooling see `general/data-analytics.md`. For how data physically arrives see `general/data-ingestion.md`. For the transformation layer that builds these models see `providers/dbt/transformation.md`. For operational (OLTP) schema design and database engine selection see `general/data.md`.

## Checklist

### Grain and Fact Table Design

- [ ] **[Critical]** Has the grain of every fact table been declared in a single business sentence before any column was chosen -- "one row per order line per shipment", "one row per policy per month-end"? Grain is the most consequential decision in the entire model and the one that outlives every platform choice made around it. Kimball's four-step process is deliberately ordered: select the business process, **declare the grain**, identify the dimensions, identify the facts. Choosing dimensions before grain is the standard route to a table nobody can aggregate correctly.
- [ ] **[Critical]** Is the fact table built at the **atomic** grain of the business process rather than pre-aggregated to today's known reporting need? You can always roll up from atomic rows; you can never drill down from a summary. Pre-aggregating at design time silently deletes every question nobody thought to ask yet, and the rebuild cost when that question arrives is a full historical reload.
- [ ] **[Critical]** Does every measure in a fact table genuinely exist at the declared grain, with no header-level amounts stored on a line-level table? Mixed-grain fact tables are the most common cause of wrong numbers in production: a shipping charge held once per order but stored on every order line double-counts against any dimension that does not roll up to order header. Either allocate the header amount down to the line, or split it into a separate header-grain fact table -- never both on one row.
- [ ] **[Critical]** Is each measure classified as additive, semi-additive, or non-additive, and is that classification enforced in the semantic layer? Additive measures sum across all dimensions. **Semi-additive** measures (balances, inventory levels, headcount) sum across every dimension except time and must be averaged or point-selected over time -- this is what periodic snapshot fact tables exist for. **Non-additive** measures (ratios, percentages, unit prices) must never be stored as the ratio: store the numerator and denominator as separate additive facts and compute the ratio after aggregation. Averaging an average is the second most common wrong-number defect after grain errors.
- [ ] **[Critical]** Is the right fact table type chosen per business process -- **transaction** (one row per event, the default), **periodic snapshot** (one row per entity per regular interval, for balances and levels that have no natural event), or **accumulating snapshot** (one row per pipeline instance, updated in place as milestones complete)? Most processes need a transaction fact; a surprising number of "we have no events" problems are actually periodic snapshot problems.
- [ ] **[Recommended]** Where an accumulating snapshot is used, is the update-in-place cost understood on the target storage? Accumulating snapshots mutate existing rows as an order progresses through its milestones. On columnar and object-storage engines that means a merge-on-write per load rather than an append, with the corresponding file-rewrite cost. This is a real reason to keep accumulating snapshots narrow and to reserve them for pipelines whose milestone lag is the actual analytical question.
- [ ] **[Recommended]** Are **factless fact tables** used for events that have no numeric measure and for coverage questions? A student attending a class, a promotion offered, a policy in force -- these have dimensional context and no measure. Critically, "what did *not* happen" (products on promotion that sold nothing, customers eligible for an offer who never took it) is unanswerable from the transaction fact alone; it requires a factless coverage table to define the universe against which absence is measured.
- [ ] **[Recommended]** Are fact tables kept narrow (keys plus measures plus degenerate dimensions) rather than accumulating descriptive attributes? Attributes belong in dimensions where they can be conformed, versioned, and reused; copying them into the fact freezes them at load time and makes every attribute change a fact-table rewrite.
- [ ] **[Optional]** Are audit columns (load batch id, source system, load timestamp, ETL process version) present on every fact row? Cheap to add at build time, impossible to reconstruct retrospectively, and the first thing asked for when a number is disputed.

### Dimension Design

- [ ] **[Critical]** Are dimensions denormalised into flat, wide tables (star) rather than normalised into hierarchies (snowflake)? Snowflaking saves negligible storage on modern engines while adding joins, obscuring the model for BI users, and breaking the "one dimension, one table" mental model that makes self-service work. The defensible exceptions are narrow: a genuinely enormous and rarely used sub-hierarchy, and outriggers that share a conformed structure (a calendar attached to a date attribute inside another dimension).
- [ ] **[Critical]** Is there a physical **date dimension** rather than reliance on SQL date functions? Fiscal calendars, retail 4-5-4 periods, holidays, trading days, and "last business day of the quarter" are organisational facts, not arithmetic; no date function knows them. A date dimension is also the only place to put the designated row for unknown or not-yet dates.
- [ ] **[Critical]** Are foreign keys in fact tables never NULL, with designated dimension rows for "unknown", "not applicable", and "pending" instead? A NULL foreign key drops the fact row from any inner join, which means rows silently disappear from reports rather than showing up in an obvious bucket. Reserve fixed surrogate values (conventionally -1, -2, 0) for these members and load them before anything else.
- [ ] **[Critical]** Are **conformed dimensions** defined and owned centrally -- the same dimension, with the same keys and the same attribute meanings, shared across every fact table that needs it? Conformance is what makes drill-across possible: two fact tables can only be compared on a dimension they genuinely share. Two "customer" dimensions with different keys are not conformed, however similar their columns look, and any comparison across them is arithmetic on incompatible populations.
- [ ] **[Critical]** Is there an **enterprise data warehouse bus matrix** -- business processes as rows, conformed dimensions as columns -- maintained as the planning artefact for the model? It is the cheapest governance instrument in the whole discipline: it makes the sequencing of marts explicit, exposes which dimension a new mart is about to fork, and gives a one-page answer to "can we compare these two things".
- [ ] **[Recommended]** Are **degenerate dimensions** (order number, invoice number, ticket id) left as bare attributes on the fact table rather than given their own dimension table? A dimension table whose only column is the key it is joined on adds a join and nothing else.
- [ ] **[Recommended]** Are low-cardinality flags and indicators collapsed into a **junk dimension** containing only the combinations that actually occur, rather than added as a dozen individual foreign keys or free-floating columns? Build the junk dimension from observed combinations, not the Cartesian product -- the product of ten binary flags is 1,024 rows of which perhaps 30 exist.
- [ ] **[Recommended]** Are **role-playing dimensions** exposed through separate views or aliases per role (order date, ship date, due date all pointing at one physical date dimension) so that column names are unambiguous in BI tools? Joining the same physical table three times without aliasing produces three columns called `day_name` and a support ticket.
- [ ] **[Recommended]** Is a **mini-dimension** (Type 4) used where a subset of attributes changes far faster than the rest of the dimension? The diagnostic is simple: if a Type 2 dimension is growing rows faster than the fact table it decorates, the volatile attributes need splitting out into their own dimension referenced directly from the fact.
- [ ] **[Recommended]** Are multi-valued relationships (a patient with several diagnoses, an account with several holders) handled by a **bridge table** with an explicit weighting factor? The weighting factor is what preserves additivity; a bridge joined without it multiplies the measure by the number of members and produces confidently wrong totals. Decide and document whether reports use the weighted (allocated) or unweighted (impact) view -- both are legitimate and they do not reconcile.
- [ ] **[Recommended]** Is there a policy for **late-arriving dimension members** (an early-arriving fact whose dimension row does not exist yet)? The standard treatment is to insert an inferred member row keyed on the natural key with attributes marked unknown, point the fact at it, and update it in place when the real record arrives. Without this the choice is to reject the fact (losing it) or point it at the generic unknown member (never repairing it).
- [ ] **[Optional]** Are hierarchies that are ragged or variable-depth (organisational structures, chart of accounts, bill of materials) modelled explicitly -- a bridge/closure table or a path-enumeration column -- rather than as fixed level columns? Fixed levels break the first time an entity sits at the wrong depth, and the repair is a model change rather than a data change.

### Slowly Changing Dimensions and History

- [ ] **[Critical]** Is the SCD type chosen **per attribute**, not per dimension, and recorded in the model specification? Almost every real dimension is mixed: a customer's marketing segment is Type 2 (history matters for cohort analysis), their misspelled surname is Type 1 (a correction, not a change), and their original acquisition channel is Type 0 (it never changes by definition). A column-level SCD register is also what an auditor asks for when they want to know how history is retained.

  | Type | Kimball name | What it does | When it is warranted |
  |---|---|---|---|
  | 0 | Retain original | Value is fixed at first load and never updated | Original terms: opening credit score, acquisition channel, original policy inception. Under-used and free. |
  | 1 | Overwrite | New value replaces old; no history | Genuine corrections of data-entry errors, and attributes nobody reports on historically. Note it silently changes every historical report that used the attribute. |
  | 2 | Add new row | New surrogate key per version with effective/expiry dates and a current flag | The default where history matters. Basis for "what did we believe on date X". Costs row growth and requires facts to join the version valid at event time. |
  | 3 | Add new attribute | A "previous value" column alongside the current one | Fixed, small number of prior values -- typically an announced reorganisation where both the old and new hierarchy must be reportable side by side. Does not generalise past one or two changes. |
  | 4 | Add mini-dimension | Volatile attributes split into their own dimension referenced from the fact | Rapidly changing attributes on a large dimension where Type 2 row growth is unacceptable. |
  | 5 | Add mini-dimension and Type 1 outrigger | Type 4, plus a Type 1 pointer from the base dimension to the *current* mini-dimension row | When you need both the as-at-event profile (via the fact) and the current profile (via the base dimension) without a second join path through the fact. |
  | 6 | Add Type 1 attributes to Type 2 dimension | Type 2 rows that also carry "current value" columns updated on every version | When the same attribute must be reportable both as-was and as-is from a single row -- e.g. sales by the territory in force at the time *and* by today's territory. |
  | 7 | Dual Type 1 and Type 2 dimensions | Fact carries both the durable natural key and the version surrogate key; the dimension is presented twice | Same goal as Type 6 with the two perspectives kept as separate presentation objects rather than extra columns. Cleaner for BI tools, one more join. |

- [ ] **[Critical]** Do facts join to Type 2 dimensions on the **surrogate key that was current when the event occurred**, resolved at load time -- not on the natural key at query time? Joining on the natural key against a Type 2 dimension fans the fact row out across every version of the entity and inflates every measure. This is the single most common defect in a Type 2 implementation and it is invisible until someone reconciles a total.
- [ ] **[Critical]** Where the requirement is to reproduce a historical report exactly, has **bi-temporal** history been considered rather than valid-time only? Type 2 records *when the fact was true in the world* (valid time). Reproducing "what the report said on 31 March" also needs *when the warehouse learned it* (transaction/system time), because a late-arriving correction backdated into a Type 2 range rewrites history that was already reported. Deciding restate-versus-as-of after the fact is a full historical reload; deciding it up front is two extra columns.
- [ ] **[Recommended]** Are Type 2 effective and expiry timestamps stored on a closed-open interval (`valid_from <= t < valid_to`) with an explicit end-of-time sentinel or NULL convention, applied consistently? Mixed closed-closed and closed-open conventions across dimensions produce single-row gaps and duplicates at midnight boundaries that nobody finds until a month-end total is off by a rounding error.
- [ ] **[Recommended]** Are hard deletes at the source represented in the dimension rather than left as "still current"? A row that vanishes from the source and is never expired asserts, forever, that the entity is live. Decide whether a source delete closes the Type 2 interval, sets a deleted flag, or is ignored -- and confirm the ingestion mechanism can actually detect deletes at all (see `general/data-ingestion.md`).
- [ ] **[Optional]** Is a durable "supernatural" key maintained on Type 2 dimensions -- a stable identifier that ties all versions of one entity together independently of the source system's key? It is what lets you count distinct entities across versions and survive a source system re-keying or a merger.

### Keys

- [ ] **[Critical]** Do dimensions use warehouse-generated **surrogate keys** as primary keys, with the source natural key retained as an ordinary attribute? Four independent reasons compel this: Type 2 needs multiple rows per natural key; source systems reuse, renumber, and recycle keys; integrating the same entity from several sources requires a key neither source owns; and narrow integer joins are materially cheaper than compound string joins.
- [ ] **[Critical]** Is referential integrity **tested** in the pipeline rather than assumed from declarations? Most cloud analytical engines either do not support primary and foreign key constraints or accept them without enforcing them, using them only as optimiser hints. A declared-not-enforced constraint that everyone believes is enforced is worse than none. Orphaned fact rows must be caught by an explicit test on every load.
- [ ] **[Recommended]** Are **hash keys** (a deterministic hash of the business key) used where loads must run in parallel and independently across many tables or systems, and sequence-generated integers used otherwise? Hashing lets a satellite be loaded without first looking up a parent's generated key, which is why Data Vault 2.0 adopted it; the costs are wider join columns, no ordering, and a collision argument you have to be willing to make in front of a risk committee. Pick the hash function deliberately and never change it.
- [ ] **[Recommended]** Are surrogate keys free of embedded meaning, with the date dimension as the single accepted exception? A `YYYYMMDD` integer date key is conventional because it makes partition pruning and readable debugging possible without a join, and because dates genuinely never change meaning. Every other "smart key" becomes a constraint the moment the encoded meaning does change.
- [ ] **[Optional]** Is there a documented policy for key collisions and re-keying events (source migration, entity merge, acquisition)? These arrive as projects, not incidents, and a model with no re-keying story handles them by rewriting history.

### Choosing a Modelling Approach

- [ ] **[Critical]** Has the modelling approach been chosen deliberately -- dimensional (Kimball), normalised enterprise warehouse (Inmon), Data Vault, or wide denormalised tables -- rather than inherited from whoever built the first mart? These are not interchangeable and the mismatch cost is a rebuild. The most common working answer in a modern estate is a layered one: an integration layer in whichever style the sources demand, and a **dimensional model at the consumption layer regardless**, because that is what BI tools and human analysts are built for.
- [ ] **[Critical]** If **Data Vault 2.0** is being proposed, does the estate actually exhibit the conditions that repay it? It repays: many source systems that disagree; frequent source schema change; a hard requirement to attribute every value to a source and a load time; parallel, independent, restartable loads at scale; and a genuine need to rebuild consumption models from an immutable, source-attributed record. It does not repay a single source system, a small team, and no audit obligation -- there it delivers three times the object count and five-to-eight joins per business question in exchange for auditability nobody asked for.
- [ ] **[Critical]** If Data Vault is adopted, is it understood that **it is not a consumption model**? Hubs (business keys), links (relationships, many-to-many by construction), and satellites (descriptive attributes, effective-dated and insert-only) are an integration and audit structure. Users never query the raw vault. Information marts -- normally star schemas -- are still built on top, so a Data Vault programme is a dimensional modelling programme *plus* a vault, not instead of one. Budgets that omit the mart layer are wrong by the cost of the mart layer.
- [ ] **[Recommended]** In a Data Vault, is every satellite row carrying record source and load timestamp, and is the vault genuinely insert-only? Those two columns plus the no-update rule are the entire audit proposition. A vault with in-place updates or without source attribution is a badly normalised warehouse with extra joins and no compensating benefit.
- [ ] **[Recommended]** Are query-assist structures (point-in-time tables and bridge tables) planned into a Data Vault from the start rather than added when queries become unusable? They exist because the join count is the known cost of the pattern -- a PIT table pre-resolves the satellite versions valid at a given instant so a query does not have to. Treating them as an afterthought is how vault programmes acquire their reputation.
- [ ] **[Recommended]** Where an Inmon-style normalised integration layer is used, is the boundary explicit -- 3NF for integration and conformance, dimensional marts for consumption, with no direct user access to 3NF? The failure mode is a normalised layer that users query directly, producing hand-written joins that reimplement business rules inconsistently in every report.
- [ ] **[Recommended]** Where **One Big Table** / wide denormalised tables are used, are they generated *from* a conformed dimensional model as a serving artefact rather than authored independently? Columnar storage and vectorised execution make wide tables genuinely fast: a published 2022 benchmark across three major cloud warehouses using TPC-DS-derived BI-style queries measured roughly 25-50% faster query times for a single denormalised table than the equivalent star schema. The performance case is real. The maintenance case is not: each independently authored OBT re-implements dimension logic, so conformance is lost; SCD semantics become implicit and undocumented; a single dimension attribute correction means rewriting every row of every OBT that embedded it; and "what did not happen" becomes unanswerable because the universe of possible combinations is no longer represented. Generate them, version them, and treat them as derived.
- [ ] **[Optional]** Has the interaction between the physical model and the consuming BI tool been checked before the model is fixed? Some engines and semantic layers materially prefer one shape (star with single-direction relationships, or a single wide table), and vendor guidance differs. This is a constraint to discover during design, not during user acceptance testing.

### Does Modelling Still Matter?

- [ ] **[Critical]** Has the "schema-on-read plus cheap compute makes modelling optional" argument been addressed explicitly rather than left to settle itself? What has genuinely changed is the **physical** side: snowflaking to save storage, aggressive pre-aggregation, index-heavy designs, and avoiding wide tables are mostly obsolete optimisations on columnar engines. What has not changed is the **logical** side, for reasons that are structural rather than nostalgic:
  - **Grain errors produce wrong numbers, not slow numbers.** No amount of compute fixes double-counting; a fast wrong answer is worse than a slow one because it is trusted.
  - **Modelling is mostly the act of agreeing what things mean.** Cheap compute does not decide whether "active customer" excludes trialists, or whether a cancelled-and-rebooked order is one order or two. Somebody decides that once in a model, or everybody decides it separately in their own query.
  - **Schema-on-read does not remove the schema, it relocates it** from one governed place into every consumer's SQL. That relocation is precisely where conflicting numbers come from.
  - **Conformance is semantic, not physical.** Two teams can each query the raw layer at speed and still disagree about revenue, because the disagreement is about the definition, not the scan.
  - **Cheap compute is not cheap rewrite.** An unmodelled raw layer of several hundred tables is a permanent onboarding tax on every new consumer and every new tool.
  - **Auditability requires declared grain and declared history semantics.** Schema-on-read over a mutable raw layer cannot answer "what did this report say on 31 March", because nothing in the arrangement records what was believed then.

### Governance, Audit, and Point-in-Time Reconstruction

- [ ] **[Critical]** For any reporting subject to audit or regulatory reconstruction, are the three prerequisites for point-in-time reconstruction all present -- (a) history retained on **every** attribute the report consumes, not just the ones that seemed interesting, (b) a load batch or system-time stamp on every fact row, and (c) a documented rule for how late-arriving corrections are treated (restate the prior period, or report as-of with the correction in the current period)? Missing any one of the three makes reconstruction an estimate. Retro-fitting them requires history that was not kept.
- [ ] **[Critical]** Is the conflict between right-to-erasure obligations and immutable history resolved deliberately, per attribute, before the model is built? Physical deletion of a dimension row breaks reproducibility of every historical report that used it; pseudonymising or nulling the identifying attributes while retaining the surrogate key, the grain, and the counts usually satisfies both obligations. Insert-only patterns (Data Vault satellites, Type 2 intervals) make this harder, not easier, which is a design input rather than a surprise.
- [ ] **[Recommended]** Is source attribution (record source, load timestamp) carried on every row even in a dimensional model? It is Data Vault's discipline and it is worth borrowing wholesale: it costs two columns and answers the "where did this number come from" question that otherwise consumes days.
- [ ] **[Recommended]** Is column-level lineage available from report field back to source column? Table-level lineage is enough for impact analysis on schedules; column-level is what makes a regulatory evidence request tractable and what tells you whether a source column change affects a reported figure or only a debugging field.
- [ ] **[Optional]** Are model definitions (grain statements, SCD type per column, conformance ownership) held in version control alongside the transformation code rather than in a separate document? A grain declared in a wiki and a grain implemented in SQL diverge; a grain declared in the repository next to the model that implements it is reviewable in the same pull request.

## Why This Matters

A badly grained fact table outlives every platform decision made around it. Warehouses get migrated, engines get swapped, storage formats get converted -- and the grain error travels with the data through all of it, because the migration is a faithful copy. Teams routinely spend a quarter moving from one platform to another and arrive with the same wrong numbers, having never revisited the model, because the model was never written down as something separable from the SQL that implemented it.

The specific failures are boringly repetitive across organisations. Header-level amounts on line-level fact tables inflate every total sliced by anything other than the header. Ratios stored as ratios get averaged and produce numbers that are not wrong in any single row and wrong in every aggregate. Type 2 dimensions joined on the natural key fan facts out across versions, quietly multiplying revenue by the number of times a customer changed address. NULL foreign keys drop rows from inner joins, so the report is not wrong, it is just missing -- which is much harder to detect than being wrong. None of these are exotic; all of them are still in production somewhere in most large estates.

Conformance failures are the expensive organisational version of the same problem. Two marts each define "customer" from a different source with a different key, both are individually defensible, and the first executive question that spans them is unanswerable. The cost is not the rework -- it is the eighteen months during which two teams produce two numbers and the business learns to trust neither. A bus matrix maintained from the start costs a few hours a quarter and is the only cheap defence.

Data Vault gets adopted for the wrong reason more often than any other pattern in this discipline. Its insert-only, source-attributed satellites genuinely solve a real problem: reconstructing what the organisation believed, from which system, at which time, across many disagreeing sources -- exactly the problem a regulated estate has. Adopted without that problem, it produces three times the object count, five-to-eight joins per business question, and a mart layer that still has to be built dimensionally anyway. The pattern is not the mistake; adopting it without the conditions that repay it is.

The auditability dimension is technically real and routinely under-specified. "What did we report on this date" is not answerable by querying current data, however good the platform. It requires history on every consumed attribute, a system-time stamp distinct from the business-event date, and a stated policy on restatement. Organisations discover this when the first reconstruction request arrives, at which point the required history does not exist and cannot be manufactured. The cost at design time is two columns and one written decision.

## Common Decisions (ADR Triggers)

### ADR: Modelling Approach for the Integration Layer

**Context:** Data from one or more source systems must be integrated before it can be modelled for consumption. The integration style sets the cost structure for the next several years.

| Criterion | Kimball dimensional | Inmon 3NF / CIF | Data Vault 2.0 | Wide denormalised (OBT) |
|---|---|---|---|---|
| Primary optimisation | Query and comprehension | Enterprise consistency | Auditability and load parallelism | Scan speed on columnar engines |
| Source count it suits | Few to moderate | Many, needing one enterprise semantic | Many, volatile, disagreeing | Any (it is a serving shape) |
| Handles source schema churn | Poorly -- model changes | Poorly -- model changes | Well -- add a satellite | Poorly -- rewrite the table |
| Object count | Lowest | Moderate | Highest (3x+) | Lowest |
| Joins per business question | 2-5 | 5-10 | 5-8 plus PIT/bridge assist | 0-1 |
| Auditability out of the box | Only via SCD discipline | Only via added history | Structural (insert-only, source-attributed) | None |
| Requires a separate consumption layer | No | Yes (dimensional marts) | Yes (information marts) | It *is* the consumption layer |
| Skills availability | Widest | Moderate | Narrowest, most specialist | Widest |

**Decision drivers:** Number and volatility of sources, audit and reconstruction obligations, team size and specialist availability, and whether the consumption layer is being budgeted separately (it must be, for Inmon and Data Vault).

### ADR: Fact Table Grain

**Context:** A new business process is being modelled and the grain must be declared.

**Options:** Atomic transaction grain (one row per lowest-level event) vs pre-aggregated grain (one row per day per product per store) vs periodic snapshot (one row per entity per period) vs accumulating snapshot (one row per pipeline instance, updated in place).

**Decision drivers:** Whether the process has discrete events at all; whether the measures are semi-additive balances (which forces a snapshot); volume at the atomic grain against the platform's economics; and the certainty that today's known reporting questions are the only ones ever asked (they are not). Default to atomic unless volume makes it genuinely infeasible, and record why if it does.

### ADR: SCD Type per Attribute

**Context:** A dimension contains attributes with different history requirements.

**Options:** Type 0 (retain original), 1 (overwrite), 2 (add row), 3 (add prior-value column), 4 (mini-dimension), 5 (4 plus Type 1 outrigger), 6 (Type 2 rows carrying current-value columns), 7 (dual current and historical presentations).

**Decision drivers:** Whether historical reports must remain reproducible after the value changes; whether the change is a correction or a genuine change (corrections are Type 1, changes are not); the volatility of the attribute against the size of the dimension (which forces Type 4/5); and whether users need to slice by both as-was and as-is values (which forces 6 or 7). Decide per column and record the decision -- a blanket "Type 2 everything" is as much a design failure as a blanket Type 1, because it grows dimensions for attributes nobody reports historically.

### ADR: Surrogate Key Generation Strategy

**Context:** Dimension primary keys must be generated.

**Options:** Monotonic sequence integers (compact, ordered, requires a central generator and a lookup at fact load) vs deterministic hash of the business key (parallel and independent loads, no lookup, wider joins, collision argument required) vs natural keys directly (simplest, breaks under Type 2, source re-keying, and multi-source integration).

**Decision drivers:** Whether loads must run in parallel across systems without coordination, whether Type 2 is in use anywhere, the engine's join cost for wide keys, and the organisation's tolerance for a probabilistic collision argument.

### ADR: Star Schema vs One Big Table at the Serving Layer

**Context:** The consumption layer must be shaped for BI tools and analysts.

**Options:** Star schema (conformed, maintainable, small storage, more joins) vs generated wide tables per consumer (fastest scans, no join skill required, conformance and history semantics lost unless generated from a star) vs both (star as the governed model, OBT materialised from it per high-traffic consumer).

**Decision drivers:** Query latency requirements, the BI tool's preferred shape, how many independent consumers exist, and whether anyone is accountable for the two shapes agreeing. If OBTs are authored independently rather than generated, the conformance loss is certain and the reconciliation cost is permanent.

### ADR: Valid-Time Only vs Bi-Temporal History

**Context:** History must be retained on a dimension, and corrections to past values are known to occur.

**Options:** Type 2 valid-time only (simpler, answers "what was true when") vs bi-temporal (valid time plus system time; answers "what did we believe on date X, and what do we believe now about date X") vs an immutable append-only integration layer that makes both derivable.

**Decision drivers:** Whether reports are subject to reconstruction or restatement obligations, how frequently backdated corrections occur, and whether "the report changed retrospectively" is an acceptable outcome. This is a build-time decision; conversion later is a full historical reload.

### ADR: Erasure vs Immutable History

**Context:** Data subject erasure obligations apply to entities that appear in historical facts and dimensions.

**Options:** Physical deletion (satisfies the strictest reading, breaks historical reproducibility and row counts) vs pseudonymisation of identifying attributes with grain and keys retained (preserves counts and reproducibility) vs crypto-shredding (delete the key, retain the ciphertext).

**Decision drivers:** Legal interpretation available to the organisation, whether historical aggregate reproducibility is itself a regulatory obligation (the two can conflict directly), and whether the storage layer supports targeted row deletion economically at all.

### ADR: Conformed Dimension Ownership

**Context:** Multiple teams need a shared dimension and each has a candidate version.

**Options:** Central ownership with a request process (consistent, slower) vs federated ownership with a published contract and conformance tests (faster, requires enforcement) vs no ownership (each team forks; the default outcome of not deciding).

**Decision drivers:** Number of consuming teams, existence of automated conformance testing, and whether the organisation has anywhere to put the accountability. This is an organisational decision with a technical symptom, and leaving it undecided is choosing the third option.

## Reference Architectures

- **Layered dimensional (the common default)** -- raw landing (immutable, as-ingested) → staging (typed, deduplicated, renamed, one model per source table) → intermediate (business rules, joins, conformance) → marts (star schemas: conformed dimensions plus process-specific fact tables) → optional generated wide tables per high-traffic consumer. Each layer is materialised and testable; only marts are exposed to users.
- **Vault-backed regulated estate** -- raw landing → raw vault (hubs, links, satellites; insert-only, source-attributed, no business rules) → business vault (soft rules, computed satellites) → PIT and bridge tables for query assist → information marts as star schemas. The vault is the audit record; the marts are the product. Reconstruction queries go to the vault, business queries go to the marts.
- **Snapshot-first for slowly changing sources** -- where the source is mutable and the ingestion mechanism cannot capture every intermediate state, a scheduled snapshot of source state (SCD2 with effective intervals) becomes the history of record. Its resolution is the snapshot interval, and that limitation must be stated explicitly wherever the history is consumed -- it is a sampled history, not a complete one.
- **Aggregate-on-demand serving** -- atomic fact tables plus materialised views or aggregate tables built only for measured hot paths, with a documented rule that every aggregate is derived from the atomic table and tested to reconcile with it. Aggregates that are not tested against their source drift, and drift is discovered by users.

## Reference Links

- [Kimball Group: Dimensional Modeling Techniques](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/) -- the canonical index of techniques, including the full Type 0 through Type 7 SCD list
- [Kimball Group: Four-Step Dimensional Design Process](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/four-4-step-design-process/) -- select the process, declare the grain, identify dimensions, identify facts
- [Kimball Group: Enterprise Data Warehouse Bus Architecture](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/kimball-data-warehouse-bus-architecture/) -- conformed dimensions and the bus matrix
- [Kimball Group: Type 2 Slowly Changing Dimension](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2/) -- effective dating, current flags, and surrogate key versioning
- [Kimball Group: Factless Fact Tables](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/factless-fact-table/) -- event and coverage tables, and the "what did not happen" question
- [Kimball Group: Accumulating Snapshot Fact Tables](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/accumulating-snapshot-fact-table/) -- pipeline milestone modelling with in-place updates
- [Kimball Group: Surrogate Keys](https://www.kimballgroup.com/1998/05/surrogate-keys/) -- the original argument for warehouse-generated keys
- [Kimball Group: The Data Warehouse Toolkit](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/data-warehouse-dw-toolkit/) -- the reference text for dimensional modelling
- [Data Vault Alliance](https://datavaultalliance.com/) -- Data Vault 2.0 standards, certification, and community materials
- [Data vault modeling (Wikipedia)](https://en.wikipedia.org/wiki/Data_vault_modeling) -- concise vendor-neutral summary of hubs, links, and satellites
- [Slowly changing dimension (Wikipedia)](https://en.wikipedia.org/wiki/Slowly_changing_dimension) -- worked examples of each SCD type
- [Star schema (Wikipedia)](https://en.wikipedia.org/wiki/Star_schema) and [Snowflake schema (Wikipedia)](https://en.wikipedia.org/wiki/Snowflake_schema) -- structural definitions and trade-offs
- [Bill Inmon (Wikipedia)](https://en.wikipedia.org/wiki/Bill_Inmon) -- background on the Corporate Information Factory and the normalised-warehouse position
- [Fivetran: Star schema vs OBT benchmark (2022)](https://www.fivetran.com/blog/star-schema-vs-obt) -- TPC-DS-derived BI-style query timings comparing denormalised tables against star schemas across three cloud warehouses
- [dbt snapshots documentation](https://docs.getdbt.com/docs/build/snapshots) -- a widely used Type 2 implementation, including hard-delete handling and metadata column semantics

## See Also

- `general/data-analytics.md` -- warehouse vs lake vs lakehouse selection, ETL vs ELT, semantic layers, and governance tooling
- `general/data-ingestion.md` -- how change data reaches the model, and why the capture method constrains what history you can build
- `providers/dbt/transformation.md` -- the transformation layer that implements these models, including snapshots as SCD2 and incremental strategies
- `general/data.md` -- operational database design, engine selection, and normalisation for transactional workloads
- `patterns/data-pipeline.md` -- pipeline architecture, orchestration, and cost benchmarks for the pipelines that load these models
- `general/data-classification.md` -- classification and sensitivity labelling that drives the erasure and masking decisions above
- `general/governance.md` -- governance operating models, including who owns a conformed dimension
- `providers/databricks/data-platform.md` -- lakehouse implementation of these models, including merge and file-layout costs for update-in-place patterns
- `providers/snowflake/data-platform.md` -- warehouse implementation and its constraint behaviour
