# Databricks Data Platform

## Scope

Databricks lakehouse platform architecture and design decisions. Covers the lakehouse architecture (Delta Lake on cloud object storage with separated compute), workspace and account topology, cluster types (all-purpose vs job vs SQL warehouses, classic vs serverless), Photon vectorized execution, Unity Catalog governance and three-level namespace, Delta Lake features (ACID, time travel, OPTIMIZE, VACUUM, change data feed, liquid clustering), data ingestion patterns (Auto Loader, Delta Live Tables, structured streaming), Databricks Workflows for orchestration, MLflow for experiment tracking and model serving, network isolation patterns (PrivateLink, customer-managed VPC, no-public-IP), DBU-based pricing model (compute DBUs plus underlying cloud instance costs), cross-cloud differences (AWS, Azure native, GCP), and integration patterns with cloud storage, BI tools, and other data platforms.

## Checklist

### Architecture and Workspace Topology

- [ ] **[Critical]** Is the lakehouse architecture understood -- data lives in open Delta Lake format on cloud object storage (S3, ADLS Gen2, GCS) and compute (clusters, SQL warehouses) is provisioned independently? This is fundamentally different from traditional warehouses where storage and compute are coupled, and from data lakes where there are no ACID guarantees.
- [ ] **[Critical]** Is the workspace topology designed around blast-radius isolation and governance scope -- separate workspaces per environment (dev/staging/prod), per business unit, or per region rather than a single shared workspace? On AWS, the E2 account architecture allows multiple workspaces under one Databricks account with shared Unity Catalog metastore per region.
- [ ] **[Critical]** Is workspace deployment configured with customer-managed VPC/VNet rather than Databricks-managed networking when network isolation, IP CIDR control, or VPC peering is required? Customer-managed networking enables PrivateLink, no-public-IP clusters, and integration with existing network security controls.
- [ ] **[Recommended]** Is the Databricks account console used as the cross-workspace governance plane for Unity Catalog, identity federation, audit logs, and workspace creation? Workspace admins should not duplicate account-level configuration.
- [ ] **[Recommended]** On Azure, is Azure Databricks deployed as a native Azure resource with VNet injection rather than the default Databricks-managed VNet? Azure Databricks integrates with Azure AD natively and supports Azure Private Link for both the control plane and the workspace data plane.
- [ ] **[Optional]** Are workspace-level configurations (instance profiles, init scripts, library installation) managed via Databricks Asset Bundles or Terraform rather than the UI to enable reproducibility and code review?

### Compute: Clusters and SQL Warehouses

- [ ] **[Critical]** Are job clusters used for scheduled jobs and all-purpose clusters reserved for interactive notebook work? Job clusters are billed at a significantly lower DBU rate (roughly one-third) and terminate immediately after job completion. Running production jobs on shared all-purpose clusters wastes credits and creates noisy-neighbor issues.
- [ ] **[Critical]** Are SQL Warehouses used for BI and SQL workloads instead of all-purpose clusters with the SQL editor? SQL Warehouses (formerly SQL Endpoints) are optimized for SQL with Photon enabled by default, support multi-cluster auto-scaling for concurrency, and are the only compute type that supports Databricks SQL governance features.
- [ ] **[Critical]** Is SQL Warehouse type selected based on workload requirements -- Classic (customer-managed instances, lowest cost), Pro (customer-managed instances with predictive I/O and Photon for query acceleration), or Serverless (Databricks-managed instances, fastest startup, highest per-DBU cost but no idle infrastructure cost)? Serverless is typically cost-effective for bursty interactive workloads despite higher per-DBU rates.
- [ ] **[Critical]** Is Photon enabled for SQL warehouses and ETL clusters with significant SQL or DataFrame workloads? Photon is a vectorized C++ execution engine that delivers 2-3x speedup for many workloads but adds a DBU multiplier (typically ~2x DBU rate). Net cost is usually lower for Photon-eligible workloads because the runtime decreases more than the rate increases.
- [ ] **[Recommended]** Is cluster auto-termination configured aggressively (10-30 minutes for interactive clusters, immediate for job clusters)? Default cluster auto-termination of 120 minutes is far too generous for most teams and is a leading cause of unexpected DBU consumption.
- [ ] **[Recommended]** Are instance pools used to reduce cluster startup latency for frequently created job clusters and interactive clusters? Pools pre-warm idle instances; only the underlying cloud instance cost accrues for idle pool members (no DBU charge until a cluster attaches).
- [ ] **[Recommended]** Is cluster auto-scaling configured with appropriate min/max workers based on observed workload variance? Over-provisioning min workers wastes credits during quiet periods; under-provisioning max workers causes job slowdowns under burst load.
- [ ] **[Recommended]** Are spot/preemptible instances used for fault-tolerant workloads (most batch ETL) with on-demand fallback for the driver? Spot can reduce instance costs by 60-90%, but the driver must remain on-demand to survive a node loss.
- [ ] **[Optional]** Are cluster policies enforced to constrain instance types, sizes, runtime versions, and DBU spend per cluster? Policies prevent users from spinning up massive clusters by accident and are essential at scale.

### Unity Catalog and Governance

- [ ] **[Critical]** Is Unity Catalog enabled as the governance layer for all workspaces, with the legacy `hive_metastore` reserved for migration only? Unity Catalog provides centralized access control, lineage, and audit across workspaces and is required for many newer features (Lakehouse Federation, model serving with governance, online tables, AI/BI Genie).
- [ ] **[Critical]** Is the three-level namespace (`catalog.schema.table`) used consistently, with catalogs as the top-level isolation boundary -- typically one catalog per environment (dev/staging/prod) or per business domain? Cross-catalog queries work within a metastore but the catalog boundary is the natural unit for access grants and lineage scoping.
- [ ] **[Critical]** Are external locations and storage credentials configured at the Unity Catalog level for accessing data outside managed storage, rather than per-cluster instance profiles or service principals? External locations centralize cloud storage access and are visible in lineage and audit logs.
- [ ] **[Critical]** Is one Unity Catalog metastore configured per region per Databricks account, and are workspaces in the same region attached to the same metastore? A workspace can only attach to one metastore, and the metastore is the boundary for cross-workspace data sharing within an account.
- [ ] **[Recommended]** Are managed tables used for new data unless there is a specific reason to use external tables? Managed tables let Unity Catalog handle data lifecycle (storage location, file management, drop semantics) and enable features like predictive optimization. External tables are appropriate when data must remain at a fixed cloud storage path for cross-tool consumption.
- [ ] **[Recommended]** Are Unity Catalog access grants managed through groups (account-level groups synced from the IdP), not direct user grants? Direct user grants create unmanageable permission sprawl identical to the Snowflake RBAC anti-pattern.
- [ ] **[Recommended]** Is data lineage actively reviewed in Unity Catalog (table-to-table, column-level, notebook-to-table) for compliance, impact analysis, and migration planning? Lineage is captured automatically for queries that go through SQL Warehouses or shared clusters with Unity Catalog enabled.
- [ ] **[Recommended]** Are row filters and column masks applied at the Unity Catalog level for sensitive data, rather than building view-based abstractions per workspace? UC-level policies are enforced consistently across all engines (SQL Warehouse, all-purpose clusters, jobs) and external query engines via Lakehouse Federation.
- [ ] **[Optional]** Is Delta Sharing used for cross-organization or cross-cloud data sharing instead of building custom export pipelines? Delta Sharing is an open protocol that allows recipients to consume Delta tables from any platform that supports the protocol, not just Databricks.

### Delta Lake

- [ ] **[Critical]** Are all production tables stored in Delta Lake format (not raw Parquet, ORC, or CSV)? Delta provides ACID transactions, time travel, schema enforcement and evolution, MERGE operations, and is the only format Unity Catalog manages natively. Raw Parquet without a transaction log cannot be safely concurrently written.
- [ ] **[Critical]** Is OPTIMIZE configured (manually or via predictive optimization) to compact small files into the target file size (~128-256 MB)? Without OPTIMIZE, streaming writes and frequent small batches accumulate thousands of small files which destroy query performance and inflate metadata costs.
- [ ] **[Critical]** Is VACUUM run periodically (default retention 7 days) to remove unreferenced data files and reclaim storage? Time Travel queries beyond the VACUUM retention window will fail. Setting retention too low (under 24 hours) breaks concurrent writers and is blocked by default.
- [ ] **[Recommended]** Is liquid clustering used in place of partitioning and Z-ORDER for new tables? Liquid clustering avoids the cardinality and skew problems of partition pruning, supports incremental clustering changes, and is the recommended approach for tables created on Databricks Runtime 13.3+.
- [ ] **[Recommended]** Is partitioning avoided for tables under 1 TB and on columns with low cardinality? Partitioning is over-applied and frequently harms performance by creating many small files per partition. Liquid clustering or no clustering at all is usually better for medium-size tables.
- [ ] **[Recommended]** Is Change Data Feed (CDF) enabled on tables that feed downstream incremental consumers (DLT pipelines, streaming jobs, downstream sync)? CDF emits row-level change events without requiring source table redesign and is significantly cheaper than full-table reprocessing.
- [ ] **[Recommended]** Is schema evolution explicit (`mergeSchema`, `overwriteSchema`) rather than implicit, especially in production write paths? Implicit schema changes from upstream sources are a leading cause of pipeline corruption.
- [ ] **[Optional]** Are deletion vectors enabled for tables with frequent point deletes (GDPR, CCPA right-to-erasure workflows)? Deletion vectors mark rows as deleted in a side file rather than rewriting full data files, dramatically reducing the cost of small deletes.

### Data Ingestion

- [ ] **[Critical]** Is Auto Loader (`cloudFiles` source) used for incremental file ingestion from cloud storage rather than a custom file-listing job? Auto Loader uses cloud event notifications (S3 SQS, Azure Event Grid, GCS Pub/Sub) for low-latency discovery and RocksDB-based checkpointing for exactly-once semantics across millions of files without re-listing.
- [ ] **[Critical]** Is Delta Live Tables (DLT) evaluated for ETL pipelines rather than hand-coded notebooks? DLT provides declarative dataset definitions, automatic dependency resolution, data quality expectations with quarantine semantics, automatic incremental processing, and unified observability. The trade-off is a DBU premium and the pipeline-bound execution model.
- [ ] **[Recommended]** Are file sizes tuned to ~128-256 MB compacted Parquet for optimal Spark scan parallelism? Auto Loader and DLT can apply target file size automatically; raw streaming writes typically need explicit OPTIMIZE.
- [ ] **[Recommended]** Is structured streaming used with Delta Lake as both source and sink for streaming ETL? Delta supports streaming reads (with `startingVersion`/`startingTimestamp`) and provides exactly-once semantics via the Delta transaction log without requiring an external state store.
- [ ] **[Recommended]** Are Lakeflow Connect or partner connectors evaluated for SaaS source ingestion (Salesforce, Workday, ServiceNow, Google Analytics) before building custom REST API ingestion? Managed connectors handle pagination, schema evolution, and incremental sync.
- [ ] **[Optional]** Is the medallion architecture (bronze/silver/gold) used as a design pattern for layered transformations -- bronze for raw ingestion, silver for cleansed and conformed data, gold for business-aggregate marts? This is convention rather than a Databricks feature, but it maps cleanly to Unity Catalog schemas and DLT pipelines.

### Orchestration: Workflows and Jobs

- [ ] **[Critical]** Are Databricks Workflows (Jobs) used as the primary orchestrator for Databricks-native pipelines, with multi-task DAGs replacing single-notebook jobs? Multi-task jobs support task dependencies, conditional branches, retries per task, and shared job clusters across tasks.
- [ ] **[Recommended]** Are jobs defined via Databricks Asset Bundles (DAB) or Terraform rather than the UI for production pipelines? UI-defined jobs are not version-controlled, not reviewable, and not reproducible across workspaces.
- [ ] **[Recommended]** Are external orchestrators (Airflow, Dagster, Prefect) evaluated when the workflow spans multiple systems beyond Databricks (cloud storage triggers, third-party APIs, downstream warehouse loads)? Databricks Workflows are best for Databricks-native DAGs; cross-system orchestration is generally better in a dedicated tool.
- [ ] **[Recommended]** Are job alerts (email, Slack, PagerDuty webhook) configured for failures and SLA misses, with the alert routing tied to the on-call rotation rather than a shared inbox?
- [ ] **[Optional]** Are job repair runs used to re-execute only failed tasks rather than the full DAG after a partial failure? Repair runs can save significant DBU on long pipelines.

### MLflow and ML Lifecycle

- [ ] **[Critical]** Is MLflow used for experiment tracking on all model development work, with experiments organized per model or per project under Unity Catalog? Experiment tracking captures parameters, metrics, artifacts, and model versions automatically when using MLflow autologging.
- [ ] **[Critical]** Is the Unity Catalog Model Registry (not the legacy workspace model registry) used as the source of truth for model versions and lifecycle stages (development, staging, production)? The legacy workspace registry does not provide cross-workspace governance and is being deprecated.
- [ ] **[Recommended]** Are Databricks Model Serving endpoints used for online inference rather than custom Flask/FastAPI deployments? Model Serving provides auto-scaling, A/B routing, request logging to Unity Catalog, and integration with feature serving.
- [ ] **[Recommended]** Is Feature Store (now Unity Catalog feature engineering) used for feature management when features are reused across multiple models? UC feature engineering provides point-in-time correctness for training and online lookups for serving.
- [ ] **[Optional]** Are AutoML and Mosaic AI evaluated for baseline model generation and prompt-based application development? These accelerate the early phase of an ML project by automating feature engineering, model selection, and tuning.

### Security and Network Isolation

- [ ] **[Critical]** Is the workspace deployed with no-public-IP (NPIP) clusters and customer-managed VPC/VNet for production workloads? NPIP eliminates ingress exposure to the internet and is required for many regulated environments. NPIP requires customer-managed networking and a NAT gateway or PrivateLink for egress to the Databricks control plane.
- [ ] **[Critical]** Is PrivateLink configured for both the control plane (workspace UI/API) and the workspace data plane (REST API from clusters back to the control plane)? PrivateLink eliminates traffic over the public internet between customer infrastructure and the Databricks control plane. On AWS, this requires the back-end PrivateLink endpoint plus the front-end PrivateLink endpoint for browser/API access.
- [ ] **[Critical]** Are secret scopes used to store credentials, API keys, and passwords rather than embedding them in notebooks or job parameters? Databricks-backed secret scopes are sufficient for most use cases; Azure Key Vault-backed scopes are preferred when secrets are already centralized in Key Vault.
- [ ] **[Critical]** Is identity federation configured at the Databricks account level, syncing users and groups from Azure AD / Okta / Google Workspace via SCIM rather than maintaining identities per workspace? Account-level identity is required for Unity Catalog and is the only way to manage users and groups at scale.
- [ ] **[Recommended]** Are service principals (not user accounts) used for all programmatic access -- jobs, CI/CD, external integrations? Service principals can be granted Unity Catalog permissions and workspace access independently of any human user.
- [ ] **[Recommended]** Is customer-managed key (CMK) encryption configured for managed services (notebooks, results, secrets) and for the workspace storage account/bucket when compliance requires customer-controlled key material? CMK adds operational overhead for key rotation and access control.
- [ ] **[Recommended]** Is workspace IP access list configured to restrict the control plane to known corporate egress IPs, on top of (not instead of) PrivateLink? Defense in depth: PrivateLink protects the network path, IP allowlist protects against credential theft from outside the corporate network.
- [ ] **[Optional]** Is compliance security profile (HIPAA, PCI-DSS, FedRAMP) enabled at the workspace level for regulated workloads? The profile enforces additional controls including stricter cluster configurations, audit log retention, and runtime version restrictions.

### Cost Management

- [ ] **[Critical]** Is the dual-cost model understood -- every Databricks workload incurs both DBU charges (paid to Databricks) and underlying cloud instance/storage charges (paid to AWS/Azure/GCP)? DBU rates vary by tier (Standard, Premium, Enterprise) and by workload type (Jobs Compute is cheapest, All-Purpose Compute is most expensive, SQL Compute and DLT have their own rates). Cost forecasts that omit either side miss roughly half the bill.
- [ ] **[Critical]** Is Photon's DBU multiplier accounted for in cost estimates? Photon roughly doubles the per-hour DBU rate but typically reduces runtime by more than half on eligible workloads. Net cost is usually lower, but Photon should not be enabled blindly on workloads that won't benefit (e.g., Python UDF-heavy code).
- [ ] **[Critical]** Are budget alerts and DBU usage monitoring configured at the workspace and account level? Account-level usage dashboards and the system tables (`system.billing.usage`) provide DBU consumption visibility, but they require manual setup of budget thresholds and alert routing.
- [ ] **[Recommended]** Are committed-use contracts (DBCU -- Databricks Commit Units) evaluated for predictable workloads? Annual commitments offer significant discounts (typically 20-40%) but are non-refundable and require accurate consumption forecasting.
- [ ] **[Recommended]** Are jobs profiled with Spark UI and the cluster logs to identify wasted compute -- skewed shuffles, full-table scans on large unfiltered queries, missing predicate pushdown, or oversized clusters? A 20-minute profiling session on a long-running daily job often surfaces a 50%+ runtime improvement.
- [ ] **[Recommended]** Is the Databricks Premium or Enterprise tier selected based on actual feature requirements (Unity Catalog requires Premium minimum, table access control and audit logs require Premium, customer-managed keys and HIPAA compliance require Enterprise)? Tier upgrades change the DBU rate for every workload, not just the workloads that use the new features.
- [ ] **[Optional]** Is predictive optimization (managed OPTIMIZE/VACUUM) enabled for Unity Catalog managed tables to offload file maintenance to Databricks-managed serverless compute? It eliminates manual OPTIMIZE/VACUUM scheduling at a serverless DBU cost.

### Cross-Cloud Considerations

- [ ] **[Critical]** Is the cloud provider selection driven by data gravity (stay in the same cloud as the source data to avoid egress) and regulatory constraints (data residency, sovereignty)? Databricks supports AWS, Azure, and GCP but a workspace is tied to one cloud and one region.
- [ ] **[Recommended]** Is Azure Databricks chosen over AWS or GCP Databricks when the organization is Azure-native and wants tight integration with Azure AD, Azure Key Vault, Azure Monitor, and Azure DevOps? Azure Databricks is a first-party Azure resource and is operated by Microsoft and Databricks jointly, with billing through Azure.
- [ ] **[Recommended]** Is Delta Sharing used as the cross-cloud data movement strategy when data needs to be consumed from another cloud provider's Databricks workspace, rather than building S3-to-ADLS replication pipelines? Delta Sharing is platform-neutral and works without copying data.
- [ ] **[Optional]** Is Lakehouse Federation evaluated for query federation against external sources (Snowflake, Redshift, BigQuery, MySQL, PostgreSQL) without copying data into Databricks? Federation pushes predicates down to the source where possible and is appropriate for low-volume or exploratory cross-platform queries; high-volume joins should still materialize the data.

## Why This Matters

The lakehouse model is what makes Databricks distinct from both traditional warehouses (Snowflake, Redshift, BigQuery) and pure data lakes. The most expensive misconception is treating Databricks like a traditional warehouse and ignoring the open-format storage layer -- locking data into proprietary formats, building ETL to copy data out for downstream systems, or running long-lived clusters that idle during off-hours. The lakehouse value comes from having one storage tier (Delta on cloud object storage) that every workload type can read directly, with compute attached only when needed.

DBU consumption is the primary cost driver and the leading source of bill shock. Teams routinely leave 120-minute auto-termination on interactive clusters, run daily batch jobs on shared all-purpose clusters at 3x the DBU rate of job clusters, and skip Photon evaluation -- any one of these can multiply monthly spend several times over. Compounding the problem, the dual-cost model (DBUs + cloud instance fees) means cost forecasts based on instance types alone are systematically wrong by roughly 50%.

Unity Catalog adoption is the most important governance decision. Workspaces deployed on the legacy `hive_metastore` cannot access many newer features (Delta Sharing receivers, AI/BI Genie, online tables, governed model serving) and cannot apply consistent permissions across workspaces. Migrations from `hive_metastore` to Unity Catalog get harder as data and access grants accumulate, so new workspaces should start on Unity Catalog from day one.

Photon, liquid clustering, and the SQL Warehouse vs all-purpose distinction are the levers that separate teams paying $50k/month from teams paying $200k/month for similar workloads. None of these are obvious from the UI defaults -- they require deliberate decisions during workspace and pipeline design.

Network isolation (PrivateLink, no-public-IP clusters, customer-managed VPC) is non-default and is frequently bolted on later under regulatory pressure, which is significantly harder than configuring it at workspace creation. Any production workspace handling regulated data should be designed with NPIP and PrivateLink from the start.

## Common Decisions (ADR Triggers)

- **Databricks vs Snowflake vs cloud-native warehouse** -- Databricks for organizations with significant ML/AI workloads, mixed Spark/SQL teams, or a strong preference for open formats and avoiding vendor lock-in vs Snowflake for SQL-first BI and reporting workloads with simpler operational model vs cloud-native (Redshift, BigQuery, Synapse) for tight integration with a single cloud's analytics ecosystem
- **Lakehouse architecture vs traditional warehouse** -- Delta Lake on cloud object storage with separated compute (open format, multiple engines, lower storage cost) vs proprietary warehouse storage (faster for narrow workloads, no file management, simpler operations); the lakehouse trades operational complexity for openness and cost
- **Workspace topology** -- single workspace with Unity Catalog for simplicity vs multiple workspaces per environment / business unit / region for blast-radius isolation, independent administration, and cost attribution; Unity Catalog's account-level metastore means multi-workspace can share governance without sharing compute
- **Customer-managed VPC vs Databricks-managed networking** -- Databricks-managed for fastest setup and lowest operational overhead vs customer-managed VPC when network isolation, PrivateLink, no-public-IP, or VPC peering with existing infrastructure is required
- **Cluster type per workload** -- job clusters for scheduled jobs (cheapest DBU rate, ephemeral lifecycle) vs all-purpose clusters for interactive notebooks (highest DBU rate, persistent lifecycle) vs SQL Warehouses for BI/SQL (Photon by default, multi-cluster auto-scaling)
- **SQL Warehouse Classic vs Pro vs Serverless** -- Classic for cost-sensitive batch SQL with predictable patterns vs Pro for query acceleration features at moderate cost premium vs Serverless for interactive workloads with high concurrency and bursty patterns where startup latency matters
- **Photon enablement** -- enable for SQL-heavy and DataFrame-heavy workloads (typical net cost reduction despite DBU multiplier) vs disable for Python UDF-heavy or non-vectorizable workloads where Photon adds cost without benefit
- **Unity Catalog adoption strategy** -- new workspaces on Unity Catalog from day one (mandatory for new features, best long-term position) vs incremental migration of existing `hive_metastore` workspaces (necessary for existing investments, scope and effort grow with data and grant accumulation)
- **Liquid clustering vs partitioning vs Z-ORDER** -- liquid clustering for new tables on DBR 13.3+ (incremental, no cardinality concerns) vs partitioning for very large tables with high-cardinality natural partition keys (date for time-series) vs Z-ORDER for legacy tables that cannot adopt liquid clustering
- **Delta Live Tables vs hand-coded notebooks** -- DLT for declarative ETL with built-in data quality, lineage, and incremental processing (DBU premium, pipeline-bound model) vs hand-coded notebooks orchestrated by Workflows for full control (more code to maintain, no built-in quality framework)
- **MLflow Model Registry: Unity Catalog vs legacy workspace** -- Unity Catalog model registry for cross-workspace governance and lineage (required for new features, the long-term direction) vs legacy workspace registry (deprecated, no governance, scoped to a single workspace)
- **Network isolation: NPIP + PrivateLink vs default networking** -- NPIP + PrivateLink for regulated workloads or any production environment handling sensitive data (must be configured at workspace creation, hard to retrofit) vs default networking for development and non-sensitive workloads
- **Pricing tier: Standard vs Premium vs Enterprise** -- Standard rarely appropriate for production (no Unity Catalog, no audit logs) vs Premium for typical production workloads (Unity Catalog, table ACLs, audit logs, SSO) vs Enterprise for regulated workloads (HIPAA compliance security profile, customer-managed keys, FedRAMP-eligible features)

## Reference Links

- [Databricks Documentation](https://docs.databricks.com/) -- comprehensive reference for all Databricks features across AWS, Azure, and GCP
- [Lakehouse Architecture Whitepaper](https://www.databricks.com/wp-content/uploads/2020/12/cidr_lakehouse.pdf) -- the original CIDR paper introducing the lakehouse model
- [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/index.html) -- metastores, three-level namespace, external locations, lineage, and migration
- [Delta Lake Documentation](https://docs.delta.io/latest/) -- ACID transactions, time travel, OPTIMIZE/VACUUM, schema evolution, and Change Data Feed
- [Auto Loader Guide](https://docs.databricks.com/ingestion/auto-loader/index.html) -- incremental file ingestion with cloud event notifications and schema inference
- [Delta Live Tables](https://docs.databricks.com/delta-live-tables/index.html) -- declarative ETL with data quality expectations
- [Databricks SQL Warehouses](https://docs.databricks.com/sql/admin/sql-endpoints.html) -- Classic, Pro, and Serverless SQL Warehouse comparison and configuration
- [Photon Engine](https://docs.databricks.com/runtime/photon.html) -- vectorized execution, eligible workloads, and DBU pricing impact
- [Databricks Workflows (Jobs)](https://docs.databricks.com/workflows/index.html) -- multi-task DAGs, job clusters, retries, and asset bundles
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html) -- experiment tracking, model registry, and serving
- [PrivateLink Setup (AWS)](https://docs.databricks.com/security/network/classic/privatelink.html) -- back-end and front-end PrivateLink for the Databricks control plane and workspace data plane
- [Customer-Managed VPC (AWS)](https://docs.databricks.com/administration-guide/cloud-configurations/aws/customer-managed-vpc.html) -- VPC requirements, subnet sizing, and security group rules
- [Azure Databricks Networking](https://learn.microsoft.com/en-us/azure/databricks/security/network/) -- VNet injection, Azure Private Link, and no-public-IP clusters on Azure
- [Databricks Pricing](https://www.databricks.com/product/pricing) -- DBU rates by workload type and tier across AWS, Azure, and GCP
- [System Tables for Billing](https://docs.databricks.com/admin/system-tables/billing.html) -- `system.billing.usage` schema and queries for DBU consumption analysis
- [Databricks Asset Bundles](https://docs.databricks.com/dev-tools/bundles/index.html) -- IaC for jobs, pipelines, and workspace assets
- [Delta Sharing](https://delta.io/sharing/) -- open protocol for cross-organization and cross-platform data sharing
- [Lakehouse Federation](https://docs.databricks.com/query-federation/index.html) -- federated queries against external sources (Snowflake, Redshift, BigQuery, MySQL, PostgreSQL)

---

## See Also

- `providers/snowflake/data-platform.md` -- Snowflake as the alternative cloud data platform; comparison of warehouse vs lakehouse models
- `general/data-analytics.md` -- General data analytics platform patterns including warehouse vs lakehouse decision framework
- `general/data.md` -- General data architecture patterns and database selection criteria
- `general/cost.md` -- Cloud cost management strategies including DBU and committed-use planning
- `general/security.md` -- General security architecture patterns including RBAC and customer-managed encryption
- `general/disaster-recovery.md` -- DR strategy patterns applicable to multi-region and cross-cloud deployments
- `providers/aws/s3.md` -- S3 as primary storage for Databricks on AWS
- `providers/azure/storage.md` -- ADLS Gen2 as primary storage for Azure Databricks
- `providers/gcp/storage.md` -- GCS as primary storage for Databricks on GCP
- `providers/confluent/kafka.md` -- Kafka as a streaming source for Databricks structured streaming and Auto Loader
