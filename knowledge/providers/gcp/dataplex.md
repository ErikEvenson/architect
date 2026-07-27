# GCP Dataplex / Knowledge Catalog and Lakehouse for Apache Iceberg

## Scope

Google Cloud's data-lake governance layer: metadata cataloguing, automatic discovery, data profiling, data quality scans, lineage, business glossary, and data products — plus **Lakehouse for Apache Iceberg** (formerly BigLake), the layer that makes Cloud Storage data behave like a governed table with fine-grained security enforced even for non-BigQuery engines.

> **Naming, as of 2026-07-26 — two renames landed in April 2026 and the documentation is only partly consistent.**
>
> | Legacy name | Current name | Effective |
> |---|---|---|
> | Dataplex / Dataplex Universal Catalog | **Knowledge Catalog** | 2026-04-10 |
> | BigLake | **Lakehouse for Apache Iceberg** | 2026-04-20 |
> | BigLake metastore | **Lakehouse runtime catalog** | 2026-04-20 |
> | BigLake tables for Apache Iceberg in BigQuery | **Apache Iceberg managed tables** | undated |
>
> The **API, client libraries, `gcloud` CLI, IAM role names, billing SKUs, and documentation URL paths all still say `dataplex` and `biglake`.** Google states explicitly that pricing SKUs remain named "Dataplex." Several BigQuery security pages still reference the shut-down Data Catalog service in prose. Expect to use both vocabularies in the same conversation; this file keeps the file slug and API vocabulary (`dataplex`) while using current product names in the text.

This file covers the governance and lakehouse layer specifically. For the warehouse itself — slots, reservations, partitioning, clustering — see `providers/gcp/bigquery.md`. For the object storage underneath see `providers/gcp/cloud-storage.md`. For the table formats see `general/open-table-formats.md`, and for the equivalent AWS layer see `providers/aws/lake-formation.md`.

## Checklist

### Catalog Model and the Data Catalog Migration

- [ ] **[Critical]** Has any remaining dependency on the legacy **Data Catalog** service been retired? Data Catalog was deprecated on 2025-02-03 and **shut down on 2026-06-01** — a date now in the past. Its business glossary shut down on the same date, and the Dataplex **Attribute Store** was discontinued on 2026-02-18. Any design document, IaC module, or runbook still referencing these is describing a service that no longer exists.
- [ ] **[Critical]** Is it understood that **policy tags and taxonomies survived** the Data Catalog shutdown and their management now lives in BigQuery? This is the single most consequential carve-out: BigQuery column-level security depends on policy tags, they are not deprecated, and the IAM role names still carry the `datacatalog.*` prefix. Prose on some BigQuery pages is stale here; the authoritative statement is on the Knowledge Catalog transition page.
- [ ] **[Critical]** Is new metadata modelling built on **entries, entry groups, entry types, aspects, and aspect types** rather than on lakes/zones/assets? The aspect model is where all current investment sits — data products, glossary, insights, and lineage all attach to entries. Lakes and zones are **not deprecated** (they remain listed as a free capability and still have quotas), but they are a separate organizational overlay that is explicitly not registerable as catalog entries. Treating them as the primary model leads to an organizational hierarchy that the governance features do not attach to.
- [ ] **[Recommended]** Is the aspect-type design kept small and deliberate, given the documented ceilings — an entry may not exceed 5 MB, and an entry may carry up to 10,000 aspects? Aspects are the extension mechanism; a sprawling set becomes as hard to reason about as the ungoverned state it replaced.
- [ ] **[Recommended]** Are catalog search patterns validated against the search quotas before building a discovery experience on them? Search is free but rate-limited per user, project, and organization, and results are capped well below what a naive "browse everything" UI would request.
- [ ] **[Optional]** Are **entry links** used to express relationships (such as schema joins) that the automatic harvesters do not infer, so lineage and impact analysis reflect real dependencies?

### Discovery and Automatic Metadata Harvesting

- [ ] **[Critical]** Is it understood that **whether discovery produces a governed table depends on supplying a connection ID**? Discovery creates BigLake **external** tables for structured and semi-structured data *when a Google Cloud resource connection ID is provided*, plain **non-BigLake external tables** when it is not, and **object tables** for unstructured data. Omitting the connection is the difference between a table that can carry row- and column-level security and one that cannot — and nothing about the scan appears to have failed.
- [ ] **[Critical]** Are the supported formats confirmed against the actual lake contents? Discovery handles Parquet, Avro, ORC, newline-delimited JSON, and CSV — with the documented caveats that JSON must be newline-delimited and CSV files with comment rows are not supported. Data that does not match is silently not catalogued.
- [ ] **[Recommended]** Are discovery scans scheduled at a cadence matched to how the lake actually changes, with include/exclude glob filters scoping them? Scans bill on the standard processing SKU; a frequent scan across an entire bucket is a recurring charge for re-discovering data that has not changed.
- [ ] **[Recommended]** Is the layout of Cloud Storage prefixes designed for discovery (consistent Hive-style partitioning, one logical table per prefix) rather than left arbitrary? The failure mode mirrors AWS Glue crawlers: a badly structured prefix produces many tables where one was intended.
- [ ] **[Optional]** Is it noted that discovered BigLake tables are automatically ingested into the catalog for search, so discovery and cataloguing are one step rather than two?

### Data Profiling and Data Quality

- [ ] **[Critical]** Are quality scans configured with the appropriate rule types rather than only the built-ins? The built-in row-level rules are range, non-null, set membership, and regex; the aggregate rules are uniqueness and statistic-range. Beyond those, custom SQL gives a **row condition** (a WHERE-style expression scored as a passing percentage against a threshold), a **table condition** (one boolean for the whole table), and a **SQL assertion** (any returned row means failure). Most real business rules need the custom forms.
- [ ] **[Critical]** Is the scan scope set to **incremental** where the table is large and append-mostly, and is the required increment column present? Full-table scans on every run bill for re-reading history that has already passed. Incremental scanning requires a date or timestamp increment column — a schema decision that must be made before the scan is designed.
- [ ] **[Critical]** Do quality results have a consumer and an action? Results can be exported to a BigQuery table, published to the catalog under the data-quality scorecard aspect, and emitted to Cloud Logging, with alerting on score thresholds and job failures. A scan whose output nobody reads is a recurring charge with no return. See the quality-gate guidance in `patterns/lakehouse-medallion.md`.
- [ ] **[Recommended]** Is the billing model understood — profiling, quality, and lineage all bill on the **premium** processing SKU, metered in **Data Compute Units (DCU)** per second with a one-minute minimum? The naming trips people up: it is *Data* Compute Unit, and it is not a BigQuery slot.
- [ ] **[Critical]** Is it known that the **free tier does not apply to premium processing**? The published free allowance covers the standard SKU only. Discovery and harvesting get a monthly free allowance; profiling, quality, and lineage do not. Budgeting for data quality on the assumption of a free tier is a common and expensive error.
- [ ] **[Recommended]** If a **custom execution identity** is configured, is it understood that this bypasses the premium SKU entirely and bills compute and storage to the BigQuery project instead? This changes both the cost attribution and which budget the spend lands in. Data-quality anomaly detection similarly bills as ordinary BigQuery compute, storage, and BigQuery ML rather than as DCUs.
- [ ] **[Optional]** Where lightweight profiling mode is used, is it known that it supports neither sampling nor row and column filters? The standard mode is the one with the controls.

### Lineage

- [ ] **[Critical]** Is the **30-day lineage retention** limit reflected in any design that depends on lineage for audit or compliance evidence? Lineage is retained for 30 days only. It is an operational impact-analysis tool, not an audit record. Where a durable trail is required, export it.
- [ ] **[Critical]** Are the automatic lineage sources known, so gaps are recognized rather than assumed away? Lineage is emitted automatically by BigQuery (tables, views, materialized views, external tables), Cloud Data Fusion, Dataflow, Managed Service for Apache Airflow, Managed Service for Apache Spark, Vertex AI pipelines and feature store, Lakehouse Iceberg REST catalog tables, and Looker (in preview). Anything else — a third-party ETL tool, a custom job — produces no lineage unless it reports it through the API.
- [ ] **[Critical]** Is the pricing asymmetry understood before choosing how to populate lineage? **Custom lineage reporting is free**, as are retrieval and deletion. Automatic parsing for non-custom source types bills on the premium DCU SKU. A design that reports lineage explicitly from its own pipelines is materially cheaper than one relying on automatic parsing across a large estate.
- [ ] **[Recommended]** Is the documented gap accounted for that **column-level lineage is not collected for BigQuery load jobs or for routines**? Impact analysis over a pipeline that loads via load jobs will show table-level edges only.
- [ ] **[Optional]** Are the console traversal limits (a fixed maximum graph depth and link count in each direction) understood as a UI constraint rather than a data constraint, with the API used for programmatic analysis beyond them?

### Access Control: Who Actually Enforces What

- [ ] **[Critical]** Is it clearly understood that **the catalog does not enforce anything — BigQuery does**? Policy tags and taxonomies are defined in a taxonomy and enforced by BigQuery at query time; dynamic data masking is defined as a data policy on a policy tag and applied by BigQuery at runtime; row-level security is defined with BigQuery DDL row access policies and enforced by BigQuery. Knowledge Catalog is metadata and discovery. Designs that assume the catalog is an enforcement point are misdrawn.
- [ ] **[Critical]** Is the **BigQuery Storage API** recognized as the enforcement point for non-BigQuery engines? Google documents that the Storage API enforces row- and column-level governance policies on all access to BigLake tables, *including through connectors* — which is what allows Spark, Trino, Hive, and similar engines to read governed data with the policies still applied. This is GCP's strongest differentiator against the AWS and Databricks equivalents and is the reason to prefer BigLake tables over plain external tables whenever governance matters.
- [ ] **[Critical]** Have direct Cloud Storage permissions been **removed** from the analyst and consumer principals? The delegation model only holds if the underlying bucket is not directly readable. Google's own documentation warns that analysts able to read objects directly from Cloud Storage can circumvent access controls. This is the same failure mode as leaving direct S3 access in place under AWS Lake Formation, and it fails open in exactly the same silent way.
- [ ] **[Recommended]** Is the appropriate masking rule chosen from the documented set (custom routine, date-year truncation, default value, email mask, first-four, last-four, SHA-256 hash, random hash, nullify) rather than implementing masking in view logic? Policy-driven masking applies consistently across every query path; view logic applies only where the view is used.
- [ ] **[Recommended]** Where an ungoverned external table already exists, is there a plan to convert it to a BigLake table with a connection? Plain external tables are documented as being for cases where governance is not a requirement — an accurate description that is easy to adopt accidentally.
- [ ] **[Optional]** Is a classification scheme defined ahead of the taxonomy, so policy tags express an agreed sensitivity model rather than an ad-hoc one? See `general/data-classification.md`.

### Lakehouse for Apache Iceberg

- [ ] **[Critical]** Is the correct table type selected from a taxonomy that has four distinct options with materially different capabilities? **BigLake external tables** over Cloud Storage or S3/Azure Blob are read-only with metadata caching and fine-grained security. **Object tables** index unstructured objects, read-only. **Apache Iceberg managed tables** are read/write with BigQuery DML. **Iceberg external tables** are read-only over externally managed Iceberg and are explicitly documented as a distinct feature from BigLake external tables. Conflating the last two is a common and consequential error.
- [ ] **[Critical]** For Apache Iceberg managed tables, is the **one concurrent mutating DML statement per table** limit accounted for in pipeline design? Only one `UPDATE`, `DELETE`, or `MERGE` runs at a time per table. A pipeline fanning out parallel merges against a single table will serialize or fail.
- [ ] **[Critical]** Is it known that **row-level security is not supported on Apache Iceberg managed tables**, while column-level access control is? Any design pairing managed Iceberg tables with row-level multi-tenancy needs a different mechanism — separate tables, authorized views over a different table type, or filtering in the serving layer.
- [ ] **[Critical]** Is storage billing understood — Iceberg managed tables store all data, **including historical table data**, in a customer-owned Cloud Storage bucket and are billed at Cloud Storage rates, not BigQuery storage rates? This is a different cost line, a different lifecycle-policy surface, and a different retention conversation than a native BigQuery table.
- [ ] **[Recommended]** Is the **90-minute metadata lag** for streamed data accounted for where external engines read the Iceberg metadata? Google documents that Iceberg metadata may not contain data streamed in through the Storage Write API within the last 90 minutes. A Spark job reading the Iceberg snapshot sees a different freshness than a BigQuery query against the same table.
- [ ] **[Recommended]** Are the managed-table restrictions checked against requirements before adoption? Partitioning is limited to date, datetime, and timestamp columns with **no partition evolution**; several types (including JSON, GEOGRAPHY, INTERVAL, RANGE, BIGNUMERIC) are unsupported; and rename, `COPY`, `CLONE`, snapshots, materialized views, authorized views, and managed disaster recovery are not available.
- [ ] **[Recommended]** For the **Lakehouse runtime catalog**, is the Iceberg spec version confirmed against what other engines will write? Iceberg V2 is GA, V3 is in preview, and V1 is explicitly unsupported. See `general/open-table-formats.md` for why the spec version determines cross-engine compatibility.
- [ ] **[Recommended]** Is the runtime catalog's **credential vending** model understood — it issues short-lived tokens directly to client engines so they can read and write data files without broad standing IAM permissions on the buckets? This is the mechanism that makes multi-engine access governable, and it is the recommended path for new workloads over the older external-table approaches.
- [ ] **[Optional]** For BigLake external tables, is **metadata caching** configured with a `max_staleness` that matches the workload? Caching avoids listing objects from Cloud Storage on every query; staleness is configurable between 30 minutes and 7 days, automatic refresh runs on a system-defined interval, and an unrefreshed cache expires after 7 days.

### Cost and Operations

- [ ] **[Critical]** Is the cost-attribution behaviour understood before setting budgets? Discovery scans, scheduled quality and ingestion tasks, and managed connectors trigger jobs on Cloud Storage, Managed Service for Apache Spark, BigQuery, Dataflow, and Cloud Scheduler — and Google documents that those charges appear **under those services rather than under Dataplex**. A budget alarm scoped to the governance SKUs will under-report the true cost of governance.
- [ ] **[Recommended]** Are the billing labels used for attribution — the workload-type label distinguishing data quality, data profiling, and lineage, plus the per-scan and per-job identifiers? These are what make governance spend analyzable rather than a single opaque line.
- [ ] **[Recommended]** Is the **maximum of 1,000 data scans per project per region** checked against the intended design? A pattern of one scan per table reaches this ceiling faster than expected on a large estate; scans covering multiple tables, or a scan-per-domain model, scale further.
- [ ] **[Recommended]** For the Lakehouse layer, are the **runtime catalog operation charges** modelled? Class A operations (creates, registrations, lists, updates, IAM writes) and Class B operations (reads, deletes, IAM reads) each have a monthly free allowance and a per-million rate beyond it, and metadata files larger than 1 MB count each additional megabyte as a further operation. A chatty engine polling the catalog is the realistic way to exceed this.
- [ ] **[Recommended]** Is it noted that Lakehouse **table management** — storage optimization and metadata generation and refresh — bills at a higher DCU rate than the Knowledge Catalog premium SKU? They are different SKUs at different rates and should not be conflated in an estimate.
- [ ] **[Optional]** Are committed-use discounts evaluated for steady-state governance workloads? Both the standard and premium processing SKUs publish one-year and three-year commitment rates.
- [ ] **[Optional]** Is it known that **data organization features (lake, zone, and asset setup), security policy application and propagation, API calls, catalog search, and metadata storage for automatically ingested Google Cloud technical metadata are all free of charge**? The billable surface is narrower than it first appears — it is the scans and the parsing that cost money, not the catalog itself.

## Why This Matters

The naming churn is not cosmetic. Two renames landed ten days apart in April 2026, a predecessor service was shut down two months later, and the API surface, IAM roles, billing SKUs, and documentation URLs were all deliberately left on the old names. The practical consequence is that any architecture document, IaC module, or runbook written before mid-2026 uses a vocabulary that no longer matches the console, while any written strictly to the new vocabulary will not match the Terraform provider or the bill. Teams lose real time to this, and the way through is to be explicit about which layer a name belongs to — product, API, or SKU — rather than picking one and hoping.

The enforcement boundary is the thing most often drawn wrong on GCP. Knowledge Catalog is metadata: it discovers, describes, profiles, scores, and traces. It does not stop anyone reading anything. Enforcement is BigQuery's, through policy tags for columns, data policies for masking, and row access policies for rows. The genuinely distinctive part is that the BigQuery Storage API extends that enforcement to non-BigQuery engines reading BigLake tables through connectors — which is a stronger open-engine governance story than the alternatives can currently document. But it only holds if consumers cannot reach the bucket directly. Leave a data scientist with direct Cloud Storage read access and every column mask and row filter becomes advisory, silently, with the console still showing them as configured. This is the same fail-open shape as AWS Lake Formation with residual S3 access, and it deserves the same treatment: an explicit test that a control principal is actually denied, not a review that the policy exists.

The connection-ID detail in discovery is a small configuration choice with a large governance consequence. Provide one and discovery produces BigLake tables that can carry fine-grained security; omit it and it produces plain external tables that cannot. Both outcomes look like a successful scan. A lake discovered without connections has to be converted table by table later, at which point the consumers already have queries written against the ungoverned objects.

The cost model has two traps that catch teams in opposite directions. First, the free tier applies only to standard processing — discovery and harvesting — and explicitly not to the premium SKU that profiling, quality, and lineage bill against. Data quality is the feature most likely to be rolled out broadly on the assumption that a free allowance absorbs it, and it is precisely the one that does not. Second, much of the real spend does not appear under the governance service at all: scans dispatch work to BigQuery, Spark, Dataflow, and Cloud Storage, and Google documents that those charges land under those services. Governance therefore looks cheaper than it is when measured naively, and the correction usually arrives as an unexplained increase somewhere else.

Finally, Apache Iceberg managed tables are attractive and genuinely capable, but their restriction list is long enough that it should be read before adoption rather than discovered during it. One concurrent mutating statement per table constrains pipeline parallelism. No row-level security constrains multi-tenant designs. Storage billing to a customer bucket changes the retention and lifecycle conversation. No partition evolution removes one of the main reasons teams choose Iceberg elsewhere. None of these are defects — they are a coherent set of trade-offs — but several of them invalidate specific architectures, and each is cheaper to discover on paper.

## Common Decisions (ADR Triggers)

- **Catalog model: entries and aspects vs lakes and zones** — the aspect model for anything expected to use data products, glossary, insights, or lineage (all of which attach to entries) vs lakes and zones as a lightweight organizational overlay where that is genuinely all that is needed. They coexist; the decision is which one the governance features hang off, and that should be the aspect model.
- **BigLake tables vs plain external tables** — BigLake with a connection for anything requiring row-level security, column-level security, masking, or governed access from non-BigQuery engines vs plain external tables only where governance is explicitly not a requirement. Retrofitting is possible but happens after consumers have written queries.
- **Table type for lake data** — Apache Iceberg managed tables for read/write with BigQuery DML and automatic optimization (accepting one concurrent mutating statement, no row-level security, no partition evolution, Cloud Storage billing) vs Iceberg external tables for data an external engine owns and writes vs BigLake external tables over Parquet/ORC for read-only governed access with metadata caching vs native BigQuery tables where the data does not need to be open at all.
- **Catalog for multi-engine Iceberg** — the Lakehouse runtime catalog with its Iceberg REST endpoint and credential vending as the recommended path for new multi-engine workloads vs AWS Glue Data Catalog where the centre of gravity is AWS vs a metadata-file URI for the Azure case, accepting manual URI maintenance. See `general/open-table-formats.md`.
- **Where quality checks run** — Knowledge Catalog data quality scans for centralized, catalog-integrated scoring with results published as aspects (premium SKU, no free tier) vs in-pipeline assertions in dbt or the transformation framework (no per-scan charge, no catalog integration, closer to the failure) vs both, with in-pipeline gates blocking propagation and catalog scans providing the estate-level view.
- **Lineage population** — automatic parsing across supported sources (no instrumentation work, premium DCU charges, gaps for load jobs and routines) vs explicit custom lineage reporting from pipelines (free, complete, requires instrumentation) vs a third-party catalog where the estate spans clouds. The 30-day retention limit constrains all three where audit evidence is the requirement.
- **Governance platform across clouds** — GCP-native Knowledge Catalog for a GCP-centred estate vs a cross-platform catalog (DataHub, OpenMetadata, or a commercial product) where the estate spans AWS, Azure, and GCP. Native buys enforcement integration; cross-platform buys one pane of glass and gives up the Storage API enforcement path. See the governance ADR in `general/data-analytics.md`.
- **Metadata cache staleness** — short staleness for freshness-sensitive queries at the cost of more frequent refresh work vs long staleness (up to seven days) for stable partitioned data where object listing is the dominant planning cost.

## Reference Architectures

### Governed Cloud Storage lake queried from BigQuery and Spark

Cloud Storage lake with Hive-partitioned Parquet -> Knowledge Catalog discovery scans configured **with a resource connection ID**, producing BigLake external tables with metadata caching -> policy tags applied to sensitive columns from a taxonomy derived from the organization's classification scheme, with data policies providing masking -> row access policies on the tables requiring row-level isolation -> analysts and Spark jobs read through BigQuery and the BigQuery Storage API, with **no direct Cloud Storage permissions**, so the same policies apply on both paths -> quality scans on the curated tables publish scorecards to the catalog. See `providers/gcp/bigquery.md`, `general/data-classification.md`.

### Multi-engine Iceberg lakehouse

Cloud Storage buckets holding Iceberg data -> Lakehouse runtime catalog exposing the Iceberg REST catalog endpoint with credential vending -> Managed Service for Apache Spark and Flink write, Trino and BigQuery read, each receiving short-lived scoped tokens rather than standing bucket IAM -> lineage emitted automatically for the REST catalog tables -> table management (storage optimization and metadata refresh) billed per DCU. Confirm the Iceberg spec version every engine expects: V2 is GA, V3 is preview, V1 is unsupported. See `general/open-table-formats.md`, `general/query-engines.md`.

### Medallion lake with quality gates

Cloud Storage `bronze/` discovered into external tables -> Managed Service for Apache Spark or scheduled BigQuery jobs produce silver as Apache Iceberg managed tables (accepting the single-concurrent-mutation limit by serializing merges) -> incremental data quality scans run between layers with custom SQL assertions, exporting results to a BigQuery table and publishing scorecards as aspects -> gold aggregates as native BigQuery tables for BI, where row-level security is available. Note the deliberate choice of table type per layer: managed Iceberg where open-format read/write matters, native BigQuery where row-level security matters. See `patterns/lakehouse-medallion.md`.

### Data-products operating model

Domain teams own entry groups and publish **data products** composed of assets, access groups mapped to Google Groups, contracts capturing refresh schedule and quality standards, and business-glossary terms -> discovery and profiling run centrally on the standard and premium SKUs -> consumers find products through catalog search (free) and request access through the product's access groups -> quality scorecards and lineage give consumers a basis for trusting a product before adopting it. This is the GCP-native shape of the data-mesh model described in `general/data-analytics.md`.

## Reference Links

- [Knowledge Catalog documentation](https://docs.cloud.google.com/dataplex/docs) -- product overview and the current naming statement
- [Knowledge Catalog introduction](https://docs.cloud.google.com/dataplex/docs/introduction) -- capabilities, resource model, and positioning
- [Catalog overview: entries, entry groups, and aspects](https://docs.cloud.google.com/dataplex/docs/catalog-overview) -- the metadata model, and the relationship between the catalog and lakes/zones
- [Transition to the Knowledge Catalog](https://docs.cloud.google.com/dataplex/docs/transition-to-dataplex-catalog) -- Data Catalog migration, and what survived the shutdown
- [Deprecations](https://docs.cloud.google.com/dataplex/docs/deprecations) -- Data Catalog, Attribute Store, and business glossary shutdown dates
- [Automatic discovery of Cloud Storage data](https://docs.cloud.google.com/bigquery/docs/automatic-discovery) -- scan configuration, supported formats, and which table type each configuration produces
- [Auto data quality overview](https://docs.cloud.google.com/dataplex/docs/auto-data-quality-overview) -- built-in and custom SQL rule types, scan scopes, and result destinations
- [Data profiling overview](https://docs.cloud.google.com/dataplex/docs/data-profiling-overview) -- profile metrics, sampling, filters, and mode differences
- [About data lineage](https://docs.cloud.google.com/dataplex/docs/about-data-lineage) -- automatic sources, the process/run/event API model, retention, and documented gaps
- [Data products overview](https://docs.cloud.google.com/dataplex/docs/data-products-overview) -- assets, access groups, contracts, and context
- [Manage glossaries](https://docs.cloud.google.com/dataplex/docs/manage-glossaries) -- business glossary resources and management
- [Data insights](https://docs.cloud.google.com/dataplex/docs/data-insights-structured-data) -- Gemini-generated descriptions, queries, and relationship graphs
- [Knowledge Catalog quotas and limits](https://docs.cloud.google.com/dataplex/docs/quotas) -- data scan, entry, aspect, and search limits
- [Knowledge Catalog pricing](https://cloud.google.com/products/knowledge-catalog/pricing) -- standard and premium DCU rates, metadata storage, free tier scope, and the capability-to-SKU mapping
- [Use the Knowledge Catalog with BigQuery](https://docs.cloud.google.com/bigquery/docs/use-knowledge-catalog) -- the authoritative statement on policy tags remaining in BigQuery
- [BigQuery column-level security](https://docs.cloud.google.com/bigquery/docs/column-level-security-intro) -- policy tags, taxonomies, and query-time enforcement
- [BigQuery column data masking](https://docs.cloud.google.com/bigquery/docs/column-data-masking-intro) -- data policies, masking rules, and runtime application
- [BigQuery row-level security](https://docs.cloud.google.com/bigquery/docs/managing-row-level-security) -- row access policies and their enforcement
- [BigLake tables introduction](https://docs.cloud.google.com/bigquery/docs/biglake-intro) -- access delegation, connections, and Storage API enforcement for connectors
- [Apache Iceberg managed tables in BigQuery](https://docs.cloud.google.com/bigquery/docs/biglake-iceberg-tables-in-bigquery) -- write path, automatic optimization, limitations, and best practices
- [Iceberg external tables](https://docs.cloud.google.com/bigquery/docs/iceberg-external-tables) -- read-only access to externally managed Iceberg, and the three catalog options
- [Object tables](https://docs.cloud.google.com/bigquery/docs/object-table-introduction) -- structured access over unstructured Cloud Storage objects
- [External data sources](https://docs.cloud.google.com/bigquery/docs/external-data-sources) -- external vs BigLake table comparison and metadata caching
- [Lakehouse for Apache Iceberg documentation](https://docs.cloud.google.com/lakehouse/docs) -- product overview after the BigLake rename
- [Lakehouse catalogs](https://docs.cloud.google.com/lakehouse/docs/about-lakehouse-catalogs) -- the runtime catalog, supported engines, and spec-version support
- [Set up the Lakehouse Iceberg REST catalog](https://docs.cloud.google.com/lakehouse/docs/set-up-lakehouse-iceberg-rest-catalog) -- REST endpoint configuration and credential vending
- [Lakehouse release notes](https://docs.cloud.google.com/lakehouse/docs/release-notes) -- the BigLake rename and subsequent changes
- [Lakehouse pricing](https://cloud.google.com/products/lakehouse/pricing) -- table management DCU rate and runtime catalog Class A/B operation charges

## See Also

- `providers/gcp/bigquery.md` -- the engine that enforces policy tags, masking, and row access policies; slots, partitioning, and clustering
- `providers/gcp/cloud-storage.md` -- the object storage under the lake, and the direct-access path that must be closed for governance to hold
- `providers/gcp/iam-organizations.md` -- IAM hierarchy, connections, and service-account delegation
- `providers/gcp/data.md` -- broader GCP data services
- `general/open-table-formats.md` -- Iceberg spec versions, catalogs, and why cross-engine compatibility depends on them
- `general/query-engines.md` -- Spark, Trino, and other engines reading governed tables through the Storage API
- `patterns/lakehouse-medallion.md` -- layer boundaries, quality gates, and per-layer table-type selection
- `general/data-analytics.md` -- the data governance platform ADR and the data-mesh operating model
- `general/data-classification.md` -- the classification scheme that should drive taxonomy and policy tag design
- `providers/aws/lake-formation.md` -- the AWS equivalent, for comparison and for multi-cloud estates
- `providers/databricks/data-platform.md` -- Unity Catalog as the third comparable governance layer
