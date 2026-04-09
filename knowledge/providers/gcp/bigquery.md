# Google BigQuery

## Scope

BigQuery is GCP's serverless analytics data warehouse. Covers the slot-based capacity model, on-demand vs reservations (capacity-based pricing), partitioning and clustering for query performance and cost control, materialized views, authorized views and column-level security, row-level security, BigQuery Omni for cross-cloud analytics, BigQuery ML for in-database machine learning, the load patterns (batch load, streaming insert, BigQuery Storage Write API, Dataflow, Datastream), the integration with Cloud Storage as the data lake substrate, the cost optimization patterns (the most-asked BigQuery topic), and the audit characteristics of unpartitioned tables and over-permissive dataset access. Does not cover Looker / Looker Studio (separate visualization layer).

## Checklist

- [ ] **[Critical]** **Partition every large table** (typically `> 1 GB`) by a time column or by integer range. Querying a partitioned table with a `WHERE` clause on the partition key scans only the matching partitions; querying without the filter scans the entire table. The cost difference is often 50–100x for typical analytic queries on date-partitioned data.
- [ ] **[Critical]** **Cluster tables** by columns frequently used in `WHERE` and `JOIN` clauses. Clustering is free, can be combined with partitioning, and reduces both cost and query latency. The most useful clustering columns are high-cardinality columns used as filters (user IDs, customer IDs, region codes).
- [ ] **[Critical]** **Choose between on-demand and reservations deliberately**. On-demand pricing is per-TB-scanned ($6.25/TB at the time of writing) — appropriate for unpredictable workloads where the team does not know what query volume to expect. Reservations (capacity-based) are per-slot-hour, with autoscaling — appropriate for steady or predictable workloads where the team can model the slot demand. The break-even is typically around 1–2 PB scanned per month per project.
- [ ] **[Critical]** Use **customer-managed encryption keys (CMEK)** for any dataset holding sensitive data. The Google-managed key is sufficient for non-regulated workloads only. CMEK requires the BigQuery service agent in the project to have `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key — this is set up automatically when the dataset is configured for CMEK but should be verified.
- [ ] **[Critical]** Use **column-level security** for any dataset where some columns are more sensitive than others. Column-level security uses **policy tags** in Data Catalog and the `cloudresourcemanager.googleapis.com/policyTags/X` IAM permission to enforce per-column read access. The pattern is "the dataset is readable to the analytics team, but the SSN column requires an additional grant".
- [ ] **[Critical]** Use **row-level security** for any dataset where different users should see different rows of the same table. Row-level security uses access policies that filter rows based on the requesting user's identity. The pattern is "everyone can query the customer table, but each tenant only sees their own customer rows".
- [ ] **[Critical]** **Disable public dataset sharing by default**. BigQuery datasets can be shared with `allAuthenticatedUsers` or `allUsers`, which makes the dataset effectively public. Audit existing datasets for these grants and remove any that are not intentionally public.
- [ ] **[Recommended]** Use **authorized views** to provide a read-only, query-defined projection of a sensitive table to a downstream user. The downstream user is granted access to the view only, not the underlying table; the view runs with the authority of the dataset owner. This is the canonical pattern for "expose a subset of the data without copying it".
- [ ] **[Recommended]** Use **materialized views** for queries that are run repeatedly with high cost. Materialized views maintain a precomputed result set that is incrementally refreshed as the source table changes. The query cost drops from "scan the source table" to "scan the materialized view"; the materialization itself incurs storage cost.
- [ ] **[Recommended]** Set **query cost controls** at the project level: maximum bytes billed per query, maximum bytes billed per day. These prevent runaway queries (or runaway cost). The right values depend on the team's normal query volume, but a typical setting is 100–500 GB per query and 5–20 TB per day for a development project.
- [ ] **[Recommended]** Use the **BigQuery Storage Write API** for high-throughput streaming ingestion (not the legacy `tabledata.insertAll` streaming insert). The Storage Write API is exactly-once, schema-aware, and significantly cheaper than the legacy streaming insert.
- [ ] **[Recommended]** Use **scheduled queries** for routine ETL within BigQuery (e.g., daily aggregations, materialized view refreshes). Scheduled queries are free to schedule and incur only the normal query cost when they run.
- [ ] **[Optional]** Use **BigQuery Omni** when the data needs to stay in a different cloud (S3, Azure Blob Storage) for residency or contractual reasons. Omni runs BigQuery's query engine in the other cloud, with the data never leaving its origin. Pricing is different from standard BigQuery and the feature set is more limited.
- [ ] **[Optional]** Use **BigQuery ML** for in-database machine learning when the team has SQL skills but limited ML engineering capacity. BigQuery ML supports several model types (linear regression, logistic regression, k-means, ARIMA, AutoML Tables, imported TensorFlow models) and is the lowest-friction way to add ML to a SQL-centric team.
- [ ] **[Optional]** Enable **time travel** for tables that hold critical data — BigQuery automatically retains snapshots of tables for the last 7 days (configurable up to 7 days). This allows recovery from accidental deletes and updates.

## Why This Matters

BigQuery is the easiest data warehouse in GCP to misuse expensively, in two opposite directions:

1. **Querying unpartitioned tables on-demand**. A 1 TB unpartitioned table queried 100 times per day with a date filter that does nothing (because there are no partitions) costs $625/day = $19K/month for what looks like the same query the team has always run. The fix is one ALTER TABLE statement to add a partition, plus updating the queries to use the partition column. Most teams discover this only when the bill arrives.

2. **Buying reservations that exceed actual usage**. A team commits to 1000 slots ($30K/month) based on "we need a lot of capacity for the new project". The new project never materializes, the slots sit at 10% utilization, and the team is paying 10x what on-demand would have cost. The fix is to use **autoscaling slot reservations** (max + baseline) so the slots scale up only when actually needed.

The audit consequence of the first failure is "the cost team finds the query and the developer is asked to fix it". The audit consequence of the second is "the FinOps team finds the underused reservation and asks the project owner to justify it". Both are preventable with cost controls and basic monitoring.

A secondary failure mode that compounds the first two: **schemas with no documentation**. Tables get created with column names that made sense to the original engineer and are opaque to everyone else. The lack of documentation makes it harder to know which columns to filter on (so queries scan more than they should), harder to know what is sensitive (so column-level security is not applied), and harder to know what is being collected (so privacy compliance becomes harder). Use **table descriptions and column descriptions** as part of the table definition.

## Common Decisions (ADR Triggers)

- **On-demand vs reservations** — on-demand for unpredictable workloads, dev/test environments, and low-volume teams. Reservations for steady or predictable workloads where the slot demand can be modeled. Mixed (reservations for production, on-demand for dev/test) is common and reasonable.
- **Partition by time vs integer range** — time-based for time-series data (events, logs, transactions). Integer range for non-temporal data with a natural integer key (customer ID buckets, region IDs). Pick the one that matches the most common query filter.
- **Clustering columns selection** — cluster on the columns most frequently used in `WHERE` and `JOIN` clauses, in order from most-filtered to least-filtered. Clustering on columns that are not queried adds storage cost without query benefit.
- **Streaming insert vs batch load** — Storage Write API for any new streaming workload. Batch load for any non-streaming use case (cheaper per byte, no per-row cost). Avoid the legacy `tabledata.insertAll` streaming insert.
- **Authorized view vs row-level security vs separate dataset** — authorized view for "give this team a column-restricted projection of one table". Row-level security for "different users should see different rows of the same table". Separate dataset for "this team should not see anything from the source dataset".
- **CMEK vs Google-managed** — CMEK for regulated and sensitive workloads. Google-managed for everything else. Decision should be made per data classification.

## Reference Architectures

### High-volume event ingestion

- Events arrive via Pub/Sub
- Dataflow streaming pipeline reads from Pub/Sub and writes to BigQuery via the Storage Write API
- BigQuery table is partitioned by day and clustered by `event_type, user_id`
- Materialized views compute the most-frequent aggregations (daily active users, events per type)
- Scheduled query runs nightly to compute the previous day's aggregates and writes them to a separate analytics table
- Tables hold 90 days of raw events; older data is archived to Cloud Storage with a lifecycle policy

### Multi-tenant analytics with row-level security

- One BigQuery dataset shared by multiple tenants
- Tables include a `tenant_id` column
- Row-level security policy: `tenant_id = SESSION_USER_ATTRIBUTE("tenant_id")` (set by the application's auth context)
- Each tenant queries the same table, sees only their own rows
- Authorized view exposes a subset of columns to a separate "analytics" service account that needs aggregated cross-tenant statistics

### Sensitive data with column-level security

- Customer table with columns: `customer_id`, `name`, `email`, `address`, `ssn`, `signup_date`
- Policy tags applied:
  - `non-pii`: customer_id, signup_date
  - `pii-low`: name, email
  - `pii-high`: address, ssn
- Analytics team has `roles/datacatalog.categoryFineGrainedReader` for `non-pii` and `pii-low` only
- Compliance team has access to all three categories
- Engineering team has access to `non-pii` only

---

## Reference Links

- [BigQuery documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery slot reservations](https://cloud.google.com/bigquery/docs/slots)
- [Partitioned tables](https://cloud.google.com/bigquery/docs/partitioned-tables)
- [Clustered tables](https://cloud.google.com/bigquery/docs/clustered-tables)
- [Column-level security with policy tags](https://cloud.google.com/bigquery/docs/column-level-security)
- [Row-level security](https://cloud.google.com/bigquery/docs/managing-row-level-security)
- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [BigQuery cost optimization best practices](https://cloud.google.com/bigquery/docs/best-practices-costs)

## See Also

- `providers/gcp/data.md` — broader GCP data services
- `providers/gcp/storage.md` — Cloud Storage as the data lake substrate
- `providers/gcp/kms.md` — Cloud KMS for CMEK
- `providers/gcp/iam-organizations.md` — IAM model for dataset access
- `providers/aws/dynamodb.md` — different shape (NoSQL, not analytics)
- `general/data.md` — general data architecture
- `general/data-classification.md` — data classification driving column-level security
