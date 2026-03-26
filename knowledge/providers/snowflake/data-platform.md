# Snowflake Data Platform

## Scope

Snowflake cloud data platform architecture and design decisions. Covers the separated compute/storage architecture, virtual warehouse sizing and scaling, database and schema design, data sharing (direct and via Snowflake Marketplace), Snowpark for data engineering and ML, Snowpipe for continuous ingestion, Time Travel and Fail-safe for data protection, credit-based pricing model, cross-cloud replication and failover, role-based access control (RBAC), network policies, and integration patterns with cloud provider ecosystems (AWS, Azure, GCP).

## Checklist

### Architecture and Compute

- [ ] **[Critical]** Is the separation of storage and compute understood and leveraged -- storage is billed independently (compressed bytes stored) and compute is billed via virtual warehouse credits, allowing each to scale independently? Avoid treating Snowflake like a traditional on-premises data warehouse where compute and storage are coupled.
- [ ] **[Critical]** Are virtual warehouses sized appropriately for each workload type -- XS for light queries and development, S/M for typical ETL and BI workloads, L/XL/2XL+ for complex transformations and large scans? Doubling warehouse size doubles credit cost per hour but roughly halves query execution time for I/O-bound queries; CPU-bound queries may not benefit proportionally from larger warehouses.
- [ ] **[Critical]** Is multi-cluster warehousing configured for workloads with concurrency demands -- auto-scaling policy (scale out when queries queue) vs economy policy (favor queuing to minimize credits)? Are min/max cluster counts set based on observed concurrency patterns rather than guesses? Each additional cluster in a multi-cluster warehouse consumes full credits for its size.
- [ ] **[Recommended]** Are separate virtual warehouses provisioned for different workload classes -- ETL/ELT ingestion, BI/reporting queries, data science/ad-hoc exploration, and application queries -- to prevent resource contention and enable independent scaling and cost attribution?
- [ ] **[Recommended]** Is warehouse auto-suspend configured aggressively (1-5 minutes for interactive workloads, immediate for batch) to avoid paying credits for idle compute? Is auto-resume enabled so warehouses restart transparently on query submission? Default auto-suspend of 10 minutes wastes significant credits in bursty workloads.
- [ ] **[Optional]** Are query acceleration services evaluated for warehouses that experience occasional large scans among otherwise small queries, offloading the scan-heavy portions to shared compute resources rather than scaling up the entire warehouse?

### Database and Schema Design

- [ ] **[Critical]** Is the database and schema hierarchy designed to support access control boundaries -- databases as the top-level container (shared or not shared), schemas within databases to group related objects, and stages/tables/views within schemas? Cross-database queries work within an account but cross-account queries require data sharing.
- [ ] **[Critical]** Is clustering key selection based on the most common filter and join columns for large tables (hundreds of GB+)? Snowflake micro-partitions are automatically created but natural clustering degrades with DML operations. Avoid over-clustering -- clustering keys on high-cardinality columns or tables under 1 TB rarely justify the automatic reclustering credit cost.
- [ ] **[Recommended]** Are transient tables used for staging, ETL intermediate results, and other data that does not require Fail-safe protection (7-day retention after Time Travel expires)? Transient tables reduce storage costs by eliminating the Fail-safe period. Temporary tables are session-scoped and appropriate for session-local scratch data.
- [ ] **[Recommended]** Is the VARIANT column type used for semi-structured data (JSON, Avro, Parquet, ORC, XML) with automatic schema detection rather than pre-flattening into relational columns? Snowflake natively queries semi-structured data with dot notation and lateral flatten, but queries that cannot leverage columnar pruning on VARIANT subcolumns perform slower than on pre-flattened relational columns.
- [ ] **[Recommended]** Are materialized views evaluated for repeated expensive aggregation queries, with the understanding that Snowflake charges for automatic background maintenance (reclustering and refresh) credits? Standard views have no maintenance cost but re-execute the full query each time.
- [ ] **[Optional]** Are search optimization services enabled for tables with point-lookup or equality-predicate workloads on high-cardinality columns, and is the incremental storage and compute cost justified by query performance improvement?

### Data Ingestion

- [ ] **[Critical]** Is the ingestion pattern selected based on latency requirements -- bulk COPY INTO for batch loading (most cost-effective, supports all file formats), Snowpipe for continuous near-real-time ingestion (serverless, file-event-driven via cloud notifications), or Snowpipe Streaming for sub-second latency ingestion from streaming sources (Kafka, custom clients via Snowflake Ingest SDK)?
- [ ] **[Critical]** Are external stages (S3, Azure Blob, GCS) configured with appropriate storage integration objects using IAM roles (AWS), service principals (Azure), or service accounts (GCP) rather than embedded credentials? Storage integrations are reusable, auditable, and do not expose secrets in SQL statements.
- [ ] **[Recommended]** Is Snowpipe configured with auto-ingest using cloud event notifications (S3 SQS, Azure Event Grid, GCS Pub/Sub) rather than REST API calls for hands-off continuous loading? Snowpipe is billed per-file based on serverless compute, not warehouse credits -- cost is proportional to file count and size, not ingestion duration.
- [ ] **[Recommended]** Are file sizes for bulk and Snowpipe ingestion optimized to 100-250 MB compressed to balance parallelism with per-file overhead? Very small files (under 10 MB) create excessive metadata overhead in Snowpipe; very large files (over 500 MB) reduce loading parallelism.
- [ ] **[Optional]** Is Kafka connector (Snowflake Connector for Kafka) evaluated for streaming ingestion from Kafka topics, with understanding that it uses internal stages and Snowpipe or Snowpipe Streaming under the hood? The connector handles offset management and exactly-once semantics.

### Data Protection

- [ ] **[Critical]** Is Time Travel configured with appropriate retention periods -- 0 to 1 day for transient tables, up to 90 days for permanent tables on Enterprise edition or higher? Standard edition limits Time Travel to 1 day maximum. Time Travel storage costs accrue for all changed and deleted micro-partitions within the retention window.
- [ ] **[Critical]** Is Fail-safe understood as a non-user-accessible 7-day recovery window that only Snowflake Support can access for catastrophic recovery? Fail-safe applies only to permanent tables (not transient or temporary) and incurs storage costs. It is not a substitute for a backup strategy -- recovery requires a support ticket and may take hours to days.
- [ ] **[Recommended]** Are UNDROP commands tested and documented in operational runbooks for accidental table, schema, or database drops? UNDROP works within the Time Travel retention period and is the fastest recovery path for user errors. Dropping and recreating an object with the same name permanently loses the ability to UNDROP the original.
- [ ] **[Recommended]** Is cross-region or cross-cloud replication configured for disaster recovery using database replication and failover groups? Replication is asynchronous with RPO dependent on replication frequency. Failover groups include databases, warehouses, users, roles, and other account objects for a complete failover target.
- [ ] **[Optional]** Are zero-copy clones used for development, testing, and backup snapshots? Clones share underlying micro-partitions with the source (no additional storage cost until data diverges) and can be created in seconds regardless of data size. Cloning a production database for testing is a common pattern that avoids full data copies.

### Security and Access Control

- [ ] **[Critical]** Is Snowflake's role-based access control (RBAC) implemented with a role hierarchy -- ACCOUNTADMIN (top-level, restricted to break-glass), SECURITYADMIN (manages grants and roles), SYSADMIN (owns databases and warehouses), and custom functional roles granted to SYSADMIN? Never use ACCOUNTADMIN as a default working role. All custom roles should be granted to SYSADMIN to ensure ACCOUNTADMIN can manage the entire hierarchy.
- [ ] **[Critical]** Is network policy configured to restrict account access to known IP ranges (CIDR allow-lists) and is the policy applied at the account level or to specific users? Without a network policy, a Snowflake account is accessible from any IP address with valid credentials.
- [ ] **[Critical]** Is multi-factor authentication (MFA) enforced for all human users, especially ACCOUNTADMIN? Snowflake supports Duo MFA natively. Key pair authentication is recommended for service accounts and programmatic access instead of password-based authentication.
- [ ] **[Recommended]** Are column-level security (dynamic data masking) and row-level security (row access policies) implemented for sensitive data, using masking policies that return masked values based on the querying role? Masking policies are schema-level objects that can be applied to columns across tables without modifying the underlying data.
- [ ] **[Recommended]** Is Tri-Secret Secure (customer-managed key + Snowflake-managed key + composite key) enabled for Business Critical edition or higher when compliance requires customer-controlled encryption keys? Standard and Enterprise editions use Snowflake-managed encryption only.
- [ ] **[Recommended]** Are access grants managed through roles (GRANT TO ROLE) rather than directly to users (GRANT TO USER)? Direct user grants create unmanageable permission sprawl. Use database roles for object-level permissions within a database and account roles for cross-database and warehouse access.
- [ ] **[Optional]** Is external tokenization evaluated when sensitive data must be tokenized before loading into Snowflake, with external functions calling a tokenization service for detokenization at query time? This adds latency and cost but keeps plaintext sensitive data outside Snowflake entirely.

### Data Sharing and Collaboration

- [ ] **[Critical]** Is Snowflake Secure Data Sharing used instead of ETL-based data movement when sharing data between Snowflake accounts? Direct sharing provides real-time access to shared data without copying, using reader accounts for non-Snowflake consumers (reader accounts incur provider-side compute costs) and standard shares for Snowflake-to-Snowflake sharing (consumer uses their own compute).
- [ ] **[Recommended]** Are listings on Snowflake Marketplace evaluated for acquiring third-party data (weather, financial, demographic) rather than building custom ingestion pipelines? Marketplace data is shared via the same zero-copy mechanism and stays current without provider-side ETL.
- [ ] **[Recommended]** Is secure view or secure UDF used for shared objects to prevent consumers from reverse-engineering underlying data through query profiling or DDL inspection? Secure views hide the view definition and disable query plan optimizations that could expose filtered data.
- [ ] **[Optional]** Are data clean rooms evaluated for privacy-preserving collaboration where two parties need to run joint analytics without exposing raw data to each other?

### Snowpark and Programmability

- [ ] **[Recommended]** Is Snowpark evaluated for data engineering (Python, Java, Scala) workloads that require procedural logic, ML model training (Snowpark ML), or UDFs that run inside Snowflake's compute layer rather than extracting data to external compute? Snowpark DataFrames are lazily evaluated and push computation to the warehouse.
- [ ] **[Recommended]** Are Snowflake Notebooks or Streamlit in Snowflake evaluated for interactive data exploration and lightweight application development that keeps data within the Snowflake security perimeter, eliminating the need to extract data to external tools?
- [ ] **[Optional]** Are external functions evaluated for calling external APIs (AWS Lambda, Azure Functions, GCP Cloud Functions) from within Snowflake SQL when business logic cannot be implemented natively? External functions add network latency and require API integration object configuration with cloud provider IAM.

### Cost Management

- [ ] **[Critical]** Is the credit-based pricing model understood -- credits are consumed by virtual warehouses (per-second billing, minimum 60 seconds), serverless features (Snowpipe, auto-clustering, materialized view maintenance, replication, search optimization), and cloud services (query compilation, metadata operations, exceeding 10% of daily warehouse credit threshold)? Storage is billed separately per TB/month (on-demand or pre-purchased capacity).
- [ ] **[Critical]** Are resource monitors configured at the account and warehouse level with credit quotas and actions (notify, suspend, suspend immediately) to prevent runaway costs from uncontrolled queries or misconfigured auto-scaling? Without resource monitors, a single runaway query on a 4XL warehouse can consume hundreds of credits per hour.
- [ ] **[Recommended]** Is the pricing tier selected based on feature requirements -- Standard (basic features, 1-day Time Travel), Enterprise (multi-cluster warehouses, 90-day Time Travel, masking policies, row access policies), Business Critical (HIPAA/PCI compliance, Tri-Secret Secure, failover/failback), or VPS (dedicated infrastructure)? Upgrading editions is straightforward; downgrading is not supported.
- [ ] **[Recommended]** Are pre-purchased capacity commitments evaluated for predictable workloads (lower per-credit cost) vs on-demand pricing for variable or proof-of-concept workloads? Capacity commitments are annual and non-refundable.
- [ ] **[Recommended]** Is the ACCOUNT_USAGE schema (SNOWFLAKE database) queried regularly to monitor credit consumption by warehouse, user, and query type using views like WAREHOUSE_METERING_HISTORY, QUERY_HISTORY, and STORAGE_USAGE? These views have up to 45-minute latency but provide 365 days of history.

### Cross-Cloud and Replication

- [ ] **[Critical]** Is the Snowflake deployment region and cloud provider selected based on data residency requirements, proximity to data sources (minimize egress from source cloud), and proximity to consumers? Snowflake runs on AWS, Azure, and GCP, but an account is tied to a specific cloud and region. Cross-cloud access requires replication or data sharing across regions.
- [ ] **[Recommended]** Is database replication configured for cross-region disaster recovery or for placing read-only replicas closer to geographically distributed consumers? Replication is asynchronous and incurs compute credits (for data transfer) and storage costs (for the replica). Replication frequency is configurable from minutes to hours.
- [ ] **[Optional]** Is a multi-cloud Snowflake strategy evaluated when the organization operates on multiple cloud providers, using Snowflake's cross-cloud replication and data sharing to provide a unified data platform regardless of which cloud hosts the source systems?

## Why This Matters

Snowflake's separated compute/storage architecture is fundamentally different from traditional data warehouses and most cloud-native alternatives. The most expensive mistake is treating Snowflake like an on-premises appliance -- leaving large warehouses running 24/7, using a single warehouse for all workloads, or ignoring auto-suspend configuration. Credit consumption is the primary cost driver, and without resource monitors and warehouse discipline, monthly bills can escalate 5-10x beyond projections.

Virtual warehouse sizing is frequently wrong on first deployment. Teams default to large warehouses assuming bigger is better, but many BI and reporting queries are metadata-only or scan small datasets where an XS warehouse completes in the same time as a 4XL at a fraction of the cost. Conversely, undersized warehouses cause complex ETL jobs to spill to disk and run far longer than expected.

Time Travel and Fail-safe are powerful but misunderstood. Teams assume Fail-safe is a backup they can access -- it is not. Only Snowflake Support can recover data from Fail-safe, and recovery is neither instant nor guaranteed for partial table recovery. Time Travel is the user-accessible safety net and should be configured with retention periods that match the data's criticality.

Data sharing is Snowflake's strongest differentiator. Organizations that default to ETL-based data movement between Snowflake accounts waste compute, create stale copies, and miss the zero-copy sharing model that is one of the primary reasons to choose Snowflake over alternatives. Similarly, Snowpark pushes computation into the platform rather than extracting data to external tools, maintaining the security perimeter and reducing data movement costs.

RBAC misconfiguration is the most common security issue. Using ACCOUNTADMIN as a daily driver, granting privileges directly to users instead of roles, or failing to enforce MFA on privileged accounts creates audit findings and increases blast radius for credential compromise.

## Common Decisions (ADR Triggers)

- **Snowflake edition selection** -- Standard for cost-sensitive workloads with basic requirements vs Enterprise for multi-cluster warehousing, extended Time Travel, and column/row-level security vs Business Critical for regulated industries requiring HIPAA/PCI compliance, Tri-Secret Secure encryption, and native failover
- **Warehouse sizing strategy** -- right-size per workload class with separate warehouses for ETL, BI, and ad-hoc vs shared warehouses with multi-cluster auto-scaling for simplicity; oversizing wastes credits while undersizing causes query queuing and user frustration
- **Batch vs continuous ingestion** -- COPY INTO for batch windows (hourly, daily) with lowest cost vs Snowpipe for continuous file-event-driven ingestion (minutes latency) vs Snowpipe Streaming for sub-second requirements; each has different cost models and operational complexity
- **Data sharing vs ETL replication** -- Secure Data Sharing for real-time zero-copy access between accounts vs ETL pipelines that create independent copies; sharing eliminates data staleness and copy storage but requires both parties on Snowflake (or reader accounts at provider cost)
- **Snowpark vs external compute** -- Snowpark for data engineering and ML within Snowflake's compute and security perimeter vs external tools (Spark, Databricks, Python on EC2) for workloads requiring ecosystem libraries or GPU compute not available in Snowflake
- **Time Travel retention period** -- minimal retention (1 day) for cost-sensitive staging data vs extended retention (up to 90 days on Enterprise) for critical business tables; longer retention increases storage costs for every changed micro-partition
- **Single-account vs multi-account topology** -- single account with database-level isolation for simplicity vs multiple accounts (by environment, business unit, or region) with data sharing between them for stronger blast-radius isolation and independent administration
- **Clustering key strategy** -- no explicit clustering for tables under 1 TB or with varied access patterns vs defined clustering keys on large fact tables with consistent filter predicates; automatic reclustering incurs ongoing serverless compute credits
- **Customer-managed encryption (Tri-Secret Secure)** -- Snowflake-managed encryption (default, zero operational overhead) vs Tri-Secret Secure for compliance regimes that mandate customer-controlled key material (Business Critical edition required, adds key management operational burden)
- **Cross-cloud replication strategy** -- single-region deployment for simplicity and lowest cost vs cross-region replication for DR (RPO depends on replication frequency) vs cross-cloud replication for multi-cloud organizations needing a unified data layer

## Reference Links

- [Snowflake Documentation](https://docs.snowflake.com/) -- comprehensive reference for all Snowflake features, SQL commands, and administration
- [Virtual Warehouses](https://docs.snowflake.com/en/user-guide/warehouses) -- warehouse sizing, auto-scaling, multi-cluster configuration, and credit consumption
- [Data Loading Overview](https://docs.snowflake.com/en/user-guide/data-load-overview) -- bulk loading, Snowpipe, Snowpipe Streaming, file formats, and staging
- [Time Travel](https://docs.snowflake.com/en/user-guide/data-time-travel) -- retention periods, UNDROP, AT/BEFORE queries, and edition-specific limits
- [Fail-safe](https://docs.snowflake.com/en/user-guide/data-failsafe) -- 7-day non-user-accessible recovery, storage costs, and scope
- [Secure Data Sharing](https://docs.snowflake.com/en/user-guide/data-sharing-intro) -- shares, reader accounts, listings, and cross-region/cross-cloud sharing
- [Access Control Framework](https://docs.snowflake.com/en/user-guide/security-access-control-overview) -- RBAC, DAC, role hierarchy, system-defined roles, and privilege model
- [Snowpark Developer Guide](https://docs.snowflake.com/en/developer-guide/snowpark/index) -- Python, Java, and Scala APIs for data engineering and ML within Snowflake
- [Database Replication and Failover](https://docs.snowflake.com/en/user-guide/db-replication-intro) -- cross-region and cross-cloud replication, failover groups, and RPO considerations
- [Resource Monitors](https://docs.snowflake.com/en/user-guide/resource-monitors) -- credit quotas, notification actions, and account/warehouse-level monitoring
- [Understanding Snowflake Pricing](https://docs.snowflake.com/en/user-guide/cost-understanding-overall) -- credits, storage, data transfer, and serverless feature billing
- [Network Policies](https://docs.snowflake.com/en/user-guide/network-policies) -- IP allow/block lists, account-level and user-level policies
- [Snowflake Connector for Kafka](https://docs.snowflake.com/en/user-guide/kafka-connector) -- streaming ingestion from Kafka topics via Snowpipe or Snowpipe Streaming

---

## See Also

- `general/data.md` -- General data architecture patterns and database selection criteria
- `general/data-analytics.md` -- Data analytics platform patterns including warehouse vs lakehouse
- `general/cost.md` -- Cloud cost management strategies applicable to credit-based pricing
- `general/security.md` -- General security architecture patterns including RBAC and encryption
- `general/disaster-recovery.md` -- DR strategy patterns applicable to cross-region replication
- `providers/aws/s3.md` -- S3 as external stage for Snowflake data loading on AWS
- `providers/azure/storage.md` -- Azure Blob as external stage for Snowflake data loading on Azure
- `providers/gcp/storage.md` -- GCS as external stage for Snowflake data loading on GCP
