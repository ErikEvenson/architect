# Data Analytics and Warehousing Architecture

## Scope

This file covers **what** analytics and warehousing decisions need to be made during architecture design: warehouse vs lake vs lakehouse selection, ETL/ELT tooling, stream processing, data governance, semantic layers, data quality, cost management, and organizational patterns like data mesh. For provider-specific **how** (managed service configuration, pricing tiers, region availability), see the provider data files listed in See Also. For foundational database and storage decisions, see `general/data.md`. For pipeline orchestration and ingestion patterns, see `patterns/data-pipeline.md`.

## Checklist

- [ ] **[Critical]** Which analytics storage architecture fits the workload? (data warehouse for structured, schema-on-write analytics with SQL-first access — BigQuery, Redshift, Synapse, Snowflake; data lake for schema-on-read with diverse file formats and exploratory workloads — S3, GCS, ADLS Gen2; lakehouse for combining both via open table formats — Iceberg, Delta Lake, Hudi — that add ACID transactions and time travel to object storage; most mature analytics platforms evolve toward lakehouse to avoid maintaining separate copies)
- [ ] **[Critical]** What is the latency requirement for analytics data? (real-time dashboards and alerting need stream processing with sub-second to seconds latency — Kafka/Flink, Kinesis, Pub/Sub + Dataflow; near-real-time micro-batch at minutes latency suits most operational analytics — Spark Structured Streaming, dbt incremental models; daily or hourly batch is sufficient for financial reporting and trend analysis — schedule via Airflow, Dagster, or Data Factory; mixing latency tiers in one platform increases complexity significantly)
- [ ] **[Critical]** How is data quality validated before it reaches consumers? (schema validation on ingestion prevents corrupt records from propagating; statistical checks via Great Expectations, Soda, or Dataplex detect drift, null spikes, and distribution anomalies; data observability platforms like Monte Carlo provide automated anomaly detection and lineage-aware alerting; quality gates that block pipeline progression are safer than post-load alerts that require manual remediation)
- [ ] **[Critical]** What data governance controls are required? (data catalog for discoverability — Glue Catalog, Dataplex, Purview, or open-source options like DataHub and OpenMetadata; column-level lineage for impact analysis and regulatory audit trails; access control at table, column, and row level for PII and sensitive data — enforce via warehouse-native RBAC, Apache Ranger, or provider IAM policies; data classification tags that drive automated policy enforcement)
- [ ] **[Critical]** How is access to sensitive data controlled across the analytics platform? (row-level security for multi-tenant data; column masking or tokenization for PII columns in shared datasets; separate schemas or projects for sensitive vs non-sensitive data; service accounts with least-privilege access for ETL jobs; audit logging of all data access for compliance — GDPR, HIPAA, PCI-DSS require demonstrable access controls and deletion capability across the entire analytics chain)
- [ ] **[Critical]** What is the ETL/ELT strategy and tooling? (ETL transforms before loading — appropriate when data must be cleansed or redacted before landing in the warehouse, common with Glue, Dataflow, Data Factory, Fivetran; ELT loads raw data then transforms in the warehouse — leverages warehouse compute, enables analysts to iterate on transformations, standard with dbt; hybrid approaches use ETL for ingestion and ELT for business logic; tool selection affects who owns transformations — engineers vs analytics engineers)
- [ ] **[Recommended]** Is an open table format adopted for data lake storage? (Apache Iceberg, Delta Lake, and Apache Hudi add ACID transactions, schema evolution, time travel, and partition evolution to object storage; Iceberg has broadest engine compatibility — Spark, Flink, Trino, Dremio, Snowflake, BigQuery; Delta Lake is native to Databricks with growing cross-engine support; Hudi excels at upsert-heavy workloads and incremental processing; choosing a format is a long-term commitment that affects engine interoperability and vendor flexibility)
- [ ] **[Recommended]** How are analytics costs managed and optimized? (on-demand pricing suits variable workloads but can spike unpredictably — BigQuery per-TB scanning, Redshift Serverless per-RPU, Synapse Serverless per-TB; provisioned or reserved capacity provides cost predictability for steady workloads — BigQuery editions with slots, Redshift reserved nodes, Snowflake credits; partition pruning and clustering reduce scan volume and cost; materialized views trade storage for compute savings on repeated queries; storage tiering moves cold data to cheaper tiers — track cost per query and cost per team to identify optimization targets)
- [ ] **[Recommended]** What is the semantic layer strategy? (semantic layers provide consistent metric definitions across BI tools, preventing conflicting numbers — dbt Semantic Layer with MetricFlow, Looker LookML, Cube for multi-tool environments; without a semantic layer, each BI tool or analyst redefines metrics independently, leading to trust issues; headless BI via semantic layer APIs enables consistent metrics in dashboards, notebooks, and applications simultaneously)
- [ ] **[Recommended]** Is a data mesh organizational model appropriate? (data mesh suits large organizations where centralized data teams are bottlenecks — assigns domain teams ownership of their data as products with SLAs, discoverability, and quality guarantees; requires federated governance to maintain interoperability standards across domains; self-serve data platform provides infrastructure as a product so domains do not each build their own; premature adoption in small teams adds organizational overhead without proportional benefit — start with a centralized team and decentralize when the bottleneck becomes measurable)
- [ ] **[Recommended]** How is the stream processing architecture designed? (Kafka + Flink for stateful stream processing with exactly-once semantics and complex event processing; Kinesis for AWS-native workloads with simpler operational overhead; Pub/Sub + Dataflow for GCP-native serverless streaming; Event Hubs + Stream Analytics for Azure-native real-time analytics; evaluate windowing requirements — tumbling, sliding, session windows — and state management needs; stream processing adds significant operational complexity compared to micro-batch — justify the latency requirement before committing)
- [ ] **[Optional]** Are data contracts defined between producers and consumers? (data contracts specify schema, SLAs, freshness guarantees, and quality expectations as code — enforce with schema registries and CI/CD validation; prevent breaking changes from upstream systems from silently corrupting downstream analytics; particularly valuable in data mesh architectures where domain teams produce data independently)
- [ ] **[Optional]** Is a metrics store or headless BI layer needed? (metrics stores centralize business metric definitions — revenue, churn rate, conversion — so every consumer gets identical calculations; useful when multiple BI tools or applications consume the same metrics; dbt Semantic Layer, Cube, and Looker provide this capability; evaluate whether the organization has enough metric consumers to justify the additional infrastructure layer)

## Why This Matters

Analytics architecture decisions are among the most expensive to reverse because they affect data storage formats, query engines, transformation pipelines, and every downstream consumer simultaneously. Choosing the wrong warehouse-vs-lake-vs-lakehouse architecture means either maintaining expensive duplicate copies of data across systems or undertaking a multi-quarter migration that disrupts every dashboard and report in the organization. A warehouse-only approach forces all data through rigid schemas and leaves data science teams unable to work with unstructured data. A lake-only approach gives flexibility but sacrifices query performance and governance, eventually leading teams to build shadow data warehouses anyway.

Cost management is a persistent challenge because analytics workloads are inherently unpredictable. A single poorly written query in BigQuery can scan petabytes and generate a five-figure bill in minutes. Redshift clusters provisioned for peak load sit idle most of the day. Snowflake auto-scaling warehouses can multiply costs when multiple teams run concurrent workloads without cost controls. Organizations that defer cost governance until the first shocking bill discover that retrofitting controls — per-team budgets, query complexity limits, partition pruning enforcement — requires changes across every pipeline and dashboard.

Data governance failures compound over time. Without a catalog, analysts cannot find data and create their own extracts, leading to proliferation of ungoverned copies. Without lineage, a schema change in a source system breaks downstream reports in ways that take days to diagnose. Without quality checks, decision-makers lose trust in the data platform entirely and revert to spreadsheets. Without access controls, sensitive data leaks into analytics environments where it is accessible to anyone with warehouse credentials. Each of these failures is individually manageable but collectively they create a data platform that nobody trusts, everybody works around, and the organization pays for but does not fully use.

## Common Decisions (ADR Triggers)

### ADR: Analytics Storage Architecture

**Context:** The organization needs a platform for analytical workloads and must choose between dedicated warehouse, data lake, or lakehouse approaches.

**Options:**

| Criterion | Data Warehouse | Data Lake | Lakehouse |
|---|---|---|---|
| Schema Model | Schema-on-write, structured | Schema-on-read, any format | Schema-on-read with enforcement layer |
| Query Performance | Optimized for SQL analytics | Varies by engine and format | Near-warehouse performance with open formats |
| Data Types | Structured, semi-structured | Structured, semi-structured, unstructured | All types with ACID on structured |
| Governance | Built-in RBAC, audit logging | Requires external tooling | Open table format metadata + catalog |
| Cost Model | Compute + storage (often coupled) | Storage (cheap) + compute (pay per query) | Storage (cheap) + compute (flexible) |
| Vendor Lock-in | High (proprietary formats) | Low (open formats on object storage) | Low-medium (open formats, engine-portable) |
| Best Fit | BI reporting, regulated analytics | Data science, ML, raw data archival | Organizations wanting both with one copy |

**Decision drivers:** Data variety (structured only vs mixed), query patterns (SQL-heavy vs exploratory), governance requirements, cost sensitivity, and team skills.

### ADR: Cloud Data Warehouse Selection

**Context:** The organization requires a cloud data warehouse and must select a platform.

**Options:**
- **BigQuery:** Serverless, separation of storage and compute, pay-per-query or edition slots. Excels at ad-hoc analytics and geospatial queries. Native ML integration. GCP ecosystem.
- **Redshift:** Provisioned or serverless, tight AWS integration, Redshift Spectrum for S3 queries. RA3 nodes separate storage and compute. Best for AWS-heavy organizations with predictable workloads.
- **Synapse Analytics:** Dedicated or serverless SQL pools, tight Azure and Power BI integration. Serverless model is cost-effective for sporadic queries. Best for Microsoft-ecosystem organizations.
- **Snowflake:** Multi-cloud, independent scaling of compute warehouses, zero-copy data sharing. Credit-based pricing. Strong for multi-cloud strategies and data marketplace use cases.
- **Databricks SQL:** Lakehouse-native SQL analytics on Delta Lake. Combines warehouse performance with data lake flexibility. Strong for organizations already invested in Spark and Delta Lake.

**Decision drivers:** Existing cloud provider commitment, pricing model preference (on-demand vs reserved), multi-cloud requirements, data sharing needs, and integration with existing BI tools.

### ADR: ETL vs ELT Approach

**Context:** Data must be extracted from source systems, transformed, and made available for analytics. The team must decide where transformation occurs.

**Options:**
- **ETL (Extract-Transform-Load):** Transform data before loading into the warehouse. Appropriate when data must be cleansed, redacted, or aggregated before landing. Tooling: Glue, Dataflow, Data Factory, Informatica. Requires engineering skills; transformations are harder for analysts to modify.
- **ELT (Extract-Load-Transform):** Load raw data into the warehouse, then transform using SQL. Leverages warehouse compute for transformations. Tooling: dbt, Dataform, warehouse-native SQL. Enables analytics engineers to own transformation logic. Requires warehouse capacity for transformation compute.
- **Hybrid:** Use ETL for ingestion-time transformations (PII redaction, format normalization) and ELT for business logic transformations (metrics, aggregations, joins). Most mature platforms use this approach.

**Decision drivers:** Data sensitivity (must PII be removed before landing?), team composition (engineers vs analytics engineers), warehouse compute budget, transformation complexity, and iteration speed requirements.

### ADR: Open Table Format Selection

**Context:** The organization is adopting a lakehouse architecture and must select an open table format for data lake storage.

**Options:**
- **Apache Iceberg:** Broadest engine compatibility (Spark, Flink, Trino, Dremio, Snowflake, BigQuery, Athena). Hidden partitioning eliminates user error in partition specification. Partition evolution without rewriting data. Strong community momentum and vendor adoption.
- **Delta Lake:** Native to Databricks, growing support in other engines. Mature tooling with Delta Live Tables. OPTIMIZE and Z-ORDER for data layout optimization. Best choice for Databricks-centric environments.
- **Apache Hudi:** Excels at upsert-heavy and CDC workloads with merge-on-read and copy-on-write table types. Record-level indexing for fast updates. Narrower engine support than Iceberg.

**Decision drivers:** Engine ecosystem breadth, upsert frequency, existing Databricks investment, community trajectory, and query engine flexibility requirements.

### ADR: Data Governance Platform

**Context:** The organization needs data cataloging, lineage tracking, and access control across the analytics platform.

**Options:**
- **Provider-native (Glue Catalog, Dataplex, Purview):** Tight integration with the cloud ecosystem, lower operational overhead. Limited cross-cloud support. Best for single-cloud organizations.
- **Open-source (DataHub, OpenMetadata, Amundsen):** Cross-platform support, no licensing cost. Requires self-hosting and operational investment. Best for multi-cloud or avoiding vendor lock-in.
- **Commercial (Collibra, Alation, Atlan):** Feature-rich with business glossary, stewardship workflows, and compliance automation. Significant licensing cost. Best for large enterprises with dedicated data governance teams.

**Decision drivers:** Multi-cloud requirements, governance maturity, budget, team size, and regulatory complexity.

### ADR: Real-Time vs Batch Analytics

**Context:** The organization must determine which analytical workloads require real-time processing and which can use batch.

**Options:**
- **Batch only:** Simplest to build and operate. Hourly or daily refresh. Sufficient for financial reporting, trend analysis, and most business intelligence. Low cost.
- **Real-time only (Kappa architecture):** Single streaming pipeline handles all data. Consistent latency. High operational complexity. Requires stream processing expertise. Justified for fraud detection, real-time pricing, live dashboards.
- **Hybrid (Lambda architecture or tiered):** Batch for historical analysis and backfill, streaming for real-time dashboards and alerting. Most common in practice. Adds complexity of maintaining two code paths unless unified with a framework like Apache Beam or Spark Structured Streaming.

**Decision drivers:** Business latency requirements (ask "what decision changes if data is 1 hour old vs 1 second old?"), operational maturity, cost tolerance, and team streaming expertise.

## Reference Links

- [Apache Iceberg](https://iceberg.apache.org/) -- Open table format for large analytic datasets with ACID transactions, schema evolution, and partition evolution
- [Delta Lake](https://delta.io/) -- Open-source storage framework providing ACID transactions and scalable metadata handling on data lakes
- [Apache Hudi](https://hudi.apache.org/) -- Data lake platform for incremental data processing with upsert and delete capabilities
- [dbt](https://www.getdbt.com/) -- Analytics engineering framework for SQL-based data transformations using ELT methodology
- [Apache Flink](https://flink.apache.org/) -- Stateful stream processing framework for real-time data analytics and event-driven applications
- [Great Expectations](https://greatexpectations.io/) -- Data quality framework for validating, documenting, and profiling data
- [Soda](https://www.soda.io/) -- Data quality monitoring platform with SQL-based checks and alerting
- [Apache Kafka](https://kafka.apache.org/) -- Distributed event streaming platform for real-time data pipelines and streaming analytics
- [Cube](https://cube.dev/) -- Headless BI and semantic layer platform for consistent metrics across applications and BI tools
- [DataHub](https://datahubproject.io/) -- Open-source metadata platform for data discovery, observability, and governance
- [OpenMetadata](https://open-metadata.org/) -- Open-source platform for metadata management, data discovery, and data quality
- [Snowflake](https://www.snowflake.com/) -- Multi-cloud data warehouse with independent compute scaling and data sharing
- [Databricks](https://www.databricks.com/) -- Unified analytics platform combining data engineering, science, and SQL analytics on a lakehouse architecture
- [Fivetran](https://www.fivetran.com/) -- Automated data integration platform for ELT pipelines with pre-built connectors
- [Airbyte](https://airbyte.com/) -- Open-source data integration platform for building ELT pipelines with extensible connectors

## See Also

- `general/data.md` -- Database engine selection, replication, backup, and encryption fundamentals
- `patterns/data-pipeline.md` -- Pipeline architecture patterns, orchestration, cost benchmarks, and ingestion tooling
- `general/cost.md` -- Cloud cost management strategies and FinOps practices
- `general/governance.md` -- Broader governance frameworks including data governance organizational patterns
- `general/security.md` -- Security controls including data access, audit logging, and encryption
- `patterns/event-driven.md` -- Event-driven architecture patterns including streaming and messaging
- `general/data-classification.md` -- Data classification frameworks for sensitivity labeling and policy enforcement
